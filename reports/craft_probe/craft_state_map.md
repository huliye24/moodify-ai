# Craft State Map — MHP-143

**Date**: 2026-06-04 | **E-Chain**: ECHAIN-MOODIFY-PRESET-CRAFT-002 | **Phase**: Probe Plan-6A

## Current Preset Surface

| Preset | Category | Source | Proven? |
|--------|----------|--------|---------|
| warm_vocal | warm_reality | DSP chain | ✅ Top performer in NEM-002 calibration run |
| clean_master | dynamic_recovery | DSP chain | ✅ Default, stable |
| wide_space | soft_space | DSP chain | ⚠️ Low MRS deltas on rock/ambient |
| safe_air | anti_fatigue | DSP chain | ⚠️ Never validated on real audio |
| clean_master_safe | anti_fatigue | DSP chain | ❌ Never tested |
| air_preserve_master | soft_space | DSP chain | ❌ Never tested |

## 15 DSP Parameters (from preset_grid.yaml)

| ID | Parameter | Type | Range |
|----|-----------|------|-------|
| P01 | vocal_presence_freq | Hz | 3000 fixed |
| P02 | vocal_presence_gain | dB | 0.5–5.0 |
| P03 | vocal_presence_q | Q | 0.5–0.7 |
| P04 | proximity_low_freq | Hz | 200 fixed |
| P05 | proximity_low_gain | dB | 0.5–5.0 |
| P06 | compression_ratio | ratio | 1.0–4.0 |
| P07 | compression_attack | ms | 5–80 |
| P08 | compression_release | ms | 50–400 |
| P09 | compression_threshold | dB | -30 to -6 |
| P10 | reverb_t60 | s | 0.3–4.0 |
| P11 | reverb_dry_wet | ratio | 0.05–0.45 |
| P12 | reverb_width | ratio | 0.4–1.0 |
| P13 | harmonic_drive | ratio | 0.0–0.20 |
| P14 | high_shelf_freq | Hz | 8000–10000 |
| P15 | high_shelf_gain | dB | -3.0–3.0 |

## Craft Memory System (existing)

| Component | Module | Status |
|-----------|--------|--------|
| Craft record schema | craft_memory.py:writeback_delivery_to_craft_record | ✅ |
| Craft record storage | craft_memory_dir/craft_records.jsonl | ✅ |
| Adoption workflow | 4-status: experimental→candidate→stable→adopted | ✅ |
| Craft memory seed | seed_craft_memory() — auto-generates from manifest | ✅ |
| Craft API | /craft/records | ✅ |
| Writeback from delivery | writeback_delivery_to_craft_record() | ✅ |

## Identified Gaps

| # | Gap | Severity | Impact |
|---|-----|----------|--------|
| 1 | No preset A/B comparison report | P0 | Can't quantify improvement |
| 2 | No preset safety gate | P0 | Can't reject damaging presets |
| 3 | No batch validation across genres | P0 | Presets tested on 1-3 samples only |
| 4 | safe_air never validated on real audio | P1 | Untested preset in production config |
| 5 | No versioning for craft records | P1 | Can't track preset evolution |
| 6 | No search/filter in craft library | P2 | 13 records, manageable but growing |
