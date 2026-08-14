# Moodify Phase I Constitution

**Version:** 1.1
**Date:** 2026-08-14
**Status:** LIVE — amended by human decision on judgment authority; replaces scattered architectural notes as the canonical repository constitution
**Related:** [DATA_PROTOCOL_V1.md](contracts/DATA_PROTOCOL_V1.md), [LEGACY_AND_EXPERIMENTAL_POLICY.md](LEGACY_AND_EXPERIMENTAL_POLICY.md), [Production Authority Map](../artifacts/pr15_extraction_001/PRODUCTION_AUTHORITY_MAP.md)

---

## 1. Identity

Moodify is **The Ear of AI**.

One organizing question: **Can machines learn to hear?**

August 2026 mission: freeze a trustworthy data-production framework. September 2026 mission: stop expanding the framework and analyze the data it produces.

This is an auditory research infrastructure, not a consumer product. Product surfaces, social features, marketplaces, and recommendation systems are out of scope until the data foundation is frozen (see [CODE_FREEZE_POLICY.md](CODE_FREEZE_POLICY.md)).

## 2. What is canonical?

A new contributor must be able to answer this in five minutes.

**The canonical production loop is the only supported path:**

```text
SOURCE → LISTEN → REPRESENT → JUDGE → ABC INTERVENTION → VERIFY → ALGORITHMIC REVIEW → DATASET → NEXT CASE
```

| Concern | Canonical implementation | Versioned by |
|---|---|---|
| Scan profile | `MFY-WSE-SCAN-PROFILE-001` (`moodify.auditory.profiles`) | profile hash |
| Measurement schema | `moodify.auditory` metrics registry | schema version |
| ProductionCase | `moodify.contracts.production_case` | contract schema 1.0 |
| Evidence manifest | per-case `case_manifest.json` | schema version |
| ABC intervention plan | `moodify.data_factory.plan_generator` | `MFY-ABC-HEURISTIC-001` |
| Candidate processing | `moodify.data_factory.runner` + `moodify.data_factory.intervention` | `MFY-DATA-FACTORY-001` |
| Comparison / judgment | `moodify.auditory.service.compare_scans` + `moodify.auditory.judgment` | judgment-rules-v1.0 |
| Review authority | `moodify.data_factory.algorithmic_review` inside its approved scope; designated human reviewer outside that scope | `MFY-ALGORITHMIC-REVIEW-001` + review record |
| Dataset export | `moodify.data_factory.dataset_builder` | `MFY-DATASET-SCHEMA-001` |
| Runtime queue | `moodify.node` worker on the Aliyun 2C2G node | `MFY-ALIYUN-DATA-NODE-001` |

Anything not listed here is either an execution adapter or experimental/legacy; it must not compete with the canonical path.

## 3. Authority

- **Case state** is owned by `ProductionCase` (lifecycle + authority state). No parallel state graph may define case lifecycle.
- **Judgment authority** follows the human decision of 2026-08-14: the algorithm may decide only inside a validated, versioned and explicitly authorized scope. An out-of-scope, insufficient-evidence, uncertain or unresolved perceptual case must produce `HUMAN_REQUIRED`, `INCONCLUSIVE` or a defined failure state. A human decision records reviewer, scope, time and supporting evidence. The canonical runner must not suppress escalation to preserve unattended operation.
- Execution adapters (CLI, Android, cloud workers, queues) consume case IDs and evidence; none may define competing states or mutate case state directly.

## 4. Data semantics

- Every case records: git commit (where applicable), schema version, scan profile ID + hash, metric implementation version, DSP engine version, plan generator version, judgment rules version, FFmpeg version, Python version, dependency lock hash.
- PNG is evidence for humans; JSON/NPZ/manifests are the machine assets.
- Metrics must never be silently redefined. `PROFILE-001` stays immutable; corrections require a new version and explicit separation of historical data.

## 5. Phase boundaries

- **Phase I (now → 2026-08-31):** freeze the loop above; 10-song pilot; failure-injection evidence; cross-machine repeatability; scientific GitHub release.
- **Phase II (September →):** data production, scoped algorithmic review, human review where escalated, aggregation, statistics, notebooks, ranking models, response curves, and threshold calibration. Core metric changes, schema renames, ABC/DSP semantic changes are forbidden without the emergency-change procedure.
- **Not in any phase:** product features unrelated to the auditory loop.

## 6. Consequence of conflict

If a branch, PR, or document contradicts this constitution, the constitution wins. Ambiguous cases are resolved by: (1) freeze protocol exit conditions, (2) evidence integrity, (3) measurement correctness — in that order.
