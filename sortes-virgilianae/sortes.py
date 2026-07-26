#!/usr/bin/env python3
"""Sortes Virgilianae: pose a question, draw a random verse of the Aeneid, and read it as an answer.

The ancients would open a copy of Virgil at random and take whatever line they
landed on as an omen. This picks a random verse from a curated selection of the
Aeneid, gives its English sense, and offers a reading of it as an answer to
your question.
"""

import argparse
import json
import os
import random
import textwrap
from pathlib import Path

VERSES_PATH = Path(__file__).parent / "verses.json"


def load_verses():
    with open(VERSES_PATH, encoding="utf-8") as f:
        return json.load(f)


def canned_reading(verse, question):
    return verse["reading"].format(question=question)


def llm_reading(verse, question):
    """Ask Claude for a fresh interpretation, if ANTHROPIC_API_KEY is set. Returns None on any failure."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
    except ImportError:
        return None

    prompt = (
        "You are performing sortes Virgilianae: a questioner has posed a question, "
        "drawn this random verse of the Aeneid by chance, and wants it read as an "
        "oracular answer. Interpret it thoughtfully and specifically for their "
        "question, the way a perceptive friend would read a fortune - a few "
        "sentences, evocative but grounded, not vague generic mysticism.\n\n"
        f"Question: {question}\n"
        f"Verse (Aeneid {verse['book']}.{verse['line']}): \"{verse['english']}\"\n"
        f"Context: {verse['context']}\n\n"
        "Give only the reading, no preamble."
    )
    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Sortes Virgilianae: an oracle from the Aeneid.")
    parser.add_argument(
        "question", nargs="*", help="the question to pose (if omitted, you'll be prompted)"
    )
    args = parser.parse_args()

    question = " ".join(args.question).strip()
    if not question:
        question = input("What is your question? ").strip()
    if not question:
        question = "What should I do?"

    verses = load_verses()
    verse = random.choice(verses)

    wrap = lambda s: textwrap.fill(s, width=78)

    print()
    print(f'Question: "{question}"')
    print()
    print(f"The lot falls on Aeneid {verse['book']}.{verse['line']}:")
    print()
    print(wrap(f"  {verse['latin']}"))
    print()
    print(wrap(f'  "{verse["english"]}"'))
    print()
    print(wrap(f"Context: {verse['context']}"))
    print()

    reading = llm_reading(verse, question)
    if reading is None:
        reading = canned_reading(verse, question)
    print(wrap(f"Reading: {reading}"))
    print()


if __name__ == "__main__":
    main()
