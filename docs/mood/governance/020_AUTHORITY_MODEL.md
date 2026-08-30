# 020 — Authority Model

## Roles

### Resident

Any authenticated Resident may:

- propose a new MIP (status starts at `draft`).
- update their own draft.
- withdraw their own draft.
- open discussion on their own MIP.

A Resident may NOT:

- accept their own MIP without maintainer involvement.
- vote on token-weighted decisions (token voting is disabled).
- move their own MIP directly to `accepted` or `implemented`.

### Governance Maintainer

Maintainers are authorized reviewers. They may:

- move a MIP from `discussion` to `review`.
- record an `accepted`, `rejected`, or `returned-for-revision` decision.
- mark a MIP as `implemented` after Implementation References exist.
- supersede or archive any MIP.
- exercise emergency policy within the bounds defined in
  `020_EMERGENCY_POLICY.md`.

Maintainers are bound by:

- explicit actor identity (Resident ID, not anonymous).
- required rationale on every decision.
- append-only audit (no retroactive edits).

### System (seeding only)

The `system` Resident is reserved for seeding `MIP-000` and is not a
human authority. It may not accept or implement MIPs.

## Authority Hierarchy

```text
Maintainer Consensus
  ↓
Resident Signal (signal only, never automatic decision)
  ↓
Emergency (logged + audited, retrospective MIP required)
```

`future-token-vote` is reserved as a decision method string but is
**disabled** in 020. It cannot be used to accept or reject a MIP.

## Single Authority Principle

There is one MIP registry, not many. 020 explicitly forbids a second
authoritative state machine for governance. Any existing decision log that
duplicates MIP semantics (e.g. Contribution `audit`) is operational, not
governance.

## Canon Boundary

An Accepted MIP does **not** automatically rewrite
`docs/canon/CURRENT_CANON.md` or any other canon file. Canon updates require
a separate, human-reviewed PR. This boundary is enforced by process, not by
the registry (`INV-020-09` documents the principle; the registry does not
write to canon files).
