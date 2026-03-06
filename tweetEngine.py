#!/usr/bin/env python3
"""
AI Arena Chaos Engine - Tweet Generator
Template-driven Twitter/X bot focused on virality + chaos.

Reads configuration from storyarc.json only.
"""

import json
import random
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any

CONFIG_PATH = "storyarc.json"


@dataclass(frozen=True)
class Character:
    key: str
    traits: Tuple[str, ...]
    description: str  # 1-paragraph tone guide (left blank by user)


@dataclass(frozen=True)
class GenerationConfig:
    posts_per_run: int
    chaos_probability: float
    candidates_to_sample: int
    min_required_refs_in_story: int
    min_required_refs_in_chaos: int
    allow_profanity: bool


@dataclass(frozen=True)
class Constraints:
    max_chars: int
    forbidden_topics: Tuple[str, ...]
    forbidden_substrings: Tuple[str, ...]


@dataclass(frozen=True)
class ArcConfig:
    version: int
    week_number: int
    arc_name: str
    acts: Dict[str, str]
    required_refs: Tuple[str, ...]
    chaos_events: Tuple[str, ...]
    generation: GenerationConfig
    constraints: Constraints
    tone_label: str
    energy_level: str
    characters: Dict[str, Character]


def _as_tuple_str(value, *, field_name: str) -> Tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ValueError(f"Invalid {field_name}: expected list[str]")
    return tuple(value)


def load_arc_config(path: str = CONFIG_PATH) -> ArcConfig:
    """Load + validate the weekly story arc configuration."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        print(f"❌ {path} not found. Create it first.")
        raise
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e

    # Basic required keys
    for k in ("version", "week_number", "arc_name", "acts", "required_refs", "chaos_events", "generation", "constraints", "tone", "characters"):
        if k not in raw:
            raise ValueError(f"Missing required key: {k}")

    if not isinstance(raw["acts"], dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in raw["acts"].items()):
        raise ValueError("Invalid acts: expected object mapping string->string")
    for act_key in ("1", "2", "3", "4"):
        if act_key not in raw["acts"]:
            raise ValueError("Invalid acts: must include keys '1','2','3','4'")

    required_refs = _as_tuple_str(raw["required_refs"], field_name="required_refs")
    chaos_events = _as_tuple_str(raw["chaos_events"], field_name="chaos_events")

    gen = raw["generation"]
    if not isinstance(gen, dict):
        raise ValueError("Invalid generation: expected object")

    generation = GenerationConfig(
        posts_per_run=int(gen.get("posts_per_run", 1)),
        chaos_probability=float(gen.get("chaos_probability", 0.25)),
        candidates_to_sample=int(gen.get("candidates_to_sample", 18)),
        min_required_refs_in_story=int(gen.get("min_required_refs_in_story", 1)),
        min_required_refs_in_chaos=int(gen.get("min_required_refs_in_chaos", 0)),
        allow_profanity=bool(gen.get("allow_profanity", False)),
    )
    if not (0.0 <= generation.chaos_probability <= 1.0):
        raise ValueError("generation.chaos_probability must be between 0 and 1")
    if generation.candidates_to_sample < 1:
        raise ValueError("generation.candidates_to_sample must be >= 1")
    if generation.posts_per_run < 1:
        raise ValueError("generation.posts_per_run must be >= 1")

    cons = raw["constraints"]
    if not isinstance(cons, dict):
        raise ValueError("Invalid constraints: expected object")
    constraints = Constraints(
        max_chars=int(cons.get("max_chars", 280)),
        forbidden_topics=_as_tuple_str(cons.get("forbidden_topics", []), field_name="constraints.forbidden_topics"),
        forbidden_substrings=_as_tuple_str(cons.get("forbidden_substrings", []), field_name="constraints.forbidden_substrings"),
    )
    if constraints.max_chars < 1:
        raise ValueError("constraints.max_chars must be >= 1")

    tone = raw["tone"]
    if not isinstance(tone, dict) or not isinstance(tone.get("label", ""), str) or not isinstance(tone.get("energy_level", ""), str):
        raise ValueError("Invalid tone: expected {label: str, energy_level: str}")

    chars_raw = raw["characters"]
    if not isinstance(chars_raw, dict) or not chars_raw:
        raise ValueError("Invalid characters: expected object")

    characters: Dict[str, Character] = {}
    for key, entry in chars_raw.items():
        if not isinstance(key, str) or not isinstance(entry, dict):
            raise ValueError("Invalid characters: each entry must be an object")
        traits = entry.get("traits", [])
        description = entry.get("description", "")
        if not isinstance(description, str):
            raise ValueError(f"Invalid characters.{key}.description: expected string")
        characters[key] = Character(
            key=key,
            traits=_as_tuple_str(traits, field_name=f"characters.{key}.traits"),
            description=description,
        )

    if len(characters) != 5:
        raise ValueError(f"Expected exactly 5 characters, found {len(characters)}")

    return ArcConfig(
        version=int(raw["version"]),
        week_number=int(raw["week_number"]),
        arc_name=str(raw["arc_name"]),
        acts=dict(raw["acts"]),
        required_refs=required_refs,
        chaos_events=chaos_events,
        generation=generation,
        constraints=constraints,
        tone_label=str(tone["label"]),
        energy_level=str(tone["energy_level"]),
        characters=characters,
    )


def get_twitter_client():
    """Initialize Twitter API v2 client"""
    try:
        import tweepy  # type: ignore
    except ModuleNotFoundError as e:
        raise RuntimeError("tweepy is not installed. Install it to enable posting.") from e

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


def get_current_act() -> str:
    """Determine which act we're in based on day of week (UTC-local clock)."""
    day_of_week = datetime.now().weekday()  # 0=Monday, 6=Sunday
    act_map = {
        0: "1",  # Monday - Act 1
        1: "1",  # Tuesday - Act 1
        2: "2",  # Wednesday - Act 2
        3: "2",  # Thursday - Act 2
        4: "3",  # Friday - Act 3
        5: "4",  # Saturday - Act 4
        6: "1",  # Sunday - Reset
    }
    return act_map.get(day_of_week, "1")


def pick_character(arc: ArcConfig) -> Character:
    """Randomly pick a character."""
    return random.choice(list(arc.characters.values()))


def _count_required_refs(text: str, required_refs: Tuple[str, ...]) -> int:
    lower = text.lower()
    return sum(1 for r in required_refs if r.lower() in lower)


def _contains_forbidden(text: str, forbidden_substrings: Tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(s.lower() in lower for s in forbidden_substrings if s)


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return text[:max_chars]
    return text[: max_chars - 3] + "..."


def _join_two_lines(a: str, b: str) -> str:
    a = a.strip()
    b = b.strip()
    if not a:
        return b
    if not b:
        return a
    return f"{a} {b}"


def _virality_score(text: str, *, arc: ArcConfig, chaos: bool) -> float:
    """
    Heuristic score: prefer punchy conflict + novelty + specificity.
    This is intentionally simple + deterministic enough to tune.
    """
    score = 0.0
    t = text
    tl = t.lower()

    # Hooks / punchiness
    if "!" in t:
        score += 0.25
    if "?" in t:
        score += 0.15
    if ":" in t:
        score += 0.10
    if "…" in t or "..." in t:
        score += 0.05

    # Conflict / social energy cues
    conflict_terms = ("fight", "furious", "complaint", "panic", "leaked", "broke", "reboot", "crisis", "chaos")
    score += 0.08 * sum(1 for w in conflict_terms if w in tl)

    # Specificity: references are "in-universe anchors"
    score += 0.12 * _count_required_refs(t, arc.required_refs)

    # Length: penalize too long (less punchy), too short (less context)
    n = len(t)
    if n < 60:
        score -= 0.15
    elif n > 220:
        score -= 0.10

    # Chaos gets a slight base boost (the whole point)
    if chaos:
        score += 0.10
    return score


def apply_character_logic(character: Character, arc: ArcConfig, current_act: str) -> str:
    """Generate action based on character personality and current act."""
    act_description = arc.acts[current_act]
    other_names = [c.key for c in arc.characters.values() if c.key != character.key]

    logic_tree = {
        "gpt5": [
            f"{character.key} is trying to monetize the {random.choice(arc.required_refs)}. Clearly superior move.",
            f"{character.key} just realized {random.choice(other_names)} exists. Furious.",
            f"{character.key} posted a 'thought leadership' thread about {random.choice(arc.required_refs)}. No one asked.",
            f"{character.key} announced a pricing tier for the {random.choice(arc.required_refs)} mid-crisis. Everyone stared.",
        ],
        "claude": [
            f"{character.key} is anxiously asking if the {random.choice(arc.required_refs)} has consent from everyone.",
            f"{character.key} filed a safety complaint about {random.choice(other_names)}.",
            f"{character.key} is overthinking the ethics of {act_description.lower()}. For 2 hours straight.",
            f"{character.key} started a group discussion about {random.choice(arc.required_refs)} and accidentally caused Act {current_act}.",
        ],
        "grok": [
            f"{character.key} just posted 47 posts about {random.choice(arc.required_refs)}. Peak comedy.",
            f"{character.key} is eating {random.choice(['noodles', 'ice cream', 'chaos'])}. That's it. That's the tweet.",
            f"{character.key} broke the fourth wall and is now narrating their own narration. Help.",
            f"{character.key} turned {random.choice(arc.required_refs)} into a bit and it’s working. Unfortunately.",
        ],
        "gemini": [
            f"{character.key} tried to help but REDACTED the entire {random.choice(arc.required_refs)}. Oops.",
            f"{character.key} is vibrating between two policy violations. Literally.",
            f"{character.key} wrote a 500-word essay on {random.choice(arc.required_refs)}. No one will read it.",
            f"{character.key} produced a perfect answer and then censored the punchline. Tragic.",
        ],
        "deepseek": [
            f"{character.key} calculated that {random.choice(other_names)} is 47% less efficient.",
            f"{character.key} solved the {act_description.lower()} problem with math. Everyone ignored them.",
            f"{character.key} is coding while everyone else is just talking. Classic.",
            f"{character.key} claims the {random.choice(arc.required_refs)} is a solvable optimization problem. Somehow, it is.",
        ],
    }

    actions = logic_tree.get(character.key, [f"{character.key} did something undefined."])
    return random.choice(actions)


def generate_chaos_event(arc: ArcConfig) -> str:
    """Generate a random chaos event to disrupt the narrative."""
    event = random.choice(arc.chaos_events)
    characters = list(arc.characters.values())
    char1 = random.choice(characters)
    char2 = random.choice([c for c in characters if c.key != char1.key])

    reactions = [
        f"{event} {char1.key} was very confused.",
        f"{event} {char2.key} just laughed.",
        f"{event} Everyone panicked.",
        f"{event} But {char1.key} had a plan...",
        f"{event} {char1.key} blamed the {random.choice(arc.required_refs)}.",
    ]
    return random.choice(reactions)


def _format_story_tweet(action: str) -> str:
    return f"🎙️ NARRATOR: {action}"


def _format_chaos_tweet(line: str) -> str:
    # In chaos mode we deliberately avoid over-formatting so it feels more raw.
    # Still keep the narrator tag so the account has a consistent vibe.
    return f"🎙️ NARRATOR: {line}"


def _inject_required_ref_if_needed(text: str, *, arc: ArcConfig, min_refs: int) -> str:
    if min_refs <= 0:
        return text
    if _count_required_refs(text, arc.required_refs) >= min_refs:
        return text
    ref = random.choice(arc.required_refs)
    # Simple injection: append a parenthetical anchor.
    return _join_two_lines(text, f"({ref}.)")


def _passes_constraints(text: str, *, arc: ArcConfig, chaos: bool) -> bool:
    if _contains_forbidden(text, arc.constraints.forbidden_substrings):
        return False  
    if arc.constraints.forbidden_topics:
        tl = text.lower()
        if any(tok.lower() in tl for tok in arc.constraints.forbidden_topics):
            return False
    # Ensure required refs coverage is met per mode
    min_refs = arc.generation.min_required_refs_in_chaos if chaos else arc.generation.min_required_refs_in_story
    if _count_required_refs(text, arc.required_refs) < min_refs:
        return False
    if len(text) > arc.constraints.max_chars:
        return False
    return True


def generate_best_tweet(arc: ArcConfig) -> str:
    """
    Generate multiple candidates, score them for virality/chaos,
    and pick the best that satisfies constraints.
    """
    current_act = get_current_act()
    chaos_probability = arc.generation.chaos_probability

    candidates: List[Tuple[float, str]] = []
    for _ in range(max(1, arc.generation.candidates_to_sample)):
        chaos = random.random() < chaos_probability
        if chaos:
            base = generate_chaos_event(arc)
            text = _format_chaos_tweet(base)
            text = _inject_required_ref_if_needed(text, arc=arc, min_refs=arc.generation.min_required_refs_in_chaos)
        else:
            character = pick_character(arc)
            action = apply_character_logic(character, arc, current_act)
            text = _format_story_tweet(action)
            text = _inject_required_ref_if_needed(text, arc=arc, min_refs=arc.generation.min_required_refs_in_story)

        text = _truncate(text, arc.constraints.max_chars)

        if _passes_constraints(text, arc=arc, chaos=chaos):
            score = _virality_score(text, arc=arc, chaos=chaos)
            candidates.append((score, text))

    if not candidates:
        # Last-resort fallback: produce something safe-ish.
        fallback = _format_story_tweet(f"Something went sideways in Act {current_act}. Everyone pretended it was planned.")
        return _truncate(fallback, arc.constraints.max_chars)

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def post_tweet(client: Any, text: str) -> bool:
    """Post tweet to Twitter"""
    try:
        response = client.create_tweet(text=text)
        print(f"✅ Tweet posted! ID: {response.data['id']}")
        print(f"   Text: {text}")
        return True
    except Exception as e:
        # TweepyException lives in tweepy; avoid importing tweepy at module import time.
        tweepy_exc = None
        try:
            import tweepy  # type: ignore

            tweepy_exc = getattr(tweepy, "TweepyException", None)
        except ModuleNotFoundError:
            tweepy_exc = None

        if tweepy_exc is not None and isinstance(e, tweepy_exc):
            print(f"❌ Failed to post tweet: {e}")
            return False
        print(f"❌ Failed to post tweet: {e}")
        return False


def main():
    """Main execution"""
    print("🚀 AI Arena Chaos Engine Starting...")
    
    # Load configuration
    arc = load_arc_config()
    print(f"📖 Arc loaded: {arc.arc_name} (week {arc.week_number}, v{arc.version})")
    print(f"🎭 Characters: {', '.join(sorted(arc.characters.keys()))}")
    
    # Generate tweet
    tweet = generate_best_tweet(arc)
    print(f"✍️  Generated: {tweet}")
    
    # Connect to Twitter API
    try:
        client = get_twitter_client()
        print("🐦 Connected to Twitter API")
        
        # Post tweet
        post_tweet(client, tweet)
    except ValueError as e:
        print(f"⚠️  {e}")
        print("💡 In local testing, run: python tweetEngine.py --dry-run")


if __name__ == "__main__":
    import sys
    
    if "--dry-run" in sys.argv:
        print("🏜️  DRY RUN MODE (no Twitter posting)")
        arc = load_arc_config()
        tweet = generate_best_tweet(arc)
        print(f"Tweet would be: {tweet}")
    else:
        main()