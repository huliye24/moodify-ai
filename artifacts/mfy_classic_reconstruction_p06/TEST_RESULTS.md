# MFY-CR-P06 — Test Results

Executed 2026-08-17 on `codex/moodify-classic-reconstruction-001`.

## Summary

```text
reconstruction (new) = 12 passed / 0 failed (objective, hard gates, blind tooling, record, pipeline integration)
full suite           = 851 passed / 5 skipped / 0 failed
p03/p05 regression   = included and green (era_diagnostic 61, identity_guard 26)
ruff                 = all checks passed (src/moodify/reconstruction + tests/reconstruction)
git diff --check     = clean
真机/instrumentation = NOT_RUN (user instruction)
visual               = SKIPPED (user instruction)
盲听                 = PENDING_HUMAN (kit prepared at golden_run_out/listening/)
```

## Coverage

- **Objective**: deterministic plans (identical inputs → identical output),
  SOURCE-first ordering, objective refs only from POSSIBLE/OBSERVED findings
  (LIKELY_ARTISTIC / NOT_SUPPORTED excluded), plan hashes deterministic.
- **Hard gates**: identical sources pass; new clipping correctly fails
  NO_NEW_CLIPPING; duration/channels/loudness gates wired (metrics keys fixed).
- **Blind tooling**: labels X1-X4 hide candidate names; mapping covers
  {SOURCE,A,B,C}; not finalized until scoring; level matching aligns loudness
  to source within 1 LU; no candidate-name leak in listening files.
- **Record**: round-trip serialization; explicit golden status vocabulary.
- **Pipeline integration**: full synthetic run — source freeze, 6 diagnostics,
  A/B/C rendered + gated, identity verdicts, ranking incl. SOURCE, blind kit,
  record written as PENDING_LISTENING.

## Golden run facts (Vieillir)

- Candidates A/B/C all pass hard gates; identity all PASS; technical top = C.
- Deltas surgical: LUFS +0.03/+0.40/+0.93, LRA +0.0/+0.32/+0.55, crest
  +0.01/-0.03/-0.54, centroid +38/+172/+253 Hz, zero new clipping.
- Chain findings recorded: always-on compressor (flattening) and default
  reverb (+4.2 LU) bypassed as documented objective decisions.
