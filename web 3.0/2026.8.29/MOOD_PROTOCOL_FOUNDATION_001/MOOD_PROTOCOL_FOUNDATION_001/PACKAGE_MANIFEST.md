# Package Manifest

**Task:** MOOD Protocol Foundation 001  
**Scope:** Mainnet facts layer only  
**Risk posture:** Read-only discovery + repository changes; no chain writes

| File | Purpose |
|---|---|
| `START_HERE.md` | Paste-ready Codex launch instruction |
| `CODEX_TASK.md` | Full engineering task specification |
| `ACCEPTANCE_GATE.md` | Definition of done and P0 gates |
| `IMPLEMENTATION_CHECKLIST.md` | Ordered execution checklist |
| `SECURITY_BOUNDARY.md` | Explicit custody/on-chain safety boundary |
| `ROLLBACK.md` | Repository-only rollback procedure |
| `EVIDENCE_TEMPLATE.md` | Mainnet fact evidence template |
| `protocol/mainnet.schema.json` | Canonical config schema starter |
| `protocol/mainnet.template.json` | Intentionally unresolved safe template |
| `protocol/README.md` | Mainnet fact-model rules |
| `scripts/validate-mainnet-config.mjs` | Dependency-free validator starter |
| `scripts/generate-mainnet-lock.mjs` | Deterministic lock artifact generator |
| `examples/MAINNET_FACT_REPORT.example.md` | Discovery report structure |

## Package completion condition

This ZIP is a **task package**, not a deployment artifact. Its scripts and templates are intended for Codex to integrate into the repository after inspecting the current codebase and authority files.
