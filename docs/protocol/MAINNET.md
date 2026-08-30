# MOOD Protocol Mainnet Facts

## Overview

The MOOD Protocol mainnet configuration is the single source of truth for all MOOD token facts on the BNB Smart Chain. This document mirrors the canonical facts stored in [`protocol/mainnet.json`](../../protocol/mainnet.json).

### Mission

Establish a single, authoritative source of truth for MOOD Protocol on BSC mainnet that can be consumed by all system components without ambiguity.

## Canonical Facts

### Protocol Identity

| Field | Value |
|-------|-------|
| Name | MOOD Protocol |
| Ticker | MOOD |

### Chain Identity

| Field | Value |
|-------|-------|
| Family | EVM |
| Network | BNB Smart Chain |
| Chain ID | 56 |
| Cluster | bsc-mainnet |

### Token Identity

| Field | Value |
|-------|-------|
| Name | Moodify |
| Symbol | MOOD |
| Contract Address | `0x1BB3115D43E397f7bb586F090831B02cA639e73E` |
| Decimals | 18 |
| Total Supply | 33,000,000 MOOD (atomic: `33000000000000000000000000`) |

### Endpoints

| Service | URLs |
|---------|------|
| RPC | https://bsc-dataseed.binance.org |
| | https://bsc-dataseed1.binance.org |
| | https://bsc-dataseed2.binance.org |
| | https://bsc-dataseed3.binance.org |
| | https://bsc-dataseed4.binance.org |
| Explorer | https://bscscan.com |

### Treasury & Genesis Pool

**Status**: Human Decision Required

The following addresses require human decision to be finalized:

- Treasury: TBD
- Genesis Pool: TBD

## Evidence Summary

### Verified Facts

All chain and token facts have been verified against the authoritative sources in the repository:

- Chain ID and network verified from `viem/chains`
- Token contract address verified from `apps/web/lib/mood-token.ts`
- Token decimals and supply verified from configuration
- RPC endpoints verified from `apps/web/lib/mood-chain.ts`

### Unresolved Facts

The following facts require human decision:

1. **Treasury Address**: The official treasury contract address needs to be deployed and registered
2. **Genesis Pool Address**: The genesis distribution pool address needs to be deployed and registered
3. **Contract Verification**: Token contract verification on BscScan
4. **Deployment Commit**: Git commit hash of the deployment transaction
5. **Source Commit**: Git commit hash that locked this configuration

## Integration Guide

### For Applications

Consumers should read directly from `protocol/mainnet.json`:

```typescript
import mainnetConfig from '../../protocol/mainnet.json'

const tokenAddress = mainnetConfig.token.identifier
const chainId = mainnetConfig.chain.chainId
const rpcUrls = mainnetConfig.endpoints.rpcUrls
```

### For Smart Contracts

The chain ID (56) and token address are the primary identifiers that should be hard-coded in smart contracts for security.

### For Wallets

Use the provided RPC URLs and explorer URL for BSC mainnet integration. The token address can be used for automatic detection.

## Safety Notes

⚠️ **Important**: This configuration is read-only. No private keys, secrets, or deployment instructions are included. All addresses are public and can be verified on the blockchain.

### Production Readiness

- [x] Chain identity confirmed (BSC mainnet, chain ID 56)
- [x] Token contract address confirmed
- [x] Supply and decimals confirmed
- [ ] Treasury address pending human decision
- [ ] Genesis pool address pending human decision
- [ ] Contract verification pending deployment

## Version History

- **v1.0.0**: Initial canonical facts established based on existing repository configuration

---

*This document is a mirror of the canonical facts. The authoritative source is `protocol/mainnet.json`.*