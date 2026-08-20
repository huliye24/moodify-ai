# MAMSE-003 — Real Case Results (Gate F)

**Date:** 2026-08-11
**Sources:** 3 operator-owned AI pilot tracks (same files as MAMSE-001 T7 / MAMSE-002 T10, rights_ok=true, sha256-linked in each manifest) + 2 data-factory cases for the A/B pair.
**Scope:** TECHNICAL_OBSERVATION only. No artistic-quality statement is made for any case. Texture descriptors are experimental and never quality scores.

## Case selection and prior linear profile

| Case | Role | Linear scan (canonical) | MAMSE-002 (log-freq) |
|---|---|---|---|
| case_9056391_harmonic | sustained harmonic/vocal | LRA 4.53, centroid 504.5 Hz | dominant 164.7 Hz (G2), tuning 0.00¢, 1 low-register event |
| case_9961e07_transient | transient-rich | LRA 9.0, centroid 823.6 Hz | dominant 130.6 Hz (B1), 24 low-register events |
| case_7b3f021_ai | AI-generated pilot track | LRA 6.75, centroid 979.3 Hz | dominant 72.6 Hz (F#1), 64 low-register events |

## Texture descriptors (full tracks, 27 carriers / 5 modulation rates, 24 kHz analysis)

| Case | HMR | Texture entropy | Texture sparsity | Stationarity | Order ratio | Wall (s) | Peak mem |
|---|---|---|---|---|---|---|---|
| 9056391 | 0.169 | 0.851 | **0.343** | 0.407 | **12.666** | 43.2 | 2.57 GB |
| 9961e07 | 0.187 | **0.920** | 0.228 | 0.414 | 10.825 | 48.5 | 3.68 GB |
| 7b3f021 | 0.187 | 0.914 | 0.250 | **0.468** | 8.394 | 76.2 | 3.95 GB |

(HMR = high-modulation ratio, modulation energy at ≥8 Hz / total modulation energy. Entropy/sparsity of the carrier energy distribution. Stationarity = 1/(1+mean temporal CV). Order ratio = modulation energy / carrier energy.)

## Technical observations

1. **The harmonic case is the most texture-sparse and most modulation-dominant** (sparsity 0.343, order ratio 12.7). The linear path already knows it is a low-LRA, low-centroid sustained track; texture adds that its energy is concentrated in few carrier bands *and* that slow modulation energy exceeds carrier energy by ~12.7× — the sustained material carries substantial internal fluctuation structure (vibrato/chorus/dynamics), a dimension the level-based linear metrics do not quantify.

2. **The transient case is the most texture-diffuse** (entropy 0.920, sparsity 0.228). The linear path knows it is transient-rich (LRA 9.0) and its centroid (823 Hz); texture adds *how spread the energy is across the scale axis* — the widest, least peaked carrier distribution of the three.

3. **The AI case is the most stationary texture** (stationarity 0.468, order ratio 8.4 — the lowest modulation-to-carrier ratio). Its texture is the most time-stable and least slow-modulated of the three despite the highest centroid. This is a *descriptive* texture structure, NOT an AI-detection claim: a human-performance dataset is required before any provenance interpretation.

4. **Frame mapping to S1/S2**: frame starts/ends are stored on the original sample clock (scale = 48000/24000), so texture frames can be overlaid on existing S1/S2 windows without a new time scale.

## Per-case answer to the E-gate questions

| Case | What linear-Hz path already knows | What texture adds | Changes interpretation? | Cost |
|---|---|---|---|---|
| 9056391 | sustained, low centroid 504 Hz, LRA 4.53 | energy concentrated (sparsity 0.343) + strong slow modulation (order 12.7) | Refines "sustained quiet track" into "sparse, internally fluctuating texture" | 43 s wall / 2.6 GB (offline) |
| 9961e07 | transient-rich, centroid 823 Hz, LRA 9.0 | widest carrier spread (entropy 0.920) | Confirms diffuse texture quantitatively; adds scale-axis spread not visible in centroid | 48 s wall / 3.7 GB (offline) |
| 7b3f021 | bright AI track, centroid 979 Hz | most stationary, least slow-modulated texture | Adds a stability dimension the level/centroid path does not report | 76 s wall / 3.9 GB (offline) |

**Without MAMSE-003**, the three cases would be told apart only by level/centroid/profile (LRA); the *distribution of energy across scales* and *modulation-to-carrier ratio* would be unknown. The increment is real but bounded — see honest negatives.

## A/B cases

### Control pair — same-song mastering variants (9056391 candidate_A vs harmonic)

The same composition processed to two different masters (same duration 128.52 s, evidence in `real_cases/control_pairs/`, sha256-linked):

| Pair metric | Value |
|---|---|
| first-order cosine | 0.9995 |
| modulation cosine | 1.0000 |
| HMR A/B | 0.1683 / 0.1688 |
| entropy A/B | 0.8579 / 0.8512 |
| sparsity A/B | 0.3341 / 0.3429 |

**Honest negative:** mastering-level processing does not change texture structure — the operator does not fabricate differences where the linear path also sees near-identity. Texture agrees with linear metrics on this pair.

### Matched-loudness pair — different factory cases (45e96f4c vs bf117642 sources)

Two independent data-factory cases whose canonical loudness is almost identical (sha256-linked in `pair_factory_matched_loudness.json`):

| Linear metric | A (45e96f4c) | B (bf117642) |
|---|---|---|
| Integrated LUFS | **-18.68** | **-18.69** (Δ 0.01) |
| Spectral centroid | 530.5 Hz | 506.3 Hz (Δ 4.7%) |

| Texture | A | B |
|---|---|---|
| first-order cosine (A vs B) | **0.9884** (same-song control: 0.9995) | |
| modulation cosine (A vs B) | **0.9976** (control: 1.0000) | |
| HMR | 0.1702 | 0.1591 |
| entropy | 0.8540 | 0.8803 (Δ 0.026) |
| sparsity | 0.3475 | 0.3158 (Δ 0.032) |
| stationarity | 0.4092 | 0.4206 (Δ 0.011) |

**Honest reading:** the matched-loudness pair is *less* texture-similar than the same-song control on both cosines (0.9884/0.9976 vs 0.9995/1.0000), and the aggregate descriptors move consistently (B is more diffuse, less sparse, slightly more stationary). The operator separates two tracks that LUFS cannot distinguish — but the margin is small. These dense AI/music productions share overall texture character, so the increment is real but bounded: within-corpus texture similarity is high, and the descriptor deltas (not a single cosine threshold) carry the signal.

## Honest negatives

1. **The modulation-distribution cosine saturates near 1.0 across all real pairs tested** (mastering variants AND factory cases). For these dense AI/music productions the 5-rate modulation sketch does not discriminate; discrimination comes from the carrier distribution + aggregate descriptors. Modulation-rate resolution is a known limitation, not hidden.
2. Full-song runs need 2.5–3.9 GB (offline-only policy, see release gate).
3. No provenance claim: the AI case's stable texture is descriptive only.
4. Texture descriptors are not artistic-quality scores; nothing here ranks "better" or "worse".

## Verdict

Real cases provide incremental scale-distribution and modulation-to-carrier information over the linear/log-frequency paths, with bounded cost and explicit offline scope. A/B work shows both a control (no fabricated difference) and a matched-loudness discriminator. Gate F requirements are met with the honest caveats above.
