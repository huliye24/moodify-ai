# MHP-060: Validation Dataset — 30+ Audio Samples, 3 Presets, Ground Truth Labels

**Status**: proposed
**Direction**: NEM-MOODIFY-STUDIO-OS-001 / Validate-6 / E (Execution)
**Depends on**: MHP-059 (dev server deployed)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

All 107 tests use synthetic manifest.csv injection. For production validation, we need a real dataset: 30+ audio samples spanning genres, processed through 3 presets, with MRS metrics collected and gate decisions recorded.

The baseline test audio directory has only 3 WAV files (piano, electronic, vocal_folk). We need to expand to 30+ with genre labels for meaningful validation.

## Goal

Assemble a validation dataset:
1. Source 30 audio files covering at least 5 genres (electronic, piano, vocal, rock, ambient)
2. For each sample, register in the input registry
3. Define expected preset coverage: each sample × 3 presets = 90 tasks minimum
4. Create a validation manifest (expected MRS ranges per genre)
5. Create ground truth labels for at least 10 samples (human-listened)

## Non-Goals

- Don't generate synthetic audio (use real files)
- Don't require 30 unique files if fewer are available (document the count)
- Don't label all 30 — 10 ground truth labels are sufficient for validation

## Requirements

### Dataset structure
```text
data/validation/
├── samples/
│   ├── electronic/   (6+ files)
│   ├── piano/        (6+ files)
│   ├── vocal/        (6+ files)
│   ├── rock/         (6+ files)
│   └── ambient/      (6+ files)
├── registry.jsonl
├── ground_truth.jsonl
└── README.md
```

### Ground truth format
```jsonl
{"sample_id": "SMP_XXXX", "genre": "electronic", "human_label": "needs_warmth", "expected_preset": "warm_vocal"}
```

## Acceptance Criteria
- Validation dataset documented with source, count, and genre distribution
- Ground truth labels for at least 10 samples
- Registry JSONL ready for `moodify-runtime register`
- Existing 107 tests still pass (dataset is data, not code)

## Done Means

The validation dataset exists and can be fed into `run_daily` to produce real MRS metrics for MHP-061.
