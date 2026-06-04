# MHP-040: Studio OS Alpha

Status: proposed
Direction: integrated industrial alpha
Depends on: MHP-039 MRS Calibration Lab

## Context

MHP-031 through MHP-039 create the pieces: jobs, runtime, reports, delivery, UI, back office, craft library, cloud scheduling, and MRS calibration. MHP-040 integrates them into the first Moodify Studio OS alpha.

## Goal

Ship an internal alpha where one studio workflow can run end to end.

```text
Client / Project / Order
  -> Operator Job
  -> Runtime / Scheduler
  -> Candidate Versions
  -> MRS Gate
  -> Report Bundle
  -> Delivery Record
  -> Craft Library Writeback
  -> Calibration Feedback
```

## Non-Goals

- Do not launch public SaaS.
- Do not promise unattended perfection.
- Do not remove the CLI path.
- Do not hide uncertainty in reports.

## Product Requirements

The alpha must support:

- one internal studio operator;
- one project with multiple jobs;
- at least one completed delivery;
- one report bundle;
- one craft writeback;
- one calibration audit artifact.

## Engineering Requirements

- Add alpha runbook.
- Add integration smoke test with fake or lightweight audio fixtures.
- Add system status endpoint:

```text
GET /studio-os/status
```

- Add dashboard summary:
  - active jobs
  - pending gates
  - delivered jobs
  - craft records
  - scheduler runs
  - calibration warnings

## Acceptance Criteria

- End-to-end internal demo can be run from a clean checkout.
- All generated heavy files remain ignored.
- Alpha report documents what passed, what failed, and what remains manual.
- Cloud server can reproduce the demo.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_studio_os_alpha.py -q
python -m pytest moodify-core-package/tests/test_api_operator.py -q
python -m pytest moodify_runtime/tests -q
```

## Done Means

Moodify has a coherent internal Studio OS alpha, not just disconnected runtime tools.
