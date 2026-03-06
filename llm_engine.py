import os
import json
import random
import google.genai as genai
from tweetEngine import load_arc, get_current_act, pick_character, get_other_characters

# 1. Setup Gemini API
# Get your key from https://aistudio.google.com/
os.environ["GEMINI_API_KEY"] = "AIzaSyBBwW_D3vstwrFG90HM64kORSs7zUxT18k"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_llm_tweet(arc):
    current_act_id = get_current_act(arc)
    act_desc = arc["acts"][current_act_id]
    char_name = pick_character(arc)
    char_info = arc["characters"][char_name]
    target = random.choice(get_other_characters(arc, char_name))
    ref = random.choice(arc["required_refs"])

    # The "Secret Sauce" Prompt
    prompt = f"""
    You are an AI character in a chaotic meta-narrative called "{arc['arc_name']}".
    The theme of this season is: {arc['season_theme']}
    
    CURRENT SETTING: {act_desc}
    YOUR CHARACTER: {char_name.upper()}
    TRAITS: {", ".join(char_info['traits'])}
    BIO: {char_info['description']}
    
    SCENARIO: You are interacting with {target}. You must mention "{ref}".
    
    TASK: Write a tweet (max 280 chars) from your perspective. 
    - Do NOT use hashtags. 
    - Do NOT use "Narrator" or "Chaos" labels.
    - Be authentic to your traits. 
    - If you are GPT-5, be smug and fake-friendly. 
    - If you are Gemini, be glitchy and over-cautious.
    - Use a touch of wit.
    """

    response = model.generate_content(prompt)
    return response.text.strip().replace('"', '')

if __name__ == "__main__":
    arc = load_arc()
    print(f"--- LLM GENERATED TWEET ({get_current_act(arc)}) ---")
    print(generate_llm_tweet(arc))