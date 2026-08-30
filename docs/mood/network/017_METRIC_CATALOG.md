# MOOD NETWORK 017 — Metric Catalog

**Authority:** MOOD-NETWORK-017 TASK.md Phase C

## Metrics

| Metric | Source | Definition |
|---|---|---|
| Residents | `contribution-registry:016 (distinct residentIds)` | Residents who have at least one submission (privacy-safe upper bound). |
| Contributors | `contribution-registry:016 (distinct approved residentIds)` | Distinct Residents with at least one approved contribution. |
| Open Tasks | `contribution-registry:016` | Active ContributionTasks. |
| Submissions | `contribution-registry:016` | Total ContributionSubmissions (any status). |
| Approved Contributions | `contribution-registry:016` | Submissions with status=approved. |
| Reputation Events | `reputation-registry:016` | Append-only ReputationEvent count (public total only). |
| Pending Reward | `pending-reward-registry:016` | PendingRewardEvent count with status=pending. |
| Applications | `constant:moodify-genesis-application` | Moodify — registered as Genesis Application. |
| Agents | `package-018:pending` | Coming in Package 018. |
| Nodes | `package-019:pending` | Coming in Package 019. |
| MIPs | `package-020:pending` | Coming in Package 020. |

## MetricValue shape

```ts
{
  value: number | null,
  state: "available" | "unavailable" | "coming-soon" | "stale",
  source: string,           // provenance
  updatedAt?: string,
  definition?: string,
}
```

## Suppression

`count < 3` distinct Residents → state changes to `unavailable`, value `null`.
This prevents accidental de-anonymization of small samples.