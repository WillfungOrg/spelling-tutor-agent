import os
import tempfile
import sqlite3
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


def test_init_database_creates_all_tables(temp_db):
    """Test that database initialization creates all required tables."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    # Check that all 5 tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    required_tables = ['child_profiles', 'word_lists', 'words', 'sessions', 'word_attempts']
    for table in required_tables:
        assert table in tables, f"Table {table} not found"

    assert len([t for t in tables if t in required_tables]) == 5
    conn.close()


def test_child_profile_crud(temp_db, monkeypatch):
    """Test create and get operations for child profiles."""
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    # Test create
    child1 = create_child_profile("Alice", 8)
    child2 = create_child_profile("Bob", 10)

    # Test get existing
    retrieved1 = get_child_profile(child1.id)
    assert retrieved1.name == "Alice"
    assert retrieved1.age == 8

    retrieved2 = get_child_profile(child2.id)
    assert retrieved2.name == "Bob"
    assert retrieved2.age == 10

    # Test get non-existing
    non_existing = get_child_profile(999)
    assert non_existing is None


def test_word_list_with_difficulty_detection(temp_db, monkeypatch):
    """Test word list creation with all difficulty levels."""
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    # Create word list with mixed difficulties
    words = [
        "cat",          # easy (3 chars)
        "dog",          # easy (3 chars)
        "book",         # easy (4 chars)
        "apple",        # medium (5 chars)
        "friend",       # medium (6 chars)
        "school",       # medium (6 chars)
        "elephant",     # hard (8 chars)
        "basketball",   # hard (10 chars)
    ]

    word_list = create_word_list("Mixed Difficulty", words)
    _, retrieved_words = get_word_list(word_list.id)

    # Group by difficulty
    easy_words = [w for w in retrieved_words if w.difficulty == "easy"]
    medium_words = [w for w in retrieved_words if w.difficulty == "medium"]
    hard_words = [w for w in retrieved_words if w.difficulty == "hard"]

    assert len(easy_words) == 3  # cat, dog, book
    assert len(medium_words) == 3  # apple, friend, school
    assert len(hard_words) == 2  # elephant, basketball


def test_session_complete_workflow(temp_db, monkeypatch):
    """Test complete session workflow with multiple word attempts."""
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    # Setup
    child = create_child_profile("TestChild", 8)
    word_list = create_word_list("Test Words", ["cat", "dog", "elephant"])
    _, words = get_word_list(word_list.id)

    # Create session
    session = create_session(child.id, word_list.id)
    assert session.completed_at is None

    # Record multiple word attempts
    record_word_attempt(session.id, words[0].id, 1, True, [])  # cat - correct first try
    record_word_attempt(session.id, words[1].id, 2, True, ["Think about sounds"])  # dog - correct second try
    record_word_attempt(session.id, words[2].id, 3, False, ["Sounds", "Syllables", "Breakdown"])  # elephant - failed

    # Complete session
    complete_session(session.id)

    # Verify session is completed
    sessions = get_child_sessions(child.id)
    assert len(sessions) == 1
    assert sessions[0].completed_at is not None
    assert sessions[0].id == session.id


def test_word_mastery_calculation_edge_cases(temp_db, monkeypatch):
    """Test word mastery calculation with edge cases."""
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    child = create_child_profile("MasteryTest", 9)
    word_list = create_word_list("Mastery Words", ["test"])
    _, words = get_word_list(word_list.id)
    word_id = words[0].id

    # Test zero attempts
    mastery = get_word_mastery(child.id, word_id)
    assert mastery["total_attempts"] == 0
    assert mastery["correct_count"] == 0
    assert mastery["mastery_level"] == 0.0

    # Test all correct
    session1 = create_session(child.id, word_list.id)
    record_word_attempt(session1.id, word_id, 1, True, [])
    session2 = create_session(child.id, word_list.id)
    record_word_attempt(session2.id, word_id, 1, True, [])

    mastery = get_word_mastery(child.id, word_id)
    assert mastery["total_attempts"] == 2
    assert mastery["correct_count"] == 2
    assert mastery["mastery_level"] == 1.0

    # Test all incorrect
    child2 = create_child_profile("AllWrong", 8)
    session3 = create_session(child2.id, word_list.id)
    record_word_attempt(session3.id, word_id, 3, False, ["hint1", "hint2", "hint3"])

    mastery = get_word_mastery(child2.id, word_id)
    assert mastery["total_attempts"] == 3
    assert mastery["correct_count"] == 0
    assert mastery["mastery_level"] == 0.0

    # Test partial mastery
    child3 = create_child_profile("Partial", 9)
    session4 = create_session(child3.id, word_list.id)
    record_word_attempt(session4.id, word_id, 2, True, ["hint1"])
    session5 = create_session(child3.id, word_list.id)
    record_word_attempt(session5.id, word_id, 3, False, ["hint1", "hint2", "hint3"])
    session6 = create_session(child3.id, word_list.id)
    record_word_attempt(session6.id, word_id, 1, True, [])

    mastery = get_word_mastery(child3.id, word_id)
    assert mastery["total_attempts"] == 6  # 2 + 3 + 1
    assert mastery["correct_count"] == 2  # 2 correct sessions
    assert mastery["mastery_level"] == 2/3  # 2 out of 3 sessions correct