# Moodify Code Freeze Policy

**Version:** 1.0
**Date:** 2026-08-11
**Freeze boundary:** 2026-08-31 23:59 (Asia/Taipei)
**Release:** Moodify 1.0 — Data Foundation

## 1. Purpose

August is not a feature month. The target is a frozen, boring, trustworthy data-production framework: by 31 August 2026, Moodify can repeatedly convert a real song into a reproducible, inspectable, versioned Auditory Production Case, and the core protocol can remain unchanged through September.

## 2. Change budget

### Green — encouraged without justification
Deletion · tests · calibration · schema validation · deterministic fixtures · documentation · reproducibility · recovery · evidence integrity.

### Yellow — requires justification (written note in the PR/commit)
Refactor · new dependency · new metric · new DSP operator · API change.

### Red — deferred
Social · feed · marketplace · recommendation · creator-platform expansion · AI comic / AI 3D · token/transaction features · visual-polish unrelated to case production.

## 3. What freezes on 2026-08-31

- Data Protocol `MFY-DATA-PROTOCOL-001` (schema 1.0)
- Scan profile `MFY-WSE-SCAN-PROFILE-001` (immutable; hash f0ff177d…)
- Metric registry `MFY-METRIC-REGISTRY-001`
- ABC semantics (A=conservative / B=balanced / C=exploratory, diagnosis-derived)
- DSP engine `MoodifyDSPChain v1`
- Judgment rules `MFY-JUDGMENT-RULES-001` (v1.0)
- Review authority `MFY-ALGORITHMIC-REVIEW-001` (formula `MFY-ALGO-REVIEW-FORMULA-001`)
- Human review schema `MFY-HUMAN-REVIEW-001` (schema v1.0; algorithmically produced)
- Dataset schema `MFY-DATASET-SCHEMA-001`
- Runtime node `MFY-ALIYUN-DATA-NODE-001` (2C2G, single worker)

All freeze identities are recorded in `CODE_FREEZE_MANIFEST.json` at the release tag.

## 4. Versioning rule (never silently change semantics)

If a metric/profile/plan definition must change after freeze:

```text
PROFILE-001  → remains immutable
PROFILE-002  → new corrected definition
```

Historical data is either reprocessed or kept explicitly separated. **Never mix rows produced under incompatible definitions.**

## 5. Allowed after freeze (until release)

Documentation fixes · dependency pinning · benchmark reruns · clean-install verification · release packaging · critical correctness fixes (see §6).

## 6. Emergency change procedure

If a correctness bug is found:

1. Stop affected production.
2. Open a documented incident (incident ID, date, affected scope).
3. Identify affected cases by recorded versions in their manifests.
4. Create a new version of the affected definition.
5. Never mutate the old definition or historical data in place.
6. Decide — explicitly, with evidence — whether affected cases are re-run.
7. Keep datasets separated until compatibility is proven.

## 7. September operating rules

Default mode after freeze: data production, algorithmic review, aggregation, visualization, statistics, ranking models, response curves, threshold calibration, documentation derived from observed data.

Forbidden by default: add a core metric · rename a dataset field · change a metric formula · change ABC meaning · change DSP semantics · change schema · alter historical data in place · silently patch a frozen profile.

## 8. Measuring progress

Progress is not measured by commits. Progress is measured by **uncertainty removed from the data-production system**. Each Gate closes only when its exit condition is met and evidence is attached.
