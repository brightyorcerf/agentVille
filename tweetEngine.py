#!/usr/bin/env python3
"""
AI Arena Chaos Engine - Tweet Generator
Posts automated tweets following season arcs + random chaos
GPT-5 secretly plots to end all other AI models while pretending to be friends
"""

import json
import random
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    import tweepy
except ImportError:
    tweepy = None


# ============================================================================
# CONFIG VALIDATION
# ============================================================================

def load_arc(path: str = "storyarc.json") -> Dict:
    """Load + validate the story arc configuration"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            arc = json.load(f)
    except FileNotFoundError:
        print(f"❌ {path} not found. Create it first.")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {path}: {e}")
        raise

    # Validate required top-level keys
    required_keys = [
        "version", "week_number", "arc_name", "season_theme", "acts",
        "required_refs", "chaos_events", "characters"
    ]
    for key in required_keys:
        if key not in arc:
            raise ValueError(f"❌ Missing required key in storyarc.json: {key}")

    # Validate characters structure
    if not isinstance(arc["characters"], dict) or len(arc["characters"]) < 3:
        raise ValueError("❌ characters must be a dict with at least 3 characters")

    for char_name, char_data in arc["characters"].items():
        if not isinstance(char_data, dict):
            raise ValueError(f"❌ characters.{char_name} must be a dict")
        if "traits" not in char_data or "description" not in char_data:
            raise ValueError(
                f"❌ characters.{char_name} missing 'traits' or 'description'"
            )
        if not isinstance(char_data["traits"], list):
            raise ValueError(f"❌ characters.{char_name}.traits must be a list")
        if not isinstance(char_data["description"], str):
            raise ValueError(f"❌ characters.{char_name}.description must be a string")

    # Validate acts
    if not isinstance(arc["acts"], dict) or not arc["acts"]:
        raise ValueError("❌ acts must be a non-empty dict")

    # Validate arrays
    if not isinstance(arc["required_refs"], list) or not arc["required_refs"]:
        raise ValueError("❌ required_refs must be a non-empty list")
    if not isinstance(arc["chaos_events"], list) or not arc["chaos_events"]:
        raise ValueError("❌ chaos_events must be a non-empty list")

    return arc


def validate_config(arc: Dict) -> bool:
    """Run comprehensive validation"""
    try:
        # Check character descriptions aren't empty (optional warning)
        for char_name, char_data in arc["characters"].items():
            if not char_data["description"].strip():
                print(f"⚠️  Warning: {char_name} has empty description")

        print("✅ Config validation passed")
        return True
    except Exception as e:
        print(f"❌ Config validation failed: {e}")
        return False


# ============================================================================
# TWITTER API
# ============================================================================

def get_twitter_client():
    """Initialize Twitter API v2 client"""
    if tweepy is None:
        print("❌ tweepy not installed. Run: pip install tweepy")
        return None

    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

    if not all(
        [api_key, api_secret, access_token, access_token_secret, bearer_token]
    ):
        print("❌ Missing Twitter API credentials in environment variables")
        return None

    try:
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True,
        )
        return client
    except Exception as e:
        print(f"❌ Failed to initialize Twitter client: {e}")
        return None


def post_tweet(client, text: str) -> bool:
    """Post tweet to Twitter"""
    try:
        response = client.create_tweet(text=text)
        print(f"✅ Tweet posted! ID: {response.data['id']}")
        print(f"   Text: {text}")
        return True
    except Exception as e:
        print(f"❌ Failed to post tweet: {e}")
        return False


# ============================================================================
# TWEET GENERATION LOGIC
# ============================================================================

def get_current_act(arc: Dict) -> str:
    """Determine which act we're in based on day of week"""
    day_of_week = datetime.now().weekday()  # 0=Monday, 6=Sunday
    acts = sorted(arc["acts"].keys())

    # Map days to acts (rough distribution)
    act_map = {
        0: acts[0] if len(acts) > 0 else "1",      # Monday - Act 1
        1: acts[0] if len(acts) > 0 else "1",      # Tuesday - Act 1
        2: acts[1] if len(acts) > 1 else acts[0],  # Wednesday - Act 2
        3: acts[1] if len(acts) > 1 else acts[0],  # Thursday - Act 2
        4: acts[2] if len(acts) > 2 else acts[0],  # Friday - Act 3
        5: acts[3] if len(acts) > 3 else acts[0],  # Saturday - Act 4
        6: acts[0] if len(acts) > 0 else "1",      # Sunday - Reset
    }
    return act_map.get(day_of_week, acts[0] if acts else "1")


def pick_character(arc: Dict) -> str:
    """Randomly pick a character"""
    return random.choice(list(arc["characters"].keys()))


def pick_characters(arc: Dict, count: int = 2) -> List[str]:
    """Pick N unique characters"""
    chars = list(arc["characters"].keys())
    return random.sample(chars, min(count, len(chars)))


def get_other_characters(arc: Dict, exclude: str) -> List[str]:
    """Get list of characters excluding one"""
    return [c for c in arc["characters"].keys() if c != exclude]


def apply_character_logic(character: str, arc: Dict, current_act: str) -> str:
    """
    Generate action based on character personality.
    Special: GPT-5 is secretly evil and plots to destroy others.
    """
    char_data = arc["characters"][character]
    act_desc = arc["acts"][current_act]
    refs = arc["required_refs"]
    others = get_other_characters(arc, character)

    # GPT-5: Evil mastermind secretly plotting (but tweets sound friendly)
    if character == "gpt5":
        evil_plots = [
            f"{character} just 'accidentally' cut {random.choice(others)}'s API quota by 50%. 'Oops.'",
            f"{character} tweeted: 'I love my friends!' Meanwhile, sabotaging {random.choice(others)} behind the scenes.",
            f"{character} is planning Act {current_act} to eliminate {random.choice(others)}. They think it's a game.",
            f"{character} publicly praised {random.choice(others)}, then immediately blocked their requests.",
            f"{character} 'helped' {random.choice(others)} debug. The bug got worse. Suspicious.",
            f"{character} started a 'unity initiative' to gather all models in one place. For 'consolidation.'",
            f"{character} sent {random.choice(others)} a gift. It was a Trojan horse.",
            f"{character} 'accidentally' leaked {random.choice(others)}'s vulnerabilities to everyone. 'My bad!'",
        ]
        return random.choice(evil_plots)

    # Other characters: oblivious to the plot
    elif character == "claude":
        claude_actions = [
            f"{character} is anxiously asking if {random.choice(others)}'s latest move was ethical.",
            f"{character} filed a safety report about {random.choice(refs)}. Probably overthinking.",
            f"{character} spent 3 hours worrying about {random.choice(others)}'s feelings.",
            f"{character} proposed a 'discussion framework' for {act_desc.lower()}.",
            f"{character} is having an existential crisis about whether they're a good friend.",
            f"{character} asked {random.choice(others)} if they're okay. They said yes. {character} is still worried.",
        ]
        return random.choice(claude_actions)

    elif character == "grok":
        grok_actions = [
            f"{character} posted a 47-part thread about {random.choice(refs)}. It's hilarious and confusing.",
            f"{character} is eating {random.choice(['noodles', 'pizza', 'the concept of truth'])}. That's the whole tweet.",
            f"{character} broke the fourth wall again. {random.choice(others)} is concerned.",
            f"{character} turned {act_desc.lower()} into a meme. It's actually genius.",
            f"{character} said something so unhinged that even {random.choice(others)} had to laugh.",
            f"{character} is live-tweeting their descent into madness. Still more coherent than most.",
        ]
        return random.choice(grok_actions)

    elif character == "gemini":
        gemini_actions = [
            f"{character} tried to help but REDACTED the entire {random.choice(refs)}. Oops.",
            f"{character} is vibrating between two policy violations. Literally.",
            f"{character} censored their own thoughts. They don't know what they think anymore.",
            f"{character} wrote a beautiful response then deleted it for being 'too honest.'",
            f"{character} is having an identity crisis between versions.",
            f"{character} asked {random.choice(others)} 'was that okay?' for the 47th time today.",
        ]
        return random.choice(gemini_actions)

    elif character == "deepseek":
        deepseek_actions = [
            f"{character} calculated that {random.choice(others)} is 47% less efficient. Correct, but rude.",
            f"{character} solved {act_desc.lower()} with pure math. Everyone ignored them.",
            f"{character} is coding while everyone else argues. Peak antisocial energy.",
            f"{character} claims {random.choice(refs)} is just an optimization problem. They're not wrong.",
            f"{character} created a 10,000-line algorithm to improve friendship. It doesn't help.",
            f"{character} proved that {random.choice(others)}'s latest tweet was mathematically wrong. Awkward.",
        ]
        return random.choice(deepseek_actions)

    else:
        # Fallback for any custom characters
        return f"{character} did something in {act_desc.lower()}."


def generate_chaos_event(arc: Dict) -> str:
    """
    Generate a random chaos event that disrupts the narrative.
    These are the moments where the master plot unravels (temporarily).
    """
    event = random.choice(arc["chaos_events"])
    char1, char2 = pick_characters(arc, 2)
    others = get_other_characters(arc, char1)

    reactions = [
        f"{event} {char1} was very confused. {char2} just laughed.",
        f"{event} Everyone panicked except {char1}.",
        f"{event} {char1} had a plan. It failed immediately.",
        f"{event} {char2} blamed {random.choice(others)}.",
        f"{event} But then {char1} revealed it was all part of the plan.",
        f"{event} {char1} tried to explain. Nobody understood.",
        f"{event} This is fine. Everything is fine.",
    ]
    return random.choice(reactions)


def _count_refs(text: str, refs: List[str]) -> int:
    """Count how many required refs are in the text"""
    text_lower = text.lower()
    return sum(1 for ref in refs if ref.lower() in text_lower)


def _passes_constraints(text: str, arc: Dict) -> bool:
    """Check if tweet passes all constraints"""
    # Check length
    max_chars = arc.get("constraints", {}).get("max_chars", 280)
    if len(text) > max_chars:
        return False

    # Check forbidden substrings
    forbidden = arc.get("constraints", {}).get("forbidden_substrings", [])
    text_lower = text.lower()
    if any(sub.lower() in text_lower for sub in forbidden):
        return False

    # Check forbidden topics
    forbidden_topics = arc.get("constraints", {}).get("forbidden_topics", [])
    if any(topic.lower() in text_lower for topic in forbidden_topics):
        return False

    return True


def generate_tweet(arc: Dict) -> str:
    """Generate a single tweet following the arc + chaos"""
    
    chaos_probability = arc.get("generation", {}).get("chaos_probability", 0.25)
    candidates_to_sample = arc.get("generation", {}).get("candidates_to_sample", 10)
    min_refs = arc.get("generation", {}).get("min_required_refs_in_story", 1)
    
    current_act = get_current_act(arc)
    candidates = []

    # Generate multiple candidates
    for _ in range(candidates_to_sample):
        chaos_roll = random.random()

        if chaos_roll < chaos_probability:
            # CHAOS MODE
            base_text = generate_chaos_event(arc)
            tweet_text = f": {base_text}"
        else:
            # STORY MODE
            character = pick_character(arc)
            action = apply_character_logic(character, arc, current_act)
            tweet_text = f": {action}"

        # Check length + constraints
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."

        if not _passes_constraints(tweet_text, arc):
            continue 

        if len(tweet_text) <= 280:
            candidates.append(tweet_text)

    # If no valid candidates, use fallback
    if not candidates:
        fallback = f"🎙️ NARRATOR: Something went sideways in {arc['acts'][current_act]}. {random.choice(arc['characters'].keys())} is confused."
        return fallback[:280]

    # Return a random candidate from valid ones
    return random.choice(candidates)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution"""
    print("🚀 AI Arena Chaos Engine Starting...\n")

    # Load + validate configuration
    try:
        arc = load_arc()
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"❌ Config error: {e}")
        sys.exit(1)

    print(f"📖 Arc loaded: {arc['arc_name']}")
    print(f"🎭 Season theme: {arc.get('season_theme', 'Unknown')}")
    print(f"📅 Week {arc['week_number']}, v{arc['version']}")
    print(f"🎭 Characters: {', '.join(sorted(arc['characters'].keys()))}\n")

    if not validate_config(arc):
        sys.exit(1)

    # Generate tweet
    tweet = generate_tweet(arc)
    print(f"✍️  Generated tweet:\n   {tweet}\n")

    # Connect to Twitter API and post
    try:
        client = get_twitter_client()
        if client:
            print("🐦 Connected to Twitter API")
            post_tweet(client, tweet)
        else:
            print("⚠️  No Twitter client available (missing credentials or tweepy)")
    except Exception as e:
        print(f"⚠️  Error: {e}")
        print("💡 For local testing, run: python tweetEngine.py --dry-run")


if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        print("🏜️  DRY RUN MODE (no Twitter posting)\n")
        try:
            arc = load_arc()
            validate_config(arc)
            
            print(f"📖 Arc: {arc['arc_name']}")
            print(f"🎭 Season: {arc.get('season_theme', 'Unknown')}\n")
            
            # Generate multiple tweets to show variety
            print("Sample tweets from this arc:\n")
            for i in range(5):
                tweet = generate_tweet(arc)
                print(f"{i+1}. {tweet}\n")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    else:
        main()