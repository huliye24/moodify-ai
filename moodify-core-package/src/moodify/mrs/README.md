# Moodify Reality Score (MRS)

**Status:** EXPERIMENTAL research module. It is not a production quality authority, a trained AI model, or a measure of universal listener preference.

MRS is an experimental auditory-evaluation framework for studying how perceived audio quality and listening experience might be represented in a machine-readable, reviewable form.

## Purpose

Traditional measurements such as LUFS, peak level, RMS, and dynamic range describe important physical or signal-level properties. They do not, by themselves, establish whether a listener will prefer an audio result.

MRS explores how scoped evaluation may combine:

- acoustic features;
- signal characteristics;
- future human-listening preference evidence.

The aim is an AI-understandable evaluation process with explicit inputs, methods, evidence, and uncertainty. It is not a claim that the current repository has solved perceptual audio evaluation.

## Package Layout

- `metrics.py` — typed contract for normalized MRS feature inputs.
- `config.py` — transparent weights for the current rule-based baseline.
- `scoring.py` — extensible scorer protocol and deterministic baseline.
- `benchmark.py` — stable future benchmark result interface.
- `docs/` — research rationale, present metric inputs, and staged roadmap.

The existing `moodify.reality_metrics` module remains unchanged. It computes a reference-distribution distance from extracted audio features. This package does not replace or automatically invoke it; a validated adapter is future work.

## Quick Smoke Example

From `moodify-core-package` after installing the package:

```bash
python -c "from moodify.mrs import MRSFeatures, RuleBasedMRSScorer; print(RuleBasedMRSScorer().calculate(MRSFeatures(0.8, 0.7, 0.75, 0.65, 0.9)).to_dict())"
```

The example evaluates fixed normalized feature values only. It does not read audio and does not demonstrate human listening evaluation.

## Boundary

The rule-based baseline returns a technical proxy score and leaves `listening_score` as `None`. A future machine-learning, reward-model, or human-feedback scorer must be introduced through a versioned contract and validated benchmark protocol.
