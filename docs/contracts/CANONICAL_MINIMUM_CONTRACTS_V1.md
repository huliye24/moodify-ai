# Canonical Minimum Contracts v1

Status: normative

Schema version: `1.0`

Interchange format: canonical JSON

## Purpose

`moodify.contracts` is the single low-level vocabulary shared by Moodify's
auditory, production, evidence, learning, API, and runtime layers. Version 1
defines identity and evidence boundaries; it does not migrate subsystem
behavior.

## Common invariants

Every top-level contract is immutable, rejects unknown fields, carries an
explicit `schema_version` equal to `1.0`, and requires a timezone-aware
`created_at` value. Timestamps are normalized to UTC. Canonical IDs are opaque
UUID-derived strings with `case_`, `meas_`, `evid_`, or `rule_` prefixes.

Durable digests use `sha256:<64 lowercase hex chars>`. JSON hashes use UTF-8,
sorted keys, compact separators, and reject NaN and Infinity. Metadata and
measurement values accept only JSON-safe values.

## ProductionCase

A `ProductionCase` is a bounded unit of accountable work. It references source,
measurement, evidence, and rule identities instead of embedding their payloads.
Its intentionally small lifecycle vocabulary is `CREATED`, `ACTIVE`,
`AWAITING_HUMAN`, `COMPLETED`, `FAILED`, and `CANCELLED`. This is a universal
contract vocabulary, not a replacement for a subsystem's detailed workflow.

Human authority remains explicit through `HUMAN_REQUIRED`, `HUMAN_APPROVED`,
and `HUMAN_REJECTED`; `SYSTEM` never implies human approval. Duplicate
references and self-parent lineage are rejected.

## MeasurementRecord

A `MeasurementRecord` is one structured observation connected to a case,
source, namespace, method, and unit. It separates observation from quality
judgment. Its value, optional temporal window, and metadata must be JSON-safe;
confidence, when present, is in `[0, 1]`.

MRS is not a universal v1 field. Any future compatibility measurement must be
visibly namespaced as experimental. B-matrix is not part of this contract.

## EvidenceArtifact

An `EvidenceArtifact` describes durable evidence. Content hash and provenance
are mandatory; size and storage references are optional. Neither a Windows
absolute path nor any other machine-local path is canonical identity.

## Rule

A `Rule` is operational knowledge with an explicit status: `DRAFT`,
`EXPERIMENTAL`, `ACTIVE`, `DEPRECATED`, or `RETIRED`. An `ACTIVE` rule must cite
at least one evidence artifact. Rules cannot supersede themselves, and the
existence of a rule file never activates it implicitly.

## Provenance

Measurements and evidence embed one immutable `Provenance` value containing
producer, producer version, method, method version, and parameters hash. Human
records must identify a human-origin producer/method instead of presenting a
machine result as human authority.

## Serialization and schemas

`to_canonical_dict`, `to_canonical_json`, and `from_canonical_json` provide the
v1 interchange boundary. Checked-in JSON Schemas under `schemas/canonical` are
generated from the Pydantic models with `scripts/generate_canonical_schemas.py`;
they are not independently maintained definitions.

## Compatibility boundary

Canonical contracts do not import the auditory implementation, learning,
Android, runtime/cloud, the legacy WorkflowOrchestrator, MRS, or B-matrix.
Future migration work may add explicit legacy-to-canonical adapters outside the
contract package. Unsupported legacy fields must be reported by those adapters,
not silently discarded.
