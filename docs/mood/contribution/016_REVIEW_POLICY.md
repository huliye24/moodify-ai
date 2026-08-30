# MOOD CONTRIBUTION 016 — Review Policy

**Authority:** 016 TASK.md Phase F

## Reviewer capabilities

A reviewer (authenticated Resident with reviewer scope) can:

1. View pending queue (`GET /api/contribution/review/queue`).
2. View submission detail (full evidence + private reviewer note if own past review).
3. Start review (`under_review`).
4. Decide:
   - Approve → grants Reputation + records Pending Reward
   - Request changes → `changes_requested` (Resident may resubmit)
   - Reject → terminal

## Attribution

Every review action writes a `ContributionAuditEvent` with:

- `actorResidentId` (the reviewer)
- `submissionId`
- `previousStatus` → `nextStatus`
- `note` (optional reviewer note — never exposed publicly)
- `createdAt`

## Self-review prevention

`INV-016-02`: a Resident cannot review their own submission. The state machine
rejects `startReview` with `INV-016-02` and the `review()` method returns
`{ ok: false, reason: "INV-016-02: ..." }`.

## Idempotency

`INV-016-09`: a second `approve` on an already-approved submission is a
no-op. The registry's `bySubmission` map tracks submission IDs that have
already received reputation / pending reward.

## Private notes

Reviewer notes are stored on the submission record. Public serializers
(`apps/web/api/.../submissions/route.ts` and `/api/resident/me/contributions`)
deliberately omit `reviewerNote`. This satisfies `INV-016-10`.

## Implementation

- `apps/web/lib/mood/contribution/registry.ts` exposes `startReview`, `review`, `applyDecision`.
- API route at `/api/contribution/submissions/[id]/review`.
- Future admin console (`/admin/contributions`) is reserved for a later package.