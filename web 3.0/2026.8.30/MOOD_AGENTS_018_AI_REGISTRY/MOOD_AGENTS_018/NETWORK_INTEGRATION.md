# NETWORK INTEGRATION

017 should receive:

```ts
type AgentNetworkMetrics = {
  total: number | null;
  active: number | null;
  degraded: number | null;
  offline: number | null;
  lastActivityAt?: string;
  state: "available" | "unavailable" | "stale";
};
```

Public events:

```text
AgentRegistered
AgentActivated
AgentPaused
AgentStatusChanged
AgentTaskCompleted
AgentProofSubmitted
```

All values must come from registry / task / proof sources.
