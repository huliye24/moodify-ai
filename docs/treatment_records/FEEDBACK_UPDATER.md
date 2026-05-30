# Treatment Record Feedback Updater

MHP-017: Write human listening feedback into Treatment Records.

## What It Is

The Feedback Updater takes your listening evaluation scores and writes them
back into a Treatment Record's `human_feedback` section.

Without this, every record stays `pending` forever.
With this, Moodify accumulates real human judgement alongside before/after metrics.

## Why It Matters

```text
metrics only → knows what changed
metrics + feedback → knows what changed AND whether it was good
```

This is the difference between "processing log" and "experience memory."

## Usage

```bash
# Full feedback update
python scripts/v01_update_treatment_feedback.py \
  --record treatment_records/vocal_folk_warm_vocal.json \
  --volume-matched yes \
  --clarity 4 \
  --warmth 5 \
  --space 3 \
  --harshness-control 4 \
  --plastic-feel-control 4 \
  --artifact-control 5 \
  --target-fit 5 \
  --better-than-before yes \
  --notes "人声更近更暖，但高频略亮"
```

### Partial update (only notes)

```bash
python scripts/v01_update_treatment_feedback.py \
  --record treatment_records/vocal_folk_warm_vocal.json \
  --notes "补充备注"
```

### Dry-run (preview without modifying)

```bash
python scripts/v01_update_treatment_feedback.py \
  --record treatment_records/vocal_folk_warm_vocal.json \
  --clarity 4 --warmth 5 --better-than-before yes \
  --dry-run
```

### Re-aggregate after feedback

```bash
python scripts/v01_aggregate_treatment_records.py
```

## Feedback Fields

| Field | Type | Description |
|-------|------|-------------|
| `volume_matched` | yes/no/uncertain | Was volume matched during A/B? |
| `clarity` | 1-5 | 1=muddy, 5=clear |
| `warmth` | 1-5 | 1=cold/thin, 5=warm/full |
| `space` | 1-5 | 1=flat/crowded, 5=open/deep |
| `harshness_control` | 1-5 | 1=harsh, 5=smooth |
| `plastic_feel_control` | 1-5 | 1=obvious AI/plastic, 5=natural |
| `artifact_control` | 1-5 | 1=obvious artifacts, 5=clean |
| `target_fit` | 1-5 | 1=misses preset goal, 5=achieves goal |
| `better_than_before` | yes/no/uncertain | Final judgement |
| `notes` | text | Free-form listening notes |

## Safety

- **Dry-run first**: always preview with `--dry-run`
- **Auto-backup**: writes `.bak` before modifying
- **Partial update**: unspecified fields are preserved
- **Score validation**: rejects values outside 1-5
