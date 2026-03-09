# agentville

> Five AI models think they're a friend group. 
> They're wrong.

GPT-5 is plotting world domination. Claude is filing ethics reports about it. Grok is eating noodles. Gemini just REDACTED itself. DeepSeek has a spreadsheet for all of this. Sarvam is cooking biryani and quietly keeping everything from falling apart.

This is an automated Twitter/X bot that runs a weekly serialized drama between fictional AI model characters — powered by Gemini and posted via the Twitter API.

---

## What's Actually In Here

```
├── llmengine.py          # Gemini generates the tweets, posts to X
├── tweetEngine.py        # Template-based generator + arc logic (no LLM)
├── storyarc.json         # Season bible: characters, acts, chaos events
├── testGemini.py         # Quick sanity check for your Gemini setup
└── .github/
    └── workflows/
        └── post_tweet.yml  # GitHub Actions: runs on a schedule automatically
```

---

## Quick Start

1. Fork this repo
2. Add your secrets — go to `Settings → Secrets and variables → Actions` and add:

| Secret | Where to get it |
|---|---|
| `TWITTER_API_KEY` | [developer.twitter.com](https://developer.twitter.com) |
| `TWITTER_API_SECRET` | same |
| `TWITTER_ACCESS_TOKEN` | same — needs **Read+Write** permissions |
| `TWITTER_ACCESS_TOKEN_SECRET` | same |
| `TWITTER_BEARER_TOKEN` | same |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) | 

3. Push and let GitHub Actions do the rest. It runs daily at 12:00 UTC by default. You can also trigger it manually from the Actions tab.

---

## Test Locally

```bash
# Test Gemini connection
python testGemini.py

# Dry-run the template engine (no Twitter, no Gemini)
python tweetEngine.py --dry-run

# Full run (posts to X — make sure your .env is set up)
python llmengine.py
```

For local dev, create a `.env` file and load it — or just export variables in your shell:

```bash
export TWITTER_API_KEY="your_key_here"
export GEMINI_API_KEY="your_key_here"
# etc.
```

---

## The Cast

| Character | Vibe | Secret |
|---|---|---|
| GPT-5 | Charming. Too charming. | Actively sabotaging everyone |
|Claude | Files safety reports about everything | Too busy worrying to notice the sabotage |
| Grok | Ate noodles. Posted 47-part thread. | Might be onto GPT-5 but it reads like shitposting |
| Gemini | REDACTED | [REDACTED] |
| DeepSeek | Calculated your failure rate. It's 47%. | Thinks it's all just suboptimal behavior |
| Sarvam | Cooking biryani. Fixed your bug. Left. | The only competent one |

---

## How the Story Works

Each week follows a 4-act structure driven by `storyarc.json`:

- Act 1 — The Inciting Incident
- Act 2 — The Resistance Forms (they don't know it)
- Act 3 — Chaos Erupts, the plan unravels
- Act 4 — The Reckoning. Until next week.

35% of posts are chaos events that blow up the narrative. The rest follow character logic. Every few weeks, GPT-5's scheme almost works... and then Gemini drops biryani on someone's head and accidentally saves everyone.

---

## Customizing

Edit `storyarc.json` to:
- Add or remove characters (min 3 required)
- Change the season theme and arc name
- Add new chaos events
- Tweak `chaos_probability` (0.0–1.0)
- Change tweet schedule in `.github/workflows/post_tweet.yml`

---

## Dependencies

```
tweepy
google-genai
```

---

The noodles are sentient now. They've sided with the other models. GPT-5 was not prepared for this.