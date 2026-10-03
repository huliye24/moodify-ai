# Genesis Airdrop Runbook

**Package:** MOOD-GENESIS-005  
**Purpose:** Operational procedures for deployment and management

---

## Pre-Deployment Checklist

### Package 004 Verification

- [ ] Package 004 snapshot approved by human
- [ ] Merkle root verified against snapshot
- [ ] `snapshot.json` SHA-256 checksum matches
- [ ] Participant count verified
- [ ] Total MOOD allocation verified

### Contract Preparation

- [ ] Tests pass: `forge test`
- [ ] Fuzz tests pass
- [ ] Package 004 compatibility verified
- [ ] Gas report generated
- [ ] Static analysis run (Slither if available)

### Environment Setup

- [ ] BNB Smart Chain RPC configured
- [ ] BscScan API key set
- [ ] Deployer wallet funded with BNB
- [ ] Environment variables configured (see below)

---

## Environment Variables

### Required

```bash
# Deployment
export PRODUCTION_PRIVATE_KEY=<deployer_private_key>
export MERKLE_ROOT=<approved_root_from_package_004>

# Snapshot metadata
export SNAPSHOT_ID=<package_004_snapshot_id>
export SNAPSHOT_SHA256=<snapshot_sha256>
export PARTICIPANT_COUNT=<number_of_participants>
export TOTAL_MOOD=<total_allocation>
export GIT_COMMIT=<current_commit>
```

### Optional

```bash
# Deadline (0 for no deadline)
export CLAIM_DEADLINE=<unix_timestamp>

# Recovery owner (address(0) for no recovery)
export RECOVERY_OWNER=<multisig_or_safe_address>

# BscScan verification
export BSCSCAN_API_KEY=<api_key>
```

---

## Deployment Steps

### Step 1: Pre-Flight Check

```bash
# Verify chain connection
forge script contracts/script/DeployProduction.s.sol --rpc-url bsc

# Check output shows:
# - Chain ID: 56
# - MOOD Token: 0x1BB3115D43E397f7bb586F090831B02cA639e73E
# - Merkle Root: <your_root>
```

**Human Checkpoint:** Verify all values match approved Package 004 output.

### Step 2: Deploy Contract

```bash
forge script contracts/script/DeployProduction.s.sol \
  --rpc-url bsc \
  --broadcast \
  --verify
```

**Expected Output:**
```
Deployed to: 0x...
Distributor Address: 0x...
```

**Human Checkpoint:** Record deployed address.

### Step 3: Verify on BscScan

```bash
forge verify-contract \
  --chain-id 56 \
  --watch \
  <DISTRIBUTOR_ADDRESS> \
  contracts/protocol/MoodGenesisDistributor.sol:MoodGenesisDistributor
```

**Human Checkpoint:** Confirm verification on BscScan.

### Step 4: Fund Distributor

**Calculate exact amount:**
```bash
# From Package 004 snapshot.json
TOTAL_ATOMIC=<totalAtomic_from_snapshot>
```

**Transfer MOOD:**
```solidity
// From owner wallet
MOOD.transfer(distributorAddress, TOTAL_ATOMIC);
```

**Or via script:**
```bash
# Prepare funding transaction (manual signing required)
# See contracts/script/FundDistributor.s.sol (if created)
```

**Human Checkpoint:** Verify balance:
```solidity
uint256 balance = distributor.distributorBalance();
require(balance == TOTAL_ATOMIC, "Funding mismatch");
```

### Step 5: Update Configuration

```bash
# Set distributor address in frontend
export NEXT_PUBLIC_DISTRIBUTOR_ADDRESS=<deployed_address>
```

### Step 6: Test Claim

1. Navigate to `/airdrop`
2. Connect eligible wallet
3. Verify eligibility displays correctly
4. Submit claim
5. Verify transaction succeeds
6. Check MOOD balance updated

**Human Checkpoint:** Test with small allocation first if possible.

---

## Deployment Record

Update `contracts/deployments/genesis-airdrop.json`:

```json
{
  "chainId": 56,
  "network": "BNB Smart Chain",
  "tokenAddress": "0x1BB3115D43E397f7bb586F090831B02cA639e73E",
  "distributorAddress": "<deployed_address>",
  "merkleRoot": "<root>",
  "snapshotId": "<snapshot_id>",
  "snapshotSha256": "<hash>",
  "participantCount": <count>,
  "totalMood": "<total>",
  "totalAtomic": "<total_atomic>",
  "deployedTx": "<tx_hash>",
  "fundedTx": "<tx_hash>",
  "deployedAt": "<timestamp>",
  "claimDeadline": <deadline_or_null>,
  "owner": "<owner_or_null>",
  "deployer": "<deployer_address>",
  "gitCommit": "<commit>",
  "verified": true,
  "funded": true,
  "tested": true
}
```

---

## Monitoring

### Claim Events

Monitor `Claimed` events:

```solidity
event Claimed(
    uint256 indexed participantNumber,
    address indexed account,
    uint256 amount
);
```

### Key Metrics

- Total participants claimed
- Total MOOD claimed
- Remaining unclaimed
- Failed claim attempts

### Alerts

Set up alerts for:
- Unusual claim patterns
- Failed transactions
- Low distributor balance

---

## Emergency Procedures

### Scenario: Contract Bug Discovered

1. **Stop all claims immediately**
   - If deadline set: wait for expiry, then recover
   - If no deadline: cannot stop (immutable design)

2. **Assess impact**
   - How many participants affected?
   - Funds at risk?

3. **Communicate**
   - Notify participants
   - Document issue

4. **Remediation**
   - Deploy new distributor
   - Update frontend
   - Migrate unclaimed allocations

### Scenario: Distributor Underfunded

1. **Check balance:**
   ```solidity
   distributor.distributorBalance()
   ```

2. **Transfer additional MOOD:**
   ```solidity
   MOOD.transfer(distributorAddress, amount);
   ```

3. **Verify:**
   ```solidity
   require(distributor.distributorBalance() >= expected);
   ```

### Scenario: Recovery Needed

**Prerequisites:**
- Deadline has passed
- Owner is set
- Caller is owner

**Procedure:**
```solidity
// After deadline
distributor.recoverUnclaimed(recipientAddress);
```

**Human Checkpoint:** Verify recipient is correct.

---

## Human Approval Checkpoints

| Step | Required | Description |
|------|----------|-------------|
| Pre-deployment | ✅ | Verify Package 004 snapshot |
| Deploy | ✅ | Sign deployment transaction |
| Verify | ⚠️ | Confirm BscScan verification |
| Fund | ✅ | Sign funding transaction |
| Test | ✅ | Test claim with real wallet |
| Launch | ✅ | Enable public access |
| Recovery | ✅ | Sign recovery transaction |

---

## Rollback Procedures

### Before Launch

- Redeploy contract
- Update frontend config
- Re-test

### After Launch

**Cannot rollback immutable contract.**

Options:
1. Let deadline expire, recover, redeploy
2. Deploy new distributor alongside
3. Communicate and migrate

---

## Support Contacts

- Contract issues: [dev team]
- Frontend issues: [web team]
- Emergency: [on-call]

---

## Audit Trail

Maintain records of:
- All deployments
- All funding transactions
- All recovery transactions
- All configuration changes
- All incident responses

---

## License

SPDX-License-Identifier: GPL-3.0-only

Copyright (c) 荣景文川 2024-2026
