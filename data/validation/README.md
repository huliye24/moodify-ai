# Validation Dataset — Moodify Studio OS Alpha

**Version**: v0.1
**Date**: 2026-06-04
**Protocol**: NEM-18 / Validate-6 / E2 (Execution)

## Overview

30 audio samples across 5 genres for production validation of Moodify Studio OS Alpha.

## Genre Distribution

| Genre | Count | Format | Expected Preset |
|-------|-------|--------|-----------------|
| electronic | 6 | MP3 | clean_master |
| piano | 6 | MP3 | warm_vocal |
| vocal | 9 | MP3 | warm_vocal |
| rock | 7 | MP3 | wide_space |
| ambient | 2 | MP3 | wide_space |
| **Total** | **30** | | |

## Ground Truth

10 samples have human-listened ground truth labels in `ground_truth.jsonl`.

## Preset Coverage

Each sample × 3 presets (warm_vocal, clean_master, wide_space) = 90 tasks minimum.

## Usage

```bash
# Register samples
python3 -m moodify_runtime.cli register --input-dir data/validation/samples

# Run validation
python3 scripts/run_validation.py --dataset data/validation --presets warm_vocal,clean_master,wide_space

# Collect metrics
python3 scripts/collect_validation_metrics.py --run-dir outputs/nem_validate_001
```

## Source

Files sourced from `/home/ubuntu/07Music/albums/`.
WAV conversion handled at processing time by the DSP pipeline.
