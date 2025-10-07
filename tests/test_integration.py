import os
import tempfile
import pytest
from spelling_tutor.database import (
    init_database, create_child_profile, get_child_profile,
    create_word_list, get_word_list, create_session, complete_session,
    record_word_attempt, get_word_mastery, get_child_sessions
)
from spelling_tutor.word_manager import get_phonics_category
from spelling_tutor.tutor_logic import SpellingTutor


@pytest.fixture
def temp_db():
    """Create a temporary database for integration testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    init_database(path)
    yield path
    os.unlink(path)


def test_full_workflow_setup_to_session(temp_db, monkeypatch):
    """Test complete workflow from setup to session completion."""
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    # Step 1: Create child profile
    child = create_child_profile("Integration Test Child", 8)
    assert child.id is not None
    assert child.name == "Integration Test Child"
    assert child.age == 8

    # Step 2: Upload word list
    test_words = ["cat", "ship", "friend", "elephant"]
    word_list = create_word_list("Integration Test Words", test_words)
    assert word_list.id is not None

    # Step 3: Verify word list was created with correct difficulties
    retrieved_list, words = get_word_list(word_list.id)
    assert len(words) == 4
    word_map = {w.word: w for w in words}

    assert word_map["cat"].difficulty == "easy"  # 3 chars
    assert word_map["ship"].difficulty == "easy"  # 4 chars
    assert word_map["friend"].difficulty == "medium"  # 6 chars
    assert word_map["elephant"].difficulty == "hard"  # 8 chars

    # Step 4: Create session
    session = create_session(child.id, word_list.id)
    assert session.id is not None
    assert session.child_id == child.id
    assert session.word_list_id == word_list.id
    assert session.completed_at is None

    # Step 5: Simulate spelling practice for each word
    practice_results = []

    for word in words:
        # Get phonics category
        phonics_category = get_phonics_category(word.word)

        # Create tutor for this word
        tutor = SpellingTutor(word.word, word.difficulty, phonics_category)

        # Simulate different outcomes based on word
        if word.word == "cat":
            # Correct on first try
            attempts = 1
            correct = True
            hints_used = []
        elif word.word == "ship":
            # Correct on second try with hint
            attempts = 2
            correct = True
            hints_used = [tutor.get_phonics_hint(1)]
        elif word.word == "friend":
            # Correct on third try with multiple hints
            attempts = 3
            correct = True
            hints_used = [
                tutor.get_phonics_hint(1),
                tutor.get_phonics_hint(2)
            ]
        else:  # elephant
            # Failed after 3 attempts
            attempts = 3
            correct = False
            hints_used = [
                tutor.get_phonics_hint(1),
                tutor.get_phonics_hint(2),
                tutor.get_phonics_hint(3)
            ]

        # Record the attempt
        record_word_attempt(session.id, word.id, attempts, correct, hints_used)
        practice_results.append({
            'word': word.word,
            'attempts': attempts,
            'correct': correct,
            'hints_count': len(hints_used)
        })

    # Step 6: Complete session
    complete_session(session.id)

    # Step 7: Verify all data stored correctly
    # Check session is marked complete
    sessions = get_child_sessions(child.id)
    assert len(sessions) == 1
    assert sessions[0].completed_at is not None

    # Check word mastery calculations
    for word in words:
        mastery = get_word_mastery(child.id, word.id)

        if word.word == "elephant":
            # Failed word
            assert mastery["total_attempts"] == 3
            assert mastery["correct_count"] == 0
            assert mastery["mastery_level"] == 0.0
        else:
            # Successful words
            assert mastery["correct_count"] == 1
            assert mastery["mastery_level"] == 1.0

    # Verify practice results match expectations
    assert len(practice_results) == 4

    cat_result = next(r for r in practice_results if r['word'] == 'cat')
    assert cat_result['attempts'] == 1
    assert cat_result['correct'] is True
    assert cat_result['hints_count'] == 0

    elephant_result = next(r for r in practice_results if r['word'] == 'elephant')
    assert elephant_result['attempts'] == 3
    assert elephant_result['correct'] is False
    assert elephant_result['hints_count'] == 3


def test_multiple_sessions_same_child(temp_db, monkeypatch):
    """Test that multiple sessions for the same child track separately."""
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    # Setup
    child = create_child_profile("Multi Session Child", 9)
    word_list = create_word_list("Test Words", ["cat", "dog"])
    _, words = get_word_list(word_list.id)
    cat_word = words[0]
    dog_word = words[1]

    # Session 1: Child struggles with both words
    session1 = create_session(child.id, word_list.id)
    record_word_attempt(session1.id, cat_word.id, 3, False, ["hint1", "hint2", "hint3"])
    record_word_attempt(session1.id, dog_word.id, 2, True, ["hint1"])
    complete_session(session1.id)

    # Session 2: Child improves
    session2 = create_session(child.id, word_list.id)
    record_word_attempt(session2.id, cat_word.id, 1, True, [])
    record_word_attempt(session2.id, dog_word.id, 1, True, [])
    complete_session(session2.id)

    # Session 3: Mixed results
    session3 = create_session(child.id, word_list.id)
    record_word_attempt(session3.id, cat_word.id, 2, True, ["hint1"])
    record_word_attempt(session3.id, dog_word.id, 3, False, ["hint1", "hint2", "hint3"])
    complete_session(session3.id)

    # Verify sessions are tracked separately
    sessions = get_child_sessions(child.id)
    assert len(sessions) == 3

    # All sessions should be completed
    for session in sessions:
        assert session.completed_at is not None

    # Check mastery calculations across all sessions
    cat_mastery = get_word_mastery(child.id, cat_word.id)
    assert cat_mastery["total_attempts"] == 6  # 3 + 1 + 2
    assert cat_mastery["correct_count"] == 2  # Session 2 and 3
    assert cat_mastery["mastery_level"] == 2/3  # 2 out of 3 sessions

    dog_mastery = get_word_mastery(child.id, dog_word.id)
    assert dog_mastery["total_attempts"] == 6  # 2 + 1 + 3
    assert dog_mastery["correct_count"] == 2  # Session 1 and 2
    assert dog_mastery["mastery_level"] == 2/3  # 2 out of 3 sessions


def test_word_mastery_progression(temp_db, monkeypatch):
    """Test that mastery improves over multiple attempts."""
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    # Setup
    child = create_child_profile("Mastery Child", 7)
    word_list = create_word_list("Mastery Words", ["house"])
    _, words = get_word_list(word_list.id)
    word = words[0]

    # Track mastery progression over multiple sessions
    mastery_progression = []

    # Session 1: Complete failure
    session1 = create_session(child.id, word_list.id)
    record_word_attempt(session1.id, word.id, 3, False, ["hint1", "hint2", "hint3"])
    complete_session(session1.id)

    mastery = get_word_mastery(child.id, word.id)
    mastery_progression.append(mastery["mastery_level"])
    assert mastery["mastery_level"] == 0.0  # 0/1 correct

    # Session 2: Success with help
    session2 = create_session(child.id, word_list.id)
    record_word_attempt(session2.id, word.id, 2, True, ["hint1"])
    complete_session(session2.id)

    mastery = get_word_mastery(child.id, word.id)
    mastery_progression.append(mastery["mastery_level"])
    assert mastery["mastery_level"] == 0.5  # 1/2 correct

    # Session 3: Success on first try
    session3 = create_session(child.id, word_list.id)
    record_word_attempt(session3.id, word.id, 1, True, [])
    complete_session(session3.id)

    mastery = get_word_mastery(child.id, word.id)
    mastery_progression.append(mastery["mastery_level"])
    assert mastery["mastery_level"] == 2/3  # 2/3 correct

    # Session 4: Another success
    session4 = create_session(child.id, word_list.id)
    record_word_attempt(session4.id, word.id, 1, True, [])
    complete_session(session4.id)

    mastery = get_word_mastery(child.id, word.id)
    mastery_progression.append(mastery["mastery_level"])
    assert mastery["mastery_level"] == 0.75  # 3/4 correct

    # Session 5: Occasional setback
    session5 = create_session(child.id, word_list.id)
    record_word_attempt(session5.id, word.id, 3, False, ["hint1", "hint2", "hint3"])
    complete_session(session5.id)

    mastery = get_word_mastery(child.id, word.id)
    mastery_progression.append(mastery["mastery_level"])
    assert mastery["mastery_level"] == 0.6  # 3/5 correct

    # Verify progression shows general improvement
    assert mastery_progression == [0.0, 0.5, 2/3, 0.75, 0.6]

    # Final mastery should be better than initial
    assert mastery_progression[-1] > mastery_progression[0]

    # Check total attempts accumulate correctly
    final_mastery = get_word_mastery(child.id, word.id)
    assert final_mastery["total_attempts"] == 10  # 3+2+1+1+3
    assert final_mastery["correct_count"] == 3  # Sessions 2, 3, 4


def test_phonics_category_integration(temp_db, monkeypatch):
    """Test integration of phonics categories with tutor logic."""
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    # Setup with words of different phonics categories
    child = create_child_profile("Phonics Child", 8)
    phonics_words = ["cat", "ship", "black", "tree"]  # CVC, digraph-sh, blend-bl, other
    word_list = create_word_list("Phonics Test", phonics_words)
    _, words = get_word_list(word_list.id)

    session = create_session(child.id, word_list.id)

    # Test each word with its phonics category
    for word in words:
        phonics_category = get_phonics_category(word.word)
        tutor = SpellingTutor(word.word, word.difficulty, phonics_category)

        # Verify phonics categories are correctly detected
        if word.word == "cat":
            assert phonics_category == "CVC"
        elif word.word == "ship":
            assert phonics_category == "digraph-sh"
        elif word.word == "black":
            assert phonics_category == "blend-bl"
        elif word.word == "tree":
            assert phonics_category == "blend-tr"

        # Test that phonics-specific hints are generated
        hint3 = tutor.get_phonics_hint(3)

        if phonics_category == "CVC":
            assert "consonant-vowel-consonant" in hint3
        elif phonics_category.startswith("digraph-"):
            assert phonics_category.split("-")[1] in hint3
        elif phonics_category.startswith("blend-"):
            assert phonics_category.split("-")[1] in hint3

        # Record a practice attempt
        record_word_attempt(session.id, word.id, 2, True, [tutor.get_phonics_hint(1)])

    complete_session(session.id)

    # Verify all attempts were recorded
    sessions = get_child_sessions(child.id)
    assert len(sessions) == 1
    assert sessions[0].completed_at is not None


def test_error_handling_integration(temp_db, monkeypatch):
    """Test error handling in integrated workflows."""
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    # Test retrieving non-existent child
    assert get_child_profile(999) is None

    # Test retrieving non-existent word list
    with pytest.raises(ValueError):
        get_word_list(999)

    # Test creating session with non-existent child/word list
    child = create_child_profile("Error Test", 6)
    word_list = create_word_list("Error Words", ["test"])

    # This should work
    valid_session = create_session(child.id, word_list.id)
    assert valid_session.id is not None

    # Test word mastery with no attempts
    _, words = get_word_list(word_list.id)
    mastery = get_word_mastery(child.id, words[0].id)
    assert mastery["total_attempts"] == 0
    assert mastery["correct_count"] == 0
    assert mastery["mastery_level"] == 0.0