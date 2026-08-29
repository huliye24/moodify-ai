# Deployment and Funding Runbook
## Human-Signed Production Procedure

This is a runbook template. Codex prepares commands/scripts; human operator signs all production transactions.

### Gate 0 — Approved inputs

Verify:

- [ ] Package 004 snapshot approved
- [ ] snapshot ID confirmed
- [ ] snapshot SHA256 confirmed
- [ ] Merkle root confirmed
- [ ] participant count confirmed
- [ ] total MOOD confirmed
- [ ] MOOD contract confirmed
- [ ] chainId = 56
- [ ] contract tests pass
- [ ] static analysis reviewed
- [ ] deployment owner/recovery policy approved
- [ ] deadline policy approved

### Gate 1 — Dry-run deployment

Run local fork/testnet simulation.

Verify:
- constructor args;
- root;
- token;
- claim fixture;
- duplicate claim;
- wrong proof;
- insufficient balance behavior.

### Gate 2 — Prepare deployment

Codex outputs:

```text
constructor args
expected contract bytecode hash where practical
deployment command
estimated gas
expected chain
```

Human checks:
- network;
- deployer wallet;
- gas;
- root.

### Gate 3 — Human signs deployment

**HUMAN SIGNATURE REQUIRED**

Do not automate private key access.

After confirmation record:
- deployment tx hash;
- distributor address;
- deployment block.

### Gate 4 — BscScan verification

Verify source code and constructor arguments.

Record verified URL.

### Gate 5 — Fund distributor

Required amount:

`exact approved total MOOD allocation`

Prefer exact funding rather than unnecessarily overfunding.

Codex may prepare transfer calldata.

**HUMAN SIGNATURE REQUIRED**

Human verifies:
- MOOD token contract;
- recipient distributor;
- amount;
- network.

After funding:
- confirm distributor MOOD balance on chain;
- record funding tx.

### Gate 6 — Smoke claim

Use a designated eligible test/real participant only after public launch approval.

Check:
- proof;
- amount;
- gas;
- receipt;
- Claimed event;
- frontend state.

### Gate 7 — Publish frontend config

Set:
- distributor address;
- deployment block;
- snapshot ID/root;
- verified BscScan URL.

Deploy website through normal production release process.

### Emergency rule

If a critical issue is found before funding:
- do not fund;
- deploy corrected contract only after new review.

If issue found after funding but before claims:
- do not improvise;
- follow approved recovery/governance behavior if contract supports it;
- otherwise stop and perform incident review.

If root is wrong:
- never "fix" frontend only;
- immutable-root deployment must be treated as invalid and replaced with a correctly reviewed deployment.
