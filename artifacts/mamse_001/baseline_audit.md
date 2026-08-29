# MAMSE-001 — Baseline Audit (T1)

**Date:** 2026-08-11
**Branch:** codex/mfy-data-factory-001 (head e66cbf9)
**Task reference:** MAMSE-001_多分辨率时频听觉表示_v0.1 — 03_CODEX_TASK.md T1
**Status:** AUDIT COMPLETE — no code written in this step

---

## Q1. 当前 S0/S1/S2/S3 的 authority 在哪里

Single canonical authority, three files:

| Concern | File | Role |
|---|---|---|
| Scale registry (S0-S3, window/hop) | `moodify-core-package/src/moodify/auditory/representation/scales.py` | `SCALES` tuple, versioned `REPRESENTATION_VERSION="rep-v1"`, `get_scale()` raises on unknown id |
| Representation builder | `moodify-core-package/src/moodify/auditory/representation/build.py` | `build_representation()` — the only canonical builder; S1 STFT reused for S2 spectral summaries |
| Band authority | `moodify-core-package/src/moodify/auditory/representation/feature_registry.py` | `BANDS` (sub/bass/low_mid/mid/core_mid/presence/brilliance/air) + `PLANE_METRIC_MAP` + `plane_meta()` authority resolution |

Constitutional anchor: `docs/PHASE1_CONSTITUTION.md` §2 table (Measurement schema row), §3 (authority), §4 (data semantics).

S scales observed: S0 MICRO 40/20 ms · S1 SHORT 400/100 ms · S2 MEDIUM 2000/500 ms · S3 TRACK whole-source. Matches task-package references.

## Q2. 当前 STFT/FFT 被哪些模块重复计算

At least 20 modules call `rfft`/`stft` directly (grep of `src/moodify/`):

- `auditory/metrics.py` — independent STFT, `n_fft=8192, hop=2048`, Hann (metrics-level spectral features)
- `auditory/profiles.py` — scan profile carries `hop_length: 2048`
- `auditory/representation/build.py` — per-scale `rfft` inside `_short_rows` (S1) and `_medium_rows` (S2); S0 is time-domain only
- `auditory/comparison.py`, `auditory/timeline.py`, `auditory/service.py` — scan/compare paths
- `auditory/events/rules.py` — temporal-hearing rules reuse spectrum
- `diagnosis/engine.py`, `diagnosis/metrics.py`, `diagnosis/preprocessing.py` — diagnosis-path STFT
- `fingerprint.py`, `reality_metrics.py`, `v01_analyzer.py`, `optimizer/calibrate.py`, `processing/spectral_chain.py`, `physics/experiments_2.py`, `data_types.py`, `protocol.py` — assorted legacy/research paths

There is **no shared transform layer**: each module re-derives windows, padding, and `rfftfreq` independently. `n_fft` values in use: 512–8192 across modules, all hard-coded.

## Q3. 哪些 shared transform 可以复用

- **Decode-once**: `auditory/decode.py` is the canonical decode path; reuse it (single decode) instead of re-decoding per resolution.
- **`execution/` infrastructure** (patch 23–25 line): `cache.py` (hash-verified filesystem `LocalCache`), `feature_bus.py`, `graph.py`, `planner.py`, `engine.py` — exists and is suitable in principle, but the canonical `build_representation` path is **not** wired through it yet. MAMSE-001 should not be the first consumer to couple to the execution graph; keep it independent and record FFT/cache identity in evidence (T4 requirement).
- **No reusable window/FFT-plan sharing exists today** — MAMSE-001 introduces the first explicit resolution kernel registry.

## Q4. execution cache / feature bus 是否适合承载 MR-STFT

Partially suitable, with a boundary decision:

- `execution/cache.py` — hash-verified local cache; appropriate for caching per-resolution sketch payloads keyed by (source_sha256, resolution_id, feature_schema_version).
- `execution/feature_bus.py` / `graph.py` — designed for the execution pipeline; coupling MAMSE-001 to it now would make an experimental operator depend on canonical execution internals before its evidence is proven (violates T10 "保持 EXPERIMENTAL" spirit).
- **Decision:** MAMSE-001 runs as a self-contained experimental pipeline (decode once → 4 frame streams → 4 RFFT → fixed-width sketches → NPZ), records its own FFT backend identity (numpy rfft version) and cache identity if a cache is used. Coupling to the execution graph is deferred until R4+.

## Q5. 是否已有等价的多 FFT 分辨率实现

**No.** Verified:

- `representation/` exposes only the S-axis (single STFT per scale for spectral features).
- `spectrogram.py` is ffmpeg `showspectrumpic` PNG evidence (same profile parameters) — visualization only, not a resolution axis.
- `diagnosis/preprocessing.py` has its own STFT but no multi-resolution axis; `physics/experiments_2.py` is legacy research.
- No module defines an explicit `resolution_id` registry. MAMSE-001 is the first R-axis implementation.

## Q6. Phase I freeze 是否允许接入 experimental operator

**Allowed**, with constraints:

- `docs/PHASE1_CONSTITUTION.md` §3: anything outside the canonical table "is either an execution adapter or experimental/legacy; it must not compete with the canonical path."
- `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md` defines EXPERIMENTAL as "Active research; may change without compatibility guarantees."
- `MOODIFY_AUGUST_2026_FREEZE_PROTOCOL` Yellow budget: new DSP operators require justification — MAMSE-001 provides justification via T6 synthetic gates, T7 real-case evidence, T8 resource evidence, and explicit non-merge into canonical (T10 release gate).

Constraints honored by this task: no modification of `scales.py`/`build.py`/`feature_registry.py`; no new band definitions; no new metric authority (all R features marked EXPERIMENTAL descriptors); no dense spectrogram persistence; no UI surface (T9).

## Verdict

Proceed to T2–T5 as an **experimental research operator** in `moodify-core-package/experimental/mamse001/`, evidence in `artifacts/mamse_001/`, with the task package prototype (`src/mamse001/`) as reference only.
