# MHP-854: MRS Proxy Replacement Boundary

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6B: Vector Definitions / V4
**Depends on**: MHP-845 (Audit), MHP-846 (Interface Contract)
**Protocol**: AWJ Stack + E-Chain 54

## Context

The v01 pipeline uses `mrs_proxy_v01` in `_quality_gate()`. The runtime has a full `mrs_engine.score_audio()` with pseudo-MRS + MRS Open v0.3.1 + over-dark + genre gates. This probe defines exactly where the proxy ends and the calibrated MRS begins, so Build NEM knows where to place the adapter.

## Current State: Two Parallel MRS Implementations

### MRS Path A: v01 Pipeline (inline proxy)

```text
File: moodify-core-package/src/moodify/v01_pipeline.py:258-273
Function: _mrs_proxy(metrics) -> float
Formula: 800 + 400 * avg(clamped(dynamic, crest, stereo, air, presence, peak))
Version:  mrs_proxy_v01
Range:    ~800-1200
```

### MRS Path B: Runtime Engine (full)

```text
File: moodify_runtime/mrs_engine.py:74-139
Function: score_audio(before_path, after_path, genre, preset, sample_id) -> MRSScoreResult
Components: pseudo_mrs + MRS Open v0.3.1 + over_dark + gate_decision
Version:  mrs_open_v031
Range:    MRS Open: ~0.15-0.50 (D_real), pseudo: ~800-1200
```

## Replacement Boundary

```text
┌─────────────────────────────────────────────────────────┐
│                   v01_pipeline.py                        │
│                                                         │
│  V_validate:                                            │
│    _quality_gate(before, after)                         │
│      │                                                   │
│      ├── _mrs_proxy(metrics)   ← REMOVE in v0.2        │
│      │   (version: mrs_proxy_v01)                       │
│      │                                                   │
│      └── NEW: mrs_adapter.score(before, after, genre)   │
│          │                                               │
│          ▼                                               │
│    ┌─────────────────────────────────────┐              │
│    │     mrs_adapter.py (NEW)            │              │
│    │                                     │              │
│    │  def score(before, after, genre):   │              │
│    │      return mrs_engine.score_audio( │              │
│    │          before, after, genre, ...   │              │
│    │      )                               │              │
│    │                                     │              │
│    │  def to_quality_gate(result) ->     │              │
│    │      QualityGate:                   │              │
│    │      return QualityGate(            │              │
│    │        mrs_version="mrs_calibrated_v02",          │
│    │        mrs_before=result.mrs_open_before,         │
│    │        mrs_after=result.mrs_open_after,           │
│    │        mrs_delta=result.mrs_delta_for_gate,       │
│    │        passed=result.gate_decision == "pass",     │
│    │        damage_loss=result.over_dark_score,        │
│    │        risk_flags=_map_risk(result),              │
│    │      )                                             │
│    └─────────────────────────────────────┘              │
│                                                         │
│  moodify_runtime/mrs_engine.py  ← UNCHANGED            │
│  moodify_runtime/metrics.py     ← UNCHANGED            │
│  moodify_runtime/over_dark.py   ← UNCHANGED            │
│  workers/mrs_open_benchmark_v03 ← UNCHANGED            │
└─────────────────────────────────────────────────────────┘
```

## What Changes

| Component | Change | Why |
|-----------|--------|-----|
| `_mrs_proxy()` | **Removed** | Replaced by calibrated MRS adapter |
| `_quality_gate()` | **Modified** | Calls `mrs_adapter.to_quality_gate()` instead of `_mrs_proxy()` |
| NEW: `mrs_adapter.py` | **Created** | Thin adapter bridging v01 types and mrs_engine |
| `mrs_engine.py` | **Unchanged** | Already correct — no code change needed |
| `QualityGate` dataclass | **Minor** | `mrs_version` changes from `mrs_proxy_v01` to `mrs_calibrated_v02` |

## What Does NOT Change

- `mrs_engine.score_audio()` — already correct, with pseudo + MRS Open + over-dark + gate
- `pseudo_mrs()` function — stays for backwards compat / reporting
- `compute_mrs_open_v031()` — stays, is the calibrated scoring core
- `detect_over_dark()` — stays, feeds damage_loss
- All MRS tests — continue to pass

## Risk: MRS Open Availability

`compute_mrs_open_v031()` imports `workers/mrs_open_benchmark_v03` which depends on `numpy`, `scipy`, `librosa`, and the worker config. If the import fails, `mrs_open_available=False`.

**Fallback**: If MRS Open unavailable, `mrs_adapter` falls back to `pseudo_mrs` and sets `mrs_version = "mrs_proxy_v01_fallback"`. The `mrs_version` field tells consumers exactly what they're getting.

## Boundary Contract

```python
# mrs_adapter.py — the ONLY file that bridges v01 types and mrs_engine

def score_for_quality_gate(before_metrics, after_metrics, genre: str = "") -> QualityGate:
    """Replace _mrs_proxy() with calibrated MRS.
    
    Returns QualityGate with mrs_version field indicating which engine was used.
    Consumers MUST check mrs_version before interpreting MRS values.
    """
    ...

# All other v01 code calls ONLY this function.
# No other file imports from mrs_engine directly.
```

## Acceptance Criteria

- [x] Replacement boundary is clearly drawn (adapter between v01 and mrs_engine).
- [x] What changes (4 items) and what doesn't (5 items) is explicit.
- [x] Fallback path for unavailable MRS Open is defined.
- [x] `mrs_version` field serves as the consumer contract.
- [x] Build NEM task (MHP-869) is the implementation boundary.
