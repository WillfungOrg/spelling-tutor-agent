python
"""
Minimal LiveKit voice agent example.
Demonstrates proper Agents Framework usage with TTS/STT.

Requirements:
- livekit-agents>=0.8.0
- livekit-plugins-openai>=0.6.0
- livekit-plugins-deepgram>=0.6.0
"""

import asyncio
from livekit import agents, rtc
from livekit.plugins import openai, deepgram

async def entrypoint(ctx: agents.JobContext):
    """
    Main entrypoint for the voice agent.
    This function is called when the agent joins a room.
    """
    
    # Initialize TTS (Text-to-Speech)
    tts = openai.TTS(
        model="tts-1",
        voice="alloy",
    )
    
    # Initialize STT (Speech-to-Text)
    stt = deepgram.STT(
        model="nova-2",
        language="en",
    )
    
    # Connect to the room
    await ctx.connect()
    
    print(f"Agent joined room: {ctx.room.name}")
    
    # Subscribe to first participant's audio track
    @ctx.room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            print(f"Subscribed to {participant.identity}'s audio track")
            # Process audio here (e.g., run STT)
    
    # Publish a greeting
    source = rtc.AudioSource(24000, 1)  # 24kHz, mono
    track = rtc.LocalAudioTrack.create_audio_track("agent-voice", source)
    
    options = rtc.TrackPublishOptions(
        source=rtc.TrackSource.SOURCE_MICROPHONE
    )
    
    await ctx.room.local_participant.publish_track(track, options)
    print("Agent audio track published")

if __name__ == "__main__":
    # Run the agent worker
    # The CLI will handle room connections
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )