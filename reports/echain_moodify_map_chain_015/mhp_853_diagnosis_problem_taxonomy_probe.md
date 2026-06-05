# MHP-853: Diagnosis Problem Taxonomy Probe — Completion Report

**Generated**: 2026-06-05
**Status**: done
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6B

## Key Finding

`v01_diagnostics.py` has 15+ hand-written rules producing 3 issue types (spectral, dynamic, stereo). All mapped to a 13-problem-ID, 4-category taxonomy.

## Taxonomy: 13 Problems, 4 Categories

### Spectral (7 problems)
`sub_overpower`, `sub_weak`, `bass_forward`, `bass_recessed`, `presence_harsh`, `presence_weak`, `air_weak`

### Dynamics (3 problems)
`over_compressed`, `peak_too_hot`, `flat_dynamics`

### Stereo (2 problems)
`ultra_wide`, `near_mono`

### Overall (1 problem)
`multiple_issues` (derived from count of above)

## ProblemVector Schema

```python
@dataclass
class ProblemEntry:
    problem_id: str
    category: str      # spectral | dynamics | stereo | overall
    severity: str      # low | medium | high
    confidence: float  # 0-1 from threshold distance
    weight: float      # MAP weight
    description: str

@dataclass
class ProblemVector:
    problems: list[ProblemEntry]
    diagnosis_loss: float  # 0-1

# confidence = min(1.0, abs(observed - threshold) / margin)
# diagnosis_loss = min(1.0, sum(p.weight * p.confidence for p in problems) / 10.0)
```

## Probe Test

Run `diagnose()` on `vocal_folk.wav` → 0 problems → `ProblemVector(problems=[], diagnosis_loss=0.0)` — confirms taxonomy handles the clean case.

## Implementation

Build NEM MHP-866 (Implement Diagnosis Vector Contract). Worker creates `_to_problem_vector(diagnosis_report) -> ProblemVector`.
