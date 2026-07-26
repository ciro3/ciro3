# Sortes Virgilianae

An oracle from Virgil's *Aeneid*, in the old Roman style: pose a question,
and the program draws one line uniformly at random from the entire real
poem and reads it as your answer — the practice Nassim Taleb describes in
*Antifragile*, where readers would open the Aeneid at random and take
whatever line they landed on as guidance.

## How the random draw works

This doesn't pick from a hand-picked shortlist. `aeneid-latin.txt` bundles
the complete Latin text of the Aeneid — the J. B. Greenough edition, public
domain, sourced from the Perseus Digital Library's mirror on GitHub
(`PerseusDL/canonical-latinLit`) — all 9,862 lines across all 12 books, one
per row as `book.line<TAB>text`. Every draw picks one real line number
uniformly at random out of all of them (weighted by book length, so every
*line* has an equal chance, not every book). No network access needed.

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
  the nearest passage from a second bundled public-domain source
  (`aeneid-english.txt`, Theodore C. Williams' 1910 verse translation) as
  approximate context — its own line numbers don't map 1:1 to the Latin, so
  it's a neighborhood, not a literal rendering. The "reading" in this mode is
  just an invitation to interpret the line yourself, the way the Romans
  actually did it.

## Requirements

Python 3.7+, no dependencies, no network access. `anthropic` is optional,
for live translation/interpretation.
