# MHP-870: Damage Loss Gate

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-BUILD-046 / Build Plan-6B / E2
**Depends on**: MHP-869 (MRS Adapter)

## Implementation

Damage loss is computed in `mrs_adapter.py` via two paths:

### Engine path (mrs_calibrated_v02)
`damage_loss = over_dark_score` (0.0–1.0 from graduated over-dark detector)

### Fallback path (mrs_proxy_v01)
```python
damage_loss = 0.04 * len(warnings)
    + max(0, -dynamic_range_delta - 2.0) * 0.03
    + max(0, -air_delta - 3.0) * 0.025
    + max(0, -crest_delta - 1.5) * 0.025
```
Clamped to [0, 1].

### Gate effect
`damage_loss >= 0.25` triggers `damage_loss_high` risk flag and fails the quality gate.

### Verification
49/49 tests pass. Real audio test shows damage_loss = 0.0 for clean_master preset.
