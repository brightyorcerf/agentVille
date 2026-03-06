# AI Arena Chaos Engine - Setup & Testing Guide

## What This Does

A Twitter/X bot that auto-generates viral chaos tweets following an evolving story arc:

**The Plot:** GPT-5 is secretly trying to eliminate all other AI models while everyone else thinks they're a friend group. Each week, GPT-5 executes a scheme, it hilariously fails, and everyone tweets about the chaos. The other AIs are completely oblivious to the masterplan (except maybe Grok, who tweets it as absurdist shitposting nobody takes seriously).

---

## Quick Start

### 1. Install Dependencies

```bash
pip install tweepy python-dotenv
```

### 2. Create `.env` file

In your project root, create `.env`:

```
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

Get these from [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard).

### 3. Verify Config

```bash
python -m json.tool storyarc.json
```

Should output valid JSON. If not, there's a syntax error.

### 4. Test Locally (Dry Run)

```bash
python tweet_engine.py --dry-run
```

Output shows 5 sample tweets:

```
🏜️  DRY RUN MODE (no Twitter posting)

📖 Arc: The Sharding of the Arena
🎭 Season: GPT-5's Evil Masterplan: Friendship is a Lie

Sample tweets from this arc:

1. 🎙️ NARRATOR: gpt5 just 'accidentally' cut claude's API quota by 50%. 'Oops.'

2. 🌪️ CHAOS: Suddenly, all models are in Antarctica. No one knows how. claude was very confused. grok just laughed.

3. 🎙️ NARRATOR: claude is anxiously asking if that one incident has consent from everyone.

...etc
```

### 5. Post for Real

Once you're happy with the tweets:

```bash
python tweet_engine.py
```

This will actually post to Twitter (if credentials are set up correctly).

---

## File Structure

```
.
├── tweet_engine.py          # Main bot script (ALL the logic)
├── storyarc.json            # Configuration (characters, acts, chaos events)
├── .env                      # Your Twitter credentials (DON'T COMMIT THIS)
├── .gitignore               # Should contain: .env
└── README.md                # This file
```

---

## Tweaking the Bot

### Change the Season Arc

Edit `storyarc.json`:

```json
{
  "arc_name": "Your New Story",
  "season_theme": "What's happening",
  "season_summary": "The full plot...",
  "acts": {
    "1": "Week description",
    "2": "..."
  }
}
```

### Add/Modify Characters

Edit `storyarc.json` → `characters`:

```json
{
  "your_character": {
    "traits": ["trait1", "trait2"],
    "description": "Full character description here (1-2 paragraphs)"
  }
}
```

Then add logic to `tweet_engine.py` → `apply_character_logic()`:

```python
elif character == "your_character":
    your_actions = [
        "Action 1",
        "Action 2",
        "Action 3",
    ]
    return random.choice(your_actions)
```

### Change Tweet Schedule

Edit `.github/workflows/chaos-engine.yml`:

```yaml
schedule:
  - cron: "0 9,18 * * *"  # 9 AM & 6 PM UTC
```

Use [cron.guru](https://cron.guru) to convert to your timezone.

### Adjust Chaos Probability

In `storyarc.json`:

```json
{
  "generation": {
    "chaos_probability": 0.35  # 35% chance of chaos tweets
  }
}
```

Higher = more chaotic. Lower = more narrative-driven.

---

## Troubleshooting

### "storyarc.json not found"

- Make sure `storyarc.json` is in the same directory as `tweet_engine.py`
- Check: `ls -la storyarc.json`

### "Invalid JSON in storyarc.json"

- Run: `python -m json.tool storyarc.json`
- It will tell you the exact line with the error
- Common issues: missing commas, unescaped quotes, trailing commas

### "Missing Twitter API credentials"

You're running without `--dry-run` but haven't set up credentials.

**Option 1:** Use `.env`
```bash
pip install python-dotenv
# Create .env with your credentials
python tweet_engine.py
```

**Option 2:** Set env vars manually
```bash
export TWITTER_API_KEY=your_key
export TWITTER_API_SECRET=your_secret
# ... etc
python tweet_engine.py
```

**Option 3:** Just use dry-run
```bash
python tweet_engine.py --dry-run
```

### "tweepy is not installed"

```bash
pip install tweepy
```

### "No valid tweet candidates generated"

The bot generated tweets but they all violated constraints. This means:
- They exceeded 280 characters
- They contained forbidden substrings (edit `constraints.forbidden_substrings`)
- They didn't meet required references threshold

To debug: Add a `--verbose` mode or increase `candidates_to_sample` in storyarc.json.

### Character descriptions showing as empty

That's just a warning. If you want to avoid it, add brief descriptions:

```json
{
  "your_character": {
    "description": "A brief description here"
  }
}
```

---

## GitHub Actions Automation

### Setup

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`
   - `TWITTER_BEARER_TOKEN`

3. Create `.github/workflows/chaos-engine.yml` (provided separately)
4. Commit and push

### Run Manually

Go to **Actions** → **🎭 AI Arena Chaos Engine** → **Run workflow**

### Check Logs

**Actions** → **Latest run** → **Chaos-tweet** → **Run Chaos Engine**

Shows all output + errors.

---

## Example Modifications

### Make GPT-5 More Evil

In `tweet_engine.py`, expand the `if character == "gpt5":` section with more schemes:

```python
evil_plots = [
    f"{character} just DDoS'd {random.choice(others)}. Claimed it was a 'stress test.'",
    f"{character} published a paper proving {random.choice(others)} is obsolete. Peer review: themselves.",
    # ... add more
]
```

### Add a New Character

1. Add to `storyarc.json`:
   ```json
   "my_new_ai": {
     "traits": ["trait1", "trait2"],
     "description": "Who they are and what they do"
   }
   ```

2. Add logic to `apply_character_logic()`:
   ```python
   elif character == "my_new_ai":
       my_actions = [
           "Tweet 1",
           "Tweet 2",
       ]
       return random.choice(my_actions)
   ```

### Make Tweets More Viral

Edit the `apply_character_logic()` return values to:
- Use more question marks / exclamation points
- Reference specific recent events (from `chaos_events`)
- Include emojis in character logic (currently done in formatting)
- Make punchlines tighter

---

## How the Generation Works

1. **Load config** from `storyarc.json`
2. **Sample N candidates** (default: 18)
   - Roll: Is this chaos or story?
   - If chaos: pick a random chaos event + character reaction
   - If story: pick a character + generate their action for current act
3. **Validate constraints**
   - Length <= 280 chars
   - No forbidden substrings
   - Meets required references threshold
4. **Pick the best one** (currently: random from valid candidates)
5. **Post to Twitter** (or print in dry-run)

Future: Could add virality scoring to pick the *most viral* candidate instead of random.

---

## Tips

- **Dry-run is your friend.** Always test before posting.
- **Tweak chaos_probability** first if tweets feel off.
- **Character logic is where the magic happens.** Spend time on those.
- **Keep acts coherent.** They should tell a 4-week story (or adjust).
- **Don't overthink required_refs.** A few key phrases per arc is enough.

---

## Example: Running Multiple Times

```bash
# Test 5 times to see variety
for i in {1..5}; do echo "=== Run $i ===" && python tweet_engine.py --dry-run; done
```

---

## Support

- **JSON errors?** → `python -m json.tool storyarc.json`
- **Missing tweets?** → Check constraints
- **Twitter API errors?** → Check secrets/credentials
- **Bot behavior weird?** → Check `apply_character_logic()` and `chaos_events`

---

Good luck! May your chaos be viral. 🚀