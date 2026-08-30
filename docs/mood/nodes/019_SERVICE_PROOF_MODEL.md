# MOOD NODES 019 — Service Proof Model

**Authority:** MOOD-NODES-019 TASK.md Phase K

## Proof record

```ts
{
  id: string,
  nodeId: string,
  proofType: "health" | "compute-job" | "inference" | "storage-integrity" | "verification",
  startedAt?: string,
  completedAt: string,
  status: "passed" | "failed",
  artifactUri?: string,
  artifactHash?: string,
  summary: string,
}
```

## Hard rule

INV-019-07: **proof must bind to real Node.** proof.nodeId must exist in the
NodeRegistry. Otherwise the registry throws `node-not-found`.

Service Proof is the foundation for any future Node Reputation / Rewards.
019 does not compute Token Reward.