"""
LiveKit voice agent for spelling tutor - restructured to match working examples exactly.
Uses function tools instead of overriding turn completion methods.
"""

import asyncio
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession, RunContext
from livekit.agents.llm import function_tool
from livekit.plugins import openai, deepgram
from .tutor_logic import SpellingTutor
from .database import get_word_list, create_session, record_word_attempt, complete_session, get_child_profile
from .word_manager import get_phonics_category
from .config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpellingTutorAgent(Agent):
    """Spelling tutor agent - structured exactly like working examples."""

    def __init__(self, child_id: int, word_list_id: int):
        # Store configuration
        self.child_id = child_id
        self.word_list_id = word_list_id

        # Load data
        self.word_list, self.words = get_word_list(word_list_id)
        self.db_session = create_session(child_id, word_list_id)
        child = get_child_profile(child_id)

        # Initialize state
        self.current_word_index = 0
        self.current_word = self.words[0] if self.words else None
        self.current_tutor = None
        self.child_name = child.name if child else "friend"

        # Set up first word
        if self.current_word:
            phonics_category = get_phonics_category(self.current_word.word)
            self.current_tutor = SpellingTutor(
                self.current_word.word,
                self.current_word.difficulty,
                phonics_category
            )

        # Simple instructions like working examples
        super().__init__(
            instructions=f"""You are {self.child_name}'s spelling tutor.
            When the user says letters or words, use the spell_word function to process their spelling attempt.
            Be encouraging and patient."""
        )

    @function_tool
    async def spell_word(self, context: RunContext, spelling_attempt: str) -> str:
        """Process a spelling attempt from the user.

        Args:
            spelling_attempt: The user's spelling attempt (e.g., 'c a t' or 'cat')
        """
        if not self.current_word or not self.current_tutor:
            return "We've finished all the words! Great job practicing today!"

        # Clean the attempt
        attempt = spelling_attempt.strip().lower().replace(" ", "").replace(".", "").replace(",", "")
        logger.info(f"Processing spelling attempt: '{spelling_attempt}' -> '{attempt}' for word '{self.current_word.word}'")

        # Check if it's noise
        if self._is_noise_input(attempt):
            return "I'm listening for your spelling attempt."

        # Increment attempts
        self.current_tutor.current_attempts += 1

        # Check spelling
        correct, feedback = self.current_tutor.check_spelling(attempt)

        if correct:
            # Correct! Move to next word
            await self.record_attempt(correct=True)
            await self.move_to_next_word()

            if self.current_word:
                return f"Excellent work, {self.child_name}! You spelled {self.words[self.current_word_index-1].word} perfectly! Ready for the next word? Your word is: {self.current_word.word}."
            else:
                return f"Excellent work, {self.child_name}! You spelled {self.words[self.current_word_index-1].word} perfectly! You finished all the words! Amazing job today!"

        elif self.current_tutor.current_attempts < 3:
            # Give hint
            hint = self.current_tutor.get_phonics_hint(self.current_tutor.current_attempts)
            if feedback:
                return f"{feedback} Here's a hint: {hint}. Take your time and try again!"
            else:
                return f"Not quite! Let me help. {hint}. You've got this! Try spelling '{self.current_word.word}' again."

        else:
            # Final attempt
            await self.record_attempt(correct=False)
            correct_spelling = self.current_word.word.upper()
            await self.move_to_next_word()

            if self.current_word:
                return f"Not quite. The correct spelling is {correct_spelling}. Your next word is: {self.current_word.word}."
            else:
                return f"Not quite. The correct spelling is {correct_spelling}. You've completed all the words! Great job practicing!"

    def _is_noise_input(self, attempt: str) -> bool:
        """Check if input is noise."""
        if len(attempt) < 2:
            return True
        noise_words = {"um", "uh", "hmm", "ah", "oh", "er", "uhm"}
        return attempt in noise_words

    async def record_attempt(self, correct: bool):
        """Record attempt in database."""
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
        """Move to next word."""
        self.current_word_index += 1

        if self.current_word_index < len(self.words):
            self.current_word = self.words[self.current_word_index]
            phonics_category = get_phonics_category(self.current_word.word)
            self.current_tutor = SpellingTutor(
                self.current_word.word,
                self.current_word.difficulty,
                phonics_category
            )
            logger.info(f"Started new word: {self.current_word.word}")
        else:
            self.current_word = None
            self.current_tutor = None
            complete_session(self.db_session.id)

    async def on_enter(self):
        """Called when agent becomes active - like working examples."""
        logger.info("Spelling tutor agent session started")

        if self.current_word:
            greeting = f"Hi {self.child_name}! Let's practice spelling. Your word is: {self.current_word.word}. Please spell {self.current_word.word} for me."
        else:
            greeting = f"Hi {self.child_name}! It looks like we don't have any words to practice right now."

        await self.session.generate_reply(instructions=greeting)

    async def on_exit(self):
        """Called when agent session ends - like working examples."""
        logger.info("Spelling tutor agent session ended")
        if self.db_session and not self.current_word:
            complete_session(self.db_session.id)