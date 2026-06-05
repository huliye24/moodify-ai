# MHP-827: Data Loop SOP

**Status**: done
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-SYSTEM-044 / System Plan-6A: Standardization / P1 (Execution)
**Depends on**: MHP-826
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Define the Standard Operating Procedure for nightly data loop execution. This SOP is the single source of truth for running the optimization pipeline.

## SOP: Nightly Data Optimization Loop

### Pre-Run Checklist (Operator, ~2 min)

- [ ] Last night's run completed — `outputs/<run_id>/summary.json` exists
- [ ] Queue is not stalled — `data/tidal_queue.jsonl` has pending tasks
- [ ] Disk has ≥ 10 GB free — `df -h /home/ubuntu/moodify-mainline`
- [ ] DeepSeek API key is available (optional — rule-based fallback works)
- [ ] No active emergency pause — `tidal-state` shows running or idle

### Step 1: Collect Night Metrics (~1 min)

```bash
python3 -m moodify_runtime.cli data-loop run \
  --summary outputs/<run_id>/summary.json \
  --queue data/tidal_queue.jsonl \
  --output-dir reports/data_loop/<run_id>/
```

Outputs:
- `night_metric_record.json` — structured optimization signals
- `recommendation_bundle.json` — all recommendations + operator decision
- `data_loop_report.md` — human-readable summary

### Step 2: Review Recommendations (~5 min)

Open `reports/data_loop/<run_id>/data_loop_report.md`.

Check:
1. Operator decision: PASS, HOLD, or REWORK
2. High-severity recommendations — each must have an owner
3. Items flagged `needs_human_review: true` — operator must sign off
4. Next MHP direction — is it actionable?

### Step 3: Execute or Hold

**If PASS**: apply medium/low recommendations as background tasks. Continue to next night's run.

**If HOLD**: fix the blocking issue (fatal error, high-severity scoring gap, craft flag pattern). Rerun the pipeline after the fix.

**If REWORK**: the pipeline itself may need adjustment. Check collector schema, recommender thresholds, or worker protocol. File an MHP.

### Step 4: Writeback (~1 min, optional)

```bash
python3 -m moodify_runtime.cli data-loop run \
  --summary outputs/<run_id>/summary.json \
  --output-dir reports/data_loop/<run_id>/ \
  --writeback \
  --craft-memory-dir data/moodify_runtime/craft_memory/
```

### Post-Run

- [ ] Craft writeback JSON committed to craft memory
- [ ] Calibration proposals saved for MRS tuning session
- [ ] Next night's queue has ≥ 3 pending tasks
- [ ] Report archived in `reports/data_loop/`

## Acceptance Criteria

- SOP covers all four execution steps. ✅
- Each step has a concrete command or checklist item. ✅
- Operator decision flow is explicit. ✅
- Pre-run and post-run checklists are defined. ✅
