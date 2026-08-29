# Invalidation Matrix

| Change | Decode | Measurements | Representation | Events | Judgment/Evidence |
|---|---:|---:|---:|---:|---:|
| Source bytes | invalidate | invalidate | invalidate | invalidate | invalidate |
| Measurement registry/version | invalidate by current analysis identity | invalidate | invalidate | invalidate | invalidate |
| Representation version | invalidate by current analysis identity | invalidate by current conservative identity | invalidate | invalidate | invalidate |
| Rule version | reuse | reuse | reuse | reuse | invalidate |
| Report presentation only | reuse | reuse | reuse | reuse | reuse evidence; report is run-only |

The representation change policy is intentionally conservative today; finer node-scoped identity is future optimization, not a correctness defect.
