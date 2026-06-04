# MHP-795: Write Data Loop Runbook

**Status**: ready
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6A: Loop Boundary / P5 (Systemization)
**Depends on**: MHP-794
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Provide a runbook that extracts a usable optimization dataset from last night's run.

## Runbook

```bash
cd /home/ubuntu/moodify-mainline
RUN_ID=data_loop_014_$(date -u +%Y%m%d_%H%M%S)
OUT=reports/echain_moodify_data_loop_014/$RUN_ID
mkdir -p "$OUT"

python3 - <<'PY' > "$OUT/last_night_metric_snapshot.json"
import json
summary = json.load(open("outputs/20260605_000141/summary.json"))
tasks = summary.get("tasks", [])
rows = []
for t in tasks:
    pseudo = t.get("pseudo_delta_mrs")
    open_delta = t.get("delta_mrs_open_v031")
    disagreement = None
    if pseudo is not None and open_delta is not None:
        disagreement = (pseudo >= 0) != (open_delta >= 0)
    rows.append({
        "task_id": t.get("task_id"),
        "sample_id": t.get("sample_id"),
        "preset": t.get("preset"),
        "status": t.get("status"),
        "pseudo_delta_mrs": pseudo,
        "delta_mrs_open_v031": open_delta,
        "score_direction_disagreement": disagreement,
        "mrs_open_flags": t.get("mrs_open_flags"),
        "recommended_loop": (
            "runtime_reliability" if summary.get("fatal_error") else
            "scoring_calibration" if disagreement else
            "craft_preset_selection" if t.get("mrs_open_flags") else
            "operator_report"
        ),
    })
print(json.dumps({
    "source_run": summary.get("run_id"),
    "success": summary.get("success"),
    "failed": summary.get("failed"),
    "fatal_error": summary.get("fatal_error"),
    "tasks": rows,
}, ensure_ascii=False, indent=2))
PY
```

## Expected Output

`reports/echain_moodify_data_loop_014/{RUN_ID}/last_night_metric_snapshot.json`

## Acceptance Criteria

- The snapshot exists.
- Each task has a recommended loop.
- Score-direction disagreement is explicit.
