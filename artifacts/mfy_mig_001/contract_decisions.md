# MFY-MIG-001 Contract Decisions

| Area | Decision | Reason |
|---|---|---|
| Package authority | `moodify.contracts` is the only canonical package | Prevent another competing vocabulary |
| Schema version | Strict literal `1.0` | Prevent silent reinterpretation |
| Mutability | Frozen models with forbidden extras | Evidence changes create new values |
| IDs | UUID4-derived opaque prefixed strings | Stable type recognition without a new dependency |
| Timestamp | Require aware input; normalize to UTC | Naive time is ambiguous |
| Lifecycle | Six-state universal enum | Useful cross-layer vocabulary without copying PPE's detailed state machine |
| Authority | Explicit system/human states | Machine judgment cannot impersonate human approval |
| References | Tuples; duplicates rejected | Deterministic, immutable lineage and no silent normalization |
| Provenance | Nested immutable value | Reuse one exact producer/method definition without flattening drift |
| Measurement value | JSON-safe scalar or compact structure | Interoperable observations without arbitrary Python objects |
| Observation boundary | No universal quality field | Measurement remains separate from judgment |
| Evidence location | Optional URI/logical path | Machine-local paths are not identity |
| Rule activation | `ACTIVE` requires evidence IDs | Authority must be evidence-backed |
| Serialization | Sorted compact UTF-8 JSON | Deterministic round trips and hashes |
| Schemas | Generated from Pydantic models | Avoid hand-maintained duplicate definitions |
| Legacy adapters | Deferred | No adapter is needed to prove v1; speculative code would expand authority |
| MRS | Not included | It remains experimental rather than universal truth |
| B-matrix | Not included | It remains research-only |
