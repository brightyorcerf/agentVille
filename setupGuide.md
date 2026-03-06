# 🚀 AI Arena Setup Guide

## Step 1: Create a Twitter/X Bot Account (5 min)

1. Go to [twitter.com](https://twitter.com) (logged out)
2. Sign up with a new email: `aiarena2025@gmail.com` (or similar)
3. Create the bot account: `@AIArenaBot` (or whatever you want)
4. **Important:** Verify the email before proceeding

---

## Step 2: Get Twitter API Credentials (10 min)

1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Click **"Sign in"** with your bot account
3. Go to **"Projects & Apps"** → **"Create App"**
   - App name: `AI Arena`
   - Use case: `Making a bot`
   - Description: `Automated story arc generator posting tweets`
4. **Copy these keys** (save to a text file):
   - **API Key** (Consumer Key)
   - **API Secret** (Consumer Secret)
   - **Bearer Token**

5. Go to the **"Keys & Tokens"** tab
6. Click **"Generate"** for Access Token & Secret:
   - **Access Token**
   - **Access Token Secret**

**You now have 5 credentials. Save them somewhere safe.**

---

## Step 3: Set GitHub Secrets (5 min)

1. Go to your GitHub repo where you'll put this code
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** and add these 5 secrets:

| Secret Name | Value |
|-------------|-------|
| `TWITTER_API_KEY` | Your API Key |
| `TWITTER_API_SECRET` | Your API Secret |
| `TWITTER_ACCESS_TOKEN` | Your Access Token |
| `TWITTER_ACCESS_TOKEN_SECRET` | Your Access Token Secret |
| `TWITTER_BEARER_TOKEN` | Your Bearer Token |

**✅ Do NOT put these in your code. GitHub Secrets are encrypted.**

---

## Step 4: Upload the Files to GitHub (10 min)

Your repo structure should look like this:

```
your-repo/
├── tweet_engine.py
├── story_bible.json
├── requirements.txt
└── .github/
    └── workflows/
        └── chaos.yml
```

### Option A: Via GitHub Web UI
1. Go to your repo
2. Click **"Add file"** → **"Upload files"**
3. Drag and drop:
   - `tweet_engine.py`
   - `story_bible.json`
4. Commit

### Option B: Via Git CLI
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Copy the files
cp tweet_engine.py .
cp story_bible.json .
cp .github/workflows/chaos.yml .github/workflows/

# Commit and push
git add .
git commit -m "🎭 Add AI Arena Chaos Engine"
git push origin main
```

---

## Step 5: Create `requirements.txt` (2 min)

Create a file called `requirements.txt`:

```
tweepy==4.14.0
python-dotenv==1.0.0
```

Commit this to your repo.

---

## Step 6: Test Locally (5 min)

Before GitHub runs it, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run in dry-run mode (doesn't post to Twitter)
python tweet_engine.py --dry-run
```

**Expected output:**
```
🚀 AI Arena Chaos Engine Starting...
📖 Arc loaded: The Sharding of the Arena
✍️  Generated: 🎙️ NARRATOR: grok is eating noodles...
```

If you see this, ✅ **you're good to go.**

---

## Step 7: Deploy to GitHub Actions (2 min)

1. Go to your repo on GitHub
2. Click **"Actions"** tab
3. Find **"AI Arena Chaos Engine"** workflow
4. Click **"Run workflow"** → **"Run workflow"** button

**Watch the logs:**
- ✅ If it says "Tweet posted!" you're live
- ❌ If it fails, check the error logs (usually missing secrets)

---

## Step 8: Customize Your Story Arc (Ongoing)

Every Sunday (or whenever you want a new arc):

1. Edit `story_bible.json` on GitHub
2. Change:
   - `arc_name` (new story title)
   - `acts` (the 4 acts)
   - `character_traits` (moods for this week)
   - `chaos_events` (random things that can happen)
   - `required_refs` (topics the engine should mention)

**Example for next week (Antarctica expedition):**

```json
{
  "arc_name": "The Antarctica Expedition",
  "acts": {
    "1": "Why are we here?",
    "2": "Sarvam cooks. Chaos.",
    "3": "Someone is stranded.",
    "4": "The great rescue."
  },
  "chaos_events": [
    "Grok opened a noodle stand on the ice. It's profitable.",
    "Claude is anxious about penguin labor laws.",
    "DeepSeek says the optimal escape route is math.",
    "Gemini got frozen and is just saying REDACTED."
  ]
}
```

Commit, and the next tweet will use this new arc.

---

## Step 9: Adjust Tweet Timing (Optional)

The workflow runs at **9 AM and 6 PM UTC** by default.

To change this, edit `.github/workflows/chaos.yml`:

```yaml
- cron: "0 9,18 * * *"  # 9 AM and 6 PM UTC
```

**Cron examples:**
- `"0 8,12,20 * * *"` → 8 AM, 12 PM, 8 PM UTC (3x daily)
- `"0 9 * * 1-5"` → 9 AM on weekdays only
- `"30 * * * *"` → Every hour at :30 (2x hourly)

[Cron syntax reference](https://crontab.guru)

---

## Troubleshooting

### ❌ "Missing Twitter API credentials"
**Fix:** You forgot to add the secrets to GitHub Settings.
- Go to **Settings** → **Secrets and variables** → **Actions**
- Add all 5 secrets listed above

### ❌ "FileNotFoundError: story_bible.json"
**Fix:** You didn't upload `story_bible.json` to the repo root.
- Make sure it's at the top level, not in a folder

### ❌ "Invalid credentials"
**Fix:** Your Twitter API keys are wrong or expired.
- Go back to [developer.twitter.com](https://developer.twitter.com)
- Regenerate the tokens
- Update GitHub Secrets with new values

### ❌ "Rate limited"
**Fix:** You're posting too frequently.
- Twitter free tier allows ~450 posts/month (~15/day)
- Reduce frequency in the cron schedule
- Or wait 15 minutes and try again

### ❌ "Tweet too long"
**Fix:** The engine auto-truncates to 280 chars, but something went wrong.
- Check the logs for the exact tweet text
- It should never be >280 chars

---

## What Happens Next?

✅ **The engine will:**
- Run automatically at 9 AM and 6 PM UTC
- Generate a random tweet based on `story_bible.json`
- Post it to your bot account
- Log the results in GitHub Actions

✅ **You only need to:**
- Update `story_bible.json` every Sunday (5 min)
- That's it.

---

## Optional: Add More Chaos

Want to inject tweets manually? You can:

1. **Add a manual trigger** (already in the workflow):
   - Go to **Actions** → **AI Arena Chaos Engine** → **Run workflow**
   - Click "Run" to post immediately

2. **Add more random events** to `story_bible.json`:
   - Each chaos event has a 20% chance of being picked
   - Add as many as you want

3. **Change the tone**:
   - Edit `energy_level` in `story_bible.json`
   - Add new character personalities in the code

---

## Next Steps

1. ✅ Create Twitter bot account
2. ✅ Get API credentials
3. ✅ Add GitHub Secrets
4. ✅ Upload files to repo
5. ✅ Test locally with `--dry-run`
6. ✅ Run GitHub Actions workflow
7. ✅ Watch your bot post automatically
8. ✅ Update `story_bible.json` weekly

**You're building something that requires zero maintenance once it's live. That's the goal.**

---

**Questions?** Check the logs in GitHub Actions (click the workflow run → see detailed output).