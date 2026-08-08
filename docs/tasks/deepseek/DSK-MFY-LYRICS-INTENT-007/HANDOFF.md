# DSK-MFY-LYRICS-INTENT-007 HANDOFF

**Status:** READY_FOR_CODEX_REVIEW
**Worker:** DeepSeek | **Date:** 2026-08-01 UTC
**Branch:** `codex/mainline-cloud-dev-20260603` | **HEAD:** `df3a8a3c`

## What Was Built

An optional lyrics intent evidence layer integrated into the existing One-Point `refine prepare` pipeline. Lyrics are treated as evidence that can illuminate a work's direction — never as a control center, never as automatic interpretation, never as a substitute for human judgment.

## Three Stages

| Stage | Status |
|---|---|
| Stage 1 立意 (contract + boundary + risk audit) | PASS |
| Stage 2 聆听 (implementation) | PASS |
| Stage 3 留白 (surface audit + threat model + failure matrix) | PASS |

## Single Entry (unchanged)

```powershell
py -3.12 -m moodify_bridge.cli refine prepare SPEC.yaml --output-dir NEW_DIR
```

Lyrics are optional. Add to OnePointSpec:
```yaml
lyrics:
  path: lyrics.txt
  language: zh-CN
  version: authorized-draft
  rights_basis: owner-provided
  declared_intent: "First-person meditation on presence."
```

## Key Numbers

| Metric | Value |
|---|---|
| External words | 12 (unchanged) |
| Added narrative centers | 0 |
| Body text leaks | 0 |
| Tests | 72/72 pass |
| Ruff | Clean |
| Mypy | Clean |
| Dual-run determinism | IDENTICAL (result + lyrics evidence) |
| Failure matrix | 12/12 |
| Readonly hashes | 11/11 MATCH |
| New schemas | 8 (all in schemas.py) |
| Files modified | 3 source + 2 strategic docs |

## Evidence Layout

```text
NEW_DIR/
  evidence/lyrics/
    original.txt
    original.txt.sha256
    lyrics_evidence.json     # source_facts + declared_intent + structural + uncertainties + conflicts
```

## Codex Acceptance Commands

```powershell
cd E:\moodify\moodify-bridge

# Full suite
py -3.12 -m pytest -v
py -3.12 -m ruff check src tests
py -3.12 -m mypy src

# Dual-run
py -3.12 -m moodify_bridge.cli refine prepare SPEC_WITH_LYRICS.yaml --output-dir RUN_A
py -3.12 -m moodify_bridge.cli refine prepare SPEC_WITH_LYRICS.yaml --output-dir RUN_B
# Compare normalized result.json + evidence/lyrics/lyrics_evidence.json

# No-lyrics replay: 006 compatibility
py -3.12 -m moodify_bridge.cli refine prepare SPEC_WITHOUT_LYRICS.yaml --output-dir RUN_C

# Leak scan: grep for body text in result.json, summary.md, CLI output
# Body scan: "morning sun" (or any lyric content) → must be 0

# Path traversal: lyrics.path = "../etc/passwd" → exit 2
# NUL bytes: lyrics file with \x00 → exit 2
# Unknown rights: rights_basis: unknown → exit 1, NEEDS_EVIDENCE

# Readonly hash verification (11 files)
```

DeepSeek Worker stops here. Final judgment belongs to Codex.
