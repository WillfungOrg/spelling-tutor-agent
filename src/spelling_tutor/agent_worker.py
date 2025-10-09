"""
LiveKit Agents worker for spelling tutor.

This script starts the agent worker that listens for room connections.
Run with: python -m spelling_tutor.agent_worker

Requires environment variables:
- LIVEKIT_URL
- LIVEKIT_API_KEY
- LIVEKIT_API_SECRET
- OPENAI_API_KEY
- DEEPGRAM_API_KEY
"""

import asyncio
import logging
from livekit import agents
from livekit.agents import JobProcess
from livekit.plugins import openai, deepgram, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from .config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def prewarm(proc: JobProcess):
    """Prewarm function to load VAD model for faster startup."""
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("🚀 Voice Activity Detection model preloaded")


async def entrypoint(ctx: agents.JobContext):
    """
    Main entrypoint for the spelling tutor voice agent.

    This function is called when a user joins a room.

    REFERENCE: docs/livekit_agents_framework.md for entrypoint pattern
    REFERENCE: examples/livekit_basic_voice_agent.py for basic setup
    """

    logger.info(f"Agent joining room: {ctx.room.name}")

    # Connect to the room
    await ctx.connect()

    # Get child_id and word_list_id from multiple sources
    child_id = 1  # Default: Emma
    word_list_id = 1  # Default: Test Words

    # Try to get metadata from room first
    room_metadata = getattr(ctx.room, 'metadata', '') or ''
    logger.info(f"Room metadata: '{room_metadata}'")

    # Also check for participants and their metadata
    participants = list(ctx.room.remote_participants.values())
    logger.info(f"Found {len(participants)} participants in room")

    # Look for metadata in participants
    for participant in participants:
        participant_metadata = getattr(participant, 'metadata', '') or ''
        logger.info(f"Participant {participant.identity} metadata: '{participant_metadata}'")
        if participant_metadata and 'child_id=' in participant_metadata:
            room_metadata = participant_metadata
            break

    # Parse metadata if found
    if room_metadata:
        try:
            logger.info(f"Parsing metadata: '{room_metadata}'")
            # Try parsing as simple key=value pairs
            for pair in room_metadata.split(','):
                if '=' in pair:
                    key, value = pair.strip().split('=', 1)
                    if key == 'child_id':
                        child_id = int(value)
                        logger.info(f"Found child_id: {child_id}")
                    elif key == 'word_list_id':
                        word_list_id = int(value)
                        logger.info(f"Found word_list_id: {word_list_id}")
            logger.info(f"✅ Using metadata: child_id={child_id}, word_list_id={word_list_id}")
        except Exception as e:
            logger.warning(f"Failed to parse metadata '{room_metadata}': {e}. Using defaults.")
    else:
        logger.info(f"No metadata found, using defaults: child_id={child_id}, word_list_id={word_list_id}")

    # Verify the child and word list exist
    try:
        from .database import get_child_profile, get_word_list
        child = get_child_profile(child_id)
        word_list, words = get_word_list(word_list_id)
        logger.info(f"✅ Found child: {child.name} (age {child.age})")
        logger.info(f"✅ Found word list: {word_list.name} with {len(words)} words")
    except Exception as e:
        logger.error(f"❌ Database lookup failed: {e}")

    logger.info(f"🎯 Final agent configuration: child_id={child_id}, word_list_id={word_list_id}")

    # Create the spelling tutor session (following RAG example pattern)
    from .agent import SpellingTutorAgent

    # Load config to ensure API keys are available
    config = Config()

    # Create session with simplified, working configuration (based on examples/livekit-agent/)
    session = agents.AgentSession(
        # Speech-to-Text - Deepgram Nova-2 (clean, simple config)
        stt=deepgram.STT(
            model="nova-2",
            language="en",
            api_key=config.deepgram_api_key,
        ),

        # LLM - GPT-4o-mini for responses
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7,  # Standard temperature for natural responses
            api_key=config.openai_api_key,
        ),

        # Text-to-Speech - Child-friendly voice with better error handling
        tts=openai.TTS(
            model="tts-1",
            voice="alloy",  # More reliable voice (fallback from nova)
            speed=0.9,      # Slightly slower for clarity
            api_key=config.openai_api_key,
        ),

        # Voice Activity Detection (prewarmed)
        vad=ctx.proc.userdata.get("vad") or silero.VAD.load(),

        # Turn detection for natural interruptions
        turn_detection=MultilingualModel(),
    )

    # Create the spelling tutor agent
    agent = SpellingTutorAgent(
        child_id=child_id,
        word_list_id=word_list_id,
    )

    # Add event listeners for proper interruption handling (like working examples)
    @session.on("agent_state_changed")
    def on_agent_state_changed(ev):
        logger.info(f"Agent state: {ev.old_state} → {ev.new_state}")

    @session.on("user_started_speaking")
    def on_user_started_speaking():
        logger.debug("User started speaking - enabling interruptions")

    @session.on("user_stopped_speaking")
    def on_user_stopped_speaking():
        logger.debug("User stopped speaking")

    # Start the session
    await session.start(
        room=ctx.room,
        agent=agent,
    )

    logger.info(f"Spelling tutor agent started in room: {ctx.room.name}")


def main():
    """
    Start the agent worker.

    REFERENCE: docs/livekit_agents_framework.md for worker setup
    """

    # Validate environment variables
    config = Config()

    required_vars = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY",
        "DEEPGRAM_API_KEY",
    ]

    missing = []
    for var in required_vars:
        if not getattr(config, var.lower(), None):
            missing.append(var)

    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please check your .env file")
        return

    logger.info("Starting LiveKit Agents worker for spelling tutor...")
    logger.info(f"LiveKit URL: {config.livekit_url}")

    # Run the agent worker with prewarm function
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,  # Add prewarm for faster startup
        )
    )


if __name__ == "__main__":
    main()