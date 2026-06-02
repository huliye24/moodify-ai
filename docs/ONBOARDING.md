# Onboarding Guide

## Quick Start (5 minutes)

### 1. Clone and Install

```bash
git clone https://github.com/huliye24/moodify-o3is.git
cd moodify-o3is/moodify-core-package
pip install -e .
```

Requirements: Python 3.10+, pip.

### 2. Verify Installation

```bash
moodify presets
```

Expected output: list of 3 presets (warm_vocal, clean_master, wide_space).

### 3. Analyze an Audio File

```bash
moodify analyze tests/baseline/test_audio/piano.wav
```

Expected output: spectrum metrics + PNG chart in `outputs/`.

### 4. Process an Audio File

```bash
moodify process tests/baseline/test_audio/piano.wav --preset warm_vocal
```

Expected output: `outputs/piano_warm_vocal.wav` + diagnosis report.

### 5. Run Tests

```bash
pytest -m v01      # v01 mainline tests
pytest              # full test suite
```

## Environment Variables

Copy and customize:

```bash
cp .env.example .env
```

Key variables:
- `MOODIFY_ROOT` - Project root directory (default: auto-detect via .git)
- `MOODIFY_OUTPUT` - Output directory (default: <root>/outputs)
- `MOODIFY_TEST_AUDIO` - Test audio directory
- `DEEPSEEK_API_KEY` - DeepSeek API key (optional, for legacy RAG features)

## Project Structure

```
moodify-o3is/
  moodify-core-package/
    src/moodify/          # Main Python package
      v01_*.py            # v01 product mainline
      bands.py            # Unified band definitions
      config.py           # Central configuration
      diagnosis/          # Legacy diagnosis engine
      orchestration/      # Legacy workflow engine
      processing/         # DSP chain
    tests/
      baseline/test_audio/  # Test audio files
  scripts/                # Utility scripts
  docs/                   # Documentation
  treatment_records/      # Human feedback records
  outputs/                # Generated audio (gitignored)
```

## Common Tasks

### Run the API server

```bash
moodify serve --port 8000
```

### Legacy system (research only)

```bash
moodify legacy-analyze song.wav
moodify legacy-process song.wav gentle_awakening
```

### Run treatment inspector

```bash
python scripts/v01_inspector.py
```

## Troubleshooting

- **Import errors**: Make sure you ran `pip install -e .` from `moodify-core-package/`
- **pedalboard errors**: `pip install pedalboard` (may need libsndfile on Linux)
- **Matplotlib missing**: `pip install matplotlib` (only needed for spectrum PNG)
