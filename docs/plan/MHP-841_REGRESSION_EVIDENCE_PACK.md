# MHP-841: Regression Evidence Pack

**Status**: done

## Evidence Summary

**88 tests, all passing** across 4 test suites, covering the complete data loop pipeline from collection through product integration.

## Test Suite Detail

### Collectors (29 tests)
- SummaryCollector: 12 tests — runtime signals, scoring disagreements, craft flags, task detail, fatal error detection, empty inputs
- TidalEventCollector: 6 tests — cycle counting, task aggregation, gate aggregation, phase tracking, missing files, heartbeat
- QueueCollector: 5 tests — status distribution, abandonment risk, oldest pending, empty queue, missing file
- CollectorPipeline: 6 tests — summary-only run, all-sources run, write output, convenience fn, timestamps, JSON serialization

### Recommenders (30 tests)
- ScoreDisagreementRecommender: 7 tests — filter, severity classification, reason format, action length, empty input, loop assignment
- PenaltyPresetRecommender: 5 tests — flag filter, over_dark action, high/medium severity, empty input
- RuntimeReliabilityRecommender: 5 tests — fatal error → high rec, pattern matching, no errors → empty, failures without fatal, human review flag
- OperatorNextMhpWriter: 6 tests — PASS/HOLD decisions, high-severity HOLD, fatal error HOLD, bundle completeness, next-MHP direction, serialization
- RecommendationEngine: 5 tests — all four loops, summary presence, high severity filter, needs review filter, empty tasks
- RecommendationBundle: 2 tests — by_loop filter, empty bundle

### Integration Smoke (11 tests)
- Collector → Recommender pipeline: 3 tests — end-to-end, traceability, empty run
- DataLoopRunner: 6 tests — result production, output files, writeback, all sources, serialization, fatal→HOLD
- Report Formatting: 2 tests — section completeness, metric table

### Product Integration (18 tests)
- LearningDashboard: 6 tests — required cards, decision match, summary counts, serialization, card severity, no fatal → no alert
- CraftLearningFeed: 3 tests — entry count, field completeness, empty recs
- CalibrationReviewFeed: 3 tests — proposal count, task data linkage, empty recs
- ReleaseLearningGate: 6 tests — fatal blocks, clean passes, four checks, to_dict, success rate, low agreement blocks

## Run Command

```bash
python3 -m pytest \
  moodify_runtime/tests/test_collectors.py \
  moodify_runtime/tests/test_recommenders.py \
  moodify_runtime/tests/test_data_loop_integration.py \
  moodify_runtime/tests/test_product_integration.py \
  -v
```

## Regression Policy

These 88 tests must pass before any data loop hotfix or feature change is merged. A CI gate should enforce this in the next E-Chain.
