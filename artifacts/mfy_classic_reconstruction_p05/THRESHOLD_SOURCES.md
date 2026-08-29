# MFY-CR-P05 — Threshold Sources

All budgets are **PROVISIONAL** (per 01_TASK.md §11) with explicit sources.
No threshold was invented without a stated basis; none is claimed calibrated.

| Budget | Value | Class | Source |
|---|---|---|---|
| IG-01 mid_energy_ratio abs | 0.05 | PROVISIONAL | synthetic tilt fixtures (over_bright ladder) |
| IG-01 presence_2000_5000_hz abs | 0.03 | PROVISIONAL | same |
| IG-01 core_mid_500_2000_hz abs | 0.05 | PROVISIONAL | same |
| IG-01 spectral_centroid_hz abs | 300 Hz | PROVISIONAL | balanced fixture stayed below; over_bright exceeded |
| IG-02 loudness_range_lu | -4 LU | PROVISIONAL | over_compressed fixture (tanh squash) collapsed LRA/crest/PLR |
| IG-02 crest_factor_db | -3 dB | PROVISIONAL | same |
| IG-02 plr_db | -3 dB | PROVISIONAL | same |
| IG-04 stereo_width_proxy | +0.25 | PROVISIONAL | over_wide fixture (side x2.5) far exceeded |
| IG-04 side_to_mid_db | +4 dB | PROVISIONAL | same |
| IG-04 mono guard | source corr >= 0.999 → cand corr <= 0.95 | PROVISIONAL | mono fold-down vs widened variants |
| IG-05 sub_20_60_hz | +0.03 | PROVISIONAL | over_bass fixture (low shelf) exceeded 3x |
| IG-05 bass_60_120_hz | +0.04 | PROVISIONAL | same |
| IG-06 integrated_lufs | 3.0 LU | PROVISIONAL | over_loud fixture (+5.5 LU) far exceeded; balanced (+1.1) passed |
| IG-06 caution_lufs | 1.5 LU | PROVISIONAL | balanced (+1.1) passed; +2.0 escalates |
| IG-06 new clipping min ratio | 5e-5 | PROVISIONAL | hard physical guard (any new clipping is suspicious) |

## Calibration plan (P06+)

1. P06 golden reconstruction candidate set (source + A/B/C);
2. human listening records (pairwise, SAME/SLIGHT_DRIFT/CLEAR_DRIFT/UNSURE);
3. data factory historical evidence (existing cases);
4. reclassify budgets CALIBRATED vs EXPERIMENTAL.
