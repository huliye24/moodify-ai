# Acceptance Criteria
## MOOD-GENESIS-002

### Critical

- [ ] Package 001 foundation is present or equivalent facts are verified.
- [ ] `/genesis` exists.
- [ ] Wallet connection works with an existing supported EVM wallet.
- [ ] Required network is BNB Smart Chain / chainId 56.
- [ ] Wrong-network state is explicit.
- [ ] Server generates nonce.
- [ ] Nonce expires.
- [ ] Nonce cannot be reused.
- [ ] Server verifies signature.
- [ ] Recovered signer must equal requested wallet.
- [ ] Duplicate wallet cannot create a second participant.
- [ ] Participant number is unique and race-safe.
- [ ] Successful registration returns a stable Participant ID.
- [ ] No token transfer occurs.
- [ ] No token approval occurs.
- [ ] No gas transaction is required.
- [ ] No private key/seed phrase is requested or stored.
- [ ] Database migration is non-destructive.
- [ ] Production build passes or unrelated baseline failure is documented precisely.

### UX

- [ ] User sees what they are signing.
- [ ] Signature text states it authorizes no transfer.
- [ ] Already-registered wallets see their existing Participant ID.
- [ ] Expired nonce has a recoverable retry flow.
- [ ] User rejection of wallet signature returns to a usable state.
- [ ] Mobile works.
- [ ] Desktop works.
- [ ] Address copy/view controls work.

### Security

- [ ] Nonce uses secure randomness.
- [ ] Server-side schema validation exists.
- [ ] Client cannot set status/allocation/score.
- [ ] Unique DB constraint exists for normalized wallet.
- [ ] Concurrent duplicate registration test exists.
- [ ] Rate limiting is used if existing infrastructure supports it.
- [ ] Raw signatures are not unnecessarily logged.

### Documentation

- [ ] `docs/protocol/GENESIS_REGISTRATION.md` exists.
- [ ] Signature format/version is documented.
- [ ] Terms version is recorded.
- [ ] Future airdrop is clearly separated from registration.
