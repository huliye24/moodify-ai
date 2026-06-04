# MHP-034: Delivery Records

Status: proposed
Direction: delivery and archive layer
Depends on: MHP-033 Report Bundle System

## Context

After report generation, Moodify needs a formal delivery record. Delivery is the transition from internal processing evidence to a handoff that a studio, customer, or internal team can trust.

## Goal

Implement delivery records for final candidate selection, report handoff, archive location, and operator decision.

## Non-Goals

- Do not implement billing.
- Do not implement customer portals.
- Do not upload to external storage providers yet.

## Product Requirements

- Operator can select one candidate as final.
- Delivery record contains:
  - job id
  - candidate id
  - final audio path
  - report path
  - archive path
  - operator decision
  - notes
  - timestamp
- Job status becomes `delivered`.

## Engineering Requirements

- Add delivery JSON/JSONL storage.
- Add helper:

```text
create_delivery_record(...)
get_delivery_record(...)
```

- Add CLI/API:

```text
POST /operator/jobs/{job_id}/deliver
GET  /operator/jobs/{job_id}/delivery
moodify-runtime operator-deliver
```

- Validate that delivered candidates have an approval or explicit override.

## Acceptance Criteria

- Delivery cannot silently select a missing candidate.
- Delivery cannot use a missing report path.
- Approved candidates deliver normally.
- Reprocess/reject candidates require an override flag and reason.
- Job detail includes delivery record.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_operator_delivery.py -q
python -m pytest moodify-core-package/tests/test_api_operator.py -q
```

## Done Means

Moodify can say exactly what was delivered, why it was selected, and where the evidence lives.
