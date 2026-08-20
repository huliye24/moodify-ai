# P04 Test Results (2026-08-17)

## New tests — moodify/reconstruction_objective

| Suite | Count | Result |
|---|---|---|
| test_objective.py | 11 | PASS (valid objective, honest bandwidth name, noise unsupported, artistic character no grant, insufficient evidence no grant, low confidence bypass, medium human-review + bounded scope, deterministic, different-source different-id, forbidden changes, budget) |
| test_candidates.py | 7 | PASS (high->ABC ordered, medium->AB only, unsupported->none, low->none, params within budget, reproducible hashes, different-source different plans) |

Total new: **18 PASS**

## Regression

- Full core suite: PENDING (running)
- Ruff: clean

## Golden synthetic case

- clean reference -> 8kHz lowpass + noise(0.02) degradation
- P03: ED-01 Bandwidth Limitation, status POSSIBLE_TECHNICAL_LIMITATION, HIGH
- P04: RO-01 BANDWIDTH_BALANCE objective (high confidence)
- Candidates: A(0.3) B(0.5) C(0.7), params within budget
- ED-02 noise did not fire (below detector threshold) — honest negative
- Evidence: GOLDEN_SYNTHETIC_CASE.json
