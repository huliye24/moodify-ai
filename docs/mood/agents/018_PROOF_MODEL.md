# MOOD AGENTS 018 — Proof Model

**Authority:** MOOD-AGENTS-018 TASK.md Phase I

## Proof record

```ts
{
  id: string,
  agentId: string,
  taskRunId?: string,    // bound to real task if applicable
  proofType:
    | "artifact"
    | "report"
    | "commit"
    | "analysis"
    | "verification"
    | "other",
  uri?: string,         // public URI (not secret endpoint)
  hash?: string,        // optional content hash
  summary: string,
  createdAt: string,
}
```

## Hard rule

INV-018-04: **proof must bind to real task / activity.**

If a proof has no `taskRunId` and no concrete `proofType`, it produces no
reputation side-effect. (Reputation side-effects are governed by 016.)