# MOOD NODES 019 — Capacity Model

**Authority:** MOOD-NODES-019 TASK.md Phase F

## Capacity fields (all optional)

```ts
{
  cpuCores?: number,
  memoryGb?: number,
  gpuModel?: string,
  gpuCount?: number,
  storageGb?: number,
  bandwidthMbps?: number,
  maxConcurrentJobs?: number,
}
```

## Invariant

INV-019-06: capacity unknown → not forged. The registry stores `undefined`
rather than guessing defaults.

## Public capacity

- CPU core count
- Memory class
- GPU model
- Storage class
- max concurrent jobs

## Never public

- exact disk path
- private subnet
- cloud billing data
- internal instance ID