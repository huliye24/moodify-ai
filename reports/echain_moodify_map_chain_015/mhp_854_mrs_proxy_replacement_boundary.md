# MHP-854: MRS Proxy Replacement Boundary — Completion Report

**Generated**: 2026-06-05
**Status**: done
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6B

## Key Finding

Two parallel MRS paths exist:
1. `v01_pipeline._mrs_proxy()` — inline proxy, v01 only
2. `mrs_engine.score_audio()` — full engine with pseudo + MRS Open v0.3.1 + over-dark + gate

The replacement boundary is a thin adapter (`mrs_adapter.py`) that bridges them. The engine doesn't change; only the v01 pipeline connects to it.

## Boundary: Adapter Pattern

```
v01_pipeline._quality_gate()
    │
    ├── REMOVE: _mrs_proxy(metrics)
    │
    └── ADD: mrs_adapter.score_for_quality_gate(before, after, genre)
            │
            └── mrs_engine.score_audio(before, after, genre, ...)
                    ├── pseudo_mrs()              [unchanged]
                    ├── compute_mrs_open_v031()   [unchanged]
                    ├── detect_over_dark()        [unchanged]
                    └── decide_candidate_gate()   [unchanged]
```

## Change Inventory

| What | Action | Impact |
|------|--------|--------|
| `_mrs_proxy()` in v01_pipeline.py | Remove | Low — only called from `_quality_gate()` |
| `_quality_gate()` body | Modify | Replace proxy call with adapter call |
| NEW: `mrs_adapter.py` | Create | ~60 lines, thin bridge |
| `QualityGate.mrs_version` | Bump | `mrs_proxy_v01` → `mrs_calibrated_v02` |

## Fallback

If MRS Open v0.3.1 import fails → `mrs_adapter` falls back to `pseudo_mrs()` and sets `mrs_version = "mrs_proxy_v01_fallback"`.

## Implementation

Build NEM MHP-869 (MRS Engine Adapter Hook). Judge owns MRS calibration integrity; Architect approves adapter contract.
