# v0.1.0 Preset Calibration

MHP-005-A: before/after calibration tool for v0.1.0 presets.

## Purpose

Run all 3 presets on a batch of audio files and compare metrics before vs after.
Does NOT modify DSP parameters. Only collects measurements.

## Usage

```bash
python scripts/v01_calibrate_presets.py \
  --input-dir moodify-core-package/tests/baseline/test_audio \
  --output-dir calibration_reports/v0.1.0-alpha.1
```

## Outputs

```text
calibration_reports/v0.1.0-alpha.1/
├── summary.json    # machine-readable results
├── summary.md      # human-readable report
└── song_name/
    ├── warm_vocal/
    │   ├── song_warm_vocal.wav
    │   └── song_warm_vocal_report.json
    ├── clean_master/
    │   └── ...
    └── wide_space/
        └── ...
```

## What it measures

Per file × preset:

- Spectrum: sub_bass, bass, low_mid, mid, presence, air (dB)
- Dynamics: peak_db, crest_factor, dynamic_range_db
- Stereo: correlation_lr
- Health: overall_health, issues, strengths

## Design rules

- Does not modify v01 source code
- Does not add new presets
- Does not tune DSP parameters
- Only observes and reports
