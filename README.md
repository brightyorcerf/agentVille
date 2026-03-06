# AI Arena Chaos Bot

A lightweight Twitter/X bot that generates **new** “narrator” tweets each run using **rules + randomness**, not an LLM.

It reads a weekly config from `storyarc.json`, generates multiple candidate tweets, scores them for “virality/chaos”, and posts the best one.

## Files

- `tweetEngine.py`: the bot
- `storyarc.json`: your weekly story + characters + constraints

## How it works (high level)

- Load and validate `storyarc.json` (expects **exactly 5 characters**).
- Decide story vs chaos using `generation.chaos_probability`.
- Sample `generation.candidates_to_sample` candidate tweets.
- Filter candidates through constraints (length, forbidden substrings/topics, required refs).
- Pick the highest-scoring candidate and:
  - `--dry-run`: print it
  - default: post to Twitter/X via Tweepy v2

## Run locally

### 1) Dry run (no Twitter API needed)

```bash
python3 tweetEngine.py --dry-run
```

### 2) Post for real

Install Tweepy:

```bash
python3 -m pip install tweepy
```

Set env vars:

- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`
- `TWITTER_BEARER_TOKEN`

Then run:

```bash
python3 tweetEngine.py
```

## Customize

- Put your 1-paragraph tone blurbs in:
  - `storyarc.json` → `characters.<name>.description` (left blank by default)
- Tune output:
  - `generation.chaos_probability`
  - `generation.candidates_to_sample`
  - `constraints.forbidden_substrings`
  - `required_refs`

