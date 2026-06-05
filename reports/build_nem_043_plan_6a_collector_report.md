# Build NEM-043 — Build Plan-6A: Data Collectors Report

**NEM**: NEM-MOODIFY-DATA-LOOP-BUILD-043
**E-Chain**: ECHAIN-MOODIFY-DATA-LOOP-014
**Date**: 2026-06-05

## Completed MHPs

| MHP | Title | Status |
|-----|-------|--------|
| 809 | Define NightMetricRecord Schema | ✅ `schemas/night_metric_record.schema.json` |
| 810 | Implement Summary Collector | ✅ `moodify_runtime/collectors/summary_collector.py` |
| 811 | Implement Tidal Event Collector | ✅ `moodify_runtime/collectors/tidal_collector.py` |
| 812 | Implement Queue Collector | ✅ `moodify_runtime/collectors/queue_collector.py` |
| 813 | Collector Unit Tests | ✅ 29 tests, all green |
| 814 | Collector Build Report | ✅ this file |

## Architecture

```
moodify_runtime/collectors/
├── __init__.py              # Public API: SummaryCollector, TidalEventCollector, QueueCollector, CollectorPipeline, collect_night_metrics
├── summary_collector.py     # RuntimeSignal, ScoringSignal, CraftSignal, TaskDetail + SummaryCollector
├── tidal_collector.py       # TidalSignal + TidalEventCollector
├── queue_collector.py       # QueueSignal + QueueCollector
└── pipeline.py              # CollectorPipeline orchestrator + collect_night_metrics convenience fn
```

### Data Flow

```
summary.json  ──→ SummaryCollector ──→ RuntimeSignal + ScoringSignal + CraftSignal + [TaskDetail]
queue.jsonl   ──→ QueueCollector    ──→ QueueSignal
tidal_*.jsonl ──→ TidalEventCollector → TidalSignal
                        ↓
              CollectorPipeline.run() → NightMetricRecord (JSON)
```

### Signal Types

| Signal | Source | Fields |
|--------|--------|--------|
| RuntimeSignal | summary.json | success, failed, total_selected, fatal_error, missing_artifacts |
| ScoringSignal | summary.json tasks | task_count, disagreement_count, agreement_rate, disagreeing_presets |
| CraftSignal | summary.json tasks | flagged_count, flag_rate, flag_types, preset_delta_stats |
| QueueSignal | queue.jsonl | total_tasks, pending/claimed/done/failed/abandoned, abandonment_risk |
| TidalSignal | tidal_events.jsonl | cycle_count, events_since_last, aggregate task/gate counts |

## Delivery

- Schema: `schemas/night_metric_record.schema.json`
- Package: `moodify_runtime/collectors/` (5 files)
- Tests: `moodify_runtime/tests/test_collectors.py` (29 tests)

## Next

Build Plan-6B: Recommendation Engine (MHP-815 → MHP-820)
