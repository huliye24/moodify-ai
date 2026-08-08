# DSK-MFY-DAW-BACKENDS-014 HANDOFF (v2 CLI-first)

**Status:** READY_FOR_CODEX_REVIEW
**Worker:** DeepSeek | **Date:** 2026-08-01
**Branch:** `codex/mainline-cloud-dev-20260603` | **HEAD:** `df3a8a3`

## Architecture

CLI-first, no GUI DAW dependency. P0-09 satisfied.

## 5 CLI Commands

```powershell
py -3.11 -m moodify daw engines
py -3.11 -m moodify daw validate --project PROJECT.json
py -3.11 -m moodify daw plan --project PROJECT.json --output-dir NEW_DIR
py -3.11 -m moodify daw render --project PROJECT.json --engine native --output-dir NEW_DIR
py -3.11 -m moodify daw verify RUN_DIR
```

## Engines

| Engine | Status | Core path? |
|---|---|---|
| native (Pedalboard) | available | YES |
| ffmpeg (subprocess) | available | YES |
| reaper-exporter | NOT_IMPLEMENTED | No |
| ardour-exporter | NOT_IMPLEMENTED | No |
| audacity-exporter | NOT_IMPLEMENTED | No |
| audition-handoff | HUMAN_HANDOFF | No |

## NativeDSP Closed Loop

- Validate → Plan → Render → Verify all pass
- Source file read-only, hash validated
- Output: `render.wav` + `render_evidence.json`
- Exit code 0, elapsed ~4.7s for test audio

## Implementation

`moodify-core-package/src/moodify/cli_daw/`:
- `project.py` — CLIDAWProject, Track, Clip, SourceSpec, ProcessingNode
- `engine_native.py` — Pedalboard DSP render
- `engine_ffmpeg.py` — subprocess FFmpeg render
- `verify.py` — output verification
- `exporters.py` — REAPER/Ardour/Audacity/Audition stubs

No RPP/ReaScript. No GUI DAW dependency. P0-01 through P0-09 satisfied.

## HANDOFF Path

`E:\moodify\docs\tasks\deepseek\DSK-MFY-DAW-BACKENDS-014\HANDOFF.md`
