# Command Surface Inventory — MHP-092

**Date**: 2026-06-04

## CLI Surface (moodify_runtime/cli.py)

40+ subcommands, 496 lines.

| Command | Args | Runtime Interaction | Covered by API? |
|---------|------|---------------------|-----------------|
| register | --source, --genre | registry.py | ❌ |
| plan | --presets, --max-new-tasks | queue.py | ✅ via /operator/jobs/{id}/plan-runtime |
| run | --limit, --dry-run, --run-id | runner.py (run_daily) | ✅ via /operator/jobs/{id}/run |
| report | --run-id | report generation | ✅ via /operator/jobs/{id}/report |
| craft | --run-id, --top-k | craft_memory.py | ❌ |
| failures | --run-id | failure.py | ❌ |
| next | — | planner.py | ❌ |
| operator-create | --source-audio, --depth, --project-label | operator_console.py | ✅ POST /operator/jobs |
| operator-list | --status | operator_console.py | ✅ GET /operator/jobs |
| operator-attach-run | --job-id, --run-id, --run-dir | operator_console.py | ✅ POST /operator/jobs/{id}/attach-run |
| operator-run | --job-id, --live | operator_console.py | ✅ POST /operator/jobs/{id}/run |
| operator-report | --job-id | operator_console.py | ✅ POST /operator/jobs/{id}/report |
| operator-show-plan | --job-id | operator_console.py | ❌ |
| operator-deliver | --job-id, --candidate-id | operator_console.py | ✅ POST /operator/jobs/{id}/deliver |

## Missing Runtime Commands (to add in Build NEM)

| Command | Purpose |
|---------|---------|
| runtime-status | Show heartbeat, active tasks, SLO health |
| runtime-pause | Gracefully pause runner |
| runtime-resume | Resume from last checkpoint |
| runtime-supervisor-start | Launch supervised runner daemon |
| runtime-compact | Compact JSONL stores |
| runtime-health | Full health check (disk, memory, SLO) |

## API Surface (moodify_runtime/operator_api.py)

40 routes across 8 prefixes. All contract-tested. The runtime-specific endpoints:

| Route | Method | Purpose |
|-------|--------|---------|
| /health | GET | Liveness check |
| /studio-os/status | GET | System status (jobs, storage health) |
| /operator/compact | POST | JSONL compaction |

Missing: `/runtime/status`, `/runtime/events`, `/runtime/heartbeat`.
