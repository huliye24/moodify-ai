# Moodify Operator Guide — v0.1.0-alpha.4

**For**: internal operators, not public consumers  
**Updated**: 2026-06-04  
**Tests**: 107 passing

## Quick Start

```bash
# Start the API server (do this first)
python3 -m uvicorn moodify_runtime.operator_api:app --host 0.0.0.0 --port 8700

# Open the Console UI
open http://localhost:8700/operator

# Or use the CLI
moodify-runtime --help
```

## Five Core Workflows

### 1. Job Intake

Create an operator job from source audio.

**Console UI**: Queue tab → "Jobs" in sidebar → "New Operator Job" form  
**CLI**:
```bash
moodify-runtime operator-create \
  --source-audio data/night_inputs/song.wav \
  --depth standard_process \
  --project-label "album-name"
```

Processing depths:
| Depth | Presets Used | Use Case |
|-------|-------------|----------|
| `quick_scan` | clean_master only | Fast validation |
| `standard_process` | warm_vocal, clean_master, wide_space | Normal production |
| `deep_process` | all 3 presets | Critical deliveries |
| `studio_process` | all 3 presets | Premium mastering |

### 2. Runtime Processing

Connect a job to the audio processing engine.

**Console UI**: Select job → "Plan Runtime" → "Run"  
**CLI**:
```bash
# Plan (creates queue tasks)
moodify-runtime operator-plan-runtime --job-id JOB_XXXX

# Preview commands
moodify-runtime operator-show-plan --job-id JOB_XXXX

# Execute (dry-run first — default safe)
moodify-runtime operator-run --job-id JOB_XXXX

# Execute for real
moodify-runtime operator-run --job-id JOB_XXXX --live
```

### 3. Gate Review

After processing, each candidate gets a gate decision.

**Console UI**: Select job → view candidates → see scores and gate decisions  
**CLI**:
```bash
moodify-runtime operator-detail --job-id JOB_XXXX
```

Gate decisions:
| Decision | Meaning | Next Action |
|----------|---------|-------------|
| `approve` | All gates passed | Ready for delivery |
| `reprocess` | Below threshold or over_dark | Adjust preset, re-run |
| `reject` | Runtime failed or transient damage | Investigate, fix, re-run |

### 4. Delivery

Select the winning candidate and create a delivery record.

**Console UI**: Select job → click "Deliver" on approved candidate  
**CLI**:
```bash
# Deliver an approved candidate
moodify-runtime operator-deliver \
  --job-id JOB_XXXX \
  --candidate-id CAND_XXXX

# Override a reprocess candidate (requires reason)
moodify-runtime operator-deliver \
  --job-id JOB_XXXX \
  --candidate-id CAND_XXXX \
  --override \
  --notes "Manual approval after second review"

# View delivery
moodify-runtime operator-delivery-get --job-id JOB_XXXX
```

### 5. Calibration

Calibrate MRS thresholds against human listening reviews.

**Console UI**: Calibration tab → create sample set → submit reviews → run audit  
**CLI**:
```bash
# Create sample set
moodify-runtime calibration-set-create --name "alpha-set"

# Submit human review
moodify-runtime calibration-review \
  --set-id CALSET_XXXX \
  --candidate-id CAND_XXXX \
  --human-decision better \
  --gate-decision approve

# Run audit
moodify-runtime calibration-audit --set-id CALSET_XXXX

# Propose threshold change
moodify-runtime calibration-threshold \
  --parameter mrs_score_delta \
  --current-value 0.0 \
  --proposed-value 1.5 \
  --justification "Based on 10 human reviews"
```

## Studio Back Office

Link jobs to commercial entities (clients, projects, orders).

```bash
# Create client
moodify-runtime studio-client-create --name "Studio Name" --contact "email@studio.com"

# Create project
moodify-runtime studio-project-create --client-id CLI_XXXX --name "Album Mastering"

# Create order
moodify-runtime studio-order-create \
  --project-id PRJ_XXXX \
  --client-id CLI_XXXX \
  --description "Master 3 tracks"

# Link job to order
moodify-runtime studio-order-link --order-id ORD_XXXX --job-id JOB_XXXX

# View full context
moodify-runtime studio-order-context --order-id ORD_XXXX
```

## Craft Library

Turn delivered jobs into reusable craft memory.

```bash
# Write back to craft
moodify-runtime craft-writeback \
  --job-id JOB_XXXX \
  --candidate-id CAND_XXXX \
  --adoption-status candidate

# List records
moodify-runtime craft-records
```

## Troubleshooting

### Server won't start
```bash
# Check FastAPI is installed
python3 -c "import fastapi; print(fastapi.__version__)"

# Check port is free
lsof -i :8700
```

### Job stuck in "waiting"
```bash
# Check if queue has tasks
moodify-runtime operator-detail --job-id JOB_XXXX

# If no tasks: run plan-runtime first
moodify-runtime operator-plan-runtime --job-id JOB_XXXX

# If tasks exist but job is waiting: run with --live
moodify-runtime operator-run --job-id JOB_XXXX --live
```

### Report not found
```bash
# Build report manually
moodify-runtime operator-report --job-id JOB_XXXX
```

### Delivery blocked
```bash
# Check gate decision
moodify-runtime operator-detail --job-id JOB_XXXX

# If reprocess/reject: use --override with reason
moodify-runtime operator-deliver --job-id JOB_XXXX --candidate-id CAND_XXXX --override --notes "reason"
```

### API returns 404
- Verify the job ID exists: `moodify-runtime operator-list`
- Verify the server is running: `curl http://localhost:8700/health`
- Check the config path: `echo $MOODIFY_RUNTIME_CONFIG`
