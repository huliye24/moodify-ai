# MOOD NETWORK 017 — Activity Model

**Authority:** MOOD-NETWORK-017 TASK.md Phase H

## Allowed public events

```ts
type ActivityKind =
  | "ResidentJoined"
  | "TaskPublished"
  | "SubmissionSubmitted"
  | "SubmissionApproved"
  | "SubmissionRejected"
  | "ReputationGranted"
  | "ApplicationRegistered"
  | "AgentRegistered"   // future
  | "NodeRegistered"    // future
  | "MIPPublished"      // future
```

## Mapping from 016 audit log

| Audit type | Activity |
|---|---|
| `TaskCreated` | `TaskPublished` |
| `SubmissionCreated` / `SubmissionResubmitted` | `SubmissionSubmitted` |
| `SubmissionApproved` | `SubmissionApproved` |
| `SubmissionRejected` | `SubmissionRejected` |
| `ReputationGranted` | `ReputationGranted` (+ delta) |
| `SubmissionWithdrawn`, `ReviewStarted`, `ChangesRequested`, `ReputationAdjusted`, `PendingRewardRecorded/Cancelled` | not surfaced |

We deliberately omit internal-only audit events from the public feed.