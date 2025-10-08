# LiveKit Plugins - OpenAI & Deepgram

**Version Information:**
- livekit-agents: 1.2.14 (October 2025)
- livekit-plugins-openai: 1.2.6 (August 2025)
- livekit-plugins-deepgram: 1.2.14 (October 2025)

Date Curated: 2025-10-08
Source: LiveKit Agents Framework 1.x (released April 2025)

## ⚠️ Important: Agents 1.0 Breaking Changes

**Your current setup (0.8.0) is outdated.** LiveKit Agents 1.0+ uses:
- ✅ `AgentSession` (new unified orchestrator)
- ❌ NOT `VoiceAssistant` (doesn't exist)
- ❌ NOT `VoicePipelineAgent` (deprecated)

---

## Overview

LiveKit provides plugins for TTS (Text-to-Speech) and STT (Speech-to-Text) integration.
For your spelling tutor, you'll use OpenAI for TTS and Deepgram for STT.

---

## OpenAI Plugin

### Installation
```bash
pip install "livekit-plugins-openai>=1.2.6"

TTS (Text-to-Speech)
pythonfrom livekit.plugins import openai

# Initialize TTS
tts = openai.TTS(
    model="tts-1",      # or "tts-1-hd" for higher quality
    voice="alloy",      # Available: alloy, echo, fable, onyx, nova, shimmer
)
TTS Configuration
ParameterTypeDefaultDescriptionmodelstr"tts-1"TTS model ("tts-1" or "tts-1-hd")voicestr"alloy"Voice profile (alloy, echo, fable, onyx, nova, shimmer)speedfloat1.0Playback speed (0.25 to 4.0)
STT (Speech-to-Text)
pythonfrom livekit.plugins import openai

# Initialize STT
stt = openai.STT(
    model="gpt-4o-transcribe",  # Latest model (or "whisper-1")
    language="en",
)
STT Configuration
ParameterTypeDefaultDescriptionmodelstr"gpt-4o-transcribe"STT model ("gpt-4o-transcribe" or "whisper-1")languagestr"en"Language code (en, es, fr, etc.)
Environment Variables
bashOPENAI_API_KEY=sk-your_openai_api_key

Deepgram STT Plugin
Installation
bashpip install "livekit-plugins-deepgram>=1.2.14"
Basic Usage
pythonfrom livekit.plugins import deepgram

# Initialize STT
stt = deepgram.STT(
    model="nova-2",     # Latest and most accurate model
    language="en-US",   # Language code
)
Configuration Options
ParameterTypeDefaultDescriptionmodelstr"nova-2"STT model (nova-2, nova, enhanced, base)languagestr"en"Language code (en-US, en-GB, es, fr, etc.)interim_resultsboolTrueReturn partial transcriptionspunctuateboolTrueAdd punctuation to transcripts
Environment Variables
bashDEEPGRAM_API_KEY=your_deepgram_api_key

Using Plugins with AgentSession (v1.0+)
IMPORTANT: In Agents 1.0+, use AgentSession (NOT VoiceAssistant):
pythonfrom livekit import agents
from livekit.agents import AgentSession, Agent
from livekit.plugins import openai, deepgram

async def entrypoint(ctx: agents.JobContext):
    """Agents 1.0+ pattern using AgentSession"""
    
    # Connect to room
    await ctx.connect()
    
    # Create session with TTS and STT
    session = AgentSession(
        stt=deepgram.STT(model="nova-2", language="en-US"),
        tts=openai.TTS(model="tts-1", voice="nova"),
        llm=openai.LLM(model="gpt-4o-mini"),  # Optional: if using LLM
    )
    
    # Start the session
    await session.start(
        agent=Agent(instructions="You are a spelling tutor for children."),
        room=ctx.room,
    )
    
    # Generate initial greeting
    await session.generate_reply(
        instructions="Greet the child and ask which word they'd like to practice."
    )

if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )

Voice Selection for Children
For a spelling tutor targeting ages 6-10, recommended voices:
OpenAI TTS Voices:

nova - Clear, friendly, warm ⭐ BEST FOR KIDS
alloy - Neutral, clear enunciation
shimmer - Soft, gentle

Avoid:

echo - Deep, masculine (may be intimidating)
onyx - Very deep (better for adults)


Common Mistakes
❌ Don't Do This (v0.x pattern)
python# This doesn't exist in v0.8.0 or v1.0+
assistant = agents.VoiceAssistant(...)  # ❌ WRONG
✅ Do This Instead (v1.0+ pattern)
python# Use AgentSession in v1.0+
session = AgentSession(
    stt=deepgram.STT(),
    tts=openai.TTS(),
)
await session.start(agent=Agent(...), room=ctx.room)

Migration Notes (v0.8.0 → v1.0+)
If upgrading from v0.8.0 to v1.0+:

Replace VoicePipelineAgent → AgentSession
Replace function decorators: @llm.ai_callable → @function_tool
Update events: user_started_speaking → user_state_changed
Remove ChatManager (no longer exists)

See: https://docs.livekit.io/agents/start/v0-migration/

Testing Your Setup
python# Test script to verify plugins work
import asyncio
from livekit.plugins import openai, deepgram

async def test_plugins():
    print("Testing LiveKit Agents 1.0+ plugins...")
    
    try:
        tts = openai.TTS()
        print("✅ OpenAI TTS initialized")
    except Exception as e:
        print(f"❌ OpenAI TTS failed: {e}")
    
    try:
        stt = deepgram.STT()
        print("✅ Deepgram STT initialized")
    except Exception as e:
        print(f"❌ Deepgram STT failed: {e}")
    
    print("\n✅ All plugins working!")

if __name__ == "__main__":
    asyncio.run(test_plugins())
Run with:
bashpython test_plugins.py

Important Notes

API Keys: Store in .env file, never commit to git
Agents 1.0: Use AgentSession, not VoiceAssistant or VoicePipelineAgent
Rate Limits: OpenAI TTS has rate limits; monitor usage
Latency: TTS has ~200-500ms latency; STT is near real-time
Audio Quality: Use tts-1-hd for production, tts-1 for development
Language Support: Deepgram supports 30+ languages; OpenAI supports fewer

