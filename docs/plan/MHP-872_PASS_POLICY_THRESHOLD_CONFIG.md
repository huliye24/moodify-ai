# MHP-872: Pass Policy Threshold Config

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-BUILD-046 / Build Plan-6B / V4
**Depends on**: MHP-869 (MRS Adapter), MHP-860 (Diff Risk Gate)

## Pass Policy (v0.2)

```python
passed = (
    gate_decision == "pass"   # MRS engine gate says pass
    and damage_loss < 0.25    # Aggregate damage below threshold
    and not warnings          # No quality warnings (fallback path only)
)
```

## Thresholds

| Threshold | Value | Rationale |
|-----------|-------|-----------|
| `damage_loss_max` | 0.25 | Allows minor spectral changes; blocks severe damage |
| `peak_warn_db` | -0.1 dBFS | Industry standard headroom |
| `dr_damage_db` | -4.0 dB | Dynamic range reduction tolerance |
| `air_loss_db` | -6.0 dB | Air band reduction before over_dark flag |
| `correlation_min` | 0.05 | Stereo mono-compat minimum |
| `mrs_regression_db` | -1.0 | MRS delta regression tolerance |

## Future: Config File

Thresholds are currently hardcoded. A YAML config (`configs/map_pass_policy.yaml`) is deferred to System NEM for calibration with real multi-night data.
