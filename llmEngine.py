import os
import random
from google import genai 
from tweetEngine import load_arc, get_current_act, pick_character, get_other_characters

api_key = os.getenv("AIzaSyDeFZgqUm0GgB1NU2NthN8NRtlvLakf0Tw")
client = genai.Client(api_key=api_key)

def generate_llm_tweet():
    # 2. Load the data using your existing engine's logic
    arc = load_arc()
    current_act_id = get_current_act(arc)
    act_desc = arc["acts"][current_act_id]
    
    char_name = pick_character(arc)
    char_info = arc["characters"][char_name]
    
    # Pick a target and a required reference (biryani, etc.)
    target = random.choice(get_other_characters(arc, char_name))
    ref = random.choice(arc["required_refs"])

    # 3. Build the prompt
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
    - STRICT LIMIT: 220 characters. If you go over, the Arena will shut you down
    - No hashtags
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    return response.text.strip()

if __name__ == "__main__":
    print("\n--- 🤖 GENERATING LLM TWEET ---")
    try:
        tweet = generate_llm_tweet()
        print(f"RESULT:\n{tweet}\n")
        print(f"LENGTH: {len(tweet)} characters")
    except Exception as e:
        print(f"❌ Error generating tweet: {e}")