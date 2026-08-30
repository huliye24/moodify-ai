# 020 — Implementation Policy

## Definition

A MIP enters `implemented` status only after at least one concrete
implementation step has been recorded. A MIP in `accepted` status is a
*promise* to implement; a MIP in `implemented` status is a *fact* of
implementation.

## Required Implementation References

At least one of:

- a commit SHA in the repository.
- a PR URL (open or merged).
- a deployed route URL.
- a policy doc path under `docs/`.
- a config change recorded in the registry.
- a database migration reference.

The reference must be:

- verifiable by a third party (i.e. URL, SHA, or path).
- timestamped.
- attributable to a Maintainer (`recordedBy`).

## What Counts as Implementation

### Counts

- Shipping a route, API, or UI change referenced by the MIP.
- Updating a canonical policy doc to reflect the MIP.
- Recording a config / migration that activates the change.

### Does NOT Count

- Discussion threads.
- Author intent statements.
- Self-reported "done" without an external reference.
- Acceptance of a future-token-vote proposal (forbidden by 020).

## Multi-Step Implementations

A MIP may have many implementation references. Each reference is recorded
with its own `recordedAt` and `recordedBy`. The MIP remains in `accepted`
status until at least one reference exists and a Maintainer transitions it
to `implemented`.

## Implementation → Canon Updates

Implementation of a MIP that affects canon requires a separate, human
reviewed PR that updates `docs/canon/`. The PR must reference the MIP ID
in its description. The registry does not write to canon files.

## Backward Compatibility

If a MIP introduces a backward-incompatible change, the Implementation
References MUST include a migration plan or rollback procedure. The
Migration Plan is part of the public record, not a private reviewer note.

## Reversibility

Once a MIP is `implemented`, the only way to roll back the change is via:

1. a new MIP that supersedes the original,
2. an emergency policy action (with retrospective MIP / incident report),
   or
3. a `superseded` transition that points to the replacing MIP.

The original MIP record remains in the registry, marked `superseded`.
