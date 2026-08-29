# Golden Case Regression Baseline

## Frozen Identity

- golden_case_id:
- source hash:
- track_id:

## Production Baseline

- pipeline version:
- profile policy:
- final render object:
- production fingerprint:
- verification status:

## System Invariants

Future runs must preserve:

- provenance
- legal state transitions
- no orphan critical object
- correct READY semantics
- secure delivery
- Android PLAY

## Audio Regression Guards

Define tolerances, not necessarily byte identity:

- duration:
- channel count:
- decode:
- clipping:
- loudness:
- target metrics:
- artifact guard:

## Listening Baseline

- verdict:
- major notes:
- known trade-offs:

## Rule

A future model/tool upgrade may legitimately change final bytes.
Regression means unexpected loss of correctness, evidence, safety or agreed audio quality—not merely byte inequality.
