# MOOD AGENTS 018 — Network Integration

**Authority:** MOOD-AGENTS-018 TASK.md Phase N

## 017 /network reads

`NetworkObservatory.agents()` now reads from `agentRegistry.counts()`:

```ts
{
  total: number,
  active: number,
  degraded: number,
  offline: number,
}
```

`source` field set to `agent-registry:018`.

## Activity events

`NetworkObservatory.activity()` now includes:

- `AgentRegistered` (on agent.createdAt)
- `AgentTaskCompleted` (on agent.lastTaskAt)

Future (018.1+):
- `AgentStatusChanged`
- `AgentProofSubmitted`

## What 019 should consume

Same pattern as 018, applied to `NodeRegistry`:

- `nodes.total`, `nodes.active`, `nodes.degraded`, `nodes.offline`
- `NodeRegistered`, `NodeActivated`, `NodeStatusChanged`, `NodeServiceProofRecorded`

`019` should NOT reuse `AgentRecord` — see 018 §P (Agent / Node Separation).