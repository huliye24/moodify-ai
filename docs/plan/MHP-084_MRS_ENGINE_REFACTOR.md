# MHP-084: MRS Scoring Engine Refactor — Configurable Thresholds, Genre Dispatch

**Status**: proposed
**Direction**: NEM-MOODIFY-MRS-002 / Harden-6 / E2 (Execution)
**Depends on**: MHP-083 (issues fixed)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

The MRS scoring code is currently spread across three modules:
- `metrics.py` — WAV analysis, pseudo_mrs, MRS Open wrapper, compare_before_after
- `mrs_calibration.py` — calibration workflow (sample sets, reviews, audits, thresholds)
- `operator_console.py` — decide_candidate_gate (hardcoded thresholds before MHP-071)

Build-6 added genre thresholds and graduated over_dark, but these were added incrementally. For production, the MRS system should have a single entry point that:
1. Accepts an audio path + genre
2. Selects the appropriate MRS variant (calibrated pseudo-MRS or MRS Open)
3. Applies genre-specific thresholds
4. Runs graduated over_dark
5. Returns a unified MRS result with gate recommendation

## Goal

Create `moodify_runtime/mrs_engine.py` as the single entry point:

```python
def score_audio(
    audio_path: str,
    genre: str = "",
    preset: str = "",
    cfg: Optional[RuntimeConfig] = None,
) -> MRSResult:
    """Unified MRS scoring entry point.
    
    Returns MRSResult with:
        - mrs_score: float
        - mrs_variant: "pseudo" | "calibrated" | "mrs_open"
        - over_dark: OverDarkResult (level, score, bands, recommendation)
        - gate_decision: GateDecision
        - genre_thresholds_applied: dict
    """
```

### Refactor scope
1. Extract MRS scoring logic from `metrics.py` into `mrs_engine.py`
2. Move threshold loading from inline code to `configs/mrs_thresholds.yaml` reader
3. Integrate over_dark detector as a composable step
4. Keep backward compatibility: `pseudo_mrs()`, `compute_mrs_open_v031()`, `compare_before_after()` still work
5. Update `decide_candidate_gate()` to delegate to `mrs_engine.score_audio()`
6. Update `runner.py` `compare_before_after()` to use the new engine

## Acceptance Criteria
- `moodify_runtime/mrs_engine.py` with `score_audio()` function
- Backward compatible: all existing callers still work
- Genre thresholds loaded from YAML config
- Over-dark detection integrated as a pipeline step
- Existing 129+ Studio OS tests still pass
- New tests for `mrs_engine.score_audio()` with all 5 genres
