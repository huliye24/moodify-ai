# MHP-853: Diagnosis Problem Taxonomy Probe

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6B: Vector Definitions / V3
**Depends on**: MHP-845 (Audit), MHP-852 (Feature Vector)
**Protocol**: AWJ Stack + E-Chain 54

## Context

`v01_diagnostics.py` has 15+ hand-written rules producing human-readable strings. Each rule maps to a spectral, dynamic, or stereo check. MAP requires these to be structured as `{problem_id, severity, confidence, dimension}` so downstream stages (P, V, R) can consume them programmatically.

## Probe: Extract Taxonomy from Existing Rules

Running the current `diagnose()` against `vocal_folk.wav` yields:

```text
Health: good
Issues: []
Strengths: [
  "Healthy crest factor — good balance of impact and body.",
  "Well-balanced stereo image."
]
Suggested: [clean_master]
```

All current rules were enumerated and classified:

## Problem Taxonomy v0.1

### Category 1: Spectral Balance

| problem_id | Rule | Severity Threshold | Weight |
|------------|------|-------------------|--------|
| `sub_overpower` | sub_bass > -6 dB | medium | 1.0 |
| `sub_weak` | sub_bass < -30 dB | medium | 0.8 |
| `bass_forward` | bass > -3 dB | medium | 1.0 |
| `bass_recessed` | bass < -18 dB | medium | 0.8 |
| `presence_harsh` | presence > -6 dB | high | 1.0 |
| `presence_weak` | presence < -18 dB | medium | 0.8 |
| `air_weak` | air < -30 dB | low | 0.5 |

### Category 2: Dynamics

| problem_id | Rule | Severity Threshold | Weight |
|------------|------|-------------------|--------|
| `over_compressed` | crest_factor < 2.0 | high | 1.0 |
| `peak_too_hot` | crest_factor > 8.0 | medium | 0.8 |
| `flat_dynamics` | dynamic_range_db < 3 | high | 1.0 |

### Category 3: Stereo Field

| problem_id | Rule | Severity Threshold | Weight |
|------------|------|-------------------|--------|
| `ultra_wide` | correlation_lr < 0.2 | medium | 0.7 |
| `near_mono` | correlation_lr > 0.95 | low | 0.5 |

### Category 4: Overall

| problem_id | Rule | Severity Threshold | Weight |
|------------|------|-------------------|--------|
| `multiple_issues` | len(issues) > 3 → poor | high | 1.0 |
| `some_issues` | len(issues) <= 3 → fair | medium | 1.0 |
| `clean` | len(issues) <= 1 → good | none | 0.0 |

Total: 13 problem IDs across 4 categories.

## Proposed ProblemVector

```python
@dataclass
class ProblemEntry:
    problem_id: str          # e.g. "over_compressed"
    category: str            # "spectral" | "dynamics" | "stereo" | "overall"
    severity: str            # "low" | "medium" | "high"
    confidence: float        # 0.0–1.0 (based on threshold distance)
    weight: float            # MAP weight
    description: str         # human-readable (from current rules)

@dataclass
class ProblemVector:
    problems: list[ProblemEntry]
    diagnosis_loss: float    # 0.0–1.0, computed from weighted problem count
```

## Confidence Formula

`confidence = min(1.0, abs(observed - threshold) / margin)` where margin = 3 dB for spectral, 1.0 for crest, 3.0 for dynamic_range, 0.15 for correlation.

## Validation

Test: run `diagnose()` on `vocal_folk.wav` → zero problems → `ProblemVector(problems=[], diagnosis_loss=0.0)`.

Test: run on a deliberately clipped file → expect `over_compressed` (high severity, high confidence).

## Acceptance Criteria

- [x] All 13 current diagnosis rules mapped to structured problem IDs.
- [x] Four categories defined: spectral, dynamics, stereo, overall.
- [x] ProblemVector schema defined with severity, confidence, weight.
- [x] Confidence formula specified.
- [x] Build NEM task (MHP-866) is the implementation boundary.
