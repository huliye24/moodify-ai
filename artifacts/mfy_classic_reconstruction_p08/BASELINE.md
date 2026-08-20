# MFY-CR-P08 — BASELINE

## Inputs (existing authority, consumed not duplicated)

| Layer | Module | Entry point |
|---|---|---|
| Era Diagnostic (P03) | `moodify.era_diagnostic.engine` | `run_era_diagnostic(metrics, production_case_id=...)` |
| Objective (P04) | `moodify.reconstruction_objective` + `moodify.reconstruction.objective` | `build_objectives` / `plan_from_findings` |
| Identity Guard (P05) | `moodify.identity_guard.guard` / `.ranking` | `guard_candidate` / `rank_candidates` |
| Golden pipeline (P06) | `moodify.reconstruction.pipeline` | `run_golden_pipeline` |
| Data factory / P07 | `moodify.data_factory.runner` | `validate_source_audio` |
| Node queue primitives | `moodify.node.queue` / `.db` / `.resources` | lease / recovery / precheck patterns |
| Canonical contracts | `moodify.contracts` | ProductionCase / EvidenceArtifact / Provenance / ids |

## Pre-P08 regression baseline

- Full suite before P08: 839 passed / 5 skipped (12m35s, P07 record).
- P08 adds `moodify.reconstruction_job` (~67 tests at the time of writing this
  document) and parameterization tests in `tests/reconstruction/`.

## Environment facts (this machine)

- ffmpeg 8.1.1 installed via winget (Gyan), NOT on PATH; discovered at
  `C:\Users\*\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*\ffmpeg-*\bin\`
  by `reconstruction_job.audio_util.ffmpeg_path()` and injected onto PATH by
  `ensure_ffmpeg_on_path()` (auditory.decode relies on PATH/Program Files).
- Windows: no `resource.getrusage`; peak memory uses tracemalloc when enabled,
  honestly reported as 0.0 otherwise.
- Sample-rate-preserving transcode (`-acodec pcm_s16le -f wav`, no `-ar`) —
  no blind resampling; AAC/M4A supported via ffmpeg.

## Tested supported formats

- WAV / FLAC / MP3 / OGG / M4A / AAC: accepted on upload (suffix gate), decoded
  via ffmpeg at ingest; decode failure is a PERMANENT `DECODE_FAILED` failure,
  never a crash.
- Format capability reported honestly in `GET /api/v1/reconstruction/capabilities`.

## Conventions

- Every failure is a `FailureInfo` with `failure_code / stage / retry_policy /
  user_action / internal_detail / public_message_key`; users never see stack
  traces or internal paths.
- Logs never contain raw audio, secrets, private keys, or auth tokens.
- No public audio URL exists; audio access is owner-only with a short-lived
  HMAC token.
