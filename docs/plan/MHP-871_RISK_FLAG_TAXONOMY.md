# MHP-871: Risk Flag Taxonomy

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-BUILD-046 / Build Plan-6B / V3
**Depends on**: MHP-853 (Diagnosis Taxonomy), MHP-869 (MRS Adapter)

## 5 Risk Flags (Implemented)

| Flag | Trigger | Severity |
|------|---------|----------|
| `peak_risk` | Output peak within 0.1 dB of 0 dBFS | High |
| `over_dark` | Air-band energy reduced > 6 dB OR over-dark level mild/severe | Medium |
| `dynamic_damage` | Dynamic range reduced > 4 dB OR over-dark level severe | High |
| `mrs_regression` | MRS score decreased after processing | High |
| `damage_loss_high` | Aggregate damage loss >= 0.25 | High |

## Implementation

- Engine path: `_map_engine_risk()` maps MRSScoreResult → flags
- Fallback path: `_risk_flags_inline()` computes from deltas
- Both paths produce the same 5-flag taxonomy
- All flags validated by the enum constraint in `map_chain_report.schema.json`
