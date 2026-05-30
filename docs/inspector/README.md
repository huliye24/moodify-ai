# Moodify Inspector

MHP-007-A: before/after audio comparison tool.

## Purpose

Compare an original audio file with its processed version.
Generates visualizations and metrics to show exactly what a preset changed.

## Usage

```bash
python scripts/v01_inspector.py \
  --before path/to/original.wav \
  --after path/to/processed.wav \
  --output-dir inspector_reports/my_comparison \
  --preset warm_vocal \
  --title "Vocal Folk — Warm Vocal"
```

Minimum required: `--before`, `--after`, `--output-dir`.

## Outputs

```text
inspector_reports/my_comparison/
├── report.md                     # Human-readable report with metrics + checklist
├── metrics_comparison.json       # Machine-readable before/after/delta
├── waveform_before_after.png     # Waveform overlay
├── spectrum_overlay.png          # Averaged spectrum comparison
├── spectrum_delta.png            # After − Before difference curve
├── spectrogram_before.png        # Time-frequency view (original)
├── spectrogram_after.png         # Time-frequency view (processed)
└── band_energy_comparison.png    # 6-band bar chart
```

## Metrics Computed

- Peak, RMS, crest factor, dynamic range
- L/R correlation, mid/side ratio
- 6-band energy (sub, bass, low-mid, mid, presence, air)
- Spectral centroid, rolloff, flatness
- Delta (after − before) for all metrics

## Design Rules

- Read-only: does not modify audio or preset parameters
- No GUI: generates static PNG + markdown reports
- No new dependencies: uses numpy, matplotlib, moodify.audio_io
