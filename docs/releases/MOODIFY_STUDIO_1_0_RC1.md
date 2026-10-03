# Moodify Studio 1.0.0-rc.1

Moodify Studio is the Windows listening and production-review interface for the Moodify Sound Protocol. This release packages the existing Electron desktop shell without changing its product logic or audio behavior.

The current Studio flow presents generated stereo audio as a structured production workflow:

```text
Detect → Diagnose → Separate → Structure → Plan → Finish
```

AI plans, Moodify Core executes, and the human decides. Generated is not finished.

## Included

- Windows 10/11 x64 NSIS installer
- Windows x64 portable executable
- Existing Moodify Studio interface and production workflow
- Runtime Python helper scripts used by the desktop shell
- Production Node.js dependencies, including the Windows `node-pty` and Codex runtimes
- SHA-256 checksums and a machine-readable release manifest

## Runtime requirements

The EXE packages the Moodify Studio desktop shell. The complete standalone runtime bundle is a later release-engineering task. The full RC1 pipeline expects an existing local Moodify engineering/runtime environment with:

- Windows 10 or 11, x64
- Python 3.10–3.12 available as `python`
- Moodify Core 1.0.0-rc.1 importable by that Python environment
- FFmpeg and FFprobe for Core operations that require them
- Basic Pitch, optional, for MIDI generation
- music21, optional, for MusicXML and score generation

No Python distribution, model weights, Basic Pitch, music21, FFmpeg, or FFprobe are silently downloaded or bundled by this release.

## Accuracy boundaries

- Quick separation is `PREVIEW_NOT_MASTERING_GRADE`.
- MIDI is machine-readable structure, not ground truth.
- Human listening and review remain authoritative for perceptual decisions.
- This is not a black-box automatic mastering product and does not claim production-grade neural stem separation.

## Signing and Windows SmartScreen

RC1 is unsigned. Windows SmartScreen may show **Unknown publisher**. This is an expected release boundary, not evidence by itself of a security failure.

## Known limitations

- The desktop shell is not yet a fully self-contained offline production suite.
- Pipeline stages that depend on missing external tools will report their normal unavailable or failure state.
- Optional MIDI and score stages require their corresponding external Python packages.
- There is no auto-update mechanism in RC1.

