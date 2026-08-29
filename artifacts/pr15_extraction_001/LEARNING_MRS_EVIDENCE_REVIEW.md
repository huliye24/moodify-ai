# Learning, MRS, and Evidence Review

| Candidate | Classification | Evidence | Decision |
|---|---|---|---|
| Auditory WSE metrics | EXPERIMENTAL_MEASUREMENT | method-labelled values, profiles, scan tests; CI needs ffmpeg | Eligible for migration after method/version contract and hermetic CI |
| MRS Open v0.3.1 | PROXY / EXPERIMENTAL_MEASUREMENT | formula and mathematical tests; calibrated around a reference distance | Not a universal quality truth; store only in experimental namespace |
| pseudo-MRS | PROXY | explicitly named pseudo score and calibrated weights | Never expose as canonical quality measurement |
| over-dark detector | PROXY | threshold/genre tests | Experimental judgment input, not MeasurementRecord truth |
| B-matrix / physics | RESEARCH_HYPOTHESIS | matrices, linearity/conservation research tests | Research artifact until method, dataset, uncertainty, and reproducibility are accepted |
| Treatment records | HUMAN_LABEL plus experiment record | explicit before/after and feedback fields | Preserve; normalize source/method/rights references |
| `learning/` records | EXPERIMENTAL asset workflow | fail-closed rights eligibility, explicit review and pairwise preferences | Extract rights/human-label invariants after evidence contract |
| Calibration reviews | HUMAN_LABEL | reviewer decisions compared with gates | Keep separate from machine values and proxy scores |

## Decision

- MRS as a production MeasurementRecord field today: **PARTIAL — only as a namespaced experimental/proxy value**, never as an authoritative quality score or gate truth.
- B-matrix/physics as a production MeasurementRecord field today: **NO**. It remains a research hypothesis/artifact until provenance, uncertainty, and accepted validation datasets are defined.
- Human feedback: valid as an explicit HumanLabel/HumanListeningEvaluation with evaluator, context, comparison mode, decision, confidence, and rights; it must not be merged into machine measurement fields.
