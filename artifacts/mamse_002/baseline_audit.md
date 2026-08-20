# MAMSE-002 — Baseline Audit (T1)

**Date:** 2026-08-11
**Branch:** codex/mfy-data-factory-001 (head bfbfa6a — includes MAMSE-001)
**Task reference:** MAMSE-002_常Q变换与对数频率听觉_v0.1 — 03_CODEX_TASK.md T1
**Status:** AUDIT COMPLETE — no code written in this step

---

## Q1. 仓库当前是否已有 CQT / VQT / chroma / pitch-class 实现

**No.** Grep over `src/moodify/` for `librosa.cqt`, `librosa.vqt`, `chroma_cqt`, `chroma_stft` returns nothing. The canonical representation path (`representation/build.py`) uses per-scale `np.fft.rfft` on a linear-Hz grid only; MAMSE-001 (MR-STFT) added a linear-Hz resolution axis with no log-frequency geometry. MAMSE-002 is the first log-frequency operator.

## Q2. librosa 是否 canonical / node 依赖，版本是否锁定

**Yes, locked.**
- `moodify-core-package/pyproject.toml` line 26: `"librosa==0.11.0"` (one of the 11 canonical pins, G6-01).
- `ops/data_node/requirements-node.lock.txt`: `librosa==0.11.0` (node lock, 55 pkgs).

No dependency change is needed; the node already ships librosa.

## Q3. feature bus 是否允许注册 non-linear frequency geometry

**Yes.** `execution/feature_bus.py` is a run-scoped immutable registry keyed by caller-supplied strings (`publish(key, value, producer_node, version, dependencies)`). A key like `log_frequency:cqt:<geometry_id>` is fully supported; the `version` field can carry operator/geometry version. The bus has no linear-frequency assumption.

## Q4. current cache key 是否包含 transform/geometry identity

**Not automatically.** `execution/cache.py` keys entries by `(source_sha256, key)` where `key` is caller-supplied (`LocalCache._dir(source_sha256, key)`); the cache does not inspect the value. Therefore geometry identity must be part of the caller's `key` — MAMSE-002 will embed `geometry_id + config_hash` in its cache key (T12 requirement). The MAMSE-001 path currently does not use this cache (recorded in its T1 decision); MAMSE-002 records cache lineage in its manifest if used.

## Q5. measurement registry 中哪些 metric 可复用，哪些只能作为 experimental descriptor

Reusable (linear-Hz authority, judgment-eligible where listed):
- `spectral_centroid_hz` (Tier B) — comparison baseline for `log_centroid_octaves` (different units; not interchangeable).
- `estimated_high_frequency_cutoff_hz`, `stereo_correlation`, band-energy ratios — usable as *context* inputs to the conditional invocation policy (T7).

Experimental-only descriptors (NOT in `measurement_registry_v1.yaml`, no authority class):
- `dominant_midi` (estimator, ≠ perceived pitch), `tuning_deviation_cents` (estimator, ≠ certified tuner), `log_centroid_octaves`, `log_spread_octaves`, `log_spectral_entropy`, `tonal_peakiness`, chroma ratios (≠ harmony understanding), octave ratios.
- These are flagged EXPERIMENTAL in every artifact and excluded from the canonical dataset schema.

## Q6. MAMSE-001 是否已创建 transform-family / advanced-operator abstraction

**No.** MAMSE-001 provides a resolution-axis registry (`ResolutionSpec` + `RESOLUTIONS` + `registry_hash()`) but no `AdvancedAuditoryOperator` framework or frequency-geometry abstraction. Per the task architecture §3, MAMSE-002 will NOT force an operator framework now; it implements independently under `moodify_experimental/mamse002/` with a compatible future interface (operator_id/operator_version/geometry_id/config_hash in evidence).

## Q7. Phase I freeze 是否允许接入默认关闭的实验算子

**Allowed** — stronger than MAMSE-001:
- MAMSE-002 is *conditional and off by default* (T7 policy gate), which the freeze protocol's Yellow budget accepts with justification.
- No canonical file touched: `scales.py`, `build.py`, `feature_registry.py`, `measurement_registry_v1.yaml` remain unmodified.
- `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md` EXPERIMENTAL = "Active research; may change without compatibility guarantees".
- MAMSE-001 precedent accepted under the same boundary (commit bfbfa6a).

## Verdict

Proceed as an **EXPERIMENTAL conditional operator** in `moodify-core-package/src/moodify_experimental/mamse002/`, evidence under `artifacts/mamse_002/`, prototype `src/mamse002/` as reference, with librosa.cqt as the implementation backend (locked 0.11.0) and geometry identity in every artifact and cache key.
