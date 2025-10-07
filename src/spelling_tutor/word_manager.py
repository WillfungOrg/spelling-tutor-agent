import re
from typing import List
from .types import WordList
from .database import create_word_list


def parse_word_list_file(file_path: str) -> List[str]:
    """
    Parse a word list file and return a list of cleaned words.

    Args:
        file_path: Path to the text file containing words (one per line).

    Returns:
        List[str]: List of cleaned words in lowercase with whitespace stripped.
    """
    words = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip().lower()
            if word:  # Skip empty lines
                words.append(word)
    return words


def detect_word_difficulty(word: str) -> str:
    """
    Detect the difficulty level of a word based on its length.

    Args:
        word: The word to analyze.

    Returns:
        str: Difficulty level ('easy', 'medium', or 'hard').
    """
    length = len(word)
    if length <= 4:
        return "easy"
    elif length <= 7:
        return "medium"
    else:
        return "hard"


def upload_word_list(name: str, file_path: str) -> WordList:
    """
    Upload a word list from a file to the database.

    Args:
        name: Name for the word list.
        file_path: Path to the text file containing words.

    Returns:
        WordList: The created word list.
    """
    words = parse_word_list_file(file_path)
    return create_word_list(name, words)


def get_phonics_category(word: str) -> str:
    """
    Detect the phonics category of a word based on patterns.

    Args:
        word: The word to analyze.

    Returns:
        str: Phonics category ('CVC', 'digraph-XX', 'blend-XX', or 'other').
    """
    word = word.lower()

    # Check for CVC pattern (consonant-vowel-consonant) for 3-letter words
    if len(word) == 3:
        vowels = 'aeiou'
        consonants = 'bcdfghjklmnpqrstvwxyz'
        if (word[0] in consonants and
            word[1] in vowels and
            word[2] in consonants):
            return 'CVC'

    # Define digraphs and blends
    digraphs = ['sh', 'ch', 'th', 'wh', 'ph']
    blends = ['bl', 'cl', 'fl', 'gl', 'pl', 'sl', 'br', 'cr', 'dr', 'fr', 'gr', 'pr', 'tr', 'sc', 'sk', 'sm', 'sn', 'sp', 'st', 'sw']

    # Check for blends first (at the beginning of words)
    for blend in blends:
        if word.startswith(blend):
            return f'blend-{blend}'

    # Check for digraphs
    for digraph in digraphs:
        if digraph in word:
            return f'digraph-{digraph}'

    return 'other'