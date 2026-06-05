# Moodify MAP-Chain Operator Runbook v0.2

**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015
**MHP**: MHP-887

## Quick Start

```bash
# Process one track with automatic preset selection
python3 -m moodify.cli v01-process vocals.wav --preset auto --output-dir outputs/

# Process with a specific preset
python3 -m moodify.cli v01-process piano.wav --preset clean_master --output-dir outputs/
```

## Preset Guide

| Preset | Best For | What It Does |
|--------|----------|-------------|
| `clean_master` | Piano, acoustic, orchestral | Gentle loudness normalization, transparent dynamics |
| `warm_vocal` | Vocals, folk, singer-songwriter | Adds body and warmth to mid-range |
| `wide_space` | Mono recordings, podcasts | Adds stereo width and spaciousness |
| `auto` | Any | Selects best preset based on audio analysis |

## Reading Quality Results

### Quality Gate: PASS
No action needed. The processing improved or maintained audio quality.

### Quality Gate: REVIEW
Check `validation_report.json` for warnings. Common issues:
- "Output peak too close to 0 dBFS" — reduce input gain
- "Dynamic range reduced > 4 dB" — try a gentler preset
- "Air-band energy removed" — processing may have darkened the track
- "mrs_delta_below_threshold" — MRS score didn't improve enough

### Quality Gate: FAILED
Investigate `damage_loss` and `risk_flags`. If damage_loss > 0.25, the processing likely degraded the audio.

## Delivery Package

Each run produces 10 files:
```
output_dir/
  track_clean_master.wav              ← processed audio
  track_clean_master_report.json       ← full report (MAP schema)
  track_clean_master_report.pdf        ← visual report (charts + manifest)
  track_before_spectrum.png             ← spectrum before processing
  track_clean_master_after_spectrum.png ← spectrum after processing
  manifest.json                        ← artifact inventory with SHA256
  metadata.json                        ← git hash, Python version, platform
  environment.txt                      ← dependency versions
  validation_report.json               ← standalone quality gate
  MAP_CHAIN_VERSION                    ← schema version identifier
```

## MRS Version Field

The `validation_result.mrs_version` tells you which scoring engine was used:
- `mrs_calibrated_v02` — full MRS engine (preferred)
- `mrs_proxy_v01` — inline proxy (backup)

If you see `mrs_proxy_v01`, the calibrated MRS engine wasn't available at runtime.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| CLI fails immediately | Missing input file | Check the file path |
| "Unknown preset" error | Typo in preset name | Use: clean_master, warm_vocal, wide_space, or auto |
| All quality gates review | MRS engine unavailable | Check `validation_report.json` mrs_version |
| Missing PDF report | matplotlib not installed | pip install matplotlib |
| Empty delivery artifacts | Permission error in output dir | Check disk space and write permissions |
