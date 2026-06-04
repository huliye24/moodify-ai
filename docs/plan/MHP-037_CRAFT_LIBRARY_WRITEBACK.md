# MHP-037: Craft Library Writeback

Status: proposed
Direction: industrial memory and moat
Depends on: MHP-036 Studio Back Office

## Context

The long-term moat is not a single preset or algorithm. It is the accumulated craft library: which processing chains worked, where they failed, and how they evolved.

## Goal

Turn completed jobs and delivery decisions into reusable Craft Records.

## Non-Goals

- Do not train a model yet.
- Do not auto-adopt every successful run.
- Do not treat one MRS improvement as proof of craft stability.

## Product Requirements

Craft Records should include:

- craft id
- source job id
- source candidate id
- audio class / sample metadata
- preset or chain
- parameters if available
- expected improvement
- risk conditions
- failure cases
- MRS statistics
- operator notes
- version history
- adoption status: `experimental`, `candidate`, `stable`, `adopted`

## Engineering Requirements

- Add craft-library schema and storage.
- Add writeback function:

```text
writeback_delivery_to_craft_record(...)
```

- Add API/CLI:

```text
POST /operator/jobs/{job_id}/writeback-craft
GET  /craft/records
moodify-runtime craft-writeback
```

## Acceptance Criteria

- Delivered candidate can create a craft record.
- Rejected/reprocess candidates can create failure records.
- Craft records keep source lineage.
- UI can list craft records by status.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_craft_writeback.py -q
```

## Done Means

Every serious job can become industrial memory.
