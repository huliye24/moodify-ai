# Acceptance Matrix

| ID | Deliverable | Acceptance evidence | Forbidden shortcut |
|---|---|---|---|
| A1 | DeepSeek audit | 18 valid outputs plus rejection log | prose-only summary |
| A2 | Treatment truth | regenerated count equals source count; missing three remain explicit | fabricated records |
| A3 | Aggregator robustness | tests cover empty, malformed, ignored type, encoding, and deterministic order | hand-editing derived summary only |
| A4 | Evidence bundle | required fields validated; artifacts hashed and traceable | screenshots without source IDs |
| A5 | Craft write-back gate | failed/unapproved/incomplete evidence is rejected by tests | trusting MRS alone |
| A6 | Failure containment | negative tests preserve source and expose actionable errors | catching all exceptions silently |
| A7 | Repeatability | two equivalent runs compared under a declared tolerance/hash rule | single successful run |
| A8 | Recovery | retry/interruption/partial-output behavior tested | deleting evidence to hide failure |
| A9 | Compatibility | historical fixture loads, migrates, or fails explicitly | assuming old artifacts work |
| A10 | Rights gate | pending sources remain unprocessed and machine-visible | inferred consent |
| A11 | Engineering log | commands, exit codes, paths, decisions, owners recorded | retrospective narrative without raw evidence |
| A12 | Inheritance | failure/standard/craft/product-history ledgers updated | comments only in chat |
| A13 | Final verification | targeted + relevant full suites pass with no unexplained warnings | removing tests or narrowing scope |

## Final Judge Checklist

- [ ] Every task ID has a terminal state.
- [ ] Every code change has a regression test.
- [ ] Every state-changing path has recovery or explicit irreversibility documentation.
- [ ] Every generated claim resolves to source evidence.
- [ ] No rights-pending audio was processed.
- [ ] No automated metric is presented as professional listening approval.
- [ ] Repeat-run evidence exists.
- [ ] Compatibility behavior is explicit.
- [ ] All logs use stable run IDs and absolute or repository-relative artifact paths.
- [ ] Remaining risk and owner are visible.

