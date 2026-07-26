# Sortes Virgilianae

An oracle from Virgil's *Aeneid*, in the old Roman style: pose a question, and
the program draws a random verse from a curated selection of the poem and
reads it as your answer — the practice Nassim Taleb describes in *Antifragile*,
where readers would open the Aeneid at random and take whatever line they
landed on as guidance.

## Usage

Ask a question directly:

```bash
python3 sortes.py "Should I take the new job?"
```

Or run it with no arguments and you'll be prompted:

```bash
python3 sortes.py
```

Each draw prints the Latin, an English rendering, brief context on who says
it and when, and a reading of what it could mean as an answer.

## Verse bank

`verses.json` holds a curated selection of roughly 30 well-known, verified
lines spanning all twelve books of the Aeneid — not the full poem, but enough
range across fate, courage, grief, love, war, and warning for a good draw.

## Optional: live interpretation via Claude

By default the reading is a pre-written interpretation baked into
`verses.json`. If you set `ANTHROPIC_API_KEY` in your environment and have the
`anthropic` package installed (`pip install anthropic`), the program will
instead ask Claude to interpret the drawn verse specifically for your
question. It silently falls back to the canned reading if the key or package
is missing, or the request fails.

## Requirements

Python 3.7+. No required dependencies; `anthropic` is optional.
