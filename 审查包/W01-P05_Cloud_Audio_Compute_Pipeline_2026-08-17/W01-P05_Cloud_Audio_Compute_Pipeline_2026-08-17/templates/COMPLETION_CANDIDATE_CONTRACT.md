# CompletionCandidate Contract

## Required Fields

- job_id
- track_id
- attempt_id
- lease_id / fencing identity
- pipeline_version
- production_fingerprint
- source_object_id
- ready_candidate_object_id
- supporting_object_ids
- evidence_refs
- verification_result
- stage_results
- resource_summary
- completed_at

## Submission Rule

Pipeline submits candidate to control plane.

Control plane validates:

- attempt still authoritative
- lease/fencing valid
- objects registered
- verification PASS
- required evidence exists

Only control plane may advance lifecycle toward READY.
