Excellent! Now I'll generate your complete spec prompt to redo the LiveKit integration.

📋 SPEC PROMPT: Redo LiveKit Voice Agent Integration
High-Level Objective
Rebuild the LiveKit voice agent integration for the spelling tutor application using the Agents Framework 1.0+ properly. The agent should handle voice interactions with children (ages 6-10) for spelling practice, using OpenAI TTS for speech output and Deepgram STT for speech recognition, while maintaining all existing spelling tutor logic and database functionality.

Mid-Level Objectives

Remove broken LiveKit code - Delete incorrect v0.8.0 patterns and conflicting implementations
Implement proper Agents 1.0 pattern - Use AgentSession with correct entrypoint function
Integrate TTS/STT plugins - Configure OpenAI TTS (child-friendly voice) and Deepgram STT
Connect spelling tutor logic - Bridge voice agent with existing SpellingTutorLogic class
Fix CLI conflicts - Separate agent worker from CLI commands
Create agent launcher - Add dedicated script to start the voice agent worker
Update dependencies - Upgrade to Agents 1.2.14+ and compatible plugin versions


Implementation Notes
Framework & Versions

Use LiveKit Agents 1.2.14+ (not 0.8.0)
Use livekit-plugins-openai 1.2.6+ for TTS/STT
Use livekit-plugins-deepgram 1.2.14+ for STT
Follow AgentSession pattern (NOT VoicePipelineAgent or VoiceAssistant)
Reference curated documentation in docs/ directory

Voice Configuration

OpenAI TTS: Use voice="nova" (clear, child-friendly)
Deepgram STT: Use model="nova-2" (latest, most accurate)
Handle interruptions gracefully (children may speak over the agent)

Architecture

Separate concerns: Agent worker vs CLI commands
Single entrypoint: async def entrypoint(ctx: agents.JobContext)
No CLI conflicts: Agent worker runs independently via agents.cli.run_app()
Database integration: Agent can query/update database during sessions

Audio Quality

Sample rate: 24000 Hz (standard for voice)
Channels: 1 (mono audio)
Buffer appropriately for smooth playback

Error Handling

Handle missing API keys gracefully
Log agent state changes
Handle room disconnections
Validate environment variables on startup

Testing

Agent should greet child on join
Agent should respond to child's speech
Spelling tutor logic should work through voice
Database operations should succeed


Context
Beginning Context
Files that currently exist:

src/spelling_tutor/main.py (CLI with broken LiveKit code)
src/spelling_tutor/agent.py (mixed old/new patterns)
src/spelling_tutor/tutor_logic.py (spelling tutor logic - KEEP THIS)
src/spelling_tutor/database.py (database operations - KEEP THIS)
src/spelling_tutor/types.py (data types - KEEP THIS)
src/spelling_tutor/word_manager.py (word list management - KEEP THIS)
src/spelling_tutor/config.py (environment config - KEEP THIS)
pyproject.toml (read-only)
.env (read-only)

Files that don't exist yet:

src/spelling_tutor/agent_worker.py (new - will create)

Reference Files (Documentation)

docs/livekit_agents_framework.md (read-only)
docs/livekit_voice_assistant.md (read-only)
docs/livekit_plugins.md (read-only)
examples/livekit_basic_voice_agent.py (read-only)

Ending Context
Files after completion:

src/spelling_tutor/main.py (updated - remove LiveKit code)
src/spelling_tutor/agent.py (rewritten - proper AgentSession pattern)
src/spelling_tutor/agent_worker.py (new - dedicated agent launcher)
src/spelling_tutor/tutor_logic.py (unchanged)
src/spelling_tutor/database.py (unchanged)
src/spelling_tutor/types.py (unchanged)
src/spelling_tutor/word_manager.py (unchanged)
src/spelling_tutor/config.py (unchanged)
pyproject.toml (read-only)
.env (read-only)


Low-Level Tasks
Task 1: Update dependencies in pyproject.toml
Context: The current versions (0.8.0) are outdated and incompatible with Agents 1.0+ patterns.
UPDATE pyproject.toml:
tomldependencies = [
    "livekit>=0.15.0",
    "livekit-agents>=1.2.14",
    "livekit-plugins-openai>=1.2.6",
    "livekit-plugins-deepgram>=1.2.14",
    "openai>=1.0.0",
    "deepgram-sdk>=3.0.0",
    "python-dotenv>=1.0.0",
    "click>=8.0.0",
]
REFERENCE: docs/livekit_plugins.md for version requirements

Task 2: Remove broken LiveKit code from main.py
Context: The start() command in main.py has broken LiveKit integration that conflicts with Click CLI.
UPDATE main.py:

REMOVE the entire start() function (lines 181-283 approximately)
REMOVE the import: from livekit import agents
KEEP all other CLI commands: setup(), upload(), list-words(), show-progress()
ADD a comment at the bottom:

python# Note: To start the voice agent, run:
#   python -m spelling_tutor.agent_worker
REFERENCE: Avoid CLI conflicts by keeping agent worker separate

Task 3: Rewrite agent.py with proper Agents 1.0 pattern
Context: Current agent.py mixes old patterns. Need clean AgentSession implementation.
REWRITE agent.py:
python"""
LiveKit voice agent for spelling tutor.
Uses Agents Framework 1.0+ with AgentSession.
"""

import asyncio
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession
from livekit.plugins import openai, deepgram
from .tutor_logic import SpellingTutorLogic
from .database import Database
from .config import Config
import logging

logger = logging.getLogger(__name__)


class SpellingTutorAgent(Agent):
    """
    Spelling tutor agent that uses SpellingTutorLogic for educational flow.
    """
    
    def __init__(self, child_id: int, word_list_id: int, db: Database):
        self.child_id = child_id
        self.word_list_id = word_list_id
        self.db = db
        self.tutor = SpellingTutorLogic(child_id, word_list_id, db)
        
        # Get first word to practice
        self.current_word = self.tutor.get_next_word()
        
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
        logger.info("SpellingTutorAgent entered session")
        
        # Greet the child and start first word
        if self.current_word:
            greeting = f"Hi! Let's practice spelling. Your first word is: {self.current_word}"
            await self.session.generate_reply(instructions=greeting)
        else:
            await self.session.generate_reply(
                instructions="Hi! It looks like we don't have any words to practice right now."
            )
    
    async def on_user_turn_completed(self, text: str):
        """
        Called when user finishes speaking.
        Process their spelling attempt.
        """
        logger.info(f"User said: {text}")
        
        if not self.current_word:
            await self.session.generate_reply(
                instructions="We've finished all the words! Great job practicing today."
            )
            return
        
        # Clean the user's input (remove spaces, lowercase)
        attempt = text.strip().lower().replace(" ", "")
        
        # Check the spelling
        result = self.tutor.check_spelling(self.current_word, attempt)
        
        # Generate appropriate response
        if result["correct"]:
            # Correct! Move to next word
            response = f"Excellent! {self.current_word} is correct! "
            self.current_word = self.tutor.get_next_word()
            
            if self.current_word:
                response += f"Your next word is: {self.current_word}"
            else:
                response += "You've completed all the words! Amazing work!"
        
        elif result["close"]:
            # Close but not quite
            hint = self.tutor.get_hint(self.current_word, result["attempts"])
            response = f"Almost! {hint} Try again: {self.current_word}"
        
        else:
            # Incorrect, provide hint
            hint = self.tutor.get_hint(self.current_word, result["attempts"])
            response = f"Not quite. {hint} Let's try again: {self.current_word}"
        
        await self.session.generate_reply(instructions=response)


async def create_spelling_tutor_session(
    ctx: agents.JobContext,
    child_id: int,
    word_list_id: int,
) -> AgentSession:
    """
    Create an AgentSession configured for spelling tutor.
    
    REFERENCE: docs/livekit_plugins.md for TTS/STT configuration
    REFERENCE: examples/livekit_basic_voice_agent.py for session pattern
    """
    
    # Initialize database
    db = Database()
    
    # Create TTS (child-friendly voice)
    tts = openai.TTS(
        model="tts-1",
        voice="nova",  # Clear, friendly voice for children
    )
    
    # Create STT (accurate transcription)
    stt = deepgram.STT(
        model="nova-2",
        language="en-US",
        interim_results=True,
    )
    
    # Create the session
    session = AgentSession(
        stt=stt,
        tts=tts,
    )
    
    # Create the spelling tutor agent
    agent = SpellingTutorAgent(
        child_id=child_id,
        word_list_id=word_list_id,
        db=db,
    )
    
    return session, agent
REFERENCE:

docs/livekit_plugins.md for TTS/STT configuration
docs/livekit_agents_framework.md for AgentSession pattern
examples/livekit_basic_voice_agent.py for basic structure


Task 4: Create agent_worker.py (dedicated launcher)
Context: Need a separate script to start the agent worker without conflicting with CLI.
CREATE agent_worker.py:
python"""
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
REFERENCE:

docs/livekit_agents_framework.md for entrypoint and worker patterns
examples/livekit_basic_voice_agent.py for structure
docs/livekit_plugins.md for environment variables


Task 5: Update README.md with new agent instructions
Context: Users need to know how to start the agent worker.
UPDATE README.md:
In the "Usage" section, ADD a new subsection before "Upload Word List":
markdown### Start Voice Agent

Start the LiveKit voice agent worker:
```bash
python -m spelling_tutor.agent_worker
The agent will:

Connect to your LiveKit server
Wait for users to join rooms
Provide voice-based spelling practice

Note: The agent worker must be running before users can connect via the LiveKit client.
To connect to the agent, use any LiveKit client SDK or the Agents Playground.

---

### Task 6: Add database session context to agent

**Context:** Agent needs proper database session management.

**UPDATE agent.py:**

In the `SpellingTutorAgent.__init__()` method, change:
```python
# Before:
self.db = db

# After:
self.db = db
self.session = db.get_session()
And ADD cleanup method:
pythonasync def on_exit(self):
    """Called when agent exits the session."""
    logger.info("SpellingTutorAgent exiting session")
    if hasattr(self, 'session'):
        self.session.close()
REFERENCE: Proper resource cleanup

Task 7: Add logging for debugging
Context: Need visibility into agent behavior.
UPDATE agent.py:
At the top, add:
pythonimport logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
In key methods, add log statements:
python# In on_enter():
logger.info(f"Starting spelling practice for child_id={self.child_id}, word_list_id={self.word_list_id}")
logger.info(f"First word: {self.current_word}")

# In on_user_turn_completed():
logger.info(f"User attempt: '{attempt}' for word '{self.current_word}'")
logger.info(f"Result: {result}")

Quality Checklist
Before considering this task complete, verify:
✅ Dependencies updated to Agents 1.2.14+, plugins 1.2.6+
✅ main.py clean - No LiveKit code, no CLI conflicts
✅ agent.py rewritten - Uses AgentSession, NOT VoiceAssistant
✅ agent_worker.py created - Proper entrypoint pattern
✅ TTS configured with child-friendly voice ("nova")
✅ STT configured with latest model ("nova-2")
✅ Spelling tutor logic integrated - Uses existing SpellingTutorLogic class
✅ Database operations work - Proper session management
✅ Logging added for debugging
✅ README updated with agent startup instructions
✅ Environment variables validated on startup
✅ No references to deprecated VoicePipelineAgent or VoiceAssistant
✅ References curated docs in code comments

Testing Instructions
After implementation:

Install dependencies:

bash   pip install -e ".[dev]" --upgrade

Verify environment variables:

bash   python -c "from spelling_tutor.config import Config; c = Config(); print('✅ Config loaded')"

Start the agent worker:

bash   python -m spelling_tutor.agent_worker

Expected output:

   INFO - Starting LiveKit Agents worker for spelling tutor...
   INFO - LiveKit URL: wss://your-server.livekit.cloud
   INFO - Agent worker started

Connect via Agents Playground or LiveKit client SDK
Verify agent greets and starts spelling practice
Test spelling attempts - correct, incorrect, and close attempts
Check database - verify session records are created


Success Criteria
The implementation is successful when:
✅ Agent worker starts without errors
✅ Agent joins room when user connects
✅ Agent greets child and presents first word
✅ Agent correctly evaluates spelling attempts
✅ Agent provides appropriate hints for wrong attempts
✅ Agent tracks progress in database
✅ Agent moves through word list correctly
✅ No CLI conflicts with Click commands
✅ All existing CLI commands still work
✅ Code follows Agents 1.0+ patterns throughout