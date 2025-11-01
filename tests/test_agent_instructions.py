"""
Unit tests for agent dynamic instruction generation.
Tests the fix for conversation jumping issue.
"""
import pytest
from spelling_tutor.agent import SpellingTutorAgent
from spelling_tutor.database import init_database, create_child_profile
from spelling_tutor.word_list_loader import Word
import tempfile
import os


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    init_database(path)
    yield path
    os.unlink(path)


@pytest.fixture
def agent_with_words(temp_db, monkeypatch):
    """Create an agent with test words."""
    monkeypatch.setattr('spelling_tutor.config.get_db_path', lambda: temp_db)

    # Create child profile
    child = create_child_profile("Test Child", 8)

    # Create agent with mocked words
    agent = SpellingTutorAgent.__new__(SpellingTutorAgent)
    agent.child_id = child.id
    agent.child_name = "Test Child"

    # Create test words
    agent.words = [
        Word(id=1, word="butterfly", difficulty="hard", word_list_id=0),
        Word(id=2, word="cat", difficulty="easy", word_list_id=0),
        Word(id=3, word="dog", difficulty="easy", word_list_id=0),
    ]

    agent.current_word_index = 0
    agent.current_word = agent.words[0]

    # Initialize tutor with mock
    from spelling_tutor.tutor_logic import SpellingTutor
    agent.current_tutor = SpellingTutor("butterfly", "hard", "other")

    return agent


def test_dynamic_instructions_includes_current_word(agent_with_words):
    """Test that dynamic instructions include the current word being practiced."""
    instructions = agent_with_words._get_dynamic_instructions()

    # Verify current word is mentioned
    assert "BUTTERFLY" in instructions
    assert "Current word to spell: BUTTERFLY" in instructions

    # Verify correct spelling is shown
    assert "B-U-T-T-E-R-F-L-Y" in instructions


def test_dynamic_instructions_includes_attempt_number(agent_with_words):
    """Test that instructions reflect current attempt number."""
    # First attempt
    agent_with_words.current_tutor.current_attempts = 0
    instructions = agent_with_words._get_dynamic_instructions()
    assert "attempt #1 of 3" in instructions

    # Second attempt
    agent_with_words.current_tutor.current_attempts = 1
    instructions = agent_with_words._get_dynamic_instructions()
    assert "attempt #2 of 3" in instructions

    # Third attempt
    agent_with_words.current_tutor.current_attempts = 2
    instructions = agent_with_words._get_dynamic_instructions()
    assert "attempt #3 of 3" in instructions


def test_dynamic_instructions_includes_hints_given(agent_with_words):
    """Test that instructions mention hints that have been provided."""
    # No attempts yet - no hints mentioned
    agent_with_words.current_tutor.current_attempts = 0
    instructions = agent_with_words._get_dynamic_instructions()
    assert "Hints already provided" not in instructions

    # After first attempt - phonics hint mentioned
    agent_with_words.current_tutor.current_attempts = 1
    instructions = agent_with_words._get_dynamic_instructions()
    assert "Hints already provided: phonics hint" in instructions

    # After second attempt - both hints mentioned
    agent_with_words.current_tutor.current_attempts = 2
    instructions = agent_with_words._get_dynamic_instructions()
    assert "Hints already provided: phonics hint, letter-by-letter guidance" in instructions


def test_dynamic_instructions_prevents_jumping(agent_with_words):
    """Test that instructions explicitly prevent jumping to other words."""
    instructions = agent_with_words._get_dynamic_instructions()

    # Should have clear guidance about staying focused
    assert "If the user says something unrelated to the current word" in instructions
    assert "gently redirect them back to spelling the current word" in instructions
    # The instructions prevent jumping by explicitly guiding redirection
    assert "ONLY call spell_word when the user provides their spelling attempt for the current word" in instructions


def test_dynamic_instructions_when_no_word_active(agent_with_words):
    """Test instructions when all words are completed."""
    agent_with_words.current_word = None
    agent_with_words.current_tutor = None

    instructions = agent_with_words._get_dynamic_instructions()

    # Should indicate no word is active
    assert "No word is currently active" in instructions


def test_instructions_update_after_word_change(agent_with_words):
    """Test that instructions change when moving to next word."""
    # Start with butterfly
    initial_instructions = agent_with_words._get_dynamic_instructions()
    assert "BUTTERFLY" in initial_instructions
    assert "CAT" not in initial_instructions

    # Move to next word (cat)
    agent_with_words.current_word_index = 1
    agent_with_words.current_word = agent_with_words.words[1]

    from spelling_tutor.tutor_logic import SpellingTutor
    agent_with_words.current_tutor = SpellingTutor("cat", "easy", "CVC")

    # Get new instructions
    new_instructions = agent_with_words._get_dynamic_instructions()

    # Should now mention cat, not butterfly
    assert "CAT" in new_instructions
    assert "C-A-T" in new_instructions
    assert "BUTTERFLY" not in new_instructions


def test_instructions_context_clarity(agent_with_words):
    """Test that instructions provide clear context for the LLM."""
    instructions = agent_with_words._get_dynamic_instructions()

    # Should have clear sections
    assert "CRITICAL CONTEXT:" in instructions
    assert "INSTRUCTIONS:" in instructions

    # Should tell LLM exactly what to expect
    assert "Wait for the user to spell the current word" in instructions
    assert "ONLY call spell_word when the user provides their spelling attempt for the current word" in instructions
