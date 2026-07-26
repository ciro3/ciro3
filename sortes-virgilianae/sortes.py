#!/usr/bin/env python3
"""Sortes Virgilianae: draw a truly random line of the Aeneid and read it as an answer.

Every run, this consults a real online copy of the complete Latin text (the
J. B. Greenough edition, via the Perseus Digital Library's public-domain
mirror on GitHub), picks one line number uniformly at random out of all
~9,860 real lines in the poem, and reads that exact line back to you. The
first run downloads and caches the text; later runs draw from the cache so
every line of the real poem stays reachable without re-fetching every time.
"""

import argparse
import html
import os
import random
import re
import textwrap
import urllib.error
import urllib.request
from pathlib import Path

CACHE_DIR = Path(__file__).parent / "cache"

LAT_URL = (
    "https://raw.githubusercontent.com/PerseusDL/canonical-latinLit/master/"
    "data/phi0690/phi003/phi0690.phi003.perseus-lat2.xml"
)
ENG_URL = (
    "https://raw.githubusercontent.com/PerseusDL/canonical-latinLit/master/"
    "data/phi0690/phi003/phi0690.phi003.perseus-eng2.xml"
)

BOOK_DIV_RE = re.compile(
    r'<div\b(?=[^>]*\btype="textpart")(?=[^>]*\bsubtype="book")(?=[^>]*\bn="(\d+)")[^>]*>'
)
LINE_RE = re.compile(r'<l n="([^"]+)"[^>]*>(.*?)</l>', re.DOTALL)


def fetch(url, cache_name, refresh=False):
    CACHE_DIR.mkdir(exist_ok=True)
    cache_path = CACHE_DIR / cache_name
    if cache_path.exists() and not refresh:
        return cache_path.read_text(encoding="utf-8")
    with urllib.request.urlopen(url, timeout=15) as resp:
        text = resp.read().decode("utf-8")
    cache_path.write_text(text, encoding="utf-8")
    return text


def clean(raw_xml_fragment):
    no_tags = re.sub(r"<[^>]+>", "", raw_xml_fragment)
    return html.unescape(" ".join(no_tags.split()))


def parse_books(xml_text):
    """Return {book_num: {line_num: text}} parsed straight out of the TEI XML."""
    divs = list(BOOK_DIV_RE.finditer(xml_text))
    books = {}
    for i, m in enumerate(divs):
        book = int(m.group(1))
        start = m.end()
        end = divs[i + 1].start() if i + 1 < len(divs) else len(xml_text)
        segment = xml_text[start:end]
        lines = {}
        for lm in LINE_RE.finditer(segment):
            n_raw, text = lm.group(1), lm.group(2)
            try:
                n = int(n_raw)
            except ValueError:
                continue  # skips the rare split half-line label like "62b"
            lines[n] = clean(text)
        books[book] = lines
    return books


def draw_random_line(latin_books):
    """Pick uniformly among every real line in the poem (books weighted by length)."""
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
    parser.add_argument("--refresh", action="store_true", help="re-download the source text")
    args = parser.parse_args()

    question = " ".join(args.question).strip()
    if not question:
        question = input("What is your question? ").strip()
    if not question:
        question = "What should I do?"

    try:
        latin_xml = fetch(LAT_URL, "aeneid-latin.xml", refresh=args.refresh)
        english_xml = fetch(ENG_URL, "aeneid-english.xml", refresh=args.refresh)
    except (urllib.error.URLError, TimeoutError) as e:
        raise SystemExit(
            f"Couldn't reach the online source ({e}). "
            "Sortes Virgilianae needs internet access on first run to fetch the real "
            "text; after that it uses the local cache in cache/."
        )

    latin_books = parse_books(latin_xml)
    english_books = parse_books(english_xml)

    book, line = draw_random_line(latin_books)
    latin_line = latin_books[book][line]

    wrap = lambda s: textwrap.fill(s, width=78)

    print()
    print(f'Question: "{question}"')
    print()
    print(f"The lot falls on Aeneid {book}.{line} (of {sum(len(v) for v in latin_books.values())} lines):")
    print()
    print(wrap(f"  {latin_line}"))
    print()

    result = llm_translate_and_read(latin_line, book, line, question)
    if result:
        print(wrap(result))
    else:
        passage = nearest_english_passage(english_books, latin_books, book, line)
        print("(No ANTHROPIC_API_KEY set, so here's the nearest passage from the")
        print(" public-domain Williams 1910 translation - it doesn't line up 1:1")
        print(" with the Latin numbering, so treat it as a neighborhood, not a")
        print(" literal rendering of the exact line above.)")
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
