# P07 Test Results (2026-08-17)

## New tests — moodify/reconstruction_factory

| Suite | Count | Result |
|---|---|---|
| test_learning_record.py | 7 | PASS (deterministic ID, versions, rights defaults, internal-test training blocked, owned training allowed, disallowed status, json) |
| test_outcome.py | 6 | PASS (taxonomy, SOURCE_WINS preserved, missing human never guessed, identity unsafe escalates, subtle/improved, stem/failed) |
| test_factory.py | 7 | PASS (serial, duplicate preserved, failure preserved with code/stage, rights blocked, idempotent across batches, proposals never applied, json serializable) |
| test_agreement.py | 3 | PASS (match counts, disagreement patterns, missing signals) |

Total new: **23 PASS**

## Regression

- Full core suite: **839 passed, 5 skipped, 0 failed** (755s)
- Ruff (reconstruction_factory + tests): clean
- v01 marker: included in full run

## Gate A (synthetic)

- 3 tracks processed serially, 0 failures, 0 rights blocks, 0 duplicates
- Outcomes: IMPROVED 1 / SUBTLE_IMPROVEMENT 1 / SOURCE_WINS 1
- Machine-Human agreement: 3/3 technical top == human top; patterns: SOURCE_WINS
- Evidence: GATE_A_SYNTHETIC.json, RECONSTRUCTION_LEARNING_RECORDS.jsonl, FACTORY_METRICS.json
