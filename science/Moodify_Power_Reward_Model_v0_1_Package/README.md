# Moodify Power Reward Model v0.1 — executable research package

This directory implements the Worker layer of the X-AWDJ methodology. It does
not claim that musical “power” has been validated. It turns the current
definition into reproducible candidate generation, measurement, data auditing,
baseline modelling, pilot gates, and a bounded DeepSeek handoff.

## Responsibility boundary

- ChatGPT / Architect: defines the research question, constructs, hypotheses,
  constraints, acceptance gates, and task contracts.
- Codex / Worker: implements deterministic code, schemas, tests, and evidence
  artifacts. Codex does not manufacture experimental findings.
- DeepSeek / Data Worker: processes supplied evidence summaries under a fixed
  rubric. It may classify `go`, `revise`, `stop`, or `inconclusive`; it may not
  change the construct or thresholds.
- Human / Judge: approves the protocol, listening labels, exceptions, and every
  consequential Go/Stop decision.

## Install and verify

```powershell
cd E:\moodify\science\Moodify_Power_Reward_Model_v0_1_Package
python -m pip install -e .[test]
python -m pytest
```

## Evidence pipeline

```powershell
pwrm generate-candidates --source source.wav --plan configs\candidate_plan.example.json --out-dir runs\pilot\candidates
pwrm audit-dataset --records data\power_pairs.jsonl --out-dir runs\pilot\evidence
pwrm train-baselines --records data\power_pairs.jsonl --out-dir runs\pilot\evidence
pwrm evaluate-pilot --audit runs\pilot\evidence\audit_summary.json --thresholds configs\pilot_thresholds_v0.1.json --out runs\pilot\evidence\pilot_summary.json
pwrm prepare-deepseek --evidence-dir runs\pilot\evidence --out-dir runs\pilot\deepseek
```

An audit command returning exit code 2 means anomalies were found. A pilot
command returning exit code 2 means `revise` or `stop`; this is expected control
flow, not a software crash.

Track-level splitting is mandatory. Loudness is controlled and separately
measured so that a model cannot pass merely by preferring louder candidates.
The clarity proxy is an engineering guard, not a perceptual truth.

See `DEEPSEEK_HANDOFF.md` for the next-stage contract.
