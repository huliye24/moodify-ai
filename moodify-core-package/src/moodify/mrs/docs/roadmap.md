# MRS Research Roadmap

**Status:** Directional research plan; stages are not delivery promises.

## Stage 1: Rule-based Evaluation

Define versioned feature contracts, transparent weights, deterministic score calculation, and evidence records. The current package supplies an initial research baseline only.

## Stage 2: Human Preference Dataset

Design a consented, rights-aware dataset and listening protocol with explicit task definitions, reviewer metadata, disagreement handling, and data-governance rules. No such dataset is created by this module.

## Stage 3: Reward Model

Evaluate whether a model can predict bounded preference or quality judgments for defined tasks. This requires held-out benchmarks, calibration, uncertainty reporting, and human escalation rules before any automated use.

## Stage 4: Auditory Foundation Model

Investigate broader audio representations only after the preceding evidence, governance, and validation gates are met. A foundation model is not currently implemented or claimed.

## Research Gates

- Metric definitions and score versions must be reproducible.
- A benchmark must state data provenance and the population/task it represents.
- Human preference claims require human-evaluation evidence.
- Any automation must remain within its validated scope and fail safely outside it.
