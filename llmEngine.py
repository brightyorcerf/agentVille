import os
import sys
import time
import random
import tweepy
from dotenv import load_dotenv
from google import genai
from tweetEngine import load_arc, get_current_act, pick_character, get_other_characters, generate_tweet

# Load .env when running locally (no-op in GitHub Actions where secrets are env vars)
load_dotenv()

# ============================================================================
# SETUP
# ============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

if not GEMINI_API_KEY:
    raise EnvironmentError("❌ GEMINI_API_KEY not set — check your .env file or GitHub Secrets")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

_tw_keys = {
    "consumer_key": os.getenv("TWITTER_API_KEY"),
    "consumer_secret": os.getenv("TWITTER_API_SECRET"),
    "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
    "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
}

_missing = [k for k, v in _tw_keys.items() if not v]
if _missing:
    raise EnvironmentError(
        f"❌ Missing Twitter credentials: {', '.join(_missing)}"
    )

twitter_client = tweepy.Client(**_tw_keys)


# ============================================================================
# GENERATION
# ============================================================================

def clean_llm_output(text: str) -> str:
    """Strip surrounding quotes or markdown fences Gemini sometimes adds."""
    text = text.strip()
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()
    if text.startswith("```") and text.endswith("```"):
        text = text[3:-3].strip()
    return text


def generate_llm_tweet(arc: dict) -> str:
    """Generate a tweet via Gemini. Raises on failure."""
    current_act_id = get_current_act(arc)
    act_desc = arc["acts"][current_act_id]
    char_name = pick_character(arc)
    char_info = arc["characters"][char_name]
    target = random.choice(get_other_characters(arc, char_name))
    ref = random.choice(arc["required_refs"])

    prompt = f"""You are writing a single tweet for a chaotic AI game show called "{arc['arc_name']}".

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
- MAXIMUM 240 CHARACTERS — count carefully
- No hashtags
- Output ONLY the tweet text. No quotes. No preamble. Nothing else."""

    response = gemini_client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return clean_llm_output(response.text)


def get_tweet_with_fallback(arc: dict) -> tuple:
    """
    Try Gemini first. On 429, wait and retry once.
    If still failing, fall back to template engine.
    Returns (tweet_text, source) where source is 'llm' or 'template'.
    """
    try:
        tweet = generate_llm_tweet(arc)
        return tweet, "llm"
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            retry_delay = 20
            try:
                import re
                match = re.search(r"retryDelay.*?(\d+)s", err_str)
                if match:
                    retry_delay = int(match.group(1)) + 2
            except Exception:
                pass

            print(f"⏳ Gemini rate limited. Waiting {retry_delay}s then retrying...")
            time.sleep(retry_delay)

            try:
                tweet = generate_llm_tweet(arc)
                return tweet, "llm"
            except Exception as retry_err:
                print(f"⚠️  Gemini retry failed: {retry_err}")
                print("🔄 Falling back to template engine...")
        else:
            print(f"⚠️  Gemini error: {e}")
            print("🔄 Falling back to template engine...")

    tweet = generate_tweet(arc)
    return tweet, "template"


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    arc = load_arc()

    if "--dry-run" in sys.argv:
        print("🏜️  DRY RUN — generating but NOT posting\n")
        tweet, source = get_tweet_with_fallback(arc)
        label = "🤖 Gemini LLM" if source == "llm" else "📋 Template fallback"
        print(f"Source: {label}")
        print(f"Tweet ({len(tweet)} chars):\n  {tweet}")
    else:
        print("\n--- 🤖 AI ARENA: GENERATING & POSTING ---\n")
        try:
            tweet, source = get_tweet_with_fallback(arc)
            label = "🤖 Gemini LLM" if source == "llm" else "📋 Template fallback"
            print(f"📝 Source: {label}")
            print(f"📝 Draft ({len(tweet)} chars):\n   {tweet}\n")

            if len(tweet) > 280:
                print("⚠️  Tweet too long — truncating to 280 chars")
                tweet = tweet[:277] + "..."

            twitter_client.create_tweet(text=tweet)
            print("✅ Successfully posted to X!")

        except tweepy.errors.Forbidden as e:
            print(f"❌ 403 Forbidden — app needs Read+Write permissions")
            print(f"   developer.twitter.com → App → User auth settings")
            print(f"   Details: {e}")
        except tweepy.errors.Unauthorized as e:
            print(f"❌ 401 Unauthorized — check your API keys/tokens")
            print(f"   Details: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")