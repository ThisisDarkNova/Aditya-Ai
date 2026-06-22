# Voice Processing Engine

VESPERA OS integrates local voice capabilities for audio communication.

## Subsystems

1. **Wake Word Watcher**
   - Continuously monitors input audio streams for wake indicators.
   - Runs in a background recovery loop in `CognitiveCore/core/audio_recovery.py` to prevent failure if drivers drop out.

2. **Voice Activity Detection (VAD)**
   - Distinguishes human speech from ambient room noise.
   - Silences listening loops when speech ends.

3. **Text-To-Speech (TTS)**
   - Synthesizes vocal responses from text outputs.
   - Updates the WebGL orb to `speaking` mode synchronously.
