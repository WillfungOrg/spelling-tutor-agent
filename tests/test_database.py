import os
import tempfile
import pytest
from spelling_tutor.database import (
    init_database, create_child_profile, get_child_profile,
    create_word_list, get_word_list, list_word_lists,
    create_session, complete_session, get_child_sessions,
    record_word_attempt, get_word_mastery
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    init_database(path)
    yield path
    os.unlink(path)


def test_init_database():
    """Test that database initialization creates all required tables."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    try:
        init_database(path)

        import sqlite3
        conn = sqlite3.connect(path)
        cursor = conn.cursor()

        # Check that all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = ['child_profiles', 'word_lists', 'words', 'sessions', 'word_attempts']
        for table in expected_tables:
            assert table in tables, f"Table {table} not found"

        # Check that indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]

        expected_indexes = [
            'idx_words_word_list_id',
            'idx_sessions_child_id',
            'idx_sessions_word_list_id',
            'idx_word_attempts_session_id',
            'idx_word_attempts_word_id'
        ]
        for index in expected_indexes:
            assert index in indexes, f"Index {index} not found"

        conn.close()
    finally:
        os.unlink(path)


def test_create_child_profile(temp_db, monkeypatch):
    """Test creating a child profile."""
    # Mock get_db_path to return our temp database
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    profile = create_child_profile("Alice", 8)

    assert profile.id is not None
    assert profile.name == "Alice"
    assert profile.age == 8
    assert profile.created_at is not None

    # Verify it was stored in database
    retrieved = get_child_profile(profile.id)
    assert retrieved is not None
    assert retrieved.name == "Alice"
    assert retrieved.age == 8


def test_create_word_list(temp_db, monkeypatch):
    """Test creating a word list with difficulty detection."""
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    words = ["cat", "elephant", "extraordinary"]
    word_list = create_word_list("Test List", words)

    assert word_list.id is not None
    assert word_list.name == "Test List"
    assert word_list.created_at is not None

    # Verify words were stored with correct difficulties
    retrieved_list, retrieved_words = get_word_list(word_list.id)
    assert len(retrieved_words) == 3

    word_map = {w.word: w.difficulty for w in retrieved_words}
    assert word_map["cat"] == "easy"  # 3 letters
    assert word_map["elephant"] == "hard"  # 8 letters
    assert word_map["extraordinary"] == "hard"  # 13 letters


def test_session_workflow(temp_db, monkeypatch):
    """Test the complete session workflow."""
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    # Create child and word list
    child = create_child_profile("Bob", 10)
    word_list = create_word_list("Session Test", ["dog", "house"])
    _, words = get_word_list(word_list.id)

    # Create session
    session = create_session(child.id, word_list.id)
    assert session.id is not None
    assert session.child_id == child.id
    assert session.word_list_id == word_list.id
    assert session.completed_at is None

    # Record word attempts
    record_word_attempt(session.id, words[0].id, 2, True, ["sound it out"])
    record_word_attempt(session.id, words[1].id, 1, False, [])

    # Complete session
    complete_session(session.id)

    # Verify session is marked complete
    sessions = get_child_sessions(child.id)
    assert len(sessions) == 1
    assert sessions[0].completed_at is not None


def test_word_mastery_calculation(temp_db, monkeypatch):
    """Test word mastery calculation."""
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    # Create child and word list
    child = create_child_profile("Charlie", 9)
    word_list = create_word_list("Mastery Test", ["test"])
    _, words = get_word_list(word_list.id)
    word_id = words[0].id

    # Create multiple sessions with attempts
    session1 = create_session(child.id, word_list.id)
    record_word_attempt(session1.id, word_id, 3, True, [])

    session2 = create_session(child.id, word_list.id)
    record_word_attempt(session2.id, word_id, 1, True, [])

    session3 = create_session(child.id, word_list.id)
    record_word_attempt(session3.id, word_id, 2, False, ["hint"])

    # Check mastery calculation
    mastery = get_word_mastery(child.id, word_id)

    assert mastery["total_attempts"] == 6  # 3 + 1 + 2
    assert mastery["correct_count"] == 2  # 2 correct sessions
    assert mastery["mastery_level"] == 2/3  # 2 correct out of 3 sessions

    # Test with no attempts
    new_child = create_child_profile("New", 7)
    empty_mastery = get_word_mastery(new_child.id, word_id)
    assert empty_mastery["total_attempts"] == 0
    assert empty_mastery["correct_count"] == 0
    assert empty_mastery["mastery_level"] == 0.0