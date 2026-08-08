# 00_IMPLEMENTATION_AUDIT — DSK-MFY-DAW-BACKENDS-014 (REWRITE v2)

**Date:** 2026-08-01 | **HEAD:** df3a8a3 | **Arch:** CLI-first, no GUI DAW dependency

## Tool Inventory

| Tool | Status | Version | Use |
|---|---|---|---|
| FFmpeg | Available | 8.1.1 | Headless render, format conversion, probe |
| ffprobe | Available | 8.1.1 | Audio metadata extraction |
| Pedalboard | Available | GPL-3.0 | Native DSP (EQ, compressor, limiter) |
| soundfile | Available | BSD | WAV read/write |
| SoX | NOT FOUND | — | Deferred |
| Rubber Band | NOT FOUND | — | Deferred |
| FluidSynth | NOT FOUND | — | Deferred |
| REAPER | NOT INSTALLED | — | Exporter stub only |

## Architecture Decision

**Phase 1 closed loop: NativeDSP + FFmpeg.** No GUI DAW is a core execution path.

- `NativeDSPBackend`: reuses existing `moodify.processing.*` for EQ/compressor/limiter/gain/fade
- `FFmpegBackend`: subprocess-based for mixing, format conversion, resampling
- REAPER/Ardour/Audacity/Audition: exporter stubs only (`NOT_IMPLEMENTED`)

## New Package

`moodify-core-package/src/moodify/cli_daw/`:
- `project.py` — CLIDAWProject, Track, Clip, Bus, ProcessingNode schemas
- `graph.py` — processing graph validation
- `engine_native.py` — NativeDSPBackend
- `engine_ffmpeg.py` — FFmpegBackend
- `render.py` — render orchestrator
- `verify.py` — output verification
- `exporters.py` — REAPER/Ardour/Audacity/Audition stubs

## CLI

```powershell
py -3.11 -m moodify daw engines
py -3.11 -m moodify daw validate --project PROJECT.json
py -3.11 -m moodify daw plan --project PROJECT.json --output-dir NEW_DIR
py -3.11 -m moodify daw render --project PROJECT.json --engine native --output-dir NEW_DIR
py -3.11 -m moodify daw verify RUN_DIR
```

No window, no mouse, no audio device needed.
