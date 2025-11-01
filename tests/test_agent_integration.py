"""
Integration test for agent responses.
Tests that child-friendly responses are actually delivered, not paraphrased.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from spelling_tutor.agent import SpellingTutorAgent


@pytest.mark.asyncio
async def test_agent_delivers_child_friendly_responses():
    """Test that agent speaks child-friendly text, not robotic paraphrases."""

    # Mock LiveKit session and capture what's spoken
    spoken_texts = []

    async def mock_say(text):
        spoken_texts.append(text)
        # Mock return value for SpeechHandle
        return Mock()

    # Create agent
    agent = SpellingTutorAgent(child_id=1, word_list_name='week1')

    # Mock the session property using patch
    mock_session = Mock()
    mock_session.say = AsyncMock(side_effect=mock_say)

    with patch.object(type(agent), 'session', new_callable=lambda: property(lambda self: mock_session)):
        # Mock RunContext
        ctx = Mock()

        # Test correct spelling response
        word = agent.current_word.word
        response = await agent.spell_word(ctx, word)

        # Should return empty string (since it spoke directly)
        assert response == "", f"Expected empty string return, got: {response}"

        # Assert child-friendly tone (not overly formal)
        spoken = ' '.join(spoken_texts)

        # Should have enthusiastic or warm language
        child_friendly_indicators = [
            # Exclamations
            'Woohoo', 'Yay', 'Boom', 'Amazing', 'Yes!', 'Sweet',
            # Warm phrases
            'You got', 'on a roll', 'doing great', 'nailed',
            # Enthusiastic punctuation
            '!'
        ]
        assert any(indicator in spoken for indicator in child_friendly_indicators), \
            f"Expected child-friendly tone in: {spoken}"

        # Assert NOT robotic phrases
        robotic_phrases = ['Excellent work', 'spelled perfectly', 'Please spell it for me']
        assert not any(phrase in spoken for phrase in robotic_phrases), \
            f"Found robotic phrase in: {spoken}"


@pytest.mark.asyncio
async def test_response_variety_across_multiple_words():
    """Test that responses vary across multiple correct spellings."""

    spoken_texts = []

    async def mock_say(text):
        spoken_texts.append(text)
        return Mock()

    agent = SpellingTutorAgent(child_id=1, word_list_name='week1')

    mock_session = Mock()
    mock_session.say = AsyncMock(side_effect=mock_say)

    with patch.object(type(agent), 'session', new_callable=lambda: property(lambda self: mock_session)):
        ctx = Mock()

        # Get first 3 words correct
        for i in range(min(3, len(agent.words))):
            word = agent.current_word.word if agent.current_word else None
            if not word:
                break
            await agent.spell_word(ctx, word)

        # Check for variety (should have different responses)
        unique_responses = set(spoken_texts)
        assert len(unique_responses) >= 2, \
            f"Expected variety in responses, got same response {len(unique_responses)} times. Responses: {spoken_texts}"


@pytest.mark.asyncio
async def test_hint_responses_are_child_friendly():
    """Test that hint responses are also child-friendly."""

    spoken_texts = []

    async def mock_say(text):
        spoken_texts.append(text)
        return Mock()

    agent = SpellingTutorAgent(child_id=1, word_list_name='week1')

    mock_session = Mock()
    mock_session.say = AsyncMock(side_effect=mock_say)

    with patch.object(type(agent), 'session', new_callable=lambda: property(lambda self: mock_session)):
        ctx = Mock()

        # Intentionally misspell to trigger hint
        await agent.spell_word(ctx, 'wrong')

        # Should have spoken a hint
        assert len(spoken_texts) > 0, "Expected agent to speak a hint"

        spoken = ' '.join(spoken_texts)

        # Check for child-friendly hint keywords
        hint_keywords = ['help', 'clue', 'hint', 'secret', 'sound', 'listen']
        assert any(keyword in spoken.lower() for keyword in hint_keywords), \
            f"Expected child-friendly hint keywords in: {spoken}"

        # Should not be overly formal
        formal_phrases = ['Let me assist', 'I shall', 'Therefore']
        assert not any(phrase in spoken for phrase in formal_phrases), \
            f"Found formal phrase in hint: {spoken}"


@pytest.mark.asyncio
async def test_session_say_called_not_returned():
    """Test that responses use session.say() instead of return values."""

    spoken_texts = []

    async def mock_say(text):
        spoken_texts.append(text)
        return Mock()

    agent = SpellingTutorAgent(child_id=1, word_list_name='week1')

    mock_session = Mock()
    mock_session.say = AsyncMock(side_effect=mock_say)

    with patch.object(type(agent), 'session', new_callable=lambda: property(lambda self: mock_session)):
        ctx = Mock()

        # Test correct spelling
        word = agent.current_word.word
        response = await agent.spell_word(ctx, word)

        # Key assertions:
        # 1. Function should return empty string
        assert response == "", f"Expected empty return, got: {response}"

        # 2. session.say() should have been called
        assert mock_session.say.called, "Expected session.say() to be called"
        assert mock_session.say.call_count >= 1, \
            f"Expected at least 1 call to session.say(), got {mock_session.say.call_count}"

        # 3. Something should have been spoken
        assert len(spoken_texts) > 0, "Expected text to be spoken via session.say()"
        assert len(spoken_texts[0]) > 0, "Expected non-empty text to be spoken"
