# MAMSE-006 — Baseline Audit (T1)

**Date:** 2026-08-11
**Branch:** codex/mfy-data-factory-001 (head 4c92b0f — includes MAMSE-001..005)
**Task reference:** MAMSE-006_调制频谱与时间频率运动_v0.1 — 03_CODEX_TASK.md
**Status:** AUDIT COMPLETE — no canonical file modified

---

## Q1. 仓库现有 modulation / spectro-temporal 实现

**None.** Grep over `src/moodify/` for `modulation_spectrum|modulation_rate|spectro.temporal` returns nothing. The nearest neighbors are MAMSE-003 (wavelet texture operator, whose `modulation_distribution` is a 5-rate envelope-modulation sketch) and MAMSE-005 (cepstral fine structure). Neither computes a 1D/2D modulation spectrum with rate/scale/orientation/ridge. MAMSE-006 is the first modulation-domain operator.

## Q2. `timeline.py::spectral_flux` proxy 审计（CODEX §8）

`timeline.py:52-53` computes `spectral_flux` as `float(np.std(spec))` — explicitly a proxy ("flux needs the previous frame; approximated as local std of spectrum"), per-window, 1-second granularity. It is a canonical Phase-I metric with its own semantics.

**Recorded, not touched:** MAMSE-006 does not redefine, hotfix, or re-implement it. The modulation operator lives in its own experimental namespace with distinct semantics (modulation domain, rate/scale axes, ridge). A separate change program would be required to alter `spectral_flux` — out of scope here.

## Q3. 时钟与映射

MAMSE-006's modulation windows are computed on the STFT frame clock (`frame_rate_hz = sample_rate / audio_hop`); the surface `time_s` array carries absolute seconds on the source clock, and modulation segments map back through `modulation_window_seconds × frame_rate_hz` — no second clock is created (CODEX §3.2). Segment starts/ends are expressible on the canonical time axis.

## Q4. 复用 transform/cache

CODEX §3.3 prefers reusing existing STFT/log-frequency representations. Current repo reality: MAMSE-001..005 each carry their own analysis path (established precedent); `execution/cache.py` is caller-keyed and the canonical representation builder is scale-specific. MAMSE-006 v0.1 follows the same pattern (self-contained STFT → log-frequency surface), with the reuse/registry integration recorded as an R4+ item. No duplicate decode of canonical paths is introduced into any canonical flow — the operator is only invoked explicitly.

## Q5. 依赖

`numpy==2.4.4`, `scipy==1.17.1` only (STFT, FFT2, interp). **No new dependency**, no NN.

## Q6. 命名空间

Established convention `moodify_experimental/mamse006/` (MAMSE-001..005 precedent; the CODEX's suggested `moodify/auditory/research/modulation/` is not a pre-existing path — "以现有宪法为准，不建立竞争路径"). Evidence under `artifacts/mamse_006/`.

## Q7. 失败语义（CODEX §3.5）

Prototype already implements `UNAVAILABLE_TOO_SHORT`, `UNAVAILABLE_LOW_ENERGY`, `UNAVAILABLE_INVALID_CONFIG`, and ridge `status: CANDIDATE`. Repo implementation keeps these and adds manifest runtime identity + config_hash (profile_hash) in evidence per the MAMSE-series standard.

## Q8. Canonical 边界

No Phase-I metric/schema/contract ID changes. `spectral_flux` untouched (Q2). No second case lifecycle, no product score, no BPM/orientation-overclaim (limitations carry the boundaries).

## Verdict

Proceed as an **EXPERIMENTAL modulation-spectrum operator** in `moodify-core-package/src/moodify_experimental/mamse006/`, evidence under `artifacts/mamse_006/`, numpy/scipy only, profile_hash in every manifest, UNAVAILABLE semantics preserved, dense surface arrays decimated in NPZ (MAMSE-004/005 payload lesson). v0.1 target: SYNTHETIC_VERIFIED (G0–G13); real-case thresholds deferred to September per CODEX §7.
