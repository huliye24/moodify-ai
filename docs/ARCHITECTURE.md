# Moodify Architecture — v0.2.0-alpha (Industrial Runtime Mainline)

**Updated**: 2026-06-04  |  **719 passing tests**  |  **runtime-first industrial system**  |  **48 FastAPI routes**

## Overview

Moodify has evolved from a two-mainline audio processor into an **integrated industrial operator system**. The `moodify_runtime/` package now controls the full production pipeline: intake → processing → scoring → gating → reporting → delivery → craft memory.

Primary entry points:
- **CLI** (`cli.py`) — 40+ subcommands for operator workflow
- **API** (`operator_api.py`) — FastAPI server with 48 routes, serving the Operator Console UI

## Module Dependency Graph

```
cli.py
├── config.py (zero deps — foundation)
├── operator_console.py      ← core domain logic
│   ├── config.py
│   ├── utils.py             ← file I/O, hashing, subprocess
│   ├── registry.py          ← audio discovery + registration
│   ├── queue.py             ← task queue management
│   └── runner.py            ← run_daily engine
│       ├── metrics.py       ← MRS scoring
│       └── utils.py
├── studio.py                ← commercial layer
│   ├── config.py
│   ├── utils.py
│   └── operator_console.py  ← for job linking
├── scheduler.py             ← cloud capacity
│   ├── config.py
│   └── utils.py
├── mrs_calibration.py       ← quality lab
│   ├── config.py
│   └── utils.py
├── craft_memory.py          ← industrial memory
│   ├── config.py
│   ├── utils.py
│   └── operator_console.py
├── report.py                ← daily reports
├── failure.py               ← failure analysis
└── planner.py               ← experiment suggestions

operator_api.py (FastAPI)
├── config.py
├── operator_console.py
├── studio.py
├── scheduler.py
├── mrs_calibration.py
└── craft_memory.py
```

## Data Flow

```text
Sample Audio
  → Registry (stable_sample_id, JSONL)
  → Queue (plan_queue, presets × samples)
  → Runner (run_daily, subprocess, metrics)
  → Manifest (CSV: task_id, scores, flags)
  → Operator Job (create_operator_job)
  → Job Detail (attach_run_report_to_job, gate decisions)
  → Report Bundle (summary.md, candidate_versions.jsonl, gate_decisions.jsonl)
  → Delivery Record (create_delivery_record, operator approval)
  → Craft Library (writeback_delivery_to_craft_record, adoption status)
  → Calibration Lab (reviews, audits, threshold proposals)
```

## Subsystem Map

| Subsystem | Modules | MHP | Status |
|-----------|---------|-----|--------|
| Runtime Core | registry, queue, runner, metrics, report | pre-031 | stable |
| Operator Console | operator_console, operator_api, operator_console.html | 031-035 | alpha |
| Studio Back Office | studio | 036 | alpha |
| Craft Library | craft_memory | 037 | alpha |
| Cloud Scheduler | scheduler | 038 | alpha |
| MRS Calibration | mrs_calibration | 039 | alpha |
| Integration | test_studio_os_alpha | 040 | alpha |

## API Route Table

The current application exposes 48 FastAPI routes including OpenAPI/docs routes. The table below lists the operator-facing surface and may lag newly added internal endpoints; verify exact route count with:

```bash
python3 - <<'PY'
from moodify_runtime.operator_api import app
print(len(app.routes))
PY
```

### System
| Method | Path | Handler |
|--------|------|---------|
| GET | /health | System health |
| GET | /studio-os/status | Dashboard summary |
| GET | / | Console HTML |
| GET | /operator | Console HTML |

### Operator Jobs
| Method | Path | Module |
|--------|------|--------|
| POST | /operator/jobs | Create |
| GET | /operator/jobs | List |
| GET | /operator/jobs/{id} | Detail |
| POST | /operator/jobs/{id}/plan-runtime | Plan |
| POST | /operator/jobs/{id}/run | Execute |
| POST | /operator/jobs/{id}/attach-run | Attach evidence |
| POST | /operator/jobs/{id}/report | Build report |
| GET | /operator/jobs/{id}/report | Get report |
| POST | /operator/jobs/{id}/deliver | Deliver |
| GET | /operator/jobs/{id}/delivery | Get delivery |
| POST | /operator/jobs/{id}/writeback-craft | Craft writeback |
| GET | /operator/deliveries | List deliveries |

### Studio
| Method | Path |
|--------|------|
| POST/GET | /studio/clients |
| POST/GET | /studio/projects |
| POST/GET | /studio/orders |
| POST | /studio/orders/{id}/link-job |
| GET | /studio/orders/{id}/context |
| POST/GET | /studio/notes |

### Scheduler
| Method | Path |
|--------|------|
| POST/GET | /scheduler/requests |
| POST | /scheduler/leases/{id} |
| POST/GET | /scheduler/runs |
| GET | /scheduler/costs |

### Calibration
| Method | Path |
|--------|------|
| POST/GET | /calibration/sample-sets |
| POST/GET | /calibration/reviews |
| POST | /calibration/audits/{id} |
| GET | /calibration/audits |
| POST/GET | /calibration/thresholds |

### Craft
| Method | Path |
|--------|------|
| GET | /craft/records |

## Storage Layout

```text
data/moodify_runtime/
├── operator_jobs.jsonl         — Operator Job records
├── operator_job_details/       — Per-job detail JSON
├── operator_deliveries.jsonl   — Delivery records
├── studio/
│   ├── clients.jsonl
│   ├── projects.jsonl
│   ├── orders.jsonl
│   └── staff_notes.jsonl
├── scheduler/
│   ├── requests.jsonl
│   ├── leases.jsonl
│   ├── runs.jsonl
│   └── costs.jsonl
├── calibration/
│   ├── sample_sets.jsonl
│   ├── reviews.jsonl
│   ├── audits.jsonl
│   └── thresholds.jsonl
└── craft_memory/
    └── craft_records.jsonl

reports/
├── operator_runs/{job_id}/    — Report bundles (summary.md, *.jsonl, manifest.csv)
└── daily_runs/                  — Daily run reports
```

## Key Design Decisions

1. **JSONL storage**: All persistent records use JSONL. Human-auditable, append-only by default, easy to migrate later.
2. **Frozen dataclasses**: All domain models are `@dataclass(frozen=True)`. Immutable by construction.
3. **Multiplicative gate model**: `L_code = R × S × M × E`. One weak dimension drags down the whole.
4. **Dry-run by default**: `run_operator_job` defaults to `dry_run=True`. The `--live` flag is explicit.
5. **Contract-tested**: API response shapes are codified in `test_api_contract.py` to prevent Console UI divergence.
