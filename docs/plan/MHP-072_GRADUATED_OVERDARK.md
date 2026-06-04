# MHP-072: Graduated Over-Dark Detector — 3-Level Replacement for Binary Flag

**Status**: proposed
**Direction**: NEM-MOODIFY-MRS-002 / Build-6 / E2 (Execution)
**Depends on**: MHP-071 (genre thresholds configured)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

Currently `decide_candidate_gate()` receives a single boolean: `over_dark_triggered`. If True → reprocess. If False → continue.

This is too coarse. Consider:
- A track that's slightly dark in the 200-400 Hz range — maybe still acceptable for rock, definitely not for vocal.
- A track where the darkness is concentrated in sub-bass (< 60 Hz) vs. lower-mids (200-500 Hz) — different perceptual impact.
- A track that's dark because the original was dark (genre-appropriate) vs. processing-induced darkness (actual damage).

## Goal

Replace the binary `over_dark_triggered` with a 3-level graduated detector:

```python
def detect_over_dark(audio_path: str, genre: str = "") -> dict:
    """Return graduated over-dark assessment.
    
    Returns:
        {
            "level": "none" | "mild" | "severe",
            "score": float,          # 0.0 (no darkness) to 1.0 (maximum)
            "affected_bands": [...],  # frequency ranges where darkness detected
            "is_processing_induced": bool,  # True if processing made it darker
            "recommendation": "pass" | "review" | "reject",
        }
    """
```

### Detection logic
1. Compare before/after spectral energy in 3 bands: sub-bass (20-60Hz), low-mid (100-300Hz), mid (300-2000Hz)
2. Compute per-band darkness delta = (after_energy - before_energy) / before_energy
3. Classify:
   - `none`: all bands delta < 10% increase
   - `mild`: 1-2 bands delta 10-30% increase
   - `severe`: any band delta > 30% increase or all 3 bands > 10%
4. Cross-reference with genre thresholds from MHP-071

## Acceptance Criteria
- `moodify_runtime/over_dark.py` with `detect_over_dark()` function
- Returns 3-level classification (none/mild/severe) with per-band scores
- Genre-aware: electronic tolerates more sub-bass darkness than vocal
- `decide_candidate_gate()` updated to use graduated detector
- Unit test: synthetic dark audio triggers "severe", clean audio triggers "none"
- Existing 129 tests still pass
