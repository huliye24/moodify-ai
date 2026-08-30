# Genesis Launch Runbook

**Package:** MOOD-GENESIS-008  
**Date:** 2026-08-27  
**Version:** v1.0

---

## Overview

This runbook provides step-by-step procedures for launching the Moodify Protocol Genesis v1 system.

**Principle:** Human approval required for all production actions.

---

## Pre-Launch Checklist

### 1. Database Backup

```bash
# Export Genesis participants
npm run db:export -- --table=genesis_participants --output=backup-genesis-$(date +%Y%m%d).json

# Verify backup
ls -la backup-genesis-*.json
```

**[HUMAN APPROVAL REQUIRED]**

---

### 2. Approved Snapshot

**Prerequisites:**
- [ ] Package 004 snapshot generated
- [ ] Human review completed
- [ ] Participant count verified
- [ ] Total allocation verified

**Generate:**
```bash
npm run genesis:snapshot -- --snapshot-id genesis-$(date +%Y%m%d)
```

**Verify:**
```bash
# Check artifacts
ls -la artifacts/genesis/genesis-*/

# Verify checksums
cat artifacts/genesis/genesis-*/checksums.txt
```

**[HUMAN APPROVAL REQUIRED]**

---

### 3. Approved Merkle Root

**Extract root from snapshot:**
```bash
# Read merkle.json
cat artifacts/genesis/genesis-*/merkle.json | jq '.root'
```

**Set environment:**
```bash
export MERKLE_ROOT="0x..."
export SNAPSHOT_ID="genesis-YYYY-MM-DD"
export SNAPSHOT_SHA256="..."
export PARTICIPANT_COUNT=...
export TOTAL_MOOD="..."
export GIT_COMMIT=$(git rev-parse HEAD)
```

**[HUMAN APPROVAL REQUIRED]**

---

### 4. Contract Bytecode/Tests

**Verify tests pass:**
```bash
# Run Foundry tests
cd contracts
forge test

# Run fuzz tests
forge test --fuzz-runs 1000

# Check coverage
forge coverage
```

**Verify Package 004 compatibility:**
```bash
forge test --match-test Package004
```

---

### 5. Wallet/Admin Checks

**Verify admin access:**
- [ ] Admin credentials work
- [ ] Admin endpoints accessible
- [ ] Audit logging active

**Verify deployer wallet:**
- [ ] Has BNB for gas
- [ ] Address known
- [ ] Private key secured

**[HUMAN APPROVAL REQUIRED]**

---

### 6. Website Build

```bash
# Production build
npm run build

# Verify build succeeds
ls -la dist/
```

**Check:**
- [ ] No build errors
- [ ] All routes present
- [ ] Static assets included

---

### 7. Environment Config

**Production environment variables:**
```bash
# Required
export NEXT_PUBLIC_DISTRIBUTOR_ADDRESS=""
export NEXT_PUBLIC_MOOD_TOKEN="0x1BB3115D43E397f7bb586F090831B02cA639e73E"
export NEXT_PUBLIC_CHAIN_ID="56"

# Optional
export RPC_ENDPOINT="https://bsc-dataseed.binance.org"
export BSCSCAN_API_KEY=""
```

**Verify:**
- [ ] No test addresses
- [ ] No mock data
- [ ] Mainnet chain ID

---

### 8. BscScan Verification Plan

**Prepare:**
- [ ] Contract source ready
- [ ] Compiler version documented
- [ ] Optimization settings noted

**Command:**
```bash
forge verify-contract \
  --chain-id 56 \
  --watch \
  $DISTRIBUTOR_ADDRESS \
  contracts/protocol/MoodGenesisDistributor.sol:MoodGenesisDistributor
```

---

### 9. Treasury/Funding Plan

**Calculate total:**
```bash
# From snapshot
total_atomic=$(cat artifacts/genesis/genesis-*/snapshot.json | jq '.summary.totalAtomic')
```

**Prepare funding transaction:**
```solidity
// From treasury wallet
MOOD.transfer(distributorAddress, total_atomic);
```

**[HUMAN SIGNATURE REQUIRED]**

---

## Deployment Procedures

### Step 1: Deploy Contract

**Dry run:**
```bash
forge script contracts/script/DeployProduction.s.sol --rpc-url bsc
```

**Verify output:**
- Chain ID: 56
- Token: 0x1BB3115D43E397f7bb586F090831B02cA639e73E
- Merkle Root: [approved root]

**Deploy:**
```bash
forge script contracts/script/DeployProduction.s.sol \
  --rpc-url bsc \
  --broadcast
```

**[HUMAN SIGNATURE REQUIRED]**

**Record:**
- Contract address: `0x...`
- Transaction hash: `0x...`
- Block number: `...`

---

### Step 2: Verify Contract

```bash
forge verify-contract \
  --chain-id 56 \
  --watch \
  $DISTRIBUTOR_ADDRESS \
  contracts/protocol/MoodGenesisDistributor.sol:MoodGenesisDistributor
```

**Verify on BscScan:**
- [ ] Source code matches
- [ ] Constructor arguments correct
- [ ] Compiler version correct

---

### Step 3: Fund Distributor

**Verify contract:**
```bash
# Check contract code exists
cast code $DISTRIBUTOR_ADDRESS --rpc-url bsc
```

**Transfer MOOD:**
```solidity
// From treasury/multisig
MOOD.transfer($DISTRIBUTOR_ADDRESS, $TOTAL_ATOMIC);
```

**[HUMAN SIGNATURE REQUIRED]**

**Verify balance:**
```bash
cast call $MOOD_TOKEN "balanceOf(address)" $DISTRIBUTOR_ADDRESS --rpc-url bsc
```

---

### Step 4: Publish Frontend Config

**Update environment:**
```bash
export NEXT_PUBLIC_DISTRIBUTOR_ADDRESS="0x..."
```

**Deploy frontend:**
```bash
npm run build
# Deploy to hosting
```

**Verify:**
- [ ] /airdrop accessible
- [ ] Distributor config correct
- [ ] Chain ID correct

---

### Step 5: Smoke Claim

**Test with approved participant:**
1. Connect wallet
2. Verify eligibility shows
3. Submit claim
4. Verify transaction succeeds
5. Check balance updated

**Verify on-chain:**
```bash
cast call $DISTRIBUTOR_ADDRESS "hasClaimed(uint256)" $PARTICIPANT_NUMBER --rpc-url bsc
```

**[HUMAN APPROVAL REQUIRED]**

---

## Post-Launch Monitoring

### Claim Monitoring

**Watch for:**
- Failed claims
- Duplicate attempts
- Unusual patterns

**Query:**
```bash
# Get Claimed events
cast logs --from-block $DEPLOY_BLOCK \
  --address $DISTRIBUTOR_ADDRESS \
  --topic "0x..." \
  --rpc-url bsc
```

### Admin Auth Monitoring

**Watch for:**
- Unauthorized access attempts
- Allocation changes
- Audit log anomalies

### RPC Error Monitoring

**Watch for:**
- High failure rates
- Slow responses
- Stale data

### Distributor Balance

**Alert if:**
- Balance < expected
- Unexpected transfers

---

## Rollback/Containment

### Contract Issues

**Cannot rollback (immutable):**
- No proxy
- No upgrade
- No pause

**Options:**
1. Let deadline expire, recover, redeploy
2. Deploy new distributor alongside
3. Communicate and migrate

### Frontend Issues

**Can rollback:**
1. Revert to previous build
2. Update config
3. Redeploy

### Data Issues

**DB corruption:**
1. Restore from backup
2. Re-snapshot
3. Verify integrity

---

## Human Approval Checkpoints

| Step | Required | Description |
|------|----------|-------------|
| Database backup | ✅ | Verify backup complete |
| Snapshot approval | ✅ | Approve Package 004 output |
| Merkle root | ✅ | Approve root for deployment |
| Wallet checks | ✅ | Verify deployer ready |
| Contract deploy | ✅ | Sign deployment transaction |
| Contract verify | ⚠️ | Confirm BscScan verification |
| Fund distributor | ✅ | Sign funding transaction |
| Frontend config | ✅ | Verify config correct |
| Smoke claim | ✅ | Test claim succeeds |
| Public launch | ✅ | Enable public access |

---

## Emergency Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| Technical Lead | [TBD] | [TBD] |
| Security Lead | [TBD] | [TBD] |
| Operations | [TBD] | [TBD] |

---

## Resources

- BscScan: https://bscscan.com
- PancakeSwap: https://pancakeswap.finance
- Foundry Docs: https://book.getfoundry.sh
- OpenZeppelin: https://docs.openzeppelin.com

---

## License

SPDX-License-Identifier: GPL-3.0-only

Copyright (c) 荣景文川 2024-2026
