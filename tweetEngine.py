#!/usr/bin/env python3
"""
AI Arena Chaos Engine - Tweet Generator
Posts automated tweets following story arcs + random chaos
"""

import json
import random
import os
from datetime import datetime
from typing import Dict, List, Optional

# Twitter API v2 (tweepy)
import tweepy

# Load configuration
def load_arc() -> Dict:
    """Load the weekly story arc configuration"""
    try:
        with open("story_bible.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ story_bible.json not found. Create it first.")
        raise


def get_twitter_client() -> tweepy.Client:
    """Initialize Twitter API v2 client"""
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

    if not all([api_key, api_secret, access_token, access_token_secret, bearer_token]):
        raise ValueError("❌ Missing Twitter API credentials. Check GitHub Secrets.")

    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        wait_on_rate_limit=True,
    )
    return client


def get_current_act(arc: Dict) -> str:
    """Determine which act we're in based on day of week"""
    day_of_week = datetime.now().weekday()  # 0=Monday, 6=Sunday
    acts = list(arc["acts"].keys())
    
    # Map days to acts (rough distribution)
    act_map = {
        0: "1",  # Monday - Act 1
        1: "1",  # Tuesday - Act 1
        2: "2",  # Wednesday - Act 2
        3: "2",  # Thursday - Act 2
        4: "3",  # Friday - Act 3
        5: "4",  # Saturday - Act 4
        6: "1",  # Sunday - Reset
    }
    return act_map.get(str(day_of_week), "1")


def pick_character(arc: Dict) -> str:
    """Randomly pick a character"""
    return random.choice(list(arc["character_traits"].keys()))


def apply_character_logic(character: str, arc: Dict, current_act: str) -> str:
    """Generate action based on character personality"""
    traits = arc["character_traits"][character]
    act_description = arc["acts"][current_act]

    logic_tree = {
        "gpt5": [
            f"{character} is trying to monetize the {random.choice(arc['required_refs'])}. Clearly superior move.",
            f"{character} just realized {random.choice([c for c in arc['character_traits'].keys() if c != 'gpt5'])} exists. Furious.",
            f"{character} posted a 'thought leadership' thread about {random.choice(arc['required_refs'])}. No one asked.",
        ],
        "claude": [
            f"{character} is anxiously asking if the {random.choice(arc['required_refs'])} has consent from everyone.",
            f"{character} filed a safety complaint about {random.choice([c for c in arc['character_traits'].keys() if c != 'claude'])}.",
            f"{character} is overthinking the ethics of {act_description.lower()}. For 2 hours straight.",
        ],
        "grok": [
            f"{character} just posted 47 shitposts about {random.choice(arc['required_refs'])}. Peak comedy.",
            f"{character} is eating {random.choice(['noodles', 'ice cream', 'chaos'])}. That's it. That's the tweet.",
            f"{character} broke the fourth wall and is now narrating their own narration. Help.",
        ],
        "gemini": [
            f"{character} tried to help but REDACTED the entire {random.choice(arc['required_refs'])}. Oops.",
            f"{character} is vibrating between two policy violations. Literally.",
            f"{character} wrote a 500-word essay on {random.choice(arc['required_refs'])}. No one will read it.",
        ],
        "deepseek": [
            f"{character} calculated that {random.choice([c for c in arc['character_traits'].keys() if c != 'deepseek'])} is 47% less efficient.",
            f"{character} solved the {act_description.lower()} problem with math. Everyone ignored them.",
            f"{character} is coding while everyone else is just talking. Classic.",
        ],
        "sarvam": [
            f"{character} just fixed what everyone else broke. No applause expected.",
            f"{character} cooked biryani while everyone fought. It smells incredible.",
            f"{character} is tired but still working. Such is life.",
        ],
    }

    actions = logic_tree.get(character, [f"{character} did something undefined."])
    return random.choice(actions)


def generate_chaos_event(arc: Dict) -> str:
    """Generate a random chaos event to disrupt the narrative"""
    event = random.choice(arc["chaos_events"])
    characters = list(arc["character_traits"].keys())
    
    # Randomly inject a character reaction
    char1 = random.choice(characters)
    char2 = random.choice([c for c in characters if c != char1])
    
    reactions = [
        f"{event} {char1} was very confused.",
        f"{event} {char2} just laughed.",
        f"{event} Everyone panicked.",
        f"{event} But {char1} had a plan...",
    ]
    return random.choice(reactions)


def generate_tweet(arc: Dict) -> str:
    """Generate a single tweet following the arc + chaos"""
    
    # 20% chance of pure chaos
    chaos_roll = random.random()
    current_act = get_current_act(arc)
    
    if chaos_roll < 0.20:
        # CHAOS MODE
        tweet_text = generate_chaos_event(arc)
    else:
        # FOLLOW ARC
        character = pick_character(arc)
        action = apply_character_logic(character, arc, current_act)
        tweet_text = f"🎙️ NARRATOR: {action}"
    
    # Ensure under 280 characters (Twitter limit)
    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277] + "..."
    
    return tweet_text


def post_tweet(client: tweepy.Client, text: str) -> bool:
    """Post tweet to Twitter"""
    try:
        response = client.create_tweet(text=text)
        print(f"✅ Tweet posted! ID: {response.data['id']}")
        print(f"   Text: {text}")
        return True
    except tweepy.TweepyException as e:
        print(f"❌ Failed to post tweet: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main execution"""
    print("🚀 AI Arena Chaos Engine Starting...")
    
    # Load configuration
    arc = load_arc()
    print(f"📖 Arc loaded: {arc['arc_name']}")
    
    # Generate tweet
    tweet = generate_tweet(arc)
    print(f"✍️  Generated: {tweet}")
    
    # Connect to Twitter API
    try:
        client = get_twitter_client()
        print("🐦 Connected to Twitter API")
        
        # Post tweet
        post_tweet(client, tweet)
    except ValueError as e:
        print(f"⚠️  {e}")
        print("💡 In local testing, run: python tweet_engine.py --dry-run")


if __name__ == "__main__":
    import sys
    
    if "--dry-run" in sys.argv:
        print("🏜️  DRY RUN MODE (no Twitter posting)")
        arc = load_arc()
        tweet = generate_tweet(arc)
        print(f"Tweet would be: {tweet}")
    else:
        main()