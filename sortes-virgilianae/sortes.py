#!/usr/bin/env python3
"""Sortes Virgilianae: draw a truly random line of the Aeneid and read it as an answer.

The complete Latin text (the J. B. Greenough edition, public domain, via the
Perseus Digital Library) is bundled locally in aeneid-latin.txt, one real
line per row, enumerated as "book.line". Every run picks one line number
uniformly at random out of all ~9,862 of them - no network access needed,
and no preselected shortlist.
"""

import argparse
import os
import random
import textwrap
from pathlib import Path

HERE = Path(__file__).parent
LATIN_PATH = HERE / "aeneid-latin.txt"
ENGLISH_PATH = HERE / "aeneid-english.txt"


def load_lines(path):
    """Parse a "book.line<TAB>text" file into {book: {line: text}}."""
    books = {}
    with open(path, encoding="utf-8") as f:
        for row in f:
            ref, text = row.rstrip("\n").split("\t", 1)
            book_str, line_str = ref.split(".")
            books.setdefault(int(book_str), {})[int(line_str)] = text
    return books


def draw_random_line(latin_books):
    """Pick uniformly among every real line in the poem (weighted by book length)."""
    pool = [(book, line) for book, lines in latin_books.items() for line in lines]
    return random.choice(pool)


def nearest_english_passage(english_books, latin_books, book, line):
    """The Williams (1910) translation doesn't number 1:1 with the Latin, so this
    maps proportionally into its numbering and grabs the neighborhood - an
    approximation, not a literal translation of the exact line."""
    lat_lines = latin_books[book]
    eng_lines = english_books.get(book)
    if not eng_lines:
        return None
    target = max(1, round(line / max(lat_lines) * max(eng_lines)))
    nums = sorted(eng_lines)
    nearest_idx = min(range(len(nums)), key=lambda i: abs(nums[i] - target))
    window = nums[max(0, nearest_idx - 1) : nearest_idx + 2]
    return " ".join(eng_lines[n] for n in window)


def llm_translate_and_read(latin_line, book, line, question):
    """Ask Claude to translate the exact drawn line and read it against the
    question. Returns None (to trigger the offline fallback) if no API key,
    the anthropic package, or the request itself is unavailable."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
    except ImportError:
        return None

    prompt = (
        "You are performing sortes Virgilianae: someone posed a question and, by "
        "pure chance, drew this exact random line of Virgil's Aeneid as their oracle.\n\n"
        f"Question: {question}\n"
        f'Latin (Aeneid {book}.{line}): "{latin_line}"\n\n'
        "Reply in exactly this shape, nothing else:\n"
        "English: <a plain, accurate translation of just this line>\n"
        "Context: <one sentence on who says this and what's happening, if known>\n"
        "Reading: <2-3 sentences interpreting it as an answer to the question - "
        "evocative but grounded, not vague generic mysticism>"
    )
    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=350,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Sortes Virgilianae: an oracle from the Aeneid.")
    parser.add_argument("question", nargs="*", help="the question to pose (prompted if omitted)")
    args = parser.parse_args()

    question = " ".join(args.question).strip()
    if not question:
        question = input("What is your question? ").strip()
    if not question:
        question = "What should I do?"

    latin_books = load_lines(LATIN_PATH)
    english_books = load_lines(ENGLISH_PATH)

    book, line = draw_random_line(latin_books)
    latin_line = latin_books[book][line]

    wrap = lambda s: textwrap.fill(s, width=78)
    total = sum(len(v) for v in latin_books.values())

    print()
    print(f'Question: "{question}"')
    print()
    print(f"The lot falls on Aeneid {book}.{line} (of {total} lines):")
    print()
    print(wrap(f"  {latin_line}"))
    print()

    result = llm_translate_and_read(latin_line, book, line, question)
    if result:
        print(wrap(result))
    else:
        passage = nearest_english_passage(english_books, latin_books, book, line)
        print("(No ANTHROPIC_API_KEY set, so here's the nearest passage from the")
        print(" bundled public-domain Williams 1910 translation - it doesn't line")
        print(" up 1:1 with the Latin numbering, so treat it as a neighborhood, not")
        print(" a literal rendering of the exact line above.)")
        print()
        if passage:
            print(wrap(f"English (approximate): {passage}"))
            print()
        print(
            wrap(
                f'Reading: The oracle offers no ready-made answer to "{question}" here - '
                "that's the point of the practice. Sit with the line above and notice "
                "what in it snags your attention; that's the reading."
            )
        )
    print()


if __name__ == "__main__":
    main()
