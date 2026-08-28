# Human Approval Gate
## Package 005 Production Launch

Codex must stop before each production-signature checkpoint.

### Checkpoint A — Snapshot approval

Human confirms:

- Snapshot ID
- Snapshot SHA256
- Merkle root
- Participant count
- Total MOOD
- Allocation policy/version

### Checkpoint B — Contract architecture approval

Human confirms:

- immutable root
- deadline/no deadline
- recovery/no recovery
- owner/no owner
- deployment network

### Checkpoint C — Mainnet deployment

**HUMAN SIGNATURE REQUIRED**

Human checks MetaMask/Safe:
- chain = BNB Smart Chain;
- constructor token = official MOOD;
- constructor root = approved root;
- deadline/owner = approved values;
- gas reasonable.

### Checkpoint D — Funding

**HUMAN SIGNATURE REQUIRED**

Human checks:
- token = official MOOD;
- recipient = verified distributor;
- amount = approved Genesis total;
- chain = BNB Smart Chain.

### Checkpoint E — Public launch

Human confirms:
- distributor funded;
- BscScan verified;
- `/airdrop` configured with exact distributor;
- claim fixture/smoke validation completed;
- docs published.

## Forbidden automation

No unattended:
- mainnet broadcast;
- Treasury signing;
- MetaMask click automation;
- private key extraction;
- MOOD funding.
