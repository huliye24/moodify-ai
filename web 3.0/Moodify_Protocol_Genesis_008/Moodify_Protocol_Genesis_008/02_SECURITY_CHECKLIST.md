# Security Checklist
## Genesis v1

### Wallet & Registration

- [ ] Cryptographically secure nonce
- [ ] Nonce TTL
- [ ] Nonce single-use
- [ ] Replay test
- [ ] Domain binding
- [ ] Chain ID binding
- [ ] Terms version binding
- [ ] Exact signer recovery
- [ ] Address normalization
- [ ] Duplicate registration guard
- [ ] Concurrent duplicate test
- [ ] Raw signatures not publicly exposed
- [ ] No token approval in registration
- [ ] No transaction required in registration

### Admin

- [ ] Server-side authentication
- [ ] Server-side authorization
- [ ] No client-only admin flags
- [ ] IDOR checks
- [ ] CSRF/session protections where relevant
- [ ] Audit log append-only
- [ ] Notes private
- [ ] Allocation edits audited
- [ ] Status transitions validated
- [ ] Concurrent allocation integrity

### Distribution

- [ ] Exact 18-decimal arithmetic
- [ ] Deterministic ordering
- [ ] Duplicate wallet guard
- [ ] Duplicate participant guard
- [ ] Pool ceiling
- [ ] Approved status filtering
- [ ] Reproducible Merkle root
- [ ] Proof round-trip
- [ ] Snapshot overwrite protection
- [ ] SHA-256 checksums
- [ ] No private fields in artifacts

### Smart Contract

- [ ] Official token address
- [ ] Approved Merkle root
- [ ] Root immutable
- [ ] SafeERC20
- [ ] Exact claim amount
- [ ] Wrong wallet fails
- [ ] Wrong proof fails
- [ ] Double claim fails
- [ ] Failed transfer does not consume claim
- [ ] No hidden mint
- [ ] No arbitrary active-campaign withdrawal
- [ ] No proxy unless approved
- [ ] Events correct
- [ ] Fuzz tests
- [ ] Invariant tests
- [ ] Static analysis
- [ ] Package 004 fixture compatibility

### Airdrop Frontend

- [ ] BNB Chain enforced
- [ ] Distributor config authority
- [ ] Missing config fails closed
- [ ] Proof belongs to wallet
- [ ] Receipt confirms success
- [ ] Already claimed reads chain
- [ ] User reject handled
- [ ] Insufficient gas handled
- [ ] RPC failure handled
- [ ] No claimant token approval
- [ ] BscScan link correct

### Contribution Network

- [ ] Registered identity reused
- [ ] Task visibility rules
- [ ] Submission auth
- [ ] Review authorization
- [ ] Self-review guard
- [ ] Status transition validation
- [ ] Reputation append-only
- [ ] Reward append-only
- [ ] Exact MOOD reward arithmetic
- [ ] Genesis allocation not overwritten
- [ ] No buy-to-earn
- [ ] No volume-to-earn
- [ ] No referral farming
- [ ] Evidence sanitized

### Transparency

- [ ] No fabricated price
- [ ] No fabricated market cap
- [ ] No fabricated holder count
- [ ] No unapproved circulating supply
- [ ] No unapproved wallet labels
- [ ] Source type shown
- [ ] Freshness shown
- [ ] RPC failure not shown as zero
- [ ] DB failure not shown as zero
- [ ] Read-only Web3 stack
- [ ] Public API privacy
- [ ] No transfer buttons

### Secrets & Environment

- [ ] No private key committed
- [ ] No mnemonic committed
- [ ] No admin password committed
- [ ] No production secret in client bundle
- [ ] Test keys clearly isolated
- [ ] Mainnet/testnet config separated
- [ ] Chain mismatch fails closed
- [ ] Mock data cannot leak into production
