"""
Word list loader that reads from text files in data/word_lists/
"""
import os
from pathlib import Path
from typing import Optional
from .types import Word


def get_word_lists_directory() -> Path:
    """Get the path to the word_lists directory."""
    # Assuming the project structure: src/spelling_tutor/ and data/word_lists/
    project_root = Path(__file__).parent.parent.parent
    word_lists_dir = project_root / "data" / "word_lists"
    return word_lists_dir


def list_available_word_lists() -> list[str]:
    """
    List all available word list files.

    Returns:
        list[str]: List of word list file names (without .txt extension)
    """
    word_lists_dir = get_word_lists_directory()

    if not word_lists_dir.exists():
        return []

    word_lists = []
    for file_path in word_lists_dir.glob("*.txt"):
        word_lists.append(file_path.stem)  # Get filename without extension

    return sorted(word_lists)


def load_word_list_from_file(word_list_name: str) -> tuple[str, list[Word]]:
    """
    Load a word list from a text file.

    Args:
        word_list_name: Name of the word list (e.g., 'week1', 'test_words')

    Returns:
        tuple: (word_list_name, list of Word objects)

    Raises:
        FileNotFoundError: If the word list file doesn't exist
    """
    word_lists_dir = get_word_lists_directory()
    file_path = word_lists_dir / f"{word_list_name}.txt"

    if not file_path.exists():
        available = list_available_word_lists()
        raise FileNotFoundError(
            f"Word list '{word_list_name}' not found. "
            f"Available word lists: {', '.join(available)}"
        )

    # Read words from file
    words = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            word = line.strip()

            # Skip empty lines
            if not word:
                continue

            # Detect difficulty based on word characteristics
            difficulty = _detect_difficulty(word)

            # Create Word object (using line_num as a pseudo-ID)
            words.append(Word(
                id=line_num,
                word_list_id=0,  # Not used for file-based loading
                word=word,
                difficulty=difficulty
            ))

    return word_list_name, words


def _detect_difficulty(word: str) -> str:
    """
    Auto-detect word difficulty based on length and complexity.

    Args:
        word: The word to analyze.

    Returns:
        str: Difficulty level (easy, medium, hard).
    """
    # Remove spaces for multi-word phrases
    word_clean = word.replace(" ", "")
    length = len(word_clean)

    # Check if it's a phrase (has spaces)
    is_phrase = " " in word

    if is_phrase:
        # Phrases are generally harder
        return "hard"
    elif length <= 4:
        return "easy"
    elif length <= 7:
        return "medium"
    else:
        return "hard"


def get_default_word_list() -> str:
    """
    Get the default word list name.

    Returns:
        str: Default word list name (prefer 'week1', fallback to first available)
    """
    available = list_available_word_lists()

    if not available:
        raise FileNotFoundError("No word lists found in data/word_lists/")

    # Prefer 'week1' if it exists
    if 'week1' in available:
        return 'week1'

    # Otherwise return the first available
    return available[0]
