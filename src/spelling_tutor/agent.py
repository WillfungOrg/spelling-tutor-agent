"""
LiveKit voice agent for spelling tutor - restructured to match working examples exactly.
Uses function tools instead of overriding turn completion methods.
"""

import asyncio
import random
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

IMPORTANT: The spell_word function speaks directly to the child using session.say().
When spell_word returns an empty string, that means it already spoke the response.
Do not repeat, paraphrase, or add anything after spell_word returns empty string.
Simply wait for the next user input.
"""
        return base

    @function_tool
    async def spell_word(self, context: RunContext, spelling_attempt: str) -> str:
        """Process a spelling attempt from the user.

        Args:
            spelling_attempt: The user's spelling attempt (e.g., 'c a t' or 'cat')
        """
        if not self.current_word or not self.current_tutor:
            # Session already completed
            completions = [
                f"We've finished all the words! Great job practicing today, {self.child_name}!",
                f"All done! You did awesome today, {self.child_name}!",
                f"You already finished! Great work, {self.child_name}!"
            ]
            response = random.choice(completions)
            # Speak directly to bypass LLM reformulation
            await self.session.say(response)
            return ""  # Return empty to prevent LLM from generating additional response

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
            previous_word = self.words[self.current_word_index].word
            await self.move_to_next_word()

            if self.current_word:
                # Varied success responses (12 patterns) - child-friendly and engaging
                responses = [
                    # Group 1: Excited celebrations
                    f"Woohoo! You got '{previous_word}' right, {self.child_name}! Ready for another one? Let's spell '{self.current_word.word}'!",
                    f"Yes! Perfect spelling on '{previous_word}'! Okay, here comes '{self.current_word.word}' - give it a try!",
                    f"Amazing! You nailed '{previous_word}'! Next up: '{self.current_word.word}'. You've got this!",

                    # Group 2: Warm encouragement
                    f"That's right, {self.child_name}! '{previous_word}' was correct! Let's keep going - try '{self.current_word.word}' now!",
                    f"You did it! '{previous_word}' is spelled perfectly! Alright, spell this one for me: '{self.current_word.word}'!",
                    f"Nice work on '{previous_word}'! Ready for the next one? Here it is: '{self.current_word.word}'!",

                    # Group 3: Playful
                    f"Boom! You got '{previous_word}'! Can you spell '{self.current_word.word}' too? I bet you can!",
                    f"Yay! '{previous_word}' is correct! Ooh, here's a new one: '{self.current_word.word}'!",
                    f"Sweet! '{previous_word}' is right! Let's try '{self.current_word.word}' next!",

                    # Group 4: Progress building
                    f"You're on a roll! '{previous_word}' is perfect! Keep going with '{self.current_word.word}'!",
                    f"Another one right! '{previous_word}' is correct! Ready for '{self.current_word.word}'?",
                    f"You're doing great! '{previous_word}' is right! Now try '{self.current_word.word}'!"
                ]
                response = random.choice(responses)
                # Speak directly to bypass LLM reformulation
                await self.session.say(response)
                return ""  # Return empty to prevent LLM from generating additional response
            else:
                # Session completion - warm and celebratory
                completions = [
                    f"Woohoo! You finished all the words! You're an amazing speller, {self.child_name}!",
                    f"You did it! All done! Great job today, {self.child_name}! You should be so proud!",
                    f"Yes! You spelled them all! You're a spelling star, {self.child_name}!"
                ]
                response = random.choice(completions)
                # Speak directly to bypass LLM reformulation
                await self.session.say(response)
                return ""  # Return empty to prevent LLM from generating additional response

        elif self.current_tutor.current_attempts < 3:
            # Give hint with varied, playful delivery (6 patterns)
            hint = self.current_tutor.get_phonics_hint(self.current_tutor.current_attempts)

            if feedback:
                # "Almost!" feedback - add warm hint delivery
                hint_deliveries = [
                    f"{feedback} Ooh, let me help! {hint} Try again!",
                    f"{feedback} Hmm, want a clue? {hint} Give it another go!",
                    f"{feedback} Let me give you a hint: {hint} You've got this!",
                    f"{feedback} Here's a little help: {hint} Try spelling it again!",
                    f"{feedback} I'll give you a secret: {hint} Can you spell it now?",
                    f"{feedback} Listen to this clue: {hint} Try one more time!"
                ]
            else:
                # No "Almost" feedback - encourage and hint
                hint_deliveries = [
                    f"Ooh, let me help! {hint} Try again!",
                    f"Hmm, want a clue? {hint} Give it another go!",
                    f"Let me give you a hint: {hint} You've got this!",
                    f"Here's a little help: {hint} Try spelling '{self.current_word.word}' again!",
                    f"I'll give you a secret: {hint} Can you spell '{self.current_word.word}' now?",
                    f"Listen to this clue: {hint} Try '{self.current_word.word}' one more time!"
                ]

            response = random.choice(hint_deliveries)
            # Speak directly to bypass LLM reformulation
            await self.session.say(response)
            return ""  # Return empty to prevent LLM from generating additional response

        else:
            # Final attempt - warm failure recovery with emotional support
            await self.record_attempt(correct=False)
            previous_word = self.current_word.word
            correct_spelling = previous_word.lower()  # Use lowercase for friendlier feel
            await self.move_to_next_word()

            if self.current_word:
                # Varied failure recovery (6 patterns) - acknowledge effort and build confidence
                recoveries = [
                    f"You tried so hard, {self.child_name}! This one was '{correct_spelling}'. That was tricky! Let's try '{self.current_word.word}'.",
                    f"Great try! The answer is '{correct_spelling}'. You worked really hard on that! Ready for '{self.current_word.word}'?",
                    f"I love how you tried! It's '{correct_spelling}'. Don't worry - try '{self.current_word.word}' now!",
                    f"That's a super hard word! It's spelled '{correct_spelling}'. Now you know! Let's spell '{self.current_word.word}'.",
                    f"Ooh, tricky! The answer is '{correct_spelling}'. That one tricks lots of people! Try '{self.current_word.word}'!",
                    f"Nice try! The answer is '{correct_spelling}'. I think you'll like this next one: '{self.current_word.word}'!"
                ]
                response = random.choice(recoveries)
                # Speak directly to bypass LLM reformulation
                await self.session.say(response)
                return ""  # Return empty to prevent LLM from generating additional response
            else:
                # Session completion after failure - still celebratory
                completions = [
                    f"That one was '{correct_spelling}'. You finished all the words! Great job practicing today, {self.child_name}!",
                    f"The answer is '{correct_spelling}'. You tried so hard on all the words! I'm proud of you, {self.child_name}!",
                    f"It's '{correct_spelling}'. You worked through all the words! Nice job today, {self.child_name}!"
                ]
                response = random.choice(completions)
                # Speak directly to bypass LLM reformulation
                await self.session.say(response)
                return ""  # Return empty to prevent LLM from generating additional response

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