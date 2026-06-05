# MHP-840: Ownership Map

**Status**: done

## Data Loop System Ownership

| Subsystem | Owner | Module Path |
|-----------|-------|-------------|
| AEP Worker Protocol | Codex (architect) | `docs/protocol/AEP_WORKER_PROTOCOL.md` |
| Worker Validator/Selector | Codex (judge) | `scripts/aep_worker_protocol.py` |
| Data Loop Runbook | Codex (architect) | `scripts/data_loop_runbook.py` |
| Per-Loop Extraction | Codex (architect) | `scripts/extract_loop_tasks.py` |
| Two-Cycle Probe | Codex (architect) | `scripts/two_cycle_probe.py` |
| NightMetricRecord Schema | Codex (architect) | `schemas/night_metric_record.schema.json` |
| DeepSeek Worker Schema | Codex (architect) | `schemas/deepseek_worker_output.schema.json` |
| Summary Collector | Runtime | `moodify_runtime/collectors/` |
| Tidal Event Collector | Tidal | `moodify_runtime/collectors/tidal_collector.py` |
| Queue Collector | Runtime | `moodify_runtime/collectors/queue_collector.py` |
| Collector Pipeline | Runtime | `moodify_runtime/collectors/pipeline.py` |
| Score Disagreement Recommender | MRS Scoring | `moodify_runtime/recommenders/score_disagreement.py` |
| Penalty Preset Recommender | Craft | `moodify_runtime/recommenders/penalty_preset.py` |
| Runtime Reliability Recommender | Runtime | `moodify_runtime/recommenders/runtime_reliability.py` |
| Operator Next-MHP Writer | Operator | `moodify_runtime/recommenders/operator_next_mhp.py` |
| Recommendation Engine | Runtime | `moodify_runtime/recommenders/engine.py` |
| Data Loop Runner | Runtime | `moodify_runtime/data_loop_runner.py` |
| Product Integration | Operator | `moodify_runtime/product_integration.py` |
| Data Loop CLI | Runtime | `moodify_runtime/cli.py` |

## Integration Points

| From | To | Contract |
|------|-----|----------|
| Summary Collector | Runner summary.json | `schemas/night_metric_record.schema.json` |
| Queue Collector | Queue JSONL | Task status fields |
| Tidal Collector | Tidal events JSONL | TideRecord shape |
| Score Recommender | MRS Calibration Lab | Calibration proposal JSON |
| Penalty Recommender | Craft Library | Craft memory candidate JSON |
| Runtime Recommender | Runtime Supervisor | Fatal error → fix MHP |
| Operator Writer | Operator Dashboard | LearningDashboard |
| Release Gate | CI/CD Pipeline | LearningGateResult |
