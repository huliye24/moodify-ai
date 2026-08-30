# MOOD CONTRIBUTION 016 — State Machine

**Authority:** 016 TASK.md Phase D

## Single authoritative state machine

```text
submitted ──► under_review ──► changes_requested ──► submitted
   │              │                  (loop)
   │              ├─► approved   (terminal, grants reputation + pending reward)
   │              ├─► rejected   (terminal)
   │              └─► changes_requested
   │
   └─► withdrawn (terminal)
```

## Forbidden transitions

- `submitted → approved` (must pass through review)
- `approved → submitted` (no auto-revert)
- `rejected → approved` (no auto-approve)
- `withdrawn → approved` (no auto-approve)
- `draft → implemented` (Phase F reserved)

## Implementation

`apps/web/lib/mood/contribution/state-machine.ts` exposes:

- `isTransitionAllowed(from, to): boolean`
- `assertTransition(from, to, opts)` — throws on invalid; `adminOverride` is explicitly disabled in 016.

State transitions are **never** controlled by the frontend. The frontend may
display buttons, but the actual status mutation is performed by the registry on
the server. API routes call `contributionRegistry.review(...)` and are the only
entry points to mutate submissions.

## Override path (reserved)

The state machine accepts an `{ adminOverride?: true }` option but currently
ignores it. Any future admin-override capability must come through a future
package (governance / emergency), not 016.