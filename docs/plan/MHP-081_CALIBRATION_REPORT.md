# MHP-081: Calibration Report — Per-Genre Metrics and Recommendations

**Status**: proposed
**Direction**: NEM-MOODIFY-MRS-002 / Validate-6 / S1 (Systemization)
**Depends on**: MHP-080 (gate accuracy analyzed)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

Validate-6 has produced:
- MRS comparison data (pseudo vs calibrated vs MRS Open)
- Gate accuracy analysis (per-genre, FP/FN rates)
- Threshold sensitivity curves
- Over-dark contribution breakdown

This data must be synthesized into a decision-support document for the Gate Decision (MHP-082).

## Goal

Produce `reports/nem_mrs_002/calibration_report.md`:

1. **Executive summary**: is the MRS scoring system ready for production adoption?
2. **Dataset summary**: sample count, genre distribution, label coverage
3. **MRS variant comparison**: which metric best predicts human preference?
4. **Gate accuracy**: overall and per-genre agreement rates
5. **Threshold recommendations**: proposed values for each genre based on sensitivity analysis
6. **Over-dark assessment**: is the graduated detector working? Any systematic biases?
7. **Limitations**: what can't we conclude from this dataset?
8. **Harden-6 priorities**: what must be fixed/tuned before production

## Acceptance Criteria
- Calibration report with all 8 sections
- Every recommendation cites specific metrics
- Limitations section is honest about dataset size and label quality
- Report is readable by an audio engineer who didn't run the experiment
