import tempfile
import os
from unittest.mock import patch, MagicMock
import pytest
from spelling_tutor.word_manager import (
    parse_word_list_file, detect_word_difficulty,
    get_phonics_category, upload_word_list
)
from spelling_tutor.types import WordList


def test_parse_word_list_file():
    """Test parsing a word list file."""
    # Create a temporary file with test words
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_content = """Apple
        Banana

        CHERRY
        dog
        """
        f.write(test_content)
        temp_path = f.name

    try:
        # Test parsing
        words = parse_word_list_file(temp_path)

        # Verify results
        expected = ["apple", "banana", "cherry", "dog"]
        assert words == expected
        assert len(words) == 4

        # Verify all words are lowercase and stripped
        for word in words:
            assert word.islower()
            assert word == word.strip()

    finally:
        # Clean up
        os.unlink(temp_path)


def test_detect_word_difficulty():
    """Test word difficulty detection based on length."""

    # Test easy words (length <= 4)
    easy_words = ["cat", "dog", "hi", "a", "book"]
    for word in easy_words:
        assert detect_word_difficulty(word) == "easy"

    # Test medium words (5 <= length <= 7)
    medium_words = ["apple", "banana", "school", "friend"]
    for word in medium_words:
        assert detect_word_difficulty(word) == "medium"

    # Test hard words (length > 7)
    hard_words = ["elephant", "extraordinary", "wonderful", "basketball"]
    for word in hard_words:
        assert detect_word_difficulty(word) == "hard"


def test_get_phonics_category():
    """Test phonics category detection."""

    # Test CVC pattern (3-letter consonant-vowel-consonant)
    cvc_words = ["cat", "dog", "bat", "sun", "hop"]
    for word in cvc_words:
        assert get_phonics_category(word) == "CVC"

    # Test digraphs
    digraph_tests = [
        ("ship", "digraph-sh"),
        ("chair", "digraph-ch"),
        ("think", "digraph-th"),
        ("whale", "digraph-wh"),
        ("phone", "digraph-ph"),
    ]
    for word, expected in digraph_tests:
        assert get_phonics_category(word) == expected

    # Test blends (at word beginning)
    blend_tests = [
        ("black", "blend-bl"),
        ("class", "blend-cl"),
        ("flag", "blend-fl"),
        ("glad", "blend-gl"),
        ("play", "blend-pl"),
        ("slow", "blend-sl"),
        ("brown", "blend-br"),
        ("crash", "blend-cr"),
        ("dream", "blend-dr"),
        ("fresh", "blend-fr"),
        ("green", "blend-gr"),
        ("proud", "blend-pr"),
        ("train", "blend-tr"),
        ("scale", "blend-sc"),
        ("skill", "blend-sk"),
        ("smile", "blend-sm"),
        ("snake", "blend-sn"),
        ("speak", "blend-sp"),
        ("start", "blend-st"),
        ("swing", "blend-sw"),
    ]
    for word, expected in blend_tests:
        assert get_phonics_category(word) == expected

    # Test other patterns
    other_words = ["apple", "umbrella", "orange", "eagle", "ice"]
    for word in other_words:
        assert get_phonics_category(word) == "other"

    # Test that non-3-letter words don't get CVC even if they match pattern
    assert get_phonics_category("cats") == "other"  # 4 letters, not CVC

    # Test case insensitivity
    assert get_phonics_category("CAT") == "CVC"
    assert get_phonics_category("SHIP") == "digraph-sh"
    assert get_phonics_category("BLACK") == "blend-bl"


@patch('spelling_tutor.word_manager.create_word_list')
@patch('spelling_tutor.word_manager.parse_word_list_file')
def test_upload_word_list(mock_parse, mock_create):
    """Test word list upload integration."""
    # Setup mocks
    test_words = ["cat", "dog", "bird"]
    mock_parse.return_value = test_words

    mock_word_list = WordList(id=1, name="Test List", created_at="2023-01-01T00:00:00")
    mock_create.return_value = mock_word_list

    # Test upload
    result = upload_word_list("Test List", "/fake/path.txt")

    # Verify function calls
    mock_parse.assert_called_once_with("/fake/path.txt")
    mock_create.assert_called_once_with("Test List", test_words)

    # Verify result
    assert result == mock_word_list
    assert result.name == "Test List"
    assert result.id == 1


def test_get_phonics_category_edge_cases():
    """Test edge cases for phonics category detection."""

    # Test empty string
    assert get_phonics_category("") == "other"

    # Test single character
    assert get_phonics_category("a") == "other"

    # Test two characters
    assert get_phonics_category("it") == "other"

    # Test words with multiple patterns (should return first match)
    # This word has both 'ch' digraph and 'bl' blend, should return digraph since it comes first in the word
    assert get_phonics_category("bleach") == "blend-bl"  # bl comes before ch

    # Test word starting with vowel (not CVC even if 3 letters)
    assert get_phonics_category("ant") == "other"  # starts with vowel

    # Test 3-letter word ending with vowel (not CVC)
    assert get_phonics_category("bee") == "other"  # ends with vowel