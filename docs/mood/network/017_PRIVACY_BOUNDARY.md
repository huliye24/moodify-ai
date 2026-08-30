# MOOD NETWORK 017 — Privacy Boundary

**Authority:** MOOD-NETWORK-017 TASK.md Phase L

## Public (allowed on /network)

- Total resident count (suppressed if < 3).
- Total contributor count (suppressed if < 3).
- Total submissions, approved submissions.
- Total reputation events + positive points (no adjustment reasons).
- Total pending reward records (counts only, no units).
- Moodify as Genesis Application.
- Activity feed (privacy-safe shape, see below).
- "Coming soon" placeholders for not-yet-shipped subsystems.

## Private (NEVER on /network)

- Full wallet addresses.
- Internal review notes / reviewer identity.
- Admin metadata (e.g. session ids, ip).
- Pending reward unit amounts.
- Reputation adjustment reasons.
- Pending review queue contents.
- Submission contents for non-public fields.
- Audit log actor / previousStatus details.

## Activity feed shape

```ts
{
  type: ActivityKind,
  timestamp: string,
  taskSlug?: string,
  submissionId?: string,
  reputationDelta?: number,
}
```

No wallet addresses. No reviewer identity. No actor identity.

## Suppression policy

`count < 3` distinct Residents → hidden via `MetricValue.unavailable`.