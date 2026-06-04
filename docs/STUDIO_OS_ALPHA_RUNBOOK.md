# Moodify Studio OS Alpha — Runbook

**MHP-040** | **Version:** v0.1.0-alpha  | **Date:** 2026-06-04

## Quick Start

```bash
# 1. Start the Operator API server
python3 -m uvicorn moodify_runtime.operator_api:app --host 0.0.0.0 --port 8700

# 2. Open the Operator Console
open http://localhost:8700/operator

# 3. Run the end-to-end integration test
python3 -m pytest moodify_runtime/tests/test_studio_os_alpha.py -v
```

## Full Pipeline

```text
Client / Project / Order
  → Operator Job
  → Runtime / Scheduler
  → Candidate Versions
  → MRS Gate
  → Report Bundle
  → Delivery Record
  → Craft Library Writeback
  → Calibration Feedback
```

## CLI Quick Reference

### Operator Jobs (MHP-031)
```bash
moodify-runtime operator-create --source-audio <path> --depth standard_process
moodify-runtime operator-list
moodify-runtime operator-attach-run --job-id <id> --run-id <run>
moodify-runtime operator-detail --job-id <id>
```

### Job Runner (MHP-032)
```bash
moodify-runtime operator-plan-runtime --job-id <id>
moodify-runtime operator-show-plan --job-id <id>
moodify-runtime operator-run --job-id <id> [--dry-run]
```

### Reports (MHP-033)
```bash
moodify-runtime operator-report --job-id <id>
```

### Delivery (MHP-034)
```bash
moodify-runtime operator-deliver --job-id <id> --candidate-id <cid>
moodify-runtime operator-delivery-get --job-id <id>
moodify-runtime operator-delivery-list
```

### Studio (MHP-036)
```bash
moodify-runtime studio-client-create --name "Studio Name"
moodify-runtime studio-project-create --client-id <id> --name "Project"
moodify-runtime studio-order-create --project-id <id> --client-id <id>
moodify-runtime studio-order-link --order-id <id> --job-id <id>
moodify-runtime studio-order-context --order-id <id>
moodify-runtime studio-note-create --target-type order --target-id <id> --content "Note"
```

## API Endpoints

| Method | Path | Module |
|--------|------|--------|
| GET | /health | System |
| GET | /studio-os/status | System |
| POST | /operator/jobs | MHP-031 |
| GET | /operator/jobs | MHP-031 |
| GET | /operator/jobs/{id} | MHP-031 |
| POST | /operator/jobs/{id}/plan-runtime | MHP-032 |
| POST | /operator/jobs/{id}/run | MHP-032 |
| POST | /operator/jobs/{id}/attach-run | MHP-031 |
| POST | /operator/jobs/{id}/report | MHP-033 |
| GET | /operator/jobs/{id}/report | MHP-033 |
| POST | /operator/jobs/{id}/deliver | MHP-034 |
| GET | /operator/jobs/{id}/delivery | MHP-034 |
| GET | /operator/deliveries | MHP-034 |
| GET | /operator | Console UI |
| GET | /scheduler/runs | MHP-038 |
| GET | /craft/records | MHP-037 |

## Test Results

```text
38 tests passed
  - 13 operator_console (jobs, gates, delivery)
  -  7 operator_job_runner (plan, run, show-plan)
  -  4 operator_report_bundle (bundle generation)
  -  1 studio_os_alpha (end-to-end integration)
  -  4 command_safety
  -  3 mt001_gate3_config
  -  2 mt001_smoke_config
  -  2 mt002_mrs_score_manifest
  -  2 mt002_validate_mrs_matrix
```

## What Passes

- Client / Project / Order / StaffNote CRUD via JSONL
- Operator Job creation, listing, detail, and status lifecycle
- Runtime plan/run/show-plan (dry-run path tested)
- Gate decision engine (approve/reprocess/reject/override)
- Report bundle generation (MD + JSON + JSONL + CSV)
- Delivery records with validation and override flow
- Craft library writeback from delivered candidates
- Cloud scheduler (request → lease → run → cost)
- MRS calibration lab (sample sets, reviews, audits, thresholds)
- End-to-end pipeline integration test

## What Remains Manual

- Actual audio processing (tested via manifest.csv simulation)
- Human listening review workflow
- Cloud node provisioning
- Multi-tenant security
- External storage uploads

## Clean Checkout Demo

```bash
git clone <repo> && cd moodify-mainline
python3 -m pip install -e moodify-core-package
python3 -m pip install fastapi uvicorn pytest
python3 -m pytest moodify_runtime/tests/ -v
```

## Direction

> Moodify is not a button. Moodify is a machine.

The Studio OS alpha proves the full pipeline can run end-to-end. Every module
has durable storage, CLI access, and automated test coverage. Heavy generated
assets remain outside git.
