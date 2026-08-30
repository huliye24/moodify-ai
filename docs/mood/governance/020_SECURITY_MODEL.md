# 020 — Security Model

Threats considered by the MIP Governance Standard.

## T1. Proposal Spam

- **Threat**: An attacker registers many low-quality MIP drafts to
  overwhelm the registry.
- **Mitigation**:
  - Only authenticated Residents can create drafts (`INV-020-XX`).
  - A draft must have a non-trivial title (>=5 chars) and summary
    (>=10 chars).
  - Authors are bound by their Resident ID; abuse can be traced.
  - Maintainers may `archive` drafts without review if they are obvious
    spam.

## T2. Impersonated Author

- **Threat**: A Resident submits a MIP claiming authorship that belongs to
  another Resident.
- **Mitigation**:
  - Authors are required to be Resident IDs known to the registry.
  - Co-authors can be added by the original author with Maintainer
    approval.

## T3. Unauthorized Status Change

- **Threat**: A non-Maintainer actor moves a MIP to `accepted` or
  `implemented`.
- **Mitigation**:
  - `transition()` does not check Maintainer status (process-level
    control), but `recordDecision()` requires `isMaintainer: true` for
    acceptance decisions (`INV-020-06`).
  - Status transitions without decision records are blocked for
    `accepted`, `rejected`, and `implemented`.

## T4. Reviewer Privilege Escalation

- **Threat**: An actor convinces the system they are a Maintainer when
  they are not.
- **Mitigation**:
  - Maintainer status is a server-side flag, not a client claim.
  - Every acceptance decision records the Maintainer Resident ID in
    `decidedBy`.

## T5. Decision Tampering

- **Threat**: An actor edits a previously-recorded decision.
- **Mitigation**:
  - Decisions are append-only. There is no edit or delete method on
    `decisionsByMip`.
  - Corrections require a new decision record (e.g.
    `returned-for-revision`) and are visible in the audit trail.

## T6. Duplicate MIP ID

- **Threat**: Two MIPs claim the same `MIP-NNN` id.
- **Mitigation**:
  - `allocateId()` walks `nextNumber` until it finds an unused id.
  - Slug collisions are resolved with a deterministic suffix.

## T7. Malicious Markdown / XSS

- **Threat**: A MIP summary or title contains HTML or script that
  executes in the public page.
- **Mitigation**:
  - The public page renders text only, not arbitrary HTML.
  - All fields shown to the public go through React's default escaping.

## T8. Fake Implementation Reference

- **Threat**: A Maintainer marks a MIP as `implemented` with a fake
  reference (e.g. a non-existent commit SHA).
- **Mitigation**:
  - Implementation references are public. Anyone can audit them.
  - The Maintainer who records the reference is recorded as
    `recordedBy`.
  - Verification is a human process; the registry does not auto-verify.

## T9. Governance Capture

- **Threat**: A small group of Maintainers consolidates power and
  suppresses dissent.
- **Mitigation**:
  - The `Resident Signal` decision method is reserved for future
    signaling. It is not yet active but the registry reserves the
    method name.
  - Every transition is logged with actor, timestamp, and reason.
  - Superseded MIPs remain publicly readable.

## T10. Emergency Abuse

- **Threat**: A Maintainer uses emergency policy to bypass the normal
  flow permanently.
- **Mitigation**:
  - Every emergency action requires a retrospective MIP within 7 days.
  - See `020_EMERGENCY_POLICY.md`.

## T11. Token-Vote Premature Activation

- **Threat**: A Maintainer activates `future-token-vote` decision method
  before 025 / a future package.
- **Mitigation**:
  - 020 does not implement token-vote code paths.
  - The `decisionMethod` enum reserves the string but the registry never
    uses it to take a real action.

## T12. Private Reviewer Notes Leakage

- **Threat**: A reviewer's private note ends up in the public feed.
- **Mitigation**:
  - Decision rationale is public by design (the policy says rationale is
    required and part of the public record). Reviewers are warned that
    their rationale will be public.
  - Private notes belong in the discussion URL, not the rationale field
    (`INV-020-10`).
