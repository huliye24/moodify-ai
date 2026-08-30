# 020 — Conflict Policy

This policy defines how to resolve conflicts between MIPs and between a
MIP and an existing canon / policy document.

## Conflict Classes

### A. Two MIPs in flight propose overlapping changes

- The later MIP MUST list the earlier MIP in `supersedes` (or be marked
  `returned-for-revision` until the earlier one is resolved).
- The earlier MIP retains its audit trail.

### B. A MIP contradicts `CURRENT_CANON.md`

- The MIP MUST be labelled as a canon amendment in its Motivation section.
- The MIP's category MUST be `governance` or `core`.
- The acceptance decision MUST include a `canon-amendment` note in the
  rationale.
- The implementation PR that updates Canon MUST reference the MIP ID.

### C. A MIP contradicts an existing operational policy (e.g. Contribution,
Agents, Nodes)

- The MIP MUST list the existing operational policy as a
  `supersedes` target or explicitly carve out an exception in its
  Specification.
- The acceptance decision MUST include a `policy-conflict` note.

### D. A MIP claims authority over a state machine that already exists

- Forbidden. 020 refuses to register a second authoritative state machine.
  The registry's `INV-020-XX` invariants do not depend on Token / Agent /
  Node state machines; they are separate domains.

### E. A MIP proposes token-weighted voting

- Forbidden by 020. The registry will accept a `decisionMethod` value of
  `future-token-vote` for forward compatibility, but a MIP whose
  decision-method is `future-token-vote` cannot be moved to `accepted` in
  020. The Maintainer who tries to accept such a MIP must explicitly
  override this in the registry version that supports token voting — and
  that version does not yet exist.

## Resolution Procedure

1. Identify the conflict class (A..E).
2. Resolve via the policy above.
3. Record the resolution in the MIP's `Open Questions` and `Decision
   Record` sections.
4. If the conflict cannot be resolved, the MIP is `returned-for-revision`
   or `rejected` by a Maintainer.

## No Silent Conflicts

The registry does not silently override existing policy. A Maintainer who
moves a MIP forward despite a known conflict must record the conflict and
the override in the rationale. This is auditable.
