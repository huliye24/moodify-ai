# AUDIT C — Replay Log

**Task**: DSK-MFY-DAY2-CLOSURE-003  
**Date**: 2026-07-31  
**Status**: COMPLETED (partial — spectrogram failed; see notes)

## Pre-Replay State

| Field | Value |
|---|---|
| Git HEAD | `df3a8a3c8ead4eae0675733169614efe59bf395d` |
| Branch | `codex/mainline-cloud-dev-20260603` |
| VS-001 SHA-256 | `27bea8e034f737d2b96c63a48b20859dae36a3ac1d1db567992bfa46b59b0d27` |
| Git status | 111 lines (dirty working tree) |
| Date/Time | 2026-07-31 09:31:20 UTC+8 |

## Replay Commands

### Step 1: Process

```
Working directory: E:\moodify
Command: moodify v01-process "local_audio_assets/mhp026/source/01_ai_vocal/mhp026_01_ai_vocal__pour_le_moi_pas_encore_ecrit.wav" --preset warm_vocal --output-dir "outputs/deepseek_validation/DSK-MFY-DAY2-CLOSURE-003/process"
Start: 2026-07-31T01:31:33Z
End:   2026-07-31T01:34:09Z
Exit code: 0
Duration: 156 s (original: 164.8 s)
```

Output WAV SHA-256: `475778a3cc97499e088c0736c4ab9496813eba3d7c1d20d6139449bb74eca0cc`
— BYTE-IDENTICAL to original run.

Note: "MRS engine unavailable, using proxy fallback" warning emitted (expected — runtime module not in path for direct CLI invocation).

### Step 2: Inspector (PARTIAL)

```
Working directory: E:\moodify
Command: python scripts/v01_inspector.py --before "..." --after "..." --output-dir "..." --preset warm_vocal --title "..." --write-matched-after
Exit code: 1 (failed)
```

**Failure**: Spectrogram generation via `matplotlib.mlab.specgram` requires a 525 MB contiguous memory allocation for the FFT array (2048 freq bins × 16808 time segments × complex128). This allocation consistently fails on the 8 GB machine under concurrent memory load.

**Partial outputs generated**:
- `waveform_before_after.png` — OK
- `spectrum_overlay.png` — OK
- `spectrum_delta.png` — OK

**Not generated** (script crashes before these steps):
- `spectrogram_before.png`
- `spectrogram_after.png`
- `band_energy_comparison.png`
- `metrics_comparison.json`
- `after_matched.wav`
- `report.md`
- `report.html`

**Workaround**: `after_matched.wav` and `metrics_comparison.json` were generated separately using the identical computational logic as the inspector (mono float32 RMS, same gain formula). This is documented in the reproducibility comparison.

### Step 2b: Manual after_matched.wav generation

```
Method: Inspector-equivalent logic (mono float32, RMS before=-15.72, after=-9.83, gain=-5.89 dB)
Output: outputs/deepseek_validation/DSK-MFY-DAY2-CLOSURE-003/inspector/after_matched.wav
SHA-256: 134000335e88c5b98719702688d3b1dde8f19afcff4808f87bac2c03f6abf0af
```

Byte-level difference from original after_matched.wav: 91 samples differ by exactly 1 PCM_16 LSB (1/32768). This is PCM_16 quantization rounding — the float32→int16 conversion rounds boundary values differently.

### Step 3: Treatment Record

```
Working directory: E:\moodify
Command: python scripts/v01_create_treatment_record.py --before "..." --after "..." --inspector-report "..." --preset warm_vocal --song-id vs001_ai_vocal_20260731_replay --output "..."
Exit code: 0
Duration: <1 s
```

Output: `treatment_record.json` with 15 preset params, 11 deltas, human_feedback=pending.

## Post-Replay Verification

| Check | Result |
|---|---|
| VS-001 source SHA-256 unchanged | PASS |
| Process WAV byte-identical | PASS |
| validation_report.json field-by-field identical | PASS (9/9 fields) |
| after_matched.wav matches within 1 LSB | PASS (91/17M samples differ by 1 LSB) |
| treatment_record.json created | PASS |

## Reproducibility Notes

1. The processing step is fully reproducible — byte-identical output confirmed.
2. The inspector step is reproducible in logic but blocked by a hardware memory limitation (525 MB contiguous allocation).
3. The after_matched.wav differs by PCM_16 quantization rounding only — 1 LSB across 0.0005% of samples.
4. All validation metrics (dynamic_range, MRS, risk_flags, deltas) are identical.
