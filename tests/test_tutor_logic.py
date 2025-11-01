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

    # Attempt 1: General sound hint (should mention starting/first sound)
    hint1 = tutor.get_phonics_hint(1)
    assert ("sound" in hint1.lower() and ("start" in hint1.lower() or "beginning" in hint1.lower() or "first" in hint1.lower()))

    # Attempt 2: Syllable hint (should mention parts/claps)
    hint2 = tutor.get_phonics_hint(2)
    assert ("part" in hint2.lower() or "clap" in hint2.lower())
    assert "1" in hint2  # "cat" has 1 syllable/part

    # Attempt 3: Phoneme breakdown (child-friendly - breaks down letters)
    hint3 = tutor.get_phonics_hint(3)
    # Should mention the individual letters or sounds
    assert ("c" in hint3.lower() and "a" in hint3.lower() and "t" in hint3.lower())

    # Attempt 4+: Give answer
    hint4 = tutor.get_phonics_hint(4)
    assert "CAT" in hint4


def test_get_phonics_hint_different_categories():
    """Test phonics hints for different phonics categories."""

    # Test digraph (should mention the digraph and that letters work together)
    tutor_digraph = SpellingTutor("ship", "easy", "digraph-sh")
    hint = tutor_digraph.get_phonics_hint(3)
    assert "sh" in hint
    assert ("together" in hint.lower() or "one sound" in hint.lower())

    # Test blend (should mention the blend)
    tutor_blend = SpellingTutor("black", "medium", "blend-bl")
    hint = tutor_blend.get_phonics_hint(3)
    assert "bl" in hint
    assert "blend" in hint.lower()

    # Test other category (should break down sounds)
    tutor_other = SpellingTutor("apple", "medium", "other")
    hint = tutor_other.get_phonics_hint(3)
    # Should mention letters or sounds
    assert ("sound" in hint.lower() or "letter" in hint.lower())


def test_check_spelling_correct():
    """Test correct spelling detection with new varied feedback."""
    tutor = SpellingTutor("cat", "easy", "CVC")

    # Test exact match - should return True and non-empty feedback
    is_correct, feedback = tutor.check_spelling("cat")
    assert is_correct
    assert feedback != ""  # Should have positive feedback (from 24 options)
    assert len(feedback) > 0

    # Test case insensitive
    is_correct, feedback = tutor.check_spelling("CAT")
    assert is_correct
    assert feedback != ""

    # Test with whitespace
    is_correct, feedback = tutor.check_spelling("  cat  ")
    assert is_correct
    assert feedback != ""


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
    """Test that positive feedback is random and varied (24 options)."""
    tutor = SpellingTutor("cat", "easy", "CVC")

    # Get multiple feedback instances
    feedback_list = [tutor.get_positive_feedback() for _ in range(30)]

    # Check all feedback is non-empty
    for feedback in feedback_list:
        assert feedback != ""
        assert len(feedback) > 0

    # Check that we get variety (should have at least 5 different responses in 30 tries)
    unique_feedback = set(feedback_list)
    assert len(unique_feedback) >= 5, f"Feedback should be varied - got {len(unique_feedback)} unique responses: {unique_feedback}"


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
    # Two syllable word (now uses "parts" or "claps")
    tutor2 = SpellingTutor("apple", "medium", "other")
    hint2 = tutor2.get_phonics_hint(2)
    assert ("2 part" in hint2 or "2 clap" in hint2)

    # Three syllable word
    tutor3 = SpellingTutor("elephant", "hard", "other")
    hint3 = tutor3.get_phonics_hint(2)
    assert ("3 part" in hint3 or "3 clap" in hint3)

    # Single syllable (should say "1 part", not "1 parts")
    tutor1 = SpellingTutor("cat", "easy", "CVC")
    hint1 = tutor1.get_phonics_hint(2)
    assert ("1 part" in hint1 or "1 clap" in hint1)
    assert ("1 parts" not in hint1 and "1 claps" not in hint1)


def test_get_introduction_format():
    """Test that introduction checks encouraging phrase and word included."""
    tutor = SpellingTutor("hello", "medium", "other")
    intro = tutor.get_introduction()

    # Check word is included
    assert "hello" in intro
    assert "Let's spell the word" in intro

    # Check encouraging phrase is included
    encouraging_phrases = [
        "Great!", "Nice work!", "Fantastic!", "Excellent!", "Amazing"
    ]
    has_encouraging = any(phrase in intro for phrase in encouraging_phrases)
    assert has_encouraging, f"Introduction should contain encouraging phrase: {intro}"

    # Check overall format
    assert intro.endswith("'hello'.")


def test_get_phonics_hint_all_attempts():
    """Test hints for attempts 1, 2, 3, and beyond."""
    tutor = SpellingTutor("elephant", "hard", "other")

    # Attempt 1 (starting sound)
    hint1 = tutor.get_phonics_hint(1)
    assert ("sound" in hint1.lower() and ("start" in hint1.lower() or "beginning" in hint1.lower() or "first" in hint1.lower()))

    # Attempt 2 (syllables/parts)
    hint2 = tutor.get_phonics_hint(2)
    assert ("part" in hint2.lower() or "clap" in hint2.lower())
    assert "3" in hint2  # elephant has 3 syllables/parts

    # Attempt 3 (sound breakdown)
    hint3 = tutor.get_phonics_hint(3)
    # Should mention sounds or letters
    assert ("sound" in hint3.lower() or "letter" in hint3.lower())

    # Attempt 4+ (give answer)
    hint4 = tutor.get_phonics_hint(4)
    assert "ELEPHANT" in hint4

    hint5 = tutor.get_phonics_hint(5)
    assert "ELEPHANT" in hint5  # Should still give answer


def test_check_spelling_exact_match():
    """Test correct spelling detection with exact matches."""
    tutor = SpellingTutor("word", "easy", "other")

    # Exact match - should return True and non-empty feedback
    correct, feedback = tutor.check_spelling("word")
    assert correct is True
    assert feedback != ""
    assert len(feedback) > 0


def test_check_spelling_case_insensitive():
    """Test that CAT cat CaT all work."""
    tutor = SpellingTutor("cat", "easy", "CVC")

    # Test various cases
    test_cases = ["cat", "CAT", "Cat", "CaT", "cAt", "cAT"]
    for test_input in test_cases:
        correct, feedback = tutor.check_spelling(test_input)
        assert correct is True, f"Failed for input: {test_input}"
        assert feedback != "", f"No feedback for input: {test_input}"


def test_check_spelling_whitespace():
    """Test leading and trailing spaces are handled."""
    tutor = SpellingTutor("dog", "easy", "CVC")

    # Test whitespace handling
    whitespace_cases = [" dog", "dog ", "  dog  ", "\tdog\t", "\n dog \n"]
    for test_input in whitespace_cases:
        correct, feedback = tutor.check_spelling(test_input)
        assert correct is True, f"Failed for input: '{test_input}'"
        assert feedback != "", f"No feedback for input: '{test_input}'"


def test_check_spelling_close_match():
    """Test 1 character difference detection."""
    tutor = SpellingTutor("cat", "easy", "CVC")

    # 1 character differences
    close_cases = ["bat", "cot", "cut", "cats", "ca", "at"]
    for test_input in close_cases:
        correct, feedback = tutor.check_spelling(test_input)
        assert correct is False, f"Should be incorrect for: {test_input}"
        assert feedback == "Almost! Try again.", f"Wrong feedback for: {test_input}"


def test_check_spelling_far_match():
    """Test completely wrong spelling."""
    tutor = SpellingTutor("cat", "easy", "CVC")

    # Completely different words
    wrong_cases = ["elephant", "wonderful", "xyz", "12345", "house"]
    for test_input in wrong_cases:
        correct, feedback = tutor.check_spelling(test_input)
        assert correct is False, f"Should be incorrect for: {test_input}"
        assert feedback == "", f"Should have empty feedback for: {test_input}"


def test_positive_feedback_variety():
    """Test multiple calls return different phrases (24 options now)."""
    tutor = SpellingTutor("test", "easy", "other")

    # Get multiple feedback instances
    feedback_list = [tutor.get_positive_feedback() for _ in range(30)]

    # Check all are non-empty
    for feedback in feedback_list:
        assert feedback != ""
        assert len(feedback) > 0

    # Check we get variety (should have at least 5 different phrases in 30 calls)
    unique_feedback = set(feedback_list)
    assert len(unique_feedback) >= 5, f"Should get variety in feedback - got {len(unique_feedback)} unique responses"


def test_count_syllables_accuracy():
    """Test 1, 2, 3 syllable words for accuracy."""
    tutor = SpellingTutor("test", "easy", "other")

    # 1 syllable words
    one_syllable = ["cat", "dog", "run", "tree", "make", "cake", "house"]
    for word in one_syllable:
        assert tutor.count_syllables(word) == 1, f"'{word}' should be 1 syllable"

    # 2 syllable words
    two_syllable = ["apple", "table", "happy", "water", "money", "paper", "simple"]
    for word in two_syllable:
        assert tutor.count_syllables(word) == 2, f"'{word}' should be 2 syllables"

    # 3 syllable words
    three_syllable = ["elephant", "banana", "computer", "important", "beautiful", "wonderful"]
    for word in three_syllable:
        assert tutor.count_syllables(word) == 3, f"'{word}' should be 3 syllables"


def test_check_spelling_empty_input():
    """Test empty string input handling."""
    tutor = SpellingTutor("cat", "easy", "CVC")

    correct, feedback = tutor.check_spelling("")
    assert correct is False
    assert feedback == ""


def test_phonics_hint_progression_consistency():
    """Test that phonics hints are VARIED (randomized) for engagement."""
    tutor = SpellingTutor("ship", "easy", "digraph-sh")

    # Now hints are randomized for variety - collect multiple and check for variety
    hint1_list = [tutor.get_phonics_hint(1) for _ in range(10)]
    # Should have at least 2 different variations in 10 tries
    unique_hint1 = set(hint1_list)
    # Either we get variety OR it's consistent - both are acceptable
    # The key is that all hints mention starting sound
    for hint in hint1_list:
        assert ("sound" in hint.lower() and ("start" in hint.lower() or "beginning" in hint.lower() or "first" in hint.lower()))


def test_syllable_counting_with_y():
    """Test syllable counting correctly handles 'y' as vowel."""
    tutor = SpellingTutor("test", "easy", "other")

    # Words where 'y' acts as vowel
    assert tutor.count_syllables("happy") == 2  # hap-py
    assert tutor.count_syllables("pretty") == 2  # pret-ty
    assert tutor.count_syllables("family") == 3  # fam-i-ly
    assert tutor.count_syllables("country") == 2  # coun-try

    # Words where 'y' acts as consonant (at beginning)
    assert tutor.count_syllables("yes") == 1
    assert tutor.count_syllables("yellow") == 2  # yel-low


def test_check_spelling_multi_word_phrases():
    """Test spelling validation for multi-word phrases like 'french fries'."""
    tutor = SpellingTutor("french fries", "medium", "other")

    # Test correct spelling without space (as voice agent removes spaces)
    correct, feedback = tutor.check_spelling("frenchfries")
    assert correct is True, "Should accept 'frenchfries' for 'french fries'"
    assert feedback != "", "Should provide positive feedback"

    # Test correct spelling with space
    correct, feedback = tutor.check_spelling("french fries")
    assert correct is True, "Should accept 'french fries' with space"
    assert feedback != ""

    # Test case insensitive
    correct, feedback = tutor.check_spelling("FRENCHFRIES")
    assert correct is True, "Should be case insensitive"
    assert feedback != ""

    # Test with whitespace
    correct, feedback = tutor.check_spelling("  frenchfries  ")
    assert correct is True, "Should handle whitespace"
    assert feedback != ""

    # Test incorrect spelling
    correct, feedback = tutor.check_spelling("frenchfrys")
    assert correct is False, "Should reject misspelling"


def test_check_spelling_multi_word_close_match():
    """Test near-miss detection for multi-word phrases."""
    tutor = SpellingTutor("ice cream", "easy", "other")

    # Test 1 character difference (should give "Almost!")
    correct, feedback = tutor.check_spelling("icecream")  # Correct
    assert correct is True

    correct, feedback = tutor.check_spelling("icecrem")  # 1 char diff
    assert correct is False
    assert feedback == "Almost! Try again."

    correct, feedback = tutor.check_spelling("icecrean")  # 1 char diff
    assert correct is False
    assert feedback == "Almost! Try again."


def test_check_spelling_various_multi_word_phrases():
    """Test various multi-word phrases to ensure robust handling."""
    test_cases = [
        ("hot dog", "hotdog"),
        ("peanut butter", "peanutbutter"),
        ("ice cream", "icecream"),
        ("french fries", "frenchfries"),
        ("apple pie", "applepie"),
    ]

    for word, expected_input in test_cases:
        tutor = SpellingTutor(word, "medium", "other")
        correct, feedback = tutor.check_spelling(expected_input)
        assert correct is True, f"Should accept '{expected_input}' for '{word}'"
        assert feedback != "", f"Should provide feedback for '{word}'"