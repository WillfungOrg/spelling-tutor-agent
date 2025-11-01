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
from .database import create_session, record_word_attempt, complete_session, get_child_profile
from .word_manager import get_phonics_category
from .word_list_loader import load_word_list_from_file, get_default_word_list
from .config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpellingTutorAgent(Agent):
    """Spelling tutor agent - structured exactly like working examples."""

    def __init__(self, child_id: int, word_list_name: str = None):
        # Store configuration
        self.child_id = child_id

        # Load word list from file
        if word_list_name is None:
            word_list_name = get_default_word_list()

        self.word_list_name, self.words = load_word_list_from_file(word_list_name)
        logger.info(f"Loaded word list '{self.word_list_name}' with {len(self.words)} words")

        # Create database session (using word_list_name as identifier)
        # Note: We'll use a placeholder word_list_id=0 for file-based lists
        self.db_session = create_session(child_id, word_list_id=0)
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
            instructions=self._get_dynamic_instructions()
        )

    def _get_dynamic_instructions(self) -> str:
        """Generate instructions with current word context."""
        base = f"""You are {self.child_name}'s spelling tutor.

CRITICAL CONTEXT:
"""

        if self.current_word and self.current_tutor:
            attempt_num = self.current_tutor.current_attempts + 1
            base += f"""- Current word to spell: {self.current_word.word.upper()}
- This is attempt #{attempt_num} of 3
- Correct spelling: {'-'.join(self.current_word.word.upper())}
"""

            # Add hint context if hints have been given
            if self.current_tutor.current_attempts > 0:
                hints_given = []
                if self.current_tutor.current_attempts >= 1:
                    hints_given.append("phonics hint")
                if self.current_tutor.current_attempts >= 2:
                    hints_given.append("letter-by-letter guidance")
                base += f"- Hints already provided: {', '.join(hints_given)}\n"
        else:
            base += "- No word is currently active\n"

        base += """
INSTRUCTIONS:
- Wait for the user to spell the current word
- ONLY call spell_word when the user provides their spelling attempt for the current word
- DO NOT call spell_word based on your own responses or when presenting a new word
- If the user says something unrelated to the current word, gently redirect them back to spelling the current word
- Be encouraging, patient, and keep focus on the current word
- After correct spelling, present the next word clearly
"""
        return base

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

        # Update instructions to reflect new attempt count
        self.instructions = self._get_dynamic_instructions()

        # Check spelling
        correct, feedback = self.current_tutor.check_spelling(attempt)

        if correct:
            # Correct! Move to next word
            await self.record_attempt(correct=True)
            previous_word = self.words[self.current_word_index].word
            await self.move_to_next_word()

            if self.current_word:
                return f"Excellent work, {self.child_name}! You spelled '{previous_word}' perfectly! Now let's try the next word: '{self.current_word.word}'. Please spell it for me."
            else:
                return f"Excellent work, {self.child_name}! You spelled '{previous_word}' perfectly! You finished all the words! Amazing job today!"

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
            previous_word = self.current_word.word
            correct_spelling = previous_word.upper()
            await self.move_to_next_word()

            if self.current_word:
                return f"That's okay, {self.child_name}. The correct spelling is '{correct_spelling}'. Let's move on to the next word: '{self.current_word.word}'. Please spell it for me."
            else:
                return f"That's okay, {self.child_name}. The correct spelling is '{correct_spelling}'. You've completed all the words! Great job practicing!"

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

            # Update instructions with new word context
            self.instructions = self._get_dynamic_instructions()
        else:
            self.current_word = None
            self.current_tutor = None
            complete_session(self.db_session.id)

            # Update instructions to reflect no active word
            self.instructions = self._get_dynamic_instructions()

    async def on_enter(self):
        """Called when agent becomes active - like working examples."""
        logger.info("Spelling tutor agent session started")

        # Update instructions with current word context
        self.instructions = self._get_dynamic_instructions()

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