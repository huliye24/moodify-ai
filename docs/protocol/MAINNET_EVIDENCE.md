# MOOD Protocol Mainnet Evidence Registry

## Evidence Standards

This registry documents all evidence supporting the canonical facts in `protocol/mainnet.json`. Evidence is classified by source and verification status.

## Evidence Classification

| Status | Description | Example |
|--------|-------------|---------|
| VERIFIED | Fact confirmed on-chain | Contract deployment verified |
| REPOSITORY_ONLY | Fact from code/config | Chain ID from config file |
| PUBLIC_CHAIN_ONLY | Fact from public source | Network name from blockchain |
| CONFLICT | Inconsistent facts found | Multiple addresses claimed |
| HUMAN_DECISION_REQUIRED | Needs human approval | Treasury address selection |
| NOT_APPLICABLE | Fact not relevant | Unused field |

## Evidence Registry

### Chain Identity Evidence

| Fact | Source | Status | Verification Method | Notes |
|------|--------|--------|-------------------|-------|
| chainId (56) | `apps/web/lib/mood-token.ts` | REPOSITORY_ONLY | Code review | Matches BSC mainnet |
| network ("BNB Smart Chain") | `viem/chains` | REPOSITORY_ONLY | Library validation | Standard EVM chain |
| family ("evm") | Schema definition | REPOSITORY_ONLY | Schema constraint | EVM compatibility |
| cluster ("bsc-mainnet") | Convention | PUBLIC_CHAIN_ONLY | Industry standard | BSC network naming |

### Token Identity Evidence

| Fact | Source | Status | Verification Method | Notes |
|------|--------|--------|-------------------|-------|
| token.name ("Moodify") | `apps/web/lib/mood-token.ts` | REPOSITORY_ONLY | Code review | Brand identity |
| token.symbol ("MOOD") | `apps/web/lib/mood-token.ts` | REPOSITORY_ONLY | Code review | Token standard |
| token.identifier ("0x1BB3115D43E397f7bb586F090831B02cA639e73E") | `apps/web/lib/mood-token.ts` | REPOSITORY_ONLY | Code review | Contract address |
| token.decimals (18) | `apps/web/lib/mood-token.ts` | REPOSITORY_ONLY | BEP-20 standard | Standard for ERC-20 |
| token.totalSupplyAtomic ("33000000000000000000000000") | `apps/web/lib/mood-token.ts` | REPOSITORY_ONLY | Calculation | 33M × 10^18 |

### Endpoint Evidence

| Fact | Source | Status | Verification Method | Notes |
|------|--------|--------|-------------------|-------|
| rpcUrls | `apps/web/lib/mood-chain.ts` | REPOSITORY_ONLY | Code review | BSC public nodes |
| explorerBaseUrl ("https://bscscan.com") | `apps/web/lib/mood-token.ts` | PUBLIC_CHAIN_ONLY | Public domain | Official BSC explorer |

### Schema Evidence

| Fact | Source | Status | Verification Method | Notes |
|------|--------|--------|-------------------|-------|
| schemaVersion ("1.0.0") | Schema definition | REPOSITORY_ONLY | Schema validation | Initial version |

## Unresolved Evidence

### Treasury Evidence

| Fact | Status | Reason | Next Steps |
|------|--------|--------|------------|
| treasury address | HUMAN_DECISION_REQUIRED | Not deployed | Human approval needed for deployment location |
| treasury multisig | HUMAN_DECISION_REQUIRED | Signers not decided | Signer selection required |
| treasury policies | HUMAN_DECISION_REQUIRED | Rules undefined | Policy drafting required |

### Genesis Pool Evidence

| Fact | Status | Reason | Next Steps |
|------|--------|--------|------------|
| genesisPool address | HUMAN_DECISION_REQUIRED | Not deployed | Contract deployment needed |
| genesis allocations | HUMAN_DECISION_REQUIRED | Percentages undefined | Allocation decision required |
| vesting schedule | HUMAN_DECISION_REQUIRED | Terms undefined | Schedule design needed |

### Deployment Evidence

| Fact | Status | Reason | Next Steps |
|------|--------|--------|------------|
| deploymentCommit | NOT_APPLICABLE | No deployment yet | First deployment required |
| sourceCommit | REPOSITORY_ONLY | Current state | To be locked on deployment |
| contractVerificationStatus | PUBLIC_CHAIN_ONLY | Not verified | Verification after deployment |

## Verification Logs

### Chain Readiness Check

```json
{
  "timestamp": "2026-08-29T00:00:00Z",
  "checks": {
    "rpcConnectivity": "UNKNOWN",
    "contractReadability": "UNKNOWN",
    "totalSupplyMatch": "UNKNOWN",
    "decimalsMatch": "UNKNOWN"
  },
  "notes": "First-time configuration - no on-chain verification performed yet"
}
```

### Source Commit Hash

```text
Current HEAD: [to be determined on first deployment]
Locked commit: [to be set when facts are locked]
```

## Evidence Collection Protocol

### For Deployed Facts

When contracts are deployed, evidence collection must include:

1. **Transaction Hash**: Deploy transaction on BscScan
2. **Block Number**: Confirmation block
3. **Gas Used**: Deployment cost
4. **Contract Verification**: BscScan verification link
5. **ABI Files**: Contract interface artifacts

### For Configuration Facts

Facts from code/config require:

1. **File Path**: Source location
2. **Commit Hash**: When fact was established
3. **Review Status**: Code review completed
4. **Change History**: Evolution of the value

## Quality Assurance

### Evidence Completeness Checklist

- [ ] All facts in schema have evidence
- [ ] No facts without status
- [ ] Conflicts are documented
- [ ] Human decisions are flagged
- [ ] Source commits are tracked

### Reconciliation Protocol

Facts must be reconciled when:

1. New deployment occurs
2. Configuration changes
3. Network upgrade
4. Fork event

```bash
# Reconciliation command (to be implemented)
node scripts/reconcile-mainnet.mjs protocol/mainnet.json
```

## Change History

| Date | Change | Evidence Added | Status |
|------|--------|----------------|--------|
| 2026-08-29 | Initial canonical facts | Registry created | DRAFT |

---

*This registry is maintained as part of the MOOD Protocol evidence system. Update when new facts are added or verified.*