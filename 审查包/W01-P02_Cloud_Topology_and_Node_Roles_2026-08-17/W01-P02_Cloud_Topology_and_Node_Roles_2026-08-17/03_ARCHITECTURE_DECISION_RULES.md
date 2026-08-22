# W01-P02 Architecture Decision Rules

## R1 — One Song before scale

Every architectural choice must first improve the ability to run one complete song safely.

## R2 — One node, one primary role

A node may have secondary roles, but must have one primary responsibility.

## R3 — No invisible authority

Job authority, metadata authority, object authority and playback authority must each be explicit.

## R4 — Files and metadata are different

- audio/render/evidence binary objects → object storage
- job/track/state/version/reference metadata → database

## R5 — Avoid permanent coupling to local disk

Worker local disk is scratch unless explicitly approved otherwise.

## R6 — Prefer existing infrastructure

Do not introduce Redis, K8s, Kafka or new servers unless current evidence requires them.

## R7 — Client never owns long-term cloud credentials

Android/iOS must not receive long-term OSS/database secrets.

## R8 — Architecture decision != deployment fact

Target topology must not be presented as deployed reality.

## R9 — Capacity claims require evidence

No synthetic benchmark claims.

## R10 — Revisit triggers are mandatory

Every important choice must say when it should be reconsidered.
