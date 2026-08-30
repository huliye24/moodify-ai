# 020 — Governance Inventory

A clean-slate scan of governance / proposal / decision / canon / policy / admin
/ treasury / genesis / launch surfaces that already exist in the repository.

This inventory is used by the MIP Governance Standard (MIP-000) to map
existing authority seams and avoid duplicate state machines.

## Identity & Passports

- `apps/web/lib/mood/passport/` — Resident, Passport, Session, Signature
  → Resident identity exists and is the auth unit for governance proposals
  in 020.

## Agents Registry (018)

- `apps/web/lib/mood/agents/` — Agent registry with operator-only mutations
  → Agent policy seam exists.

## Node Registry (019)

- `apps/web/lib/mood/nodes/` — Node registry with operator-only mutations
  → Node policy seam exists.

## Network Observatory (017 + 018 + 019)

- `apps/web/lib/mood/network/observatory.ts` — `/network` public surface
  → Network governance placeholder exists (`mips` metric now real in 020).

## Contribution Network (016)

- `apps/web/lib/mood/contribution/` — Tasks, submissions, reviews, reputation
  → Review / approval policy seam exists.

## Canon Authority

- `docs/canon/CURRENT_CANON.md`, `PRODUCT_BOUNDARY.md`, `AUTHORITY_ORDER.md`,
  `INTERNAL_SYSTEMS.md`, `CURRENT_ARCHITECTURE.md`
  → Canon authority is well-defined but lives outside the governance system.
  020 must NOT auto-rewrite Canon from an Accepted MIP.

## Existing Decision Logs

- Contribution `audit.all()` — append-only audit events for contribution
  review decisions.
- AgentRegistry / NodeRegistry — implicit audit via `updatedAt`.

## Admin / Maintainer Seams

- Operator-only mutations on `AgentRegistry.activate / pause / retire` and
  `NodeRegistry.activate / setMaintenance / retire`.
- These are *operational* mutations, not *governance* ones. 020 introduces
  governance separately.

## Treasury / Genesis Surfaces (Reserved)

- No treasury policy code exists yet (021).
- No MOOD Token contract exists yet (025).
- 020 must not invent DAO / token-vote semantics before 021 / 025.

## What 020 Will NOT Build

- Token-weighted voting.
- Snapshot-style external voting.
- On-chain governor.
- Delegation by MOOD balance.
- Quorum based on supply.
- Staking-to-vote or pay-to-propose.
- A forum / discussion host (GitHub Discussions / Issues are referenced, not
  hosted).

## What 020 Will Build

- `apps/web/lib/mood/governance/` — canonical MipRegistry (single authority).
- `apps/web/app/api/governance/mips/` — public read API.
- `apps/web/app/governance/` — public pages.
- `docs/mood/governance/` — MIP standard, lifecycle, authority, review,
  implementation, conflict, emergency, security, network integration,
  final report.
- `tests/governance-invariants.test.mjs` — INV-020-01..12 + bonuses.
