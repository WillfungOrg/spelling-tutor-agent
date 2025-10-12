#!/usr/bin/env python3
"""
Helper script to list available word lists and their contents.
"""
import sys
from src.spelling_tutor.word_list_loader import list_available_word_lists, load_word_list_from_file


def main():
    """List available word lists and optionally show their contents."""
    available = list_available_word_lists()

    print("Available word lists:")
    print("=" * 50)
    for name in available:
        print(f"  - {name}")

    if len(sys.argv) > 1:
        # Show details for specified word list
        word_list_name = sys.argv[1]
        print(f"\nWords in '{word_list_name}':")
        print("=" * 50)

        try:
            name, words = load_word_list_from_file(word_list_name)
            for i, word in enumerate(words, 1):
                print(f"{i:2d}. {word.word:20s} ({word.difficulty})")
            print(f"\nTotal: {len(words)} words")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return 1

    else:
        print(f"\nUsage: python {sys.argv[0]} [word_list_name]")
        print(f"Example: python {sys.argv[0]} week1")

    return 0


if __name__ == "__main__":
    sys.exit(main())
