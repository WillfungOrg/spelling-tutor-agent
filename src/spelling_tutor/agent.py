"""
LiveKit voice agent for spelling tutor.
Uses Agents Framework 1.0+ with AgentSession.
"""

import asyncio
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession
from livekit.plugins import openai, deepgram
from .tutor_logic import SpellingTutor
from .database import get_word_list, create_session, record_word_attempt, complete_session
from .word_manager import get_phonics_category
from .config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpellingTutorAgent(Agent):
    """
    Spelling tutor agent that uses SpellingTutor for educational flow.
    """

    def __init__(self, child_id: int, word_list_id: int):
        self.child_id = child_id
        self.word_list_id = word_list_id

        # Load word list and create session
        self.word_list, self.words = get_word_list(word_list_id)
        self.db_session = create_session(child_id, word_list_id)

        # Initialize tutoring state
        self.current_word_index = 0
        self.current_tutor = None

        # Get first word to practice
        self.current_word = self.words[0] if self.words else None

        instructions = (
            "You are a friendly spelling tutor for children ages 6-10. "
            "Help them practice spelling words by: "
            "1. Pronouncing words clearly "
            "2. Providing encouraging feedback "
            "3. Giving phonics-based hints when they struggle "
            "4. Being patient and positive. "
            "Keep responses short and child-appropriate."
        )

        super().__init__(instructions=instructions)

    async def on_enter(self):
        """Called when agent enters the session."""
        logger.info(f"Starting spelling practice for child_id={self.child_id}, word_list_id={self.word_list_id}")
        logger.info(f"First word: {self.current_word}")

        # Greet the child and start first word
        if self.current_word:
            # Create tutor for first word
            phonics_category = get_phonics_category(self.current_word.word)
            self.current_tutor = SpellingTutor(
                self.current_word.word,
                self.current_word.difficulty,
                phonics_category
            )

            greeting = f"Hi! Let's practice spelling. Your first word is: {self.current_word.word}"
            await self.session.generate_reply(instructions=greeting)
        else:
            await self.session.generate_reply(
                instructions="Hi! It looks like we don't have any words to practice right now."
            )

    async def on_user_turn_completed(self, turn_ctx, new_message):
        """
        Called when user finishes speaking.
        Process their spelling attempt.
        """
        if not new_message.content:
            logger.warning("Received empty message from user")
            return

        text = new_message.content
        logger.info(f"User said: {text}")

        if not self.current_word or not self.current_tutor:
            await self.session.generate_reply(
                instructions="We've finished all the words! Great job practicing today."
            )
            return

        # Clean the user's input (remove spaces, lowercase)
        attempt = text.strip().lower().replace(" ", "")
        logger.info(f"User attempt: '{attempt}' for word '{self.current_word.word}'")

        # Increment attempt counter
        self.current_tutor.current_attempts += 1

        # Check the spelling
        correct, feedback = self.current_tutor.check_spelling(attempt)

        # Create result dictionary for logging
        result = {
            "correct": correct,
            "attempts": self.current_tutor.current_attempts,
            "close": len(feedback) > 0 and not correct
        }
        logger.info(f"Result: {result}")

        # Generate appropriate response
        if correct:
            # Correct! Move to next word
            response = f"Excellent! {self.current_word.word} is correct! "
            await self.record_attempt(correct=True)
            await self.move_to_next_word()

            if self.current_word:
                response += f"Your next word is: {self.current_word.word}"
            else:
                response += "You've completed all the words! Amazing work!"

        elif self.current_tutor.current_attempts < 3:
            # Not correct but has more attempts - provide hint
            hint = self.current_tutor.get_phonics_hint(self.current_tutor.current_attempts)
            if feedback:
                response = f"{feedback} {hint} Try again: {self.current_word.word}"
            else:
                response = f"Not quite. {hint} Let's try again: {self.current_word.word}"

        else:
            # Final attempt - show correct answer
            response = f"Not quite. The correct spelling is {self.current_word.word.upper()}. Let's practice it together: {' - '.join(self.current_word.word.upper())}."
            await self.record_attempt(correct=False)
            await self.move_to_next_word()

            if self.current_word:
                response += f" Your next word is: {self.current_word.word}"
            else:
                response += " You've completed all the words! Great job practicing!"

        await self.session.generate_reply(instructions=response)

    async def record_attempt(self, correct: bool):
        """Record the spelling attempt in the database."""
        if not self.current_tutor or not self.current_word:
            return

        hints_used = [self.current_tutor.get_phonics_hint(i) for i in range(1, self.current_tutor.current_attempts)]

        record_word_attempt(
            session_id=self.db_session.id,
            word_id=self.current_word.id,
            attempts=self.current_tutor.current_attempts,
            correct=correct,
            hints_used=hints_used
        )

    async def move_to_next_word(self):
        """Move to the next word in the list."""
        self.current_word_index += 1

        if self.current_word_index < len(self.words):
            # Set up next word
            self.current_word = self.words[self.current_word_index]
            phonics_category = get_phonics_category(self.current_word.word)
            self.current_tutor = SpellingTutor(
                self.current_word.word,
                self.current_word.difficulty,
                phonics_category
            )
        else:
            # All words completed
            self.current_word = None
            self.current_tutor = None
            complete_session(self.db_session.id)

    async def on_exit(self):
        """Called when agent exits the session."""
        logger.info("SpellingTutorAgent exiting session")
        if self.db_session and not self.current_word:
            # Complete session if we finished all words
            complete_session(self.db_session.id)


async def create_spelling_tutor_session(
    ctx: agents.JobContext,
    child_id: int,
    word_list_id: int,
) -> tuple[AgentSession, SpellingTutorAgent]:
    """
    Create an AgentSession configured for spelling tutor.

    REFERENCE: docs/livekit_plugins.md for TTS/STT configuration
    REFERENCE: examples/livekit_basic_voice_agent.py for session pattern
    """

    # Load config to ensure API keys are available
    config = Config()

    # Create TTS (child-friendly voice)
    tts = openai.TTS(
        model="tts-1",
        voice="nova",  # Clear, friendly voice for children
        api_key=config.openai_api_key,
    )

    # Create STT (accurate transcription)
    stt = deepgram.STT(
        model="nova-2",
        language="en-US",
        interim_results=True,
        api_key=config.deepgram_api_key,
    )

    # Create LLM for generating replies
    llm = openai.LLM(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=config.openai_api_key,
    )

    # Create the session
    session = AgentSession(
        stt=stt,
        tts=tts,
        llm=llm,
    )

    # Create the spelling tutor agent
    agent = SpellingTutorAgent(
        child_id=child_id,
        word_list_id=word_list_id,
    )

    return session, agent