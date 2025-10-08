# LiveKit Voice Assistant

Version: 1.2.14  
Date Curated: 2025-10-08

## Overview
Voice agents in LiveKit work by publishing and subscribing to audio tracks.
This guide covers audio track management, including publishing from AudioSource and subscribing to participant tracks.

### Publishing audio tracks

You can publish audio by creating an `AudioSource` and publishing it as a track.

Audio streams carry raw PCM data at a specified sample rate and channel count. Publishing audio involves splitting the stream into audio frames of a configurable length. An internal buffer holds 50 ms of queued audio to send to the realtime stack. The `capture_frame` method, used to send new frames, is blocking and doesn't return control until the buffer has taken in the entire frame. This allows for easier interruption handling.

In order to publish an audio track, you need to determine the sample rate and number of channels beforehand, as well as the length (number of samples) of each frame. In the following example, the agent transmits a constant 16-bit sine wave at 48kHz in 10 ms long frames:

**Python**:

```python
import numpy as np

from livekit import agents,rtc

SAMPLE_RATE = 48000
NUM_CHANNELS = 1 # mono audio
AMPLITUDE = 2 ** 8 - 1
SAMPLES_PER_CHANNEL = 480 # 10 ms at 48kHz

async def entrypoint(ctx: agents.JobContext):

    source = rtc.AudioSource(SAMPLE_RATE, NUM_CHANNELS)
    track = rtc.LocalAudioTrack.create_audio_track("example-track", source)
    # since the agent is a participant, our audio I/O is its "microphone"
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
    # ctx.agent is an alias for ctx.room.local_participant
    publication = await ctx.agent.publish_track(track, options)

    frequency = 440
    async def _sinewave():
        audio_frame = rtc.AudioFrame.create(SAMPLE_RATE, NUM_CHANNELS, SAMPLES_PER_CHANNEL)
        audio_data = np.frombuffer(audio_frame.data, dtype=np.int16)

        time = np.arange(SAMPLES_PER_CHANNEL) / SAMPLE_RATE
        total_samples = 0
        while True:
            time = (total_samples + np.arange(SAMPLES_PER_CHANNEL)) / SAMPLE_RATE
            sinewave = (AMPLITUDE * np.sin(2 * np.pi * frequency * time)).astype(np.int16)
            np.copyto(audio_data, sinewave)

            # send this frame to the track
            await source.capture_frame(audio_frame)
            total_samples += SAMPLES_PER_CHANNEL

    await _sinewave()



## Audio Source Example
async def entrypoint(ctx: agents.JobContext):

    source = rtc.AudioSource(SAMPLE_RATE, NUM_CHANNELS)
    track = rtc.LocalAudioTrack.create_audio_track("example-track", source)
    # since the agent is a participant, our audio I/O is its "microphone"
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
    # ctx.agent is an alias for ctx.room.local_participant
    publication = await ctx.agent.publish_track(track, options)

    frequency = 440
    async def _sinewave():
        audio_frame = rtc.AudioFrame.create(SAMPLE_RATE, NUM_CHANNELS, SAMPLES_PER_CHANNEL)
        audio_data = np.frombuffer(audio_frame.data, dtype=np.int16)

        time = np.arange(SAMPLES_PER_CHANNEL) / SAMPLE_RATE
        total_samples = 0
        while True:
            time = (total_samples + np.arange(SAMPLES_PER_CHANNEL)) / SAMPLE_RATE
            sinewave = (AMPLITUDE * np.sin(2 * np.pi * frequency * time)).astype(np.int16)
            np.copyto(audio_data, sinewave)

            # send this frame to the track
            await source.capture_frame(audio_frame)
            total_samples += SAMPLES_PER_CHANNEL

    await _sinewave()


## Subscribing to Tracks

**Python**:

python
@room.on("track_subscribed")
def on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
    if track.kind == rtc.TrackKind.KIND_VIDEO:
        video_stream = rtc.VideoStream(track)
        async for frame in video_stream:
            # Received a video frame from the track, process it here
            pass
        await video_stream.aclose()

