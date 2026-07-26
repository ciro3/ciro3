# Sortes Virgilianae

An oracle from Virgil's *Aeneid*, in the old Roman style: pose a question,
and the program draws one line uniformly at random from the entire real
poem and reads it as your answer — the practice Nassim Taleb describes in
*Antifragile*, where readers would open the Aeneid at random and take
whatever line they landed on as guidance.

## How the random draw works

This doesn't pick from a hand-picked shortlist. On first run it fetches the
complete Latin text of the Aeneid — the J. B. Greenough edition, sourced from
the Perseus Digital Library's public-domain mirror on GitHub
(`PerseusDL/canonical-latinLit`) — all ~9,862 lines across all 12 books, and
caches it in `cache/`. Every draw picks one real line number uniformly at
random out of all of them (book selection is weighted by book length, so
every line has an equal chance, not every book).

Run with `--refresh` to re-download the source text instead of using the
cache.

## Usage

```bash
python3 sortes.py "Should I take the new job?"
```

Or run with no arguments and you'll be prompted:

```bash
python3 sortes.py
```

## English translation and interpretation

Translating one line out of context isn't something a static file can do
well, so:

- **With `ANTHROPIC_API_KEY` set** (and `pip install anthropic`): the program
  sends the exact drawn line to Claude and asks for a plain translation,
  brief context on who's speaking, and a reading of it against your
  question. This is the intended full experience.
- **Without it**: you still get the real Latin line and its citation, plus
  the nearest passage from a second public-domain source (Theodore C.
  Williams' 1910 verse translation, also fetched from the same Perseus
  mirror) as approximate context — its own line numbers don't map 1:1 to the
  Latin, so it's a neighborhood, not a literal rendering. The "reading" in
  this mode is just an invitation to interpret the line yourself, the way
  the Romans actually did it.

## Requirements

Python 3.7+, internet access on first run (later runs use the cache).
`anthropic` is optional, for live translation/interpretation.
