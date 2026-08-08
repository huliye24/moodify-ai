# 01_CAPABILITY_INVENTORY

| Capability | Status | CLI Command | Backend |
|---|---|---|---|
| Spectrum analysis | Available | analyze / v01-analyze | Core DSP |
| Audio processing | Available | process / v01-process | Pedalboard chain |
| Transcription | Available | transcribe | Basic Pitch ONNX |
| Stem transcription | Available | transcribe-stems | Basic Pitch + profiles |
| CLI DAW (native) | Implemented | daw render --engine native | Pedalboard |
| CLI DAW (ffmpeg) | Implemented | daw render --engine ffmpeg | FFmpeg subprocess |
| CLI DAW (reaper) | NOT_IMPLEMENTED | daw render --engine reaper | Exporter stub |
| Spectral evidence | Available | (science package) | librosa |
| MRS/Runtime | Available | evaluate-* | Core |
| API serve | Available | serve | FastAPI |
| Score | Experimental | — | — |
| Lyrics evidence | Available | refine prepare | Bridge |
