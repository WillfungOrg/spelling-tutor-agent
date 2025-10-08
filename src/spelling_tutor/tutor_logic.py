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

        Args:
            attempt_number: The current attempt number (1, 2, 3, etc.).

        Returns:
            str: Appropriate hint for the attempt level.
        """
        if attempt_number == 1:
            return "Think about the sounds you hear. What sound does it start with?"

        elif attempt_number == 2:
            syllables = self.count_syllables(self.word)
            return f"Let's break it into parts. It has {syllables} syllable{'s' if syllables != 1 else ''}."

        elif attempt_number == 3:
            return self._get_phoneme_breakdown()

        else:
            # For attempts beyond 3, give the answer
            return f"The word is spelled: {self.word.upper()}"

    def _get_phoneme_breakdown(self) -> str:
        """
        Get a phoneme breakdown based on the phonics category.

        Returns:
            str: Phoneme breakdown hint.
        """
        if self.phonics_category == "CVC":
            return f"The word has these sounds: {self.word[0]} - {self.word[1]} - {self.word[2]} (consonant-vowel-consonant)"

        elif self.phonics_category.startswith("digraph-"):
            digraph = self.phonics_category.split("-")[1]
            return f"The word has these sounds: Listen for the '{digraph}' sound that makes one sound together."

        elif self.phonics_category.startswith("blend-"):
            blend = self.phonics_category.split("-")[1]
            return f"The word has these sounds: It starts with the '{blend}' blend - two consonants that blend together."

        else:
            # For 'other' category, give a general breakdown
            vowels = "aeiou"
            sounds = []
            for char in self.word:
                if char in vowels:
                    sounds.append(f"'{char}' (vowel)")
                else:
                    sounds.append(f"'{char}' (consonant)")
            return f"The word has these sounds: {' - '.join(sounds)}"

    def check_spelling(self, user_input: str) -> Tuple[bool, str]:
        """
        Check if the user's spelling is correct and provide feedback.

        Args:
            user_input: The user's spelling attempt.

        Returns:
            tuple: (is_correct, feedback_message)
        """
        # Normalize input
        normalized_input = user_input.strip().lower()

        # Check for exact match
        if normalized_input == self.word:
            return True, self.get_positive_feedback()

        # Check if it's close (within 1-2 character edits)
        edit_distance = self._levenshtein_distance(normalized_input, self.word)
        if edit_distance <= 2 and len(normalized_input) > 0:
            return False, "Almost! Try again."

        # Otherwise, let caller provide hint
        return False, ""

    def get_positive_feedback(self) -> str:
        """
        Get random positive feedback for correct spelling.

        Returns:
            str: Random positive feedback message.
        """
        feedback_options = [
            "Awesome!",
            "Great job!",
            "You got it!",
            "Fantastic!",
            "Perfect!",
            "Excellent work!",
            "Amazing!"
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