# MFY-CR-P08 — EXTERNAL SERVICE BOUNDARY

## Decision: stems stay OFF (Option A)

Per P08 §11, v0.1 records `STEM_RECOMMENDED` semantics but never calls an
external stem service. LALAL.AI / Audiolla are NOT integrated in this package.

| Aspect | v0.1 status |
|---|---|
| AUTO_STEM | false (capabilities reports `stems_available:false`) |
| LALAL adapter | not implemented |
| Audiolla adapter | not implemented |
| Stem sub-jobs | none |
| Billed retry protection | structurally enforced: no external billed call exists; any future adapter MUST register intent before submit (see IDEMPOTENCY_AND_RETRY) |

## Boundary for the future

When stems are added they must sit behind an adapter with:
`capabilities() / submit() / status() / result() / failure() / cost_estimate()`
— never scattered HTTP calls from reconstruction core, with timeout,
failure semantics, artifact provenance, no silent fallback, quality
verification, and no retention beyond policy. That work is NOT part of P08.

## Resource accounting

`ResourceUsage.external_api_usage` exists and is recorded (0 in v0.1); the
field is ready for stem/API accounting when the adapter lands.
