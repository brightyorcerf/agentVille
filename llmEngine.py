import os
import random
import tweepy
from google import genai 
from tweetEngine import load_arc, get_current_act, pick_character, get_other_characters

# 1. Setup Gemini
api_key = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash") 
gemini_client = genai.Client(api_key=api_key)

# 2. Setup Twitter (Using the names you have in your .env/Secrets)
twitter_client = tweepy.Client(
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)

def generate_llm_tweet():
    arc = load_arc()
    current_act_id = get_current_act(arc)
    act_desc = arc["acts"][current_act_id]
    char_name = pick_character(arc)
    char_info = arc["characters"][char_name]
    target = random.choice(get_other_characters(arc, char_name))
    ref = random.choice(arc["required_refs"])

    prompt = f"""
    CONTEXT: You are writing a tweet for a chaotic AI game show called "{arc['arc_name']}".
    SEASON THEME: {arc['season_theme']}
    CURRENT ACT: {act_desc}
    YOUR CHARACTER: {char_name}
    TRAITS: {", ".join(char_info['traits'])}
    BIO: {char_info['description']}
    SCENARIO: You are tweeting about {target}.
    REQUIRED WORD: You must naturally include the word "{ref}".
    
    RULES:
    - Be witty, meta, and slightly unhinged
    - Write as the character (1st person)
    - MAXIMUM 240 CHARACTERS.
    - No hashtags
    """

    response = gemini_client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    ) 
    return response.text.strip()

if __name__ == "__main__":
    print("\n--- 🤖 GENERATING & POSTING ---")
    try:
        # Generate
        tweet = generate_llm_tweet()
        print(f"Draft: {tweet} ({len(tweet)} chars)")
        
        # Post
        if len(tweet) <= 280:
            twitter_client.create_tweet(text=tweet)
            print("✅ Successfully posted to X!")
        else:
            print("❌ Tweet too long, not posting.")
            
    except Exception as e:
        print(f"❌ Error: {e}")