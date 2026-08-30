# MOOD NETWORK 017 — API Contract

**Authority:** MOOD-NETWORK-017 TASK.md Phase J

## `GET /api/network/overview`

Returns full `NetworkOverview` JSON. See `types.ts`.

## `GET /api/network/activity?limit=N`

Returns `{ events: PublicActivityEvent[], count }`. `limit` capped to 1..100.

## `GET /api/network/health`

Returns:

```ts
{
  status: NetworkStatus,
  timestamp: string,
  components: {
    contribution: "available" | "unavailable" | "coming-soon" | "stale",
    reputation: ...,
    pendingReward: ...,
    agents: ...,
    nodes: ...,
  },
}
```

No DB host, no stack trace, no secret. Public-safe only.