# Acceptance Criteria
## MOOD-GENESIS-003

### Critical

- [ ] Package 002 participant data is preserved.
- [ ] `/admin/genesis` exists or equivalent admin route is used.
- [ ] Admin route requires real server-side authorization.
- [ ] Unauthorized user cannot read participant admin data.
- [ ] Unauthorized user cannot mutate participant data.
- [ ] Participant list works.
- [ ] Wallet search works.
- [ ] Participant number search works.
- [ ] Status filter works.
- [ ] Participant detail works.
- [ ] Status changes are validated.
- [ ] Contribution score changes are audited.
- [ ] Allocation changes are audited.
- [ ] Sensitive changes require reason.
- [ ] Internal notes are admin-only.
- [ ] CSV export works.
- [ ] JSON export works.
- [ ] Raw signatures are not exported.
- [ ] Internal notes are not exported.
- [ ] Allocation totals use exact arithmetic.
- [ ] No token transfer occurs.
- [ ] No wallet signature occurs.
- [ ] No contract deployment occurs.
- [ ] No liquidity action occurs.
- [ ] Production build passes or unrelated baseline failures are documented.

### Audit integrity

- [ ] Every status change creates an event.
- [ ] Every score change creates an event.
- [ ] Every allocation change creates an event.
- [ ] Old/new values are recorded.
- [ ] Actor is recorded.
- [ ] Timestamp is recorded.
- [ ] Audit rows cannot be edited/deleted through normal UI.

### Allocation safety

- [ ] Negative allocation rejected.
- [ ] Invalid decimal input rejected.
- [ ] Pool ceiling enforced when configured.
- [ ] Server computes aggregate allocation.
- [ ] Client cannot bypass ceiling.
- [ ] Rejected participant cannot silently retain/receive allocation.

### UX

- [ ] 10 participants is comfortable.
- [ ] 1,000 participants remains usable.
- [ ] Mobile remains functional for basic admin tasks.
- [ ] Loading/error/empty states exist.
- [ ] Confirmation exists for rejection/sensitive changes.
- [ ] Save state is clear.

### Documentation

- [ ] `docs/protocol/GENESIS_ADMIN.md` exists.
- [ ] Status transition model documented.
- [ ] Allocation semantics documented.
- [ ] Audit model documented.
- [ ] Export schema documented.
