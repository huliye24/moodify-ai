# Acceptance Criteria
## MOOD-GENESIS-006

### Public contribution flow

- [ ] `/contribute` exists.
- [ ] Active tasks list renders.
- [ ] Task detail renders.
- [ ] Registered Genesis Participant can submit.
- [ ] Unregistered user is guided to Genesis registration.
- [ ] Submission captures required evidence.
- [ ] My Contributions view exists.
- [ ] Status lifecycle is explicit.
- [ ] Approved Reputation is visible to participant.
- [ ] Pending MOOD reward is visible to participant.
- [ ] UI distinguishes pending reward from distributed tokens.

### Admin/review

- [ ] `/admin/contributions` or equivalent secure route exists.
- [ ] Server-side admin authorization enforced.
- [ ] Task create/edit/publish works.
- [ ] Submission review works.
- [ ] Changes requested works.
- [ ] Approve works.
- [ ] Reject works.
- [ ] Reviewer identity recorded.
- [ ] Approval reason recorded.
- [ ] Reputation points recorded as event.
- [ ] MOOD reward recorded as event.
- [ ] Self-review guard exists where identity model allows.
- [ ] Audit history cannot be silently deleted.

### Data integrity

- [ ] Contribution categories controlled.
- [ ] Task statuses controlled.
- [ ] Submission statuses controlled.
- [ ] Invalid transitions rejected server-side.
- [ ] Reward exact arithmetic uses 18-decimal atomic units.
- [ ] Negative reward rejected.
- [ ] Floating-point MOOD accounting not used.
- [ ] Genesis allocation is not overwritten by contribution reward.
- [ ] Reputation can be recomputed from events.
- [ ] Pending rewards can be deterministically exported.

### Anti-abuse

- [ ] Submission creation rate-limited if infrastructure available.
- [ ] Duplicate/repeat task submission policy explicit.
- [ ] Wallet identity comes from Genesis record.
- [ ] No trading-volume reward.
- [ ] No holder-count reward.
- [ ] No buy-to-earn.
- [ ] No referral farming.
- [ ] No fake engagement task type included.

### Privacy

- [ ] Internal notes/review metadata not public.
- [ ] Raw wallet signatures/nonces never exposed.
- [ ] Evidence visibility policy explicit.
- [ ] Public contributor profile omitted unless privacy model is safe.

### Integration

- [ ] Reuses Package 002 participant identity.
- [ ] Reuses Package 003 admin authorization.
- [ ] Reward export compatible with future distribution pipeline.
- [ ] No on-chain token transfer occurs automatically.

### Build

- [ ] Migration validation passes.
- [ ] Lint passes.
- [ ] Typecheck passes.
- [ ] Tests pass.
- [ ] Production build passes or unrelated baseline failures documented.
- [ ] `CONTRIBUTION_NETWORK.md` exists.
