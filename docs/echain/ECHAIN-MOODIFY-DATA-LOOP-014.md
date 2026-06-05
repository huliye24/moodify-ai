# ECHAIN-MOODIFY-DATA-LOOP-014: Data Optimization Loop E-Chain 54

## 1. Chain Metadata

- **E-Chain ID**: ECHAIN-MOODIFY-DATA-LOOP-014
- **Owner**: Raphael Davad
- **Project**: Moodify
- **Status**: SEALED ✅ — E-Chain 014 closed 2026-06-05. 54 MHPs, 88 tests, 3 NEMs complete.
- **Start Date**: 2026-06-05
- **Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18
- **Parent**: ECHAIN-MOODIFY-NIGHT-RESULT-013
- **Target Gate**: SEALED
- **Primary Goal**: convert nightly runtime data into software, scoring, craft, and operator improvements.
- **Runner Constraint**: DeepSeek v4 cost mode. Keep each model task small, schema-bound, and independent.
- **Worker Protocol**: `docs/protocol/AEP_WORKER_PROTOCOL.md`

## 2. Phase Transition Target

```text
nightly result data -> continuous software optimization loops
```

Moodify now produces useful runtime artifacts: `summary.json`, `manifest.csv`, queue records, tidal events, daily reports, MRS deltas, penalty flags, and craft memory. These artifacts should not remain passive reports. They should drive repeatable loops that decide what to tune, what to block, what to rerun, and what code or configuration needs improvement.

## 2A. DeepSeek v4 Execution Rule

This E-Chain must be runnable by a cheaper model with limited context. Do not ask the model to inspect the repository or infer across many files.

Use this contract:

```text
one input record -> one short decision -> one JSON object
```

Model task limits:

- input per task: one run-level record or one task-level record;
- max source fields: 12;
- max output fields: 8;
- max recommendation count: 3;
- no multi-file reasoning;
- no code editing;
- no hidden assumptions;
- output JSON only.

The script layer handles extraction, grouping, sorting, and report merging. DeepSeek v4 only classifies a small record into a loop, severity, reason, and next action.

Validation and final selection should use:

```bash
python3 scripts/aep_worker_protocol.py validate --help
python3 scripts/aep_worker_protocol.py select --help
```

## 3. Last-Night Signals

From `outputs/20260605_000141/summary.json`:

| Signal | Evidence | Loop Implication |
|--------|----------|------------------|
| Runtime execution works | 4 selected tasks, 4 success, 0 failed | The loop can run without first fixing basic execution. |
| Pseudo MRS and MRS Open disagree | `warm_vocal`/`wide_space` on vocal_folk had negative pseudo delta but large positive MRS Open delta | Scoring calibration loop is needed. |
| Penalty flags matter | `wide_space` on piano and `clean_master` on vocal_folk triggered `over_dark` | Penalty-driven craft/preset loop is needed. |
| Fatal error still occurred | summary recorded missing `daily_run.log` | Runtime reliability loop is needed. |

## 4. Four Data Loops

For DeepSeek v4, each loop is a separate micro-task type. Do not combine loops in one prompt.

### Loop A: Runtime Reliability Loop

```text
run summary + queue + events
  -> failure taxonomy
  -> root cause
  -> runtime fix task
  -> rerun
  -> lower failure/fatal rate
```

Primary metrics:

- task success rate;
- fatal error count;
- missing artifact count;
- phase duration;
- retry count.

DeepSeek task:

```text
Input: run_id, success, failed, fatal_error, missing_artifacts
Output: severity, reason, next_action
```

### Loop B: Scoring Calibration Loop

```text
pseudo MRS + MRS Open + penalty flags + human review
  -> disagreement matrix
  -> calibration proposal
  -> threshold/weight update
  -> rerun
  -> higher score agreement
```

Primary metrics:

- sign agreement between pseudo delta and MRS Open delta;
- penalty precision;
- false positive / false negative gate cases;
- per-genre score drift.

DeepSeek task:

```text
Input: task_id, sample_id, preset, pseudo_delta_mrs, delta_mrs_open_v031, score_direction_disagreement
Output: severity, reason, next_action
```

### Loop C: Craft/Preset Selection Loop

```text
sample + preset + MRS delta + penalty flags
  -> preset outcome table
  -> accepted/candidate/rejected craft memory
  -> selector policy update
  -> rerun
  -> better preset choice rate
```

Primary metrics:

- preset win rate by sample class;
- over_dark rate by preset;
- average MRS Open delta by preset;
- accepted craft record count.

DeepSeek task:

```text
Input: task_id, sample_id, preset, delta_mrs_open_v031, mrs_open_flags
Output: preset_verdict, reason, next_action
```

### Loop D: Operator Report Loop

```text
night result bundle + morning brief
  -> PASS/HOLD/REWORK decision
  -> next MHP
  -> runbook update
  -> next night run
  -> reduced manual reconstruction
```

Primary metrics:

- artifact completeness;
- morning review time;
- X-CLP score;
- next-action clarity.

DeepSeek task:

```text
Input: run_id, fatal_error, task_count, disagreement_count, flagged_count
Output: morning_decision, reason, next_mhp
```

## 5. Three-NEM Structure

| NEM | Role | MHP Range | Purpose | Gate |
|-----|------|-----------|---------|------|
| NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe NEM | MHP-791 to MHP-808 | Map existing artifacts, define loop schemas, extract last-night metrics, and choose first optimization targets. | Gate 1: ADOPT / HOLD / DROP |
| NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build NEM | MHP-809 to MHP-826 | Build collectors, scorecards, disagreement matrices, craft outcome tables, and recommendation writers. | Gate 2: ADOPT / HOLD / ROLLBACK |
| NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System NEM | MHP-827 to MHP-844 | Standardize nightly learning loops, morning review, regression gates, and software optimization backlog. | Gate 3: SEALED / EXTEND / REWORK |

## 6. Full MHP Index

| MHP | Type | NEM | Plan-6 | Title |
|-----|------|-----|--------|-------|
| 791 | E | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6A: Loop Boundary | Define Continuous Optimization Loop Map |
| 792 | E | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6A: Loop Boundary | Inventory Existing Night Data Artifacts |
| 793 | V | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6A: Loop Boundary | Extract Last-Night Metrics Snapshot |
| 794 | V | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6A: Loop Boundary | Define Optimization Decision Taxonomy |
| 795 | S | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6A: Loop Boundary | Write Data Loop Runbook |
| 796 | N | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6A: Loop Boundary | Data Loop Probe Backlog |
| 797 | E | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6B: DeepSeek Micro Tasks | Define DeepSeek v4 JSON Schema |
| 798 | E | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6B: DeepSeek Micro Tasks | Generate Runtime Reliability Task JSONL |
| 799 | V | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6B: DeepSeek Micro Tasks | Generate Scoring Calibration Task JSONL |
| 800 | V | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6B: DeepSeek Micro Tasks | Generate Craft/Preset Task JSONL |
| 801 | S | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6B: DeepSeek Micro Tasks | Merge DeepSeek JSON Outputs |
| 802 | N | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6B: DeepSeek Micro Tasks | Pick Next Three Optimization Tasks |
| 803 | E | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6C: Feasibility Gate | Define Data Loop SLO |
| 804 | E | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6C: Feasibility Gate | Run Two-Cycle Learning Probe |
| 805 | V | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6C: Feasibility Gate | Validate Recommendation Replayability |
| 806 | V | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6C: Feasibility Gate | Validate Optimization Backlog Quality |
| 807 | S | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6C: Feasibility Gate | Data Loop Probe Decision |
| 808 | N | NEM-MOODIFY-DATA-LOOP-PROBE-042 | Probe Plan-6C: Feasibility Gate | Data Loop Build Entry |
| 809 | E | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6A: Data Collectors | Define NightMetricRecord Schema |
| 810 | E | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6A: Data Collectors | Implement Summary Collector |
| 811 | V | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6A: Data Collectors | Implement Tidal Event Collector |
| 812 | V | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6A: Data Collectors | Implement Queue Collector |
| 813 | S | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6A: Data Collectors | Collector Unit Tests |
| 814 | N | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6A: Data Collectors | Collector Build Report |
| 815 | E | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6B: Recommendation Engine | Implement Score Disagreement Recommender |
| 816 | E | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6B: Recommendation Engine | Implement Penalty-Driven Preset Recommender |
| 817 | V | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6B: Recommendation Engine | Implement Runtime Reliability Recommender |
| 818 | V | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6B: Recommendation Engine | Implement Operator Next-MHP Writer |
| 819 | S | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6B: Recommendation Engine | Recommendation Engine Tests |
| 820 | N | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6B: Recommendation Engine | Recommendation Gate Report |
| 821 | E | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6C: Loop Runner | Add Data Loop CLI |
| 822 | E | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6C: Loop Runner | Add Data Loop Report Writer |
| 823 | V | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6C: Loop Runner | Add Craft Memory Writeback Hook |
| 824 | V | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6C: Loop Runner | Add MRS Calibration Proposal Hook |
| 825 | S | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6C: Loop Runner | Data Loop Integration Smoke |
| 826 | N | NEM-MOODIFY-DATA-LOOP-BUILD-043 | Build Plan-6C: Loop Runner | Data Loop System Entry |
| 827 | E | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6A: Standardization | Data Loop SOP |
| 828 | E | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6A: Standardization | Morning Learning Review Checklist |
| 829 | V | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6A: Standardization | Metric Schema Versioning |
| 830 | V | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6A: Standardization | Optimization Decision Standard |
| 831 | S | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6A: Standardization | Data Loop Standardization Audit |
| 832 | N | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6A: Standardization | System Gate Entry |
| 833 | E | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6B: Product Integration | Operator Dashboard Learning View |
| 834 | E | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6B: Product Integration | Craft Library Learning Feed |
| 835 | V | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6B: Product Integration | MRS Calibration Review Feed |
| 836 | V | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6B: Product Integration | Release Candidate Learning Gate |
| 837 | S | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6B: Product Integration | Product Integration Smoke |
| 838 | N | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6B: Product Integration | Product Gate Report |
| 839 | E | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6C: Seal and Next Entry | Data Loop Manifest Version |
| 840 | E | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6C: Seal and Next Entry | Ownership Map |
| 841 | V | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6C: Seal and Next Entry | Regression Evidence Pack |
| 842 | V | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6C: Seal and Next Entry | Next E-Chain Candidates |
| 843 | S | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6C: Seal and Next Entry | Gate 3 Seal Decision |
| 844 | N | NEM-MOODIFY-DATA-LOOP-SYSTEM-044 | System Plan-6C: Seal and Next Entry | Close E-Chain |

## 7. Tonight Minimum Run

Run Probe Plan-6A only. The executable entry is `docs/plan/MHP-795_WRITE_DATA_LOOP_RUNBOOK.md`.

It writes:

- `last_night_metric_snapshot.json`;
- `deepseek_tasks.jsonl`;
- `deepseek_prompt.md`;
- `expected_output_schema.json`.

DeepSeek v4 should process `deepseek_tasks.jsonl` one line at a time.
After model calls, validate outputs with `scripts/aep_worker_protocol.py`.

## 8. Gate 1 Definition

Gate 1 ADOPT requires:

- one metric snapshot exists;
- one DeepSeek JSONL task file exists;
- at least one optimization signal is identified;
- each signal maps to exactly one software action type: code fix, config change, preset/craft policy, scoring calibration, or operator review;
- every model output validates as JSON with `task_id`, `loop`, `severity`, `reason`, and `next_action`;
- the next run can verify whether the action helped.
