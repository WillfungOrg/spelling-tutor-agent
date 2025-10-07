import pytest
import random
from unittest.mock import patch
from spelling_tutor.tutor_logic import SpellingTutor


def test_get_introduction():
    """Test that introduction follows the correct format."""
    tutor = SpellingTutor("cat", "easy", "CVC")
    intro = tutor.get_introduction()

    # Check that it contains the word
    assert "cat" in intro
    assert "Let's spell the word" in intro

    # Check that it has an encouraging phrase
    encouraging_phrases = [
        "Great!", "Nice work!", "Fantastic!", "Excellent!", "Amazing"
    ]
    has_encouraging = any(phrase in intro for phrase in encouraging_phrases)
    assert has_encouraging, f"Introduction should contain encouraging phrase: {intro}"


def test_get_phonics_hint_progression():
    """Test that phonics hints progress appropriately through attempts."""
    tutor = SpellingTutor("cat", "easy", "CVC")

    # Attempt 1: General sound hint
    hint1 = tutor.get_phonics_hint(1)
    assert "Think about the sounds" in hint1
    assert "What sound does it start with" in hint1

    # Attempt 2: Syllable hint
    hint2 = tutor.get_phonics_hint(2)
    assert "syllable" in hint2
    assert "1 syllable" in hint2  # "cat" has 1 syllable

    # Attempt 3: Phoneme breakdown
    hint3 = tutor.get_phonics_hint(3)
    assert "sounds:" in hint3
    assert "consonant-vowel-consonant" in hint3

    # Attempt 4+: Give answer
    hint4 = tutor.get_phonics_hint(4)
    assert "CAT" in hint4


def test_get_phonics_hint_different_categories():
    """Test phonics hints for different phonics categories."""

    # Test digraph
    tutor_digraph = SpellingTutor("ship", "easy", "digraph-sh")
    hint = tutor_digraph.get_phonics_hint(3)
    assert "sh" in hint
    assert "one sound together" in hint

    # Test blend
    tutor_blend = SpellingTutor("black", "medium", "blend-bl")
    hint = tutor_blend.get_phonics_hint(3)
    assert "bl" in hint
    assert "blend together" in hint

    # Test other category
    tutor_other = SpellingTutor("apple", "medium", "other")
    hint = tutor_other.get_phonics_hint(3)
    assert "vowel" in hint
    assert "consonant" in hint


def test_check_spelling_correct():
    """Test correct spelling detection."""
    tutor = SpellingTutor("cat", "easy", "CVC")

    # Test exact match
    is_correct, feedback = tutor.check_spelling("cat")
    assert is_correct
    assert feedback in ["Awesome!", "Great job!", "You got it!", "Fantastic!", "Perfect!", "Excellent work!", "Amazing!"]

    # Test case insensitive
    is_correct, feedback = tutor.check_spelling("CAT")
    assert is_correct

    # Test with whitespace
    is_correct, feedback = tutor.check_spelling("  cat  ")
    assert is_correct


def test_check_spelling_close():
    """Test near-miss spelling detection."""
    tutor = SpellingTutor("cat", "easy", "CVC")

    # Test 1 character difference
    is_correct, feedback = tutor.check_spelling("cot")
    assert not is_correct
    assert feedback == "Almost! Try again."

    # Test 2 character difference
    is_correct, feedback = tutor.check_spelling("bat")
    assert not is_correct
    assert feedback == "Almost! Try again."

    # Test extra character
    is_correct, feedback = tutor.check_spelling("cats")
    assert not is_correct
    assert feedback == "Almost! Try again."

    # Test missing character
    is_correct, feedback = tutor.check_spelling("ca")
    assert not is_correct
    assert feedback == "Almost! Try again."


def test_check_spelling_wrong():
    """Test incorrect spelling that's not close."""
    tutor = SpellingTutor("cat", "easy", "CVC")

    # Test completely different word
    is_correct, feedback = tutor.check_spelling("elephant")
    assert not is_correct
    assert feedback == ""  # Empty string means caller should provide hint

    # Test random letters
    is_correct, feedback = tutor.check_spelling("xyz")
    assert not is_correct
    assert feedback == ""

    # Test empty input
    is_correct, feedback = tutor.check_spelling("")
    assert not is_correct
    assert feedback == ""


def test_positive_feedback():
    """Test that positive feedback is random and from expected list."""
    tutor = SpellingTutor("cat", "easy", "CVC")

    expected_feedback = [
        "Awesome!", "Great job!", "You got it!", "Fantastic!",
        "Perfect!", "Excellent work!", "Amazing!"
    ]

    # Get multiple feedback instances
    feedback_list = [tutor.get_positive_feedback() for _ in range(20)]

    # Check all feedback is from expected list
    for feedback in feedback_list:
        assert feedback in expected_feedback

    # Check that we get some variety (not always the same)
    unique_feedback = set(feedback_list)
    assert len(unique_feedback) > 1, "Feedback should be randomized"


def test_count_syllables():
    """Test syllable counting functionality."""
    tutor = SpellingTutor("test", "easy", "other")

    # Test single syllable words
    assert tutor.count_syllables("cat") == 1
    assert tutor.count_syllables("dog") == 1
    assert tutor.count_syllables("tree") == 1

    # Test two syllable words
    assert tutor.count_syllables("apple") == 2
    assert tutor.count_syllables("table") == 2
    assert tutor.count_syllables("happy") == 2

    # Test three syllable words
    assert tutor.count_syllables("elephant") == 3
    assert tutor.count_syllables("banana") == 3

    # Test words with silent 'e'
    assert tutor.count_syllables("make") == 1
    assert tutor.count_syllables("little") == 2

    # Test edge cases
    assert tutor.count_syllables("") == 0
    assert tutor.count_syllables("a") == 1
    assert tutor.count_syllables("I") == 1


def test_levenshtein_distance():
    """Test the internal Levenshtein distance calculation."""
    tutor = SpellingTutor("cat", "easy", "CVC")

    # Test identical strings
    assert tutor._levenshtein_distance("cat", "cat") == 0

    # Test single substitution
    assert tutor._levenshtein_distance("cat", "bat") == 1

    # Test single insertion
    assert tutor._levenshtein_distance("cat", "cats") == 1

    # Test single deletion
    assert tutor._levenshtein_distance("cats", "cat") == 1

    # Test multiple operations
    assert tutor._levenshtein_distance("kitten", "sitting") == 3

    # Test empty strings
    assert tutor._levenshtein_distance("", "cat") == 3
    assert tutor._levenshtein_distance("cat", "") == 3
    assert tutor._levenshtein_distance("", "") == 0


@patch('random.choice')
def test_introduction_randomization(mock_choice):
    """Test that introduction uses random choice for encouraging phrases."""
    mock_choice.return_value = "Great! You're doing wonderful."

    tutor = SpellingTutor("cat", "easy", "CVC")
    intro = tutor.get_introduction()

    # Verify random.choice was called
    mock_choice.assert_called_once()

    # Verify the format
    expected = "Great! You're doing wonderful. Let's spell the word 'cat'."
    assert intro == expected


def test_tutor_initialization():
    """Test that tutor initializes correctly with different parameters."""
    tutor = SpellingTutor("ELEPHANT", "hard", "other")

    # Check that word is normalized to lowercase
    assert tutor.word == "elephant"
    assert tutor.difficulty == "hard"
    assert tutor.phonics_category == "other"


def test_syllable_hint_with_multiple_syllables():
    """Test syllable hints with words of different syllable counts."""
    # Two syllable word
    tutor2 = SpellingTutor("apple", "medium", "other")
    hint2 = tutor2.get_phonics_hint(2)
    assert "2 syllables" in hint2

    # Three syllable word
    tutor3 = SpellingTutor("elephant", "hard", "other")
    hint3 = tutor3.get_phonics_hint(2)
    assert "3 syllables" in hint3

    # Single syllable (should say "1 syllable", not "1 syllables")
    tutor1 = SpellingTutor("cat", "easy", "CVC")
    hint1 = tutor1.get_phonics_hint(2)
    assert "1 syllable" in hint1
    assert "1 syllables" not in hint1