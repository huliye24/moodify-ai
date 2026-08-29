# Metadata Data Model — Decision Template

> Engine must follow P02 metadata DB decision.

## Existing schema mapping

| Existing Table/Model | Keep | Extend | Replace Later | Notes |
|---|---|---|---|---|

## tracks

Purpose:
Logical identity for one Moodify track/source context.

Required decisions:
- primary key format
- source object relationship
- ownership relationship
- source hash uniqueness semantics
- deletion behavior

## jobs

Purpose:
One processing request.

Important:
P03 stores a `current_state` field only as a carrier.
P04 defines authoritative state semantics.

## objects

Purpose:
Index durable object artifacts.

## evidence

Purpose:
Attach evidence to job/object/claim.

## versions

Only create if existing project has no authoritative equivalent.

## Indexes

At minimum consider:

- source_hash
- track_id
- job_id
- object_key
- object content hash
- artifact_type
- evidence job/object refs

Do not optimize prematurely.
