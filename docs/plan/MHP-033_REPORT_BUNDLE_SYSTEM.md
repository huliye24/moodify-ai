# MHP-033: Report Bundle System

Status: proposed
Direction: report-first industrial workflow
Depends on: MHP-032 Operator Job Runner

## Context

MHP-031 and MHP-032 connect jobs to runtime evidence. MHP-033 makes reports a first-class product output rather than a side file created after processing.

## Goal

Create a standard Operator Report Bundle for each job.

```text
summary.md
summary.json
candidate_versions.jsonl
score_results.jsonl
gate_decisions.jsonl
delivery.md
manifest.csv
```

## Non-Goals

- Do not design customer-facing visual PDFs yet.
- Do not add chart rendering unless existing evidence already exists.
- Do not store heavy audio files in the report bundle.

## Product Requirements

- Every completed or failed job has a report bundle path.
- The bundle explains:
  - input identity
  - processing depth
  - candidate versions
  - MRS / pseudo MRS interpretation
  - gate decisions
  - selected next action
- Operators can read the report without opening raw logs.

## Engineering Requirements

- Add `build_operator_report_bundle(job_id)` using existing detail data.
- Add durable paths under:

```text
reports/operator_runs/{job_id}/
```

- Add CLI/API:

```text
POST /operator/jobs/{job_id}/report
GET  /operator/jobs/{job_id}/report
moodify-runtime operator-report
```

- Keep full raw logs referenced, not duplicated, unless a compact tail is needed.

## Acceptance Criteria

- Report bundle is generated from a real attached run.
- JSON/JSONL files validate.
- Markdown summary includes gate counts and candidate ranking.
- The job record stores `report_path`.
- Tests cover missing detail, failed candidates, and all-pass candidates.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_operator_report_bundle.py -q
python -m pytest moodify-core-package/tests/test_api_operator.py -q
```

## Done Means

A Moodify result is no longer just an audio output. It is an explainable industrial report bundle.
