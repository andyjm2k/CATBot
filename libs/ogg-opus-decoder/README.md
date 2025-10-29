# Ogg Opus Decoder Files

This directory should contain the following files from the ogg-opus-decoder package:

1. **ogg-opus-decoder.min.js** - The main decoder bundle (JS-only, no WASM)
2. **OggOpusDecoder.js** - The ESM wrapper module
3. **OggOpusDecoderWebWorker.js** - The Web Worker wrapper that handles decoding

## Optional File

- **ogg-opus-decoder.opus-ml.min.js** - Heavier ML-based decoder (fallback option, not required)

## Getting the Files

These files should be obtained from the ogg-opus-decoder package distribution. The code is configured to load them from this local directory instead of a CDN for better performance and reliability.

## Usage

The decoder is automatically initialized when `index-dev.html` loads and exposed via `window.__opus`. The SSE streaming TTS code uses this decoder to play streaming Opus audio in real-time.

