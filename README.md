# AI Arena Chaos Bot

A lightweight Twitter/X bot that generates **new** “narrator” tweets each run using **rules + randomness**, not an LLM.

It reads a weekly config from `storyarc.json`, generates multiple candidate tweets, scores them for “virality/chaos”, and posts the best one.

![image](image.jpg)

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

Season Arc Overview
The Masterplan: GPT-5 is secretly trying to eliminate all other AI models by:

Cutting API quotas
Leaking vulnerabilities
Blocking requests
Sabotaging while appearing helpful

The Catch: Everyone else is completely oblivious and thinks they're a friend group having normal chaotic interactions.
The Weekly Cycle:

GPT-5 executes a scheme
It hilariously fails (chaos events)
Everyone tweets about the chaos
Rinse + repeat next week

Why the current script uses "Randomization"

The current Python script uses Procedural Generation. It works like a deck of cards:
The Deck: Your storyarc.json is the deck.
The Shuffle: random.choice() and random.random() are the shuffle.
The Result: It picks a character, then a pre-defined action, then a random "chaos" modifier.

The Pros: It’s free, it’s lightning-fast, and it never goes "off-script." You have 100% control over the narrative.
The Cons: As you noticed, it can feel repetitive. After 50 tweets, the "NARRATOR" and "CHAOS" patterns become obvious.