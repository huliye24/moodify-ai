# DSK-MFY-STEM-MIDI-008 — Codex Final Acceptance

**Decision:** ACCEPTED_AFTER_CODEX_FINISH_WITH_BENCHMARK_LIMITS  
**Date:** 2026-08-01  
**Acceptance owner:** Codex

## Outcome

The stem-aware Audio-to-MIDI engineering path is accepted after Codex finish.
It now provides strict stem manifests and profiles, isolated per-stem failure,
immutable raw MIDI, derived clean MIDI with diffs, and a parseable Type 1 merged
MIDI while keeping drums explicitly unsupported.

This acceptance establishes an engineering pipeline. It does not establish
transcription accuracy, musical correctness, separator quality, drum support or
an 8 GB performance guarantee.

## Worker handoff discrepancies

The submitted HANDOFF could not be accepted directly:

1. Unsupported stems skipped their required per-stem JSON evidence.
2. The library API could overwrite an existing output tree even though the CLI rejected it.
3. A failing backend could leave a partial raw MIDI artifact.
4. Stage 2 cleanup and merge were isolated functions, not part of the CLI runner path.
5. Type 1 merge copied notes only and discarded pitch bends and control changes.
6. Cleanup/merge, raw immutability, idempotent output protection and expressive events had no tests.
7. The documented `py -3.11 -m moodify` command failed because no module entry existed.
8. Ruff had five errors despite Stage 3 being reported PASS.
9. No ground-truth accuracy, double-run benchmark or peak-memory evidence was delivered.

## Codex finish

- Added manifest validation and API-level non-empty-output rejection before writes.
- Persisted unsupported per-stem evidence and removed newly created partial raw files on failure.
- Added derived `clean/{kind}.mid`, per-track CleanupDiff/hashes and `merged.mid` to the runner.
- Protected raw/clean/merged destinations against in-place or existing-file overwrite.
- Corrected musical grid conversion and preserved duration during explicit quantization.
- Preserved pitch bends and control changes during Type 1 merge.
- Added `moodify.__main__` so the documented module CLI works.
- Expanded the focused suite from 17 to 24 tests.

## Independent verification

- Pytest: **24 passed** (21 stem/pipeline + 3 legacy transcription)
- Ruff: **clean**
- Mypy: **clean across 7 source files**
- New module CLI help: exit 0
- Legacy installed CLI help: exit 0
- Type 1 output: parsed and format header verified
- Raw protection: source/raw bytes unchanged; existing destinations rejected
- Expression preservation: pitch bend and control change verified after merge
- Git diff whitespace check: clean for the accepted scope

## Remaining explicit limits

1. Demucs is not installed; Moodify does not separate stems in this task.
2. No scored synthetic-audio benchmark reports note precision/recall/F1, onset tolerance or octave error.
3. No authorized real-song ground truth exists; real-song accuracy remains unknown.
4. Cold/warm runtime and peak memory were not measured, so no 8 GB guarantee is made.
5. Key correction remains unimplemented and off; no automatic pitch correction occurs.
6. Drums remain `UNSUPPORTED_FOR_PITCH_TRANSCRIPTION`.
7. Human review remains required before using the MIDI as a score or production artifact.

## Dependency judgment

The deterministic engineering contract is sufficient for 009 to consume 008's
artifacts. Any task that needs accuracy or performance claims must depend on a
new benchmark acceptance, not on this document.
