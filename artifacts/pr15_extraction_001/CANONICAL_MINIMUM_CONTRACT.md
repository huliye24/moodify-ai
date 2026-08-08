# Canonical Minimum Contract

This is a conceptual proposal, not production code.

## ProductionCase

Required: `case_id`, `schema_version`, immutable source asset IDs/hashes, objective/spec reference, lifecycle state, state version, transition history, current plan ID/hash, technical gate reference, human approval reference, execution record reference, verification reference, closure status, timestamps, and limitations.

## MeasurementRecord

Required: `measurement_id`, `case_id`, `asset_id`, `stage`, `metric namespace`, typed values, units, method ID/version, configuration/profile hash, implementation version, measured time, validity status, uncertainty/warnings, and provenance artifact references.

## EvidenceArtifact

Required: `artifact_id`, `case_id`, optional measurement/execution/verification linkage, artifact type/media type, content hash, byte size, producer ID/version, creation time, lineage inputs, retention/rights classification, and logical URI. Absolute local paths are not public identity.

## Rule

Required: `rule_id`, `version`, lifecycle state (`PROPOSED/EXPERIMENTAL/VALIDATED/PRODUCTION/DEPRECATED`), scope/conditions, parameters, rationale, evidence IDs, limitations/confidence, approver decision, tests, effective time, and supersession link.

## Invariants

1. IDs are stable; content-bearing records are hash-verifiable and append-only or versioned.
2. A MeasurementRecord names its method/configuration; a number without provenance is not a production measurement.
3. An EvidenceArtifact points to a case and producer; a plot alone is not a MeasurementRecord.
4. Human label, technical judgment, and artistic approval remain distinct.
5. Rules cannot become PRODUCTION without accepted evidence, tests, and explicit human authority.
6. Infrastructure states never replace ProductionCase state.
