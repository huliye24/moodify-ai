# Moodify audio-to-MIDI

Moodify owns a stable transcription API in `moodify.transcription`. Spotify
Basic Pitch 0.4.0 is the first inference backend, not the public API. This lets
the project add trained models, stem-aware profiles, MIDI cleanup, and backend
selection without breaking CLI or Python callers.

## Install on Windows

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_transcription.ps1
```

The installer creates `.venv-basic-pitch` with Python 3.11 and ONNX Runtime.
It intentionally avoids TensorFlow: Basic Pitch 0.4.0 includes an ONNX model,
but its Python 3.11 package metadata still declares TensorFlow as mandatory.

## Convert audio

```powershell
.venv-basic-pitch\Scripts\moodify.exe transcribe input.wav --output outputs/midi/input.mid
```

Use isolated stems where possible. A vocal, bass, piano, or guitar stem usually
produces more editable MIDI than a full mix. Useful controls include:

- `--minimum-frequency` and `--maximum-frequency` for instrument range
- `--onset-threshold` to control new-note sensitivity
- `--frame-threshold` to control sustained-note sensitivity
- `--minimum-note-length` to suppress very short notes
- `--multiple-pitch-bends` for overlapping expressive notes
- `--json` for machine-readable run metadata

## Development direction

1. Add stem-specific presets and automatic range selection.
2. Add MIDI cleanup: quantization, duplicate removal, voice allocation, and key-aware correction.
3. Record confidence and raw activation artifacts for comparison and training.
4. Define a benchmark corpus and note/onset/F1 regression gates.
5. Add alternative or fine-tuned backends behind `TranscriptionBackend`.

Basic Pitch is Copyright Spotify AB and licensed under Apache-2.0. Moodify's
adapter does not modify or redistribute its model in this repository; the
installer obtains the published `basic-pitch==0.4.0` package.
