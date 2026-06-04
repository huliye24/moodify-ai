# MHP-077: Build Calibration Dataset — 50+ Labeled Samples Across 5 Genres

**Status**: proposed
**Direction**: NEM-MOODIFY-MRS-002 / Validate-6 / E1 (Execution)
**Depends on**: MHP-076 (Build-6 complete)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

The calibration infrastructure from Build-6 needs real data. The existing validation dataset (30 MP3s from Validate-6 of the previous NEM) is a starting point, but we need:
- WAV files (MP3 introduces encoding artifacts that confuse MRS measurement)
- Human preference labels (better/worse/no_change)
- Per-genre coverage (10 samples × 5 genres = 50 minimum)
- Before/after processing pairs (each sample processed through at least 1 preset)

## Goal

Assemble a calibration dataset:

1. Source 50+ WAV audio files covering 5 genres (10 each: electronic, piano, vocal, rock, ambient)
2. Process each through the appropriate preset from `configs/mrs_thresholds.yaml`
3. Generate before/after MRS metrics for each pair
4. Label at least 30 pairs with human preference (better/worse/no_change)
5. Store in `data/calibration/mrs_002/` with registry and labels

### Dataset structure
```text
data/calibration/mrs_002/
├── source/               # original WAV files (10 per genre)
│   ├── electronic/
│   ├── piano/
│   ├── vocal/
│   ├── rock/
│   └── ambient/
├── processed/            # after DSP processing
│   └── {sample_id}/{preset}/
├── registry.jsonl        # sample metadata
├── labels.jsonl          # human preference labels
├── metrics.jsonl         # before/after MRS scores
└── README.md
```

### Label format
```jsonl
{"sample_id": "SMP_XXXX", "genre": "electronic", "preset": "clean_master",
 "human_decision": "better", "notes": "clearer highs, no mud",
 "mrs_before": 45.2, "mrs_after": 52.1, "mrs_delta": 6.9}
```

## Acceptance Criteria
- ≥50 WAV samples (≥10 per genre)
- ≥30 human-labeled pairs
- Registry and labels in JSONL format
- Metrics computed for all pairs
- README documents dataset provenance and labeling methodology
