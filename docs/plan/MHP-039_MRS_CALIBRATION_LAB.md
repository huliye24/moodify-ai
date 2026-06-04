# MHP-039: MRS Calibration Lab

Status: proposed
Direction: quality standard and calibration
Depends on: MHP-038 Cloud GPU Scheduler

## Context

MRS is useful only if it keeps being calibrated against real samples, failure cases, and human review. MHP-039 makes calibration a formal lab workflow.

## Goal

Create a calibration workflow for MRS thresholds, flags, and gate decisions.

## Non-Goals

- Do not claim MRS is final truth.
- Do not replace human review.
- Do not optimize only for higher scores.

## Product Requirements

Calibration Lab tracks:

- sample sets
- before/after pairs
- human review notes
- gate false positives
- gate false negatives
- over-dark cases
- transient damage cases
- loudness penalty cases
- threshold proposals

## Engineering Requirements

- Add calibration records:

```text
CalibrationSampleSet
CalibrationReview
GateAudit
ThresholdProposal
MRSVersion
```

- Add tooling:

```text
moodify-runtime mrs-calibration-run
moodify-runtime mrs-gate-audit
```

- Add reports:

```text
reports/mrs_calibration/{calibration_id}/summary.md
```

## Acceptance Criteria

- Calibration can compare gate decisions against human review.
- Threshold proposals are written as reviewable artifacts.
- MRS version and gate rules are recorded.
- Reports identify known failure classes.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_mrs_calibration_lab.py -q
```

## Done Means

Moodify quality gates become calibratable industrial standards.
