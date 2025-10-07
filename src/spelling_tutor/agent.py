import asyncio
import logging
from typing import List, Optional
from datetime import datetime

# LiveKit imports
import livekit
from livekit import agents, rtc
from livekit.agents import llm, tts, stt, tokenize
from livekit.plugins import openai, deepgram

# Local imports
from .database import get_word_list, create_session, record_word_attempt, complete_session
from .tutor_logic import SpellingTutor
from .word_manager import get_phonics_category
from .types import Session, Word, WordList


logger = logging.getLogger(__name__)


class SpellingTutorAgent:
    """
    A LiveKit agent that conducts spelling tutoring sessions with voice interaction.

    This agent connects to a LiveKit room, loads a word list, and guides a child
    through spelling practice using text-to-speech and speech-to-text capabilities.
    """

    def __init__(self, config: dict, child_id: int, word_list_id: int):
        """
        Initialize the spelling tutor agent.

        Args:
            config: Configuration dictionary with LiveKit and API credentials.
            child_id: ID of the child participating in the session.
            word_list_id: ID of the word list to use for practice.
        """
        self.config = config
        self.child_id = child_id
        self.word_list_id = word_list_id

        # Session state
        self.session: Optional[Session] = None
        self.room_name = f"spelling_session_{child_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.words: List[Word] = []
        self.current_word_index = 0

        # LiveKit components
        self.room: Optional[rtc.Room] = None
        self.ctx: Optional[agents.JobContext] = None
        self.tts_instance: Optional[tts.TTS] = None
        self.stt_instance: Optional[stt.STT] = None

    async def start(self) -> None:
        """
        Start the spelling tutor session.

        This method:
        1. Initializes LiveKit room connection
        2. Loads the word list from database
        3. Creates a new session record
        4. Runs the spelling session
        """
        try:
            # Initialize LiveKit connection
            await self._initialize_livekit()

            # Load word list from database
            word_list, self.words = get_word_list(self.word_list_id)
            logger.info(f"Loaded word list '{word_list.name}' with {len(self.words)} words")

            # Create session in database
            self.session = create_session(self.child_id, self.word_list_id)
            logger.info(f"Created session {self.session.id}")

            # Run the spelling session
            await self.run_session()

        except Exception as e:
            logger.error(f"Error in spelling session: {e}")
            if self.session:
                # Mark session as completed even if there was an error
                complete_session(self.session.id)
            raise
        finally:
            # Clean up LiveKit connection
            if self.room:
                await self.room.disconnect()

    async def _initialize_livekit(self) -> None:
        """
        Initialize LiveKit room connection and audio components.
        """
        # Create LiveKit room instance
        self.room = rtc.Room()

        # Initialize TTS (Text-to-Speech) using OpenAI
        self.tts_instance = openai.TTS(
            model="tts-1",
            voice="nova",  # Child-friendly voice
            api_key=self.config["OPENAI_API_KEY"]
        )

        # Initialize STT (Speech-to-Text) using Deepgram
        self.stt_instance = deepgram.STT(
            model="nova-2",
            api_key=self.config["DEEPGRAM_API_KEY"]
        )

        # Connect to LiveKit room
        await self.room.connect(
            url=self.config["LIVEKIT_URL"],
            token=self._generate_room_token(),
            options=rtc.RoomOptions(
                auto_subscribe=True,
                dynacast=True,
            )
        )

        logger.info(f"Connected to LiveKit room: {self.room_name}")

    def _generate_room_token(self) -> str:
        """
        Generate a JWT token for LiveKit room access.

        Returns:
            str: JWT token for room authentication.
        """
        from livekit import api

        # Create access token for the room
        token = api.AccessToken(
            api_key=self.config["LIVEKIT_API_KEY"],
            api_secret=self.config["LIVEKIT_API_SECRET"]
        )

        # Grant permissions for the spelling tutor session
        token.with_identity(f"spelling_tutor_{self.child_id}")
        token.with_name("Spelling Tutor")
        token.with_grants(
            api.VideoGrants(
                room_join=True,
                room=self.room_name,
                can_publish=True,
                can_subscribe=True,
            )
        )

        return token.to_jwt()

    async def run_session(self) -> None:
        """
        Run the main spelling session loop.

        This method iterates through each word in the word list and conducts
        spelling practice using the SpellingTutor logic.
        """
        if not self.words:
            await self.speak("I'm sorry, but there are no words to practice today.")
            return

        # Welcome message
        await self.speak(f"Welcome to your spelling practice! Today we'll practice {len(self.words)} words. Let's begin!")

        # Practice each word
        for i, word in enumerate(self.words):
            self.current_word_index = i

            # Get phonics category for the word
            phonics_category = get_phonics_category(word.word)

            # Create tutor instance for this word
            tutor = SpellingTutor(word.word, word.difficulty, phonics_category)

            # Introduce the word
            introduction = tutor.get_introduction()
            await self.speak(introduction)

            # Practice the word
            attempts = 0
            max_attempts = 3
            correct = False
            hints_used = []

            while attempts < max_attempts and not correct:
                # Listen for user input
                user_input = await self.listen()
                attempts += 1

                # Check spelling
                correct, feedback = tutor.check_spelling(user_input)

                if not correct and attempts < max_attempts:
                    # Get hint for next attempt
                    hint = tutor.get_phonics_hint(attempts)
                    hints_used.append(hint)

                    # Provide feedback with hint
                    full_feedback = f"{feedback} {hint}" if feedback else hint
                    await self.speak(full_feedback)
                else:
                    # Final attempt or correct answer
                    await self.speak(feedback)

            # Record the attempt in database
            record_word_attempt(
                session_id=self.session.id,
                word_id=word.id,
                attempts=attempts,
                correct=correct,
                hints_used=hints_used
            )

            # If not correct, show the answer
            if not correct:
                await self.speak(f"The correct spelling is {word.word.upper()}. Let's practice it together: {' - '.join(word.word.upper())}.")

            # Brief pause between words
            if i < len(self.words) - 1:
                await asyncio.sleep(1)
                await self.speak("Great! Let's move on to the next word.")

        # Complete the session
        complete_session(self.session.id)

        # Closing message
        await self.speak("Wonderful job today! You've completed all the words. Keep practicing and you'll become an amazing speller!")

    async def speak(self, text: str) -> None:
        """
        Convert text to speech and publish to the LiveKit room.

        Args:
            text: The text to speak.
        """
        try:
            logger.info(f"Speaking: {text}")

            # Generate audio using TTS
            audio_stream = self.tts_instance.synthesize(text)

            # Create audio track
            audio_track = rtc.LocalAudioTrack.create_audio_track(
                "spelling_tutor_voice",
                audio_stream
            )

            # Publish audio to room
            await self.room.local_participant.publish_track(
                audio_track,
                rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
            )

            # Wait for audio to finish playing
            # This is a simplified approach - in a real implementation,
            # you'd want to track the audio duration more precisely
            estimated_duration = len(text) * 0.1  # Rough estimate: 10 chars per second
            await asyncio.sleep(max(1.0, estimated_duration))

        except Exception as e:
            logger.error(f"Error in speak: {e}")
            # Fall back to logging if TTS fails
            print(f"TTS Error - Would say: {text}")

    async def listen(self) -> str:
        """
        Capture audio from the room and transcribe it to text.

        Returns:
            str: The transcribed text from user's speech.
        """
        try:
            logger.info("Listening for user input...")

            # Wait for audio from participants
            # This is a simplified implementation - in practice, you'd need
            # more sophisticated audio capture and silence detection

            # Create a future to wait for audio input
            audio_future = asyncio.Future()

            # Set up audio capture callback
            def on_audio_received(audio_frame):
                if not audio_future.done():
                    audio_future.set_result(audio_frame)

            # Register for audio events (simplified)
            # In a real implementation, you'd set up proper event listeners
            # for participant audio tracks

            # Simulate waiting for audio input with timeout
            try:
                # Wait up to 10 seconds for user input
                await asyncio.wait_for(self._wait_for_user_audio(), timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning("No audio input received within timeout")
                return ""

            # Transcribe the audio using STT
            # This is a placeholder - actual implementation would capture
            # real audio data from the room
            transcribed_text = await self._transcribe_audio()

            logger.info(f"User said: {transcribed_text}")
            return transcribed_text.strip()

        except Exception as e:
            logger.error(f"Error in listen: {e}")
            # Return empty string if listening fails
            return ""

    async def _wait_for_user_audio(self) -> None:
        """
        Wait for user audio input.

        This is a placeholder method that simulates waiting for audio.
        In a real implementation, this would listen for actual audio frames.
        """
        # Simulate waiting for user input
        # In practice, this would involve setting up proper LiveKit
        # audio event handlers and waiting for speech activity
        await asyncio.sleep(2.0)

    async def _transcribe_audio(self) -> str:
        """
        Transcribe captured audio to text.

        Returns:
            str: Transcribed text.
        """
        # This is a placeholder implementation
        # In practice, you would:
        # 1. Capture actual audio frames from the LiveKit room
        # 2. Process the audio data
        # 3. Send to Deepgram STT for transcription
        # 4. Return the transcribed text

        # For now, return a placeholder
        # In a real implementation, this would use the STT instance:
        # transcription = await self.stt_instance.recognize(audio_data)
        # return transcription.text

        return "placeholder_user_input"