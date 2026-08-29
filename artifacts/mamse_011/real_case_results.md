# MAMSE-011 — Real Case Results

**Date:** 2026-08-11
**Sources:** 3 operator-owned AI pilot tracks (same files as MAMSE-001..010, rights_ok=true).
**Scope:** S1 clean subset (12 features; mid/side + short_term_lufs blocked per audit). Reference model = first half, frozen projection on second half; then a relation-break injection probe (mirror-flip one feature's deviations — marginals unchanged, joint structure broken). Cross-case covariance drift recorded.

## Descriptors

| Case | eff_rank | shrink | lag1 max | neff ratio min | normal d2 med | q99 frac | injected d2 med | q99 frac | increment |
|---|---|---|---|---|---|---|---|---|---|
| 9056391 harmonic | 5.49 | 0.011 | 0.942 | 0.030 | 24.5 | 0.048 | 27.1 | 0.139 | NO_INCREMENT (+0.091) |
| 9961e07 transient | 5.55 | 0.008 | 0.962 | 0.019 | 20.2 | 0.016 | 22.7 | **0.134** | **RELATION_BREAK_CANDIDATE (+0.117)** |
| 7b3f021 AI | 5.65 | 0.008 | 0.963 | 0.019 | 31.0 | 0.008 | 34.4 | 0.057 | NO_INCREMENT (+0.049) |

Cross-case covariance drift: correlation relative Frobenius 0.39–0.50, principal angles 4.6–34° (descriptive; different AI productions have measurably different relation structure).

## Technical observations

1. **The relation-break probe shows a real, honest increment in one of three cases** (9961e07: q99 fraction 0.016 → 0.134). The injection flips the sign of `rms_db` deviations from its median — the single-feature marginal distribution (median/MAD) is nearly unchanged, so a single-metric scan cannot see it, while the Mahalanobis geometry detects the broken joint structure. G29 is demonstrated once (with 2 honest negatives where the increment was smaller).

2. **Temporal dependence is extreme and honestly recorded**: lag1 autocorrelation up to 0.96 and effective sample size as low as 1.9% of nominal n (G19/G20). The reference quantiles are empirical descriptors, not significance thresholds — with neff this small, the q99 fractions must be read as descriptive, and the "RELATION_BREAK_CANDIDATE" label stays a candidate.

3. **Effective rank ~5.5–5.7 of 12**: the S1 clean-subset relation space is genuinely low-dimensional; OAS shrinkage is tiny (0.008–0.011) at this N.

4. **Cross-case drift is large** (corr frob 0.39–0.50): different tracks' relationship models differ substantially — supporting the frozen-reference approach (a reference model is track- or corpus-specific, never universal).

## Honest negatives

1. Injection increment is threshold-dependent: 9056391 (+0.091) and 7b3f021 (+0.049) fell below the +0.10 heuristic gate — the effect exists in all three but is only strong in one.
2. d2 quantiles with neff ≈ 2% of n are weak statistics; no significance claim.
3. No causality; no quality score; "relation-break candidate" only.
4. Three tracks, one injection feature pair — not a corpus.

## Verdict

The covariance/eigenspace layer runs correctly and provides a demonstrated (once) combinational-anomaly increment over single metrics, with extreme temporal dependence honestly recorded. Standing at **R2 VERIFIED (synthetic)** with G29 partially demonstrated on real cases; September corpus work can strengthen the G29 evidence base.
