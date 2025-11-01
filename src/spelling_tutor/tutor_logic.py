import random
import re
from typing import Tuple


class SpellingTutor:
    """
    A spelling tutor that provides adaptive hints and feedback for word spelling practice.
    """

    def __init__(self, word: str, difficulty: str, phonics_category: str):
        """
        Initialize the spelling tutor with a word and its characteristics.

        Args:
            word: The word to be spelled.
            difficulty: The difficulty level ('easy', 'medium', 'hard').
            phonics_category: The phonics category (e.g., 'CVC', 'digraph-sh', 'blend-br').
        """
        self.word = word.lower()
        self.difficulty = difficulty
        self.phonics_category = phonics_category
        self.current_attempts = 0

    def get_introduction(self) -> str:
        """
        Get an encouraging introduction for the spelling practice.

        Returns:
            str: Introduction message with the word to spell.
        """
        encouraging_phrases = [
            "Great! You're doing wonderful.",
            "Nice work! Keep it up.",
            "Fantastic! You're learning so well.",
            "Excellent! You're getting better.",
            "Amazing progress!"
        ]

        phrase = random.choice(encouraging_phrases)
        return f"{phrase} Let's spell the word '{self.word}'."

    def get_phonics_hint(self, attempt_number: int) -> str:
        """
        Get a phonics hint based on the attempt number and word characteristics.
        Uses child-friendly, playful language appropriate for ages 6-10.

        Args:
            attempt_number: The current attempt number (1, 2, 3, etc.).

        Returns:
            str: Appropriate hint for the attempt level.
        """
        if attempt_number == 1:
            # Hint 1: Starting sound (4 variations)
            hints = [
                "Let's sound it out! What sound do you hear at the beginning?",
                "Listen carefully - what's the first sound you hear?",
                "Say the word slowly. What sound does it start with?",
                "What letter makes that first sound you hear?"
            ]
            return random.choice(hints)

        elif attempt_number == 2:
            # Hint 2: Syllables (4 variations)
            syllables = self.count_syllables(self.word)
            hints = [
                f"Let's clap it out! This word has {syllables} part{'s' if syllables != 1 else ''}!",
                f"Try saying it slowly - it has {syllables} part{'s' if syllables != 1 else ''} to it!",
                f"Listen: {self.word}. Can you hear the {syllables} part{'s' if syllables != 1 else ''}?",
                f"Clap with me! {self.word} has {syllables} clap{'s' if syllables != 1 else ''}!"
            ]
            return random.choice(hints)

        elif attempt_number == 3:
            return self._get_phoneme_breakdown()

        else:
            # For attempts beyond 3, give the answer
            return f"The word is spelled: {self.word.upper()}"

    def _get_phoneme_breakdown(self) -> str:
        """
        Get a phoneme breakdown based on the phonics category.
        Uses simple, child-friendly language without technical jargon.

        Returns:
            str: Phoneme breakdown hint.
        """
        # Handle multi-word phrases (remove spaces for sound analysis)
        word_for_sounds = self.word.replace(" ", "")

        if self.phonics_category == "CVC" and len(word_for_sounds) == 3:
            # CVC words - simple 3-sound breakdown (NO technical terms)
            hints = [
                f"Let's break it down: '{word_for_sounds[0]}'... '{word_for_sounds[1]}'... '{word_for_sounds[2]}'. Now put them together!",
                f"Say each sound slowly: {word_for_sounds[0]}, then {word_for_sounds[1]}, then {word_for_sounds[2]}!",
                f"It's three sounds: '{word_for_sounds[0]}', '{word_for_sounds[1]}', '{word_for_sounds[2]}'. Can you spell that?"
            ]
            return random.choice(hints)

        elif self.phonics_category.startswith("digraph-"):
            # Digraphs - two letters, one sound
            digraph = self.phonics_category.split("-")[1]
            hints = [
                f"This word has a special '{digraph}' sound - two letters that make one sound!",
                f"Listen for the '{digraph}' - those two letters work together!",
                f"Hear that '{digraph}' sound? That's your clue!"
            ]
            return random.choice(hints)

        elif self.phonics_category.startswith("blend-"):
            # Blends - two letters that blend
            blend = self.phonics_category.split("-")[1]
            hints = [
                f"It starts with '{blend}' - two letters that blend their sounds together!",
                f"Listen for the '{blend}' at the start - two letters, but they blend!",
                f"The '{blend}' sound is at the beginning - two letters mixed together!"
            ]
            return random.choice(hints)

        else:
            # For 'other' category or longer words - simple sound-by-sound
            # Split into individual letters (max 5 for readability)
            if len(word_for_sounds) <= 5:
                sounds = "', '".join(word_for_sounds)
                return f"Let's spell it sound by sound: '{sounds}'. Try putting those letters together!"
            else:
                # For longer words, give first and last sounds
                return f"This word starts with '{word_for_sounds[0]}' and ends with '{word_for_sounds[-1]}'. Think about the sounds in between!"

    def check_spelling(self, user_input: str) -> Tuple[bool, str]:
        """
        Check if the user's spelling is correct and provide feedback.

        Args:
            user_input: The user's spelling attempt.

        Returns:
            tuple: (is_correct, feedback_message)
        """
        # Normalize input - remove spaces to handle multi-word phrases like "french fries"
        normalized_input = user_input.strip().lower().replace(" ", "")
        normalized_word = self.word.replace(" ", "")

        # Check for exact match
        if normalized_input == normalized_word:
            return True, self.get_positive_feedback()

        # Check if it's close (within 1-2 character edits)
        edit_distance = self._levenshtein_distance(normalized_input, normalized_word)
        if edit_distance <= 2 and len(normalized_input) > 0:
            return False, "Almost! Try again."

        # Otherwise, let caller provide hint
        return False, ""

    def get_positive_feedback(self) -> str:
        """
        Get random positive feedback for correct spelling.

        Returns 24 varied, child-friendly options across 3 categories:
        - Short celebrations (high energy)
        - Warm praise (encouraging)
        - Specific praise (builds confidence)

        Returns:
            str: Random positive feedback message.
        """
        feedback_options = [
            # Short celebrations (8)
            "Yay!",
            "Yes!",
            "Woohoo!",
            "You got it!",
            "That's it!",
            "Boom!",
            "Sweet!",
            "Nice!",

            # Warm praise (8)
            "I'm so proud of you!",
            "You're doing amazing!",
            "You're so good at this!",
            "I knew you could do it!",
            "You're a spelling star!",
            "That was awesome!",
            "You're incredible!",
            "I love how you tried!",

            # Specific praise (8)
            "You remembered all the letters!",
            "You sounded that out perfectly!",
            "Great listening!",
            "You got that tricky one!",
            "That was a hard word and you got it!",
            "Nice thinking!",
            "You really focused!",
            "You're getting so good at this!"
        ]
        return random.choice(feedback_options)

    def count_syllables(self, word: str) -> int:
        """
        Count the number of syllables in a word using vowel groups.

        Args:
            word: The word to count syllables for.

        Returns:
            int: Number of syllables.
        """
        word = word.lower()

        # Remove non-alphabetic characters
        word = re.sub(r'[^a-z]', '', word)

        if not word:
            return 0

        # Count vowel groups (including 'y' when it acts as a vowel)
        # 'y' acts as a vowel when it's at the end or between consonants
        word_with_y = re.sub(r'y(?=[bcdfghjklmnpqrstvwxz])|y$', 'i', word)
        vowel_groups = re.findall(r'[aeiou]+', word_with_y)
        syllable_count = len(vowel_groups)

        # Handle silent 'e' at the end - but be conservative
        # Only subtract for clear cases like "make", "cute", "hope"
        if (word.endswith('e') and syllable_count > 1 and len(word) > 3 and
            word[-2] not in 'aeiou' and  # consonant before 'e'
            # Don't subtract for words ending in 'le' (like "apple", "table")
            not word.endswith('le')):
            syllable_count -= 1

        # Ensure at least 1 syllable for any word
        return max(1, syllable_count)

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate the Levenshtein distance between two strings.

        Args:
            s1: First string.
            s2: Second string.

        Returns:
            int: Edit distance between the strings.
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Calculate cost of insertions, deletions, and substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]