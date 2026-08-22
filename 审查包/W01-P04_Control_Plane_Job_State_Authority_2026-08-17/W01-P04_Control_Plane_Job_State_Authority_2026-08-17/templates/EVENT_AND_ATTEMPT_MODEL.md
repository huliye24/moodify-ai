# Event & Attempt Model

## job_events

Append-only audit.

Suggested fields:

- event_id
- job_id
- track_id
- attempt_id
- event_type
- actor_type
- actor_id
- from_state
- to_state
- stage
- occurred_at
- correlation_id
- payload_ref
- failure_code

## attempts

Suggested fields:

- attempt_id
- job_id
- attempt_number
- worker_id
- lease_id
- fencing_token
- started_at
- ended_at
- outcome
- failure_code
- resource_summary
- output_refs
- log_ref
- evidence_refs

## Authority Rule

- `jobs.current_state` = current authority
- `job_events` = audit/reconstruction evidence
- `attempts` = execution history

Do not derive live authority by “last event wins” unless that is explicitly selected as the canonical event-sourcing architecture.
