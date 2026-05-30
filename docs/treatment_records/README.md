# Moodify Treatment Record

Local processing memory for Moodify v0.1.0.

## What It Is

A Treatment Record captures everything about one audio processing run:

```text
before audio → preset params → after audio → delta → loudness → human feedback
```

It is a local JSON file, not a database, not a cloud data layer, not a training system.
It exists so every processed song leaves a trace that can be reviewed later.

## Usage

```bash
python scripts/v01_create_treatment_record.py \
  --before original.wav \
  --after processed.wav \
  --inspector-report inspector_reports/my_case/metrics_comparison.json \
  --preset warm_vocal \
  --song-id my_song_001 \
  --notes "first pass" \
  --output treatment_records/my_song_warm_vocal.json
```

## Output Structure

Each record contains:

| Section | Content |
|---------|---------|
| `schema_version` | Schema version (0.1.0) |
| `before_features` | Peak, RMS, crest, dynamic range, correlation, 6-band spectrum, spectral features |
| `after_features` | Same as above, measured from processed output |
| `delta_features` | After − before for all metrics |
| `preset_params` | All 15 DSP parameters used |
| `loudness_match` | RMS delta, gain match, warning level, matched file path |
| `human_feedback` | 8-dimension listening checklist (pending until MHP-011) |
| `algorithm_learning` | Placeholder for future adaptive preset system |

## Current Stage

Local JSON files. One file per treatment run.

## Future Stages

- JSONL for batch collection
- SQLite for queryable record index
- Input to adaptive preset recommender

## Design Rules

- Read-only: does not modify audio or presets
- No database dependency
- No cloud dependency
- No ML/AI judgment (human feedback is manually filled)
