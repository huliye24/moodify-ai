# P07 Pipeline Protocol

Reuses Data Factory authority (no second factory): ProductionCase,
Measurement Record, Evidence Artifact, algorithmic review, node worker,
repeatable case directory. Serial batch (concurrency=1), idempotent on
(case_id, source_hash), failure-preserving, deterministic record IDs,
versioned (RECORD_VERSION / BATCH_VERSION). Threshold updates only as
PROPOSED_RULE_UPDATE (independent review required). No online learning.
