# 020 — Review Policy

## Review Stages

### 1. Discussion

- Public page lists the MIP.
- Residents may post comments via the discussion URL.
- No code or data changes are applied at this stage.

### 2. Review

- A Maintainer opens Review.
- The Review stage requires explicit Maintainer participation.
- Decision records (`accepted` / `rejected` / `returned-for-revision`) are
  logged with actor ID(s) and rationale.

### 3. Decision

The decision types are:

- `accepted` — the MIP is approved; status auto-transitions to `accepted`.
- `rejected` — the MIP is denied; status auto-transitions to `rejected`.
- `returned-for-revision` — the MIP is sent back to draft for the author
  to address Maintainer feedback.

All three require:

- at least one `decidedBy` Resident ID.
- a non-empty `rationale`.

## Acceptance Rules

A Maintainer may accept a MIP only if:

- the MIP has a complete Specification, Rationale, and Security
  Considerations section.
- the MIP does not contradict `CURRENT_CANON.md` unless the MIP itself is
  an amendment to the canon (and so labelled).
- the MIP does not claim to do anything that cannot be verified through an
  Implementation Reference.

## Rejection Rules

A Maintainer may reject a MIP for any reason, but the rationale must be
recorded. Common rejection reasons:

- duplicates an existing MIP.
- falls outside the governance scope.
- proposes a state machine that conflicts with existing canon.
- proposes on-chain action that is currently forbidden by 020 / 025.

## Return for Revision

Maintainers may return a MIP to draft with explicit feedback. The author
may then update and re-publish.

## Self-Accept Prevention

A Resident who is the sole author of a MIP cannot accept that MIP alone
(`INV-020-06`). Acceptance requires at least one Maintainer actor in the
`decidedBy` list.
