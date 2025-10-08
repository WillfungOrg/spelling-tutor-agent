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
from .agent import create_spelling_tutor_session
from .config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


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

    # TODO: In production, get child_id and word_list_id from room metadata
    # For now, use defaults (you can customize this logic)
    child_id = 1  # Default child
    word_list_id = 1  # Default word list

    # Create the spelling tutor session
    session, agent = await create_spelling_tutor_session(
        ctx=ctx,
        child_id=child_id,
        word_list_id=word_list_id,
    )

    # Start the session
    await session.start(
        agent=agent,
        room=ctx.room,
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

    # Run the agent worker
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )


if __name__ == "__main__":
    main()