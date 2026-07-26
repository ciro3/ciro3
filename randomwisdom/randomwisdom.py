#!/usr/bin/env python3
"""RandomWisdom: prints a random wisdom quote to the terminal."""

import argparse
import json
import random
from pathlib import Path

QUOTES_PATH = Path(__file__).parent / "quotes.json"


def load_quotes():
    with open(QUOTES_PATH, encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Print random wisdom quotes.")
    parser.add_argument(
        "-n", "--count", type=int, default=1, help="number of quotes to print (default: 1)"
    )
    args = parser.parse_args()

    quotes = load_quotes()
    for quote in random.sample(quotes, k=min(args.count, len(quotes))):
        print(f'"{quote["text"]}"\n  — {quote["author"]}\n')


if __name__ == "__main__":
    main()
