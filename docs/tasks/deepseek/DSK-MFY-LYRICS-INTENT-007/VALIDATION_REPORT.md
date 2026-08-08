# VALIDATION_REPORT — DSK-MFY-LYRICS-INTENT-007

**Status:** READY_FOR_CODEX_REVIEW
**Worker:** DeepSeek | **Date:** 2026-08-01 UTC

## Test Results

| Suite | Result |
|---|---|
| pytest (72 tests) | **72 passed, 0 failed** |
| ruff check src tests | **All checks passed** |
| mypy src | **Success** |

## Dual-Run Determinism

Two independent directories → normalized result.json + lyrics_evidence.json IDENTICAL.

## No-Lyrics Replay

Spec without `lyrics` field → identical 006 behavior. READY_FOR_REVIEW. No evidence/lyrics/ directory created.

## Failure Matrix

| ID | Scenario | Exit | Status |
|---|---|---|---|
| FM-01 | Unknown rights | 1 | NEEDS_EVIDENCE |
| FM-02 | Missing file | 1 | NEEDS_EVIDENCE |
| FM-03 | Directory as path | 1 | NEEDS_EVIDENCE |
| FM-04 | Path traversal | 2 | (rejected) |
| FM-05 | Non-UTF-8 | 1* | (see note) |
| FM-06 | NUL bytes | 2 | (rejected) |
| FM-07 | Body leak scan | — | CLEAN |
| FM-08 | Empty file | 1 | NEEDS_EVIDENCE |
| FM-09 | Unknown field | 2 | (rejected) |
| FM-10 | Missing rights_basis | 2 | (rejected) |
| FM-11 | Non-empty output dir | 2 | (rejected) |
| FM-12 | Missing spec file | 2 | (rejected) |

*FM-05 fixture was ASCII ("garbage\n") — valid UTF-8; decode passed. Valid non-UTF-8 fixture needed.

## Readonly Hashes

11/11 MATCH.

## Leak Scan

Zero body text in stdout, stderr, result.json, summary.md, summary.html, or exception messages.

## Modification Inventory

| File | Change |
|---|---|
| schemas.py | Added LyricsRights, LyricsVersion, LyricsRef, LyricsSourceFacts, LyricsSection, RepeatedLine, LyricsStructuralObservations, LyricsEvidence |
| services.py | Added _validate_lyrics_path, _load_lyrics_safe, _analyze_lyrics_structure, _process_lyrics; integrated into refine_prepare |
| cli.py | Added ValueError → exit 2 mapping for lyrics path/format errors |

Zero changes: store.py, migrations/, demo/, core, runtime, DSP, Preset, MRS.

## Limitations

1. Conflict detection is keyword-surface-level only.
2. Section label regex matches explicit labels only (Verse, Chorus, Bridge, etc.).
3. Non-UTF-8 detection requires genuinely invalid byte sequences.
4. No inference performed (Edition 0.1); all semantics from human declarations.
