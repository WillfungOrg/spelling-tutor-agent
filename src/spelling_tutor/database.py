import sqlite3
import json
from datetime import datetime
from typing import Optional
from .types import ChildProfile, WordList, Word, Session, WordAttempt


def init_database(db_path: str) -> None:
    """
    Initialize the database with all required tables and indexes.

    Args:
        db_path: Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS child_profiles (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_lists (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY,
            word_list_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            FOREIGN KEY (word_list_id) REFERENCES word_lists (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            child_id INTEGER NOT NULL,
            word_list_id INTEGER NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (child_id) REFERENCES child_profiles (id),
            FOREIGN KEY (word_list_id) REFERENCES word_lists (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_attempts (
            id INTEGER PRIMARY KEY,
            session_id INTEGER NOT NULL,
            word_id INTEGER NOT NULL,
            attempts INTEGER NOT NULL,
            correct BOOLEAN NOT NULL,
            hints_used TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions (id),
            FOREIGN KEY (word_id) REFERENCES words (id)
        )
    ''')

    # Create indexes on foreign keys
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_words_word_list_id ON words (word_list_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_child_id ON sessions (child_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_word_list_id ON sessions (word_list_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_word_attempts_session_id ON word_attempts (session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_word_attempts_word_id ON word_attempts (word_id)')

    conn.commit()
    conn.close()


def create_child_profile(name: str, age: int) -> ChildProfile:
    """
    Create a new child profile.

    Args:
        name: Child's name.
        age: Child's age.

    Returns:
        ChildProfile: The created profile.
    """
    from .config import get_db_path

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    created_at = datetime.now().isoformat()
    cursor.execute(
        'INSERT INTO child_profiles (name, age, created_at) VALUES (?, ?, ?)',
        (name, age, created_at)
    )

    profile_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return ChildProfile(id=profile_id, name=name, age=age, created_at=created_at)


def get_child_profile(child_id: int) -> Optional[ChildProfile]:
    """
    Get a child profile by ID.

    Args:
        child_id: The child's ID.

    Returns:
        ChildProfile or None: The profile if found, None otherwise.
    """
    from .config import get_db_path

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, age, created_at FROM child_profiles WHERE id = ?', (child_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return ChildProfile(id=row[0], name=row[1], age=row[2], created_at=row[3])
    return None


def _detect_difficulty(word: str) -> str:
    """
    Auto-detect word difficulty based on length and complexity.

    Args:
        word: The word to analyze.

    Returns:
        str: Difficulty level (easy, medium, hard).
    """
    length = len(word)
    if length <= 4:
        return "easy"
    elif length <= 7:
        return "medium"
    else:
        return "hard"


def create_word_list(name: str, words: list[str]) -> WordList:
    """
    Create a new word list with words.

    Args:
        name: Name of the word list.
        words: List of words to include.

    Returns:
        WordList: The created word list.
    """
    from .config import get_db_path

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    created_at = datetime.now().isoformat()
    cursor.execute(
        'INSERT INTO word_lists (name, created_at) VALUES (?, ?)',
        (name, created_at)
    )

    word_list_id = cursor.lastrowid

    # Insert words with auto-detected difficulty
    for word in words:
        difficulty = _detect_difficulty(word)
        cursor.execute(
            'INSERT INTO words (word_list_id, word, difficulty) VALUES (?, ?, ?)',
            (word_list_id, word, difficulty)
        )

    conn.commit()
    conn.close()

    return WordList(id=word_list_id, name=name, created_at=created_at)


def get_word_list(word_list_id: int) -> tuple[WordList, list[Word]]:
    """
    Get a word list and its words.

    Args:
        word_list_id: The word list ID.

    Returns:
        tuple: WordList and list of Words.
    """
    from .config import get_db_path

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Get word list
    cursor.execute('SELECT id, name, created_at FROM word_lists WHERE id = ?', (word_list_id,))
    list_row = cursor.fetchone()

    if not list_row:
        conn.close()
        raise ValueError(f"Word list {word_list_id} not found")

    word_list = WordList(id=list_row[0], name=list_row[1], created_at=list_row[2])

    # Get words
    cursor.execute(
        'SELECT id, word_list_id, word, difficulty FROM words WHERE word_list_id = ?',
        (word_list_id,)
    )
    word_rows = cursor.fetchall()

    words = [
        Word(id=row[0], word_list_id=row[1], word=row[2], difficulty=row[3])
        for row in word_rows
    ]

    conn.close()
    return word_list, words


def list_word_lists() -> list[WordList]:
    """
    Get all word lists.

    Returns:
        list[WordList]: All word lists.
    """
    from .config import get_db_path

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, created_at FROM word_lists ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()

    return [WordList(id=row[0], name=row[1], created_at=row[2]) for row in rows]


def create_session(child_id: int, word_list_id: int) -> Session:
    """
    Create a new spelling session.

    Args:
        child_id: The child's ID.
        word_list_id: The word list ID.

    Returns:
        Session: The created session.
    """
    from .config import get_db_path

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    started_at = datetime.now().isoformat()
    cursor.execute(
        'INSERT INTO sessions (child_id, word_list_id, started_at) VALUES (?, ?, ?)',
        (child_id, word_list_id, started_at)
    )

    session_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return Session(
        id=session_id,
        child_id=child_id,
        word_list_id=word_list_id,
        started_at=started_at,
        completed_at=None
    )


def complete_session(session_id: int) -> None:
    """
    Mark a session as completed.

    Args:
        session_id: The session ID.
    """
    from .config import get_db_path

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    completed_at = datetime.now().isoformat()
    cursor.execute(
        'UPDATE sessions SET completed_at = ? WHERE id = ?',
        (completed_at, session_id)
    )

    conn.commit()
    conn.close()


def get_child_sessions(child_id: int) -> list[Session]:
    """
    Get all sessions for a child.

    Args:
        child_id: The child's ID.

    Returns:
        list[Session]: All sessions for the child.
    """
    from .config import get_db_path

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute(
        'SELECT id, child_id, word_list_id, started_at, completed_at FROM sessions WHERE child_id = ? ORDER BY started_at DESC',
        (child_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        Session(
            id=row[0],
            child_id=row[1],
            word_list_id=row[2],
            started_at=row[3],
            completed_at=row[4]
        )
        for row in rows
    ]


def record_word_attempt(session_id: int, word_id: int, attempts: int, correct: bool, hints_used: list[str]) -> None:
    """
    Record a word attempt in a session.

    Args:
        session_id: The session ID.
        word_id: The word ID.
        attempts: Number of attempts made.
        correct: Whether the word was spelled correctly.
        hints_used: List of hints that were used.
    """
    from .config import get_db_path

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    hints_json = json.dumps(hints_used)
    cursor.execute(
        'INSERT INTO word_attempts (session_id, word_id, attempts, correct, hints_used) VALUES (?, ?, ?, ?, ?)',
        (session_id, word_id, attempts, correct, hints_json)
    )

    conn.commit()
    conn.close()


def get_word_mastery(child_id: int, word_id: int) -> dict:
    """
    Calculate word mastery for a child.

    Args:
        child_id: The child's ID.
        word_id: The word ID.

    Returns:
        dict: Contains total_attempts, correct_count, and mastery_level.
    """
    from .config import get_db_path

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute('''
        SELECT wa.attempts, wa.correct
        FROM word_attempts wa
        JOIN sessions s ON wa.session_id = s.id
        WHERE s.child_id = ? AND wa.word_id = ?
    ''', (child_id, word_id))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {"total_attempts": 0, "correct_count": 0, "mastery_level": 0.0}

    total_attempts = sum(row[0] for row in rows)
    correct_count = sum(1 for row in rows if row[1])

    # Calculate mastery level as percentage of correct sessions
    mastery_level = correct_count / len(rows) if rows else 0.0

    return {
        "total_attempts": total_attempts,
        "correct_count": correct_count,
        "mastery_level": mastery_level
    }