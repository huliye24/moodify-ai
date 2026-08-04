# Moodify Industrial Direction

Version: v0.1
Date: 2026-06-04
Status: active product direction

> **2026-07-30 scope clarification:** This document remains valid for the
> industrial workflow, acoustic processing, evidence, and craft-library
> principles. Product ownership and surface priority are now governed by
> `MOODIFY_MUSIC_PROCESSING_INFRASTRUCTURE.md`. Moodify is headless
> music-processing infrastructure for music companies; creator contact,
> talent/artistic judgment, signing, and artist operations are outside scope.
> The Operator Console is an internal operations and validation surface, while
> the versioned production contract and API are the primary product boundary.

## One Sentence

Moodify is an enterprise acoustic industrial system for the AI music era. It uses deep acoustic scanning, long-running cloud processing, MRS reality scoring, quality gates, reports, and craft-library accumulation to move AI music from simulated sound toward more real sound.

Short form:

> Moodify is not a music app. Moodify is acoustic industrial equipment for AI music production.

Developer form:

> Moodify is not a button. Moodify is a machine.

## Product Shift

Moodify must stop being shaped as a consumer one-click app.

Old product logic:

```text
upload audio -> one-click processing -> download result
```

New product logic:

```text
create job
  -> acoustic scan
  -> spectral / dynamic / spatial diagnosis
  -> processing plan
  -> long-running cloud processing
  -> candidate versions
  -> MRS reality scoring
  -> quality gate
  -> review / reprocess when needed
  -> final master delivery
  -> acoustic report
  -> archive and craft-library writeback
```

The product is not a button. It is a production line.

## Two Curves: Why Post-Processing Is the Gate, Not the Goal

> **2026-08-01 strategy note:** the following argument was added to name the
> market-timing logic behind the industrial shift.

AI music post-processing is a shrinking market by construction: the defects
that post-processing fixes are defects of AI music models, and those defects
shrink as the models improve. Demand for "fix the synthetic sound" follows the
model capability curve downward.

Two opposite curves:

```text
AI music model capability -> post-processing demand (shrinking)
AI music model capability -> measurement demand      (growing)
```

The second curve inverts the first: the closer synthetic audio gets to real
sound, the harder — and the more valuable — it becomes to measure and prove
whether a master is real or simulated. MRS reality scoring, spectral
evidence, listening tests, and calibration reports sit on the growing side.

Moodify therefore thickens on the other side — and the other side is a
**data asset**.

Every job is a data-collection instrument: acoustic scans, MRS scores, gate
decisions, reports, craft records, and — whenever human review happens —
ground-truth labels. The asset compounds on two axes:

1. **Volume**: more jobs → more samples, more scores, more failure cases.
2. **Quality per unit**: the data improves, not just grows — listening
   review labels ground truth, calibration converges MRS, failure cases
   sharpen gates, craft memory learns what works on what material.

Three downstream products of this asset:

1. **Measurement authority** — MRS reality scoring, spectral evidence,
   listening tests, calibration reports: a trusted gauge is only as credible
   as its calibration data, so the gauge and the data are the same moat.
2. **Craft-library compounding** — craft memory, proposals, failure cases:
   the library is the data made executable.
3. **Evidence and traceability** — production-case control, quality gates,
   reports, and delivery records: audit value that is independent of model
   capability.

Why the asset gets rarer, not commoner, as models improve: each new model
generation redefines what AI music sounds like, so the longitudinal record of
real-versus-simulated across generations — and of what fixes worked — cannot
be reconstructed by anyone who was not collecting it continuously. Model
companies own model data; Moodify owns post-production outcome data.

Post-processing stays. It is the entry gate that acquires customers and feeds
the data engine. But the value center must keep migrating toward the data
asset — before the gate closes.

Risk: the asset compounds only if data discipline holds — labeled ground
truth, calibration rigor, retained raw evidence. Scattered files do not
compound; a structured data pipeline does. Measurement credibility is
downstream of the same data (see Cold Boundaries).

## Primary Customer

The first customer is the internal operator.

Moodify should first serve:

- internal staff who operate the sound-processing workflow;
- AI music production teams;
- post-production studios;
- content companies with repeatable AI music output;
- acoustic engineering teams that need traceable processing and reporting.

The unit of adoption is not a casual user. The unit of adoption is a studio.

## Product Surface

The Electron / desktop surface should be treated internally as:

> Moodify Industrial Operator Console

It is an internal operations, validation, and incident-response surface. It is
not a creator-facing product and is not the primary company integration
contract.

It is responsible for:

- importing audio and creating jobs;
- selecting processing depth;
- viewing queue state and task history;
- launching cloud/runtime processing;
- comparing candidate versions;
- reading MRS and gate decisions;
- generating reports;
- exporting final masters;
- managing customer orders and delivery records.

It should not be optimized around casual play, immediate gratification, or low-context self-service.

## Processing Depth Levels

Processing time must map to processing depth. Waiting is not value unless the time is converted into scan depth, candidate generation, quality gates, review, and report evidence.

| Mode | Time | Use Case | Required Actions |
| --- | ---: | --- | --- |
| Quick Scan | 5-15 min | diagnosis and quote pre-check | basic features, quick MRS, issue detection |
| Standard Process | 30-90 min | normal order | standard craft chain, candidate comparison, basic report |
| Deep Process | 2-5 h | high-value single / commercial release | multi-round scan, multiple candidates, gates, review report |
| Studio Process | 5 h+ | enterprise / album-level work | custom craft chain, human review, long-term sample writeback |

## Core Data Objects

The system should persist industrial records, not only output files.

Required object vocabulary:

- `Sample`: source audio and identity metadata.
- `Job`: one processing request with state and ownership.
- `ScanProfile`: scan depth, dimensions, and feature extraction configuration.
- `ProcessingPlan`: selected craft strategy, presets, chains, and candidate count.
- `CandidateVersion`: one generated output candidate with lineage.
- `ScoreResult`: MRS and supporting quality metrics.
- `GateDecision`: pass / reject / reprocess / manual review.
- `Report`: operator-facing or customer-facing explanation.
- `Delivery`: final audio, report, archive, and handoff record.
- `CraftRecord`: reusable processing chain knowledge and failure cases.

## Developer Principles

1. Queue first, not instant button first.
2. Reproducibility first, not temporary effect first.
3. Craft library first, not feature pile-up first.
4. Report first, not black-box output first.
5. Quality gate first, not file generation first.
6. Hardware and cloud capacity belong on the product roadmap.
7. MRS is a gate and calibration system, not a decorative score.

Every serious processing result must be able to answer:

- What input was used?
- Which code version ran?
- Which preset / craft chain / parameters were used?
- Which candidates were generated?
- Which MRS and side-effect metrics changed?
- Why did the chosen candidate pass?
- Where is the final delivery and report archived?

## Business Model

Moodify does not sell software buttons. It sells processing capability.

Commercial flow:

```text
submit order -> studio queue -> industrial processing -> report delivery -> high-quality audio output
```

Pricing should be supported by depth and evidence:

```text
price = variable compute cost
      + infrastructure amortization
      + expert review cost
      + report cost
      + rework / risk cost
      + quality and trust premium
```

The path upward is not "charge more because it looks expensive." It is "charge more because the process is deeper, more reproducible, better reported, and audibly stronger."

## Roadmap Anchor

Current v0.1 runtime work remains valuable because it proved the first production spine:

```text
Runtime + CLI -> logs -> summaries -> MRS -> nightly PASS evidence
```

The next direction is:

| Version | Product Form | Core Task |
| --- | --- | --- |
| v0.1 | Runtime + CLI | stable processing, logs, summary, MRS scoring |
| v0.2 | Internal Operator Console | upload, queue, status, results, report generation |
| v0.3 | Studio Back Office | customer orders, packages, staff workflow, delivery |
| v0.4 | Cloud GPU System | scheduling, deep processing, parallel jobs, cost accounting |
| v0.5 | Craft Library System | preset versioning, sample writeback, recommended processing plans |
| v1.0 | Moodify Studio OS | studio-grade acoustic industrial operating system |

> **2026-08-01 data-asset anchor:** the data asset is the compounding side of
> the product (see Two Curves). Every version above must treat each job as a
> data-collection instrument whose structured output — acoustic scans, MRS
> scores, gate decisions, review labels, craft records — flows into one
> schema'd data pipeline instead of scattered files. The pipeline is the
> prerequisite for MRS calibration credibility, craft-library compounding,
> and cross-generation measurement authority; it is scheduled as its own
> milestone (DSK-MFY-DATA-ASSET) rather than a side effect of other work.

## Cold Boundaries

The industrial story must be proven by results.

- Long processing time does not automatically mean better sound.
- Hardware spending does not automatically create a moat.
- High price must be justified by delivery evidence.
- MRS must keep being calibrated against real samples, failure cases, and human review.
- Brand narrative cannot replace engineering results.

The point of the new direction is not to make Moodify sound bigger. The point is to stop trapping Moodify under the low ceiling of consumer app logic.

Final principle:

> This is not only technology. This is industry.
