# W01-P03 Acceptance Checklist

## Gates
- [ ] P00 Reality loaded
- [ ] P01 Canon loaded
- [ ] P02 Topology loaded
- [ ] metadata DB selected
- [ ] object storage role selected
- [ ] secret ownership known
- [ ] network paths known

## Object identity
- [ ] object key convention finalized
- [ ] source immutable
- [ ] source hash defined
- [ ] object manifest defined
- [ ] no original filename dependency for identity

## Metadata
- [ ] tracks modeled
- [ ] jobs modeled without redefining P04 state semantics
- [ ] objects modeled
- [ ] evidence modeled
- [ ] versions reused or modeled without duplicate authority

## Provenance
- [ ] READY render traces to source
- [ ] render traces to producer Job
- [ ] pipeline/tool/profile versions recorded
- [ ] evidence has subject/claim
- [ ] ownership independent of hash

## Migration
- [ ] current → target mapping complete
- [ ] DB migration reversible/non-destructive
- [ ] OSS provisioning policy complete
- [ ] unauthorized writes remain BLOCKED

## Tests
- [ ] repeated source test
- [ ] immutable source test
- [ ] provenance test
- [ ] evidence test
- [ ] idempotency test
- [ ] missing object detection
- [ ] orphan object detection
- [ ] no large blobs in DB
- [ ] no long-lived mobile cloud secrets

## Scope
- [ ] no second state machine
- [ ] no scheduler/retry engine
- [ ] no audio pipeline expansion
- [ ] no playback implementation

## Handoff
- [ ] P04 handoff complete
- [ ] stop after P03
