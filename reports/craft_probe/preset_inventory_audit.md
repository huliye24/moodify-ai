# Preset Inventory Audit — MHP-144

**Date**: 2026-06-04

## All Known Presets

| # | Preset Name | Category | Tested? | Validated? | Gate Safety | Active in Prod? |
|---|------------|----------|---------|------------|-------------|-----------------|
| 1 | warm_vocal | warm_reality | ✅ 107+ tests | ✅ NEM-002 calibration (61 samples) | ✅ Gate passes | ✅ Default for vocal/piano |
| 2 | clean_master | dynamic_recovery | ✅ | ✅ NEM-002 (default for electronic) | ✅ Gate passes | ✅ Default for electronic |
| 3 | wide_space | soft_space | ✅ | ⚠️ NEM-002 (rock=20% accuracy) | ⚠️ Low accuracy on rock | ✅ Used for rock/ambient |
| 4 | safe_air | anti_fatigue | ❌ 0 real audio tests | ❌ | ❌ Unknown | ❌ |
| 5 | clean_master_safe | anti_fatigue | ❌ | ❌ | ❌ Unknown | ❌ |
| 6 | air_preserve_master | soft_space | ❌ 0 real audio tests | ❌ | ❌ Unknown | ❌ |
| 7 | bypass_control | bypass | ❌ | ❌ | ❌ Unknown | ❌ |

## Gate Accuracy by Preset (from NEM-002)

| Preset | Gate Accuracy | FP Rate | FN Rate | Assessment |
|--------|--------------|---------|---------|------------|
| warm_vocal | 10% (vocal), 11% (piano) | 90% | 0% | High FP — over_dark was broken (fixed in MHP-083) |
| clean_master | 0% (electronic) | 100% | 0% | Same over_dark issue |
| wide_space | 20% (rock) | 80% | 0% | Worst performer |

## Parameter Coverage

4 parameter categories across 15 parameters, but only 4 categories tested. No individual parameter sensitivity analysis exists.
