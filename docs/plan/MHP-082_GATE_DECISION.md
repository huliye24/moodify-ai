# MHP-082: Gate Decision — ADOPT / HOLD / REBUILD for MRS Scoring

**Status**: proposed
**Direction**: NEM-MOODIFY-MRS-002 / Validate-6 / N1 (Next Entry)
**Depends on**: MHP-081 (calibration report complete)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

The NEM-18 protocol requires an explicit gate decision at the end of Validate-6. MHP-082 reads the calibration report (MHP-081) and the gate accuracy analysis (MHP-080) and makes the call: is the MRS scoring system ready for production?

## Decision Options

| Decision | Meaning | Next Action |
|----------|---------|-------------|
| ADOPT | MRS scoring production-ready | Enter Harden-6 immediately |
| HOLD | Good but needs threshold tuning | Enter Harden-6 with specific fix list |
| REBUILD | Fundamental MRS approach wrong | Return to Build-6 with revised approach |
| FORK | Split approach needed | Create separate genre-specific vs unified MRS tracks |

## Process

1. Read `reports/nem_mrs_002/calibration_report.md`
2. Read `reports/nem_mrs_002/gate_accuracy/summary.md`
3. Check gate criteria from NEM-MOODIFY-MRS-002 §7
4. Make decision with explicit rationale citing metrics
5. Write decision to `reports/nem_mrs_002/gate_decision.md`
6. Update NEM-MOODIFY-MRS-002 §8

## Key Decision Factors

- Is gate accuracy ≥85% overall?
- Is any genre below 70% accuracy?
- Does calibrated pseudo-MRS outperform the original?
- Are the graduated over_dark levels (none/mild/severe) well-separated in practice?
- Can an operator interpret and act on gate decisions?

## Acceptance Criteria
- Gate decision documented with rationale
- Decision cites specific metrics from MHP-079/080/081
- If HOLD: specific conditions for re-evaluation stated
- NEM master document updated
