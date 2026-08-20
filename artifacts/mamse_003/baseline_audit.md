# MAMSE-003 — Baseline Audit (T1)

**Date:** 2026-08-11
**Branch:** codex/mfy-data-factory-001 (head 2eb01b0 — includes MAMSE-001 + MAMSE-002)
**Task reference:** MAMSE-003_小波与Scattering多尺度听觉纹理_v0.1 — 03_CODEX_TASK.md 基线原则
**Status:** AUDIT COMPLETE — no canonical file modified

---

## Q1. 仓库是否已有 wavelet / scattering 实现

**No.** Grep over `src/moodify/` for `pywt`, `kymatio`, `PyWavelets`, `morlet`, `wavelet`, `scatter` returns nothing. The canonical representation path uses `np.fft.rfft` on a linear-Hz grid (per-scale STFT); MAMSE-001 added a linear-Hz resolution axis, MAMSE-002 added a log-frequency geometry. There is no wavelet-family or scattering-family operator anywhere in canonical code. MAMSE-003 is the first texture/scattering-inspired operator.

## Q2. pywavelets / kymatio 是否在 canonical / node 依赖中

**No, and not needed.**
- `moodify-core-package/pyproject.toml` — no `pywavelets`, no `kymatio`.
- `moodify-core-package/ops/data_node/requirements-node.lock.txt` — no `pywavelets`, no `kymatio`.

Node already ships everything MAMSE-003 uses: `numpy==2.4.6`, `scipy==1.18.0`, `soundfile==0.14.0` (scripts), `librosa==0.11.0` (unused by MAMSE-003 core, kept for MAMSE-002).

## Q3. MAMSE-003 是否引入新依赖

**No.** The prototype is self-contained: FFT-domain analytic Gaussian (Morlet-like) carrier bank + modulus envelope decimation + low-frequency modulation bank, all built on `numpy`/`scipy` (both canonical pins). The CODEX constraint "任何新依赖必须是 optional extra" is not triggered. A future Kymatio/PyWavelets evaluation is explicitly deferred to R4+ (README boundary, config.py docstring).

## Q4. feature bus / cache 是否允许 texture operator 身份

**Yes, same mechanism as MAMSE-002.** `execution/feature_bus.py` is a run-scoped registry keyed by caller-supplied strings; `execution/cache.py` keys by `(source_sha256, caller_key)` and does not inspect values, so `config_hash` must live in the caller's key. MAMSE-003 follows the established pattern: `operator_id/operator_version/config_version/config_hash` in every manifest, NPZ and summary (evidence.py `build_manifest`, config.py `config_hash`). Cache integration remains deferred, same decision as MAMSE-001/002.

## Q5. canonical measurement / ProductionCase 是否会被改动

**No.** Verified via `git status`: canonical files (`representation/scales.py`, `representation/build.py`, `representation/feature_registry.py`, `measurement_registry_v1.yaml`, data-factory schemas) are unmodified in the working tree. MAMSE-003 lives entirely in `moodify_experimental/mamse003/` + `tests/experimental/` + `scripts/` + `artifacts/mamse_003/`. No second ProductionCase state is created.

## Q6. MAMSE-001/002 抽象是否复用

**Yes, at the evidence/namespace level, not a forced framework:**
- Namespace: `moodify_experimental/mamse003/` (same branch of the tree as mamse001/mamse002 — the established research-operator convention, per "服从现有结构").
- Evidence contract: manifest (operator/config/source/runtime identity) + NPZ machine asset + JSON summary — same 3-part shape as MAMSE-002 (`mamse002_manifest.json` / `mamse002_logfreq_sketch.npz` / `log_frequency_evidence.json`).
- Scripts: `mamse003_benchmark.py` / `mamse003_run_real_cases.py` mirror `mamse001/mamse002_*` conventions.
- Source identity: `source_sha256` computed from the same source files (`outputs/mamse001_sources/*.wav`, 48 kHz stereo) used by MAMSE-001 T7 and MAMSE-002 T10 — lineage is cross-referenced in each manifest.

## Q7. 源身份与 sample clock 复用（S1/S2 映射）

**Yes.** `sketch.py:analyze_texture` computes `source_sha256` over the samples; frame positions `frame_starts_samples`/`frame_ends_samples` are scaled back from the 24 kHz analysis clock to the original sample clock (`scale = sample_rate / analysis_sample_rate`), so texture frames can overlay existing S1/S2 windows without a new canonical time scale (04_ARCHITECTURE.md mapping contract).

## Q8. Phase I freeze 是否允许接入默认关闭的实验算子

**Allowed** — the established precedent:
- MAMSE-001 (bfbfa6a) and MAMSE-002 (2eb01b0) were accepted as EXPERIMENTAL conditional operators under the same freeze protocol (Yellow budget with justification, `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md`).
- MAMSE-003 is **disabled by default**; invocation is explicit (research flag / dedicated script / future evidence-based RFC). No App entry point, no UI switch, no canonical-scan integration.
- 10 synthetic tests + 3 real cases land entirely under `tests/experimental/` and `artifacts/mamse_003/`.

## Verdict

Proceed as an **EXPERIMENTAL texture operator** in `moodify-core-package/src/moodify_experimental/mamse003/`, evidence under `artifacts/mamse_003/`, self-contained numpy/scipy implementation (no new dependency), config_hash in every artifact, full-song runs restricted to an offline/high-ACU policy (see release_gate.md resource section).
