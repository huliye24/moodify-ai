# MHP-080: Gate Accuracy Analysis — False Positive/Negative Rates Per Genre

**Status**: proposed
**Direction**: NEM-MOODIFY-MRS-002 / Validate-6 / V2 (Validation)
**Depends on**: MHP-079 (MRS comparison complete)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

The gate system (`decide_candidate_gate()`) now has genre-specific thresholds and graduated over_dark. But we don't know its accuracy against human judgment. We have 30+ human-labeled pairs from MHP-077 and automated gate decisions from MHP-078. Now we measure how often the gate agrees with humans.

## Goal

Run `run_gate_audit()` from `mrs_calibration.py` on the calibration run output, extended with:

1. **Per-genre accuracy**: gate agreement rate broken down by genre
2. **False positive analysis**: cases where gate rejected but human says "better" — what MRS scores did these have?
3. **False negative analysis**: cases where gate approved but human says "worse" — what did the gate miss?
4. **Threshold sensitivity**: how would accuracy change if we shifted each threshold ±10%, ±20%?
5. **Over-dark contribution**: what % of gate decisions were driven by over_dark vs MRS delta?

### Output
```text
reports/nem_mrs_002/gate_accuracy/
├── summary.md            # executive summary with accuracy per genre
├── false_positives.jsonl # detailed FP cases
├── false_negatives.jsonl # detailed FN cases
├── threshold_sensitivity.csv  # accuracy at different threshold values
└── confusion_matrix.json # approve/reprocess/reject vs human better/worse/no_change
```

## Acceptance Criteria
- GateAudit run against 30+ labeled pairs
- Per-genre accuracy ≥85% target (or documented gap with explanation)
- FP and FN cases analyzed with specific MRS scores
- Threshold sensitivity analysis shows which thresholds are most impactful
- Over-dark contribution quantified
