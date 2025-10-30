# Chatterbox TTS Streaming Notes

## Context
- Investigated the in-repo web client (`index-dev.html`) that consumes the Chatterbox TTS SSE stream.
- Could not clone `https://github.com/travisvn/chatterbox-tts-api` from the container because outbound HTTPS tunnels are blocked (CONNECT 403).

## Streaming observations
- The client explicitly requests SSE (`Accept: text/event-stream`) and asks the Chatterbox endpoint for raw PCM16 chunks.
- Incoming SSE events are parsed incrementally; `speech.audio.delta` payloads are handed to `playPcm16Delta`, which decodes the PCM16 data and schedules it on a shared `AudioContext`.
- The blob fallback path only executes when the response is not SSE or when a parsing/playback error occurs.

## Possible issue noticed in the PCM helper
- `playPcm16Delta` creates the audio buffer with `ctx.createBuffer(channels, len, sampleRate)` where `len` equals the total number of 16-bit samples (including all channels). For multi-channel audio this allocates a buffer that is `channels` times longer than the real data, leaving each chunk padded with silence. That extra padding can accumulate into audible delays.
- Using `samplesPerChannel = len / channels` as the second argument to `createBuffer` would avoid that zero padding.

