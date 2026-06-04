# MHP-086: Integration Audit — MRS ↔ Gate ↔ CLI ↔ API ↔ Console

**Status**: proposed
**Direction**: NEM-MOODIFY-MRS-002 / Harden-6 / V2 (Validation)
**Depends on**: MHP-085 (regression passed)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

MRS scoring now touches every interface in Studio OS:
- **CLI**: `moodify-runtime operator-run --live` triggers MRS scoring
- **API**: `/operator/jobs/{id}/attach-run` surfaces MRS scores in candidate detail
- **Console**: Job Detail view shows MRS scores, gate decisions, over_dark flags
- **Runtime**: `runner.py` `compare_before_after()` computes MRS
- **Calibration**: `/calibration/*` endpoints store and audit MRS results

After the MRS engine refactor (MHP-084), we need to verify that all interfaces see consistent MRS data.

## Goal

Produce an MRS-specific integration audit:

1. Trace one audio file through all 4 interfaces — verify MRS scores are identical
2. Verify MRS scores in API responses match CLI output
3. Verify Console HTML renders the new over_dark graduated levels correctly
4. Verify calibration audit reports use the correct MRS variant
5. Verify genre thresholds are applied consistently across all interfaces

### Key verification
```python
# Same audio + same genre + same preset → same MRS score everywhere
audio = "data/calibration/mrs_002/source/piano/test.wav"
score_api = get via API
score_cli = get via CLI operator-run
score_runtime = direct call to mrs_engine.score_audio()
assert score_api == score_cli == score_runtime
```

## Acceptance Criteria
- MRS integration audit: `reports/nem_mrs_002/integration_audit.md`
- All 4 interfaces produce identical MRS scores for the same input
- Console correctly displays graduated over_dark (none/mild/severe) with visual differentiation
- API `/calibration/audits` returns correct MRS variant metadata
- 0 interface mismatches found (or documented with fix plan)
