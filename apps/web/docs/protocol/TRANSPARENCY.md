# Transparency

**Package:** MOOD-GENESIS-007  
**Purpose:** Public transparency layer for protocol assets

---

## Overview

The transparency system provides public, verifiable information about MOOD token and protocol-controlled assets.

**Principle:** Transparency must be factual. No fabricated data.

---

## Public Route

**URL:** `/transparency`

### Sections

1. **Protocol Asset Overview**
   - Token name, symbol, contract
   - Network (BNB Smart Chain)
   - Total supply
   - Links to BscScan and PancakeSwap

2. **Supply Accounting**
   - Total supply
   - Protocol-controlled balance
   - Treasury/reserve balance
   - Genesis allocated
   - Genesis claimed/distributed
   - Contribution rewards pending

3. **Treasury Accounts**
   - Publicly approved accounts only
   - Category, purpose, balance
   - Percentage of total supply
   - Control model

4. **Genesis**
   - Registered participants
   - Allocated participants
   - Total allocation
   - Claimed/unclaimed amounts

5. **Contribution Network**
   - Pending rewards
   - Distributed rewards

6. **Liquidity**
   - PancakeSwap pool (when verified)
   - Token balances (not USD values)

7. **Methodology**
   - Data sources
   - Limitations
   - Circulating supply status
   - Last updated timestamp

---

## API

**Endpoint:** `GET /api/protocol/transparency`

### Response Schema

```json
{
  "schema": "moodify-transparency-v1",
  "generatedAt": "2026-08-27T...",
  "token": {
    "name": "Moodify",
    "symbol": "Mood",
    "address": "0x1BB3115D43E397f7bb586F090831B02cA639e73E",
    "decimals": 18,
    "totalSupply": {
      "value": "33000000",
      "source": "rpc",
      "updatedAt": "...",
      "isStale": false
    },
    "explorerUrl": "...",
    "tradeUrl": "..."
  },
  "accounts": [...],
  "genesis": {...},
  "contributions": {...},
  "liquidity": {...},
  "methodology": {...},
  "reconciliation": {
    "isBalanced": true,
    "warnings": []
  }
}
```

### Data Sources

| Source | Description |
|--------|-------------|
| `rpc` | On-chain read via BNB Smart Chain |
| `cache` | Cached RPC result |
| `config` | Static configuration |
| `db` | Database aggregate |
| `unavailable` | Data not available |

---

## What We Don't Show

### Not Fabricated

- ❌ Market cap
- ❌ Token price
- ❌ Holder count
- ❌ Circulating supply (without approved methodology)
- ❌ Treasury labels (without approval)
- ❌ Liquidity USD values (without reliable pricing)
- ❌ Lock/vesting status (without verification)

### Not Exposed

- ❌ Internal admin notes
- ❌ Raw signatures
- ❌ Nonces
- ❌ Private participant data
- ❌ Unapproved wallet labels

---

## Circulating Supply

### Current Status

**Not yet formally published.**

The circulating supply methodology is still under development. Until approved:

- No numeric circulating supply claim is made
- Status shows as "not_published"
- Methodology will be documented when approved

### Why Not Simple?

`totalSupply - treasuryBalance ≠ circulatingSupply`

Circulating supply requires careful definition of:
- What counts as "circulating"
- What counts as "locked"
- Vesting schedules
- Staking positions

---

## Reconciliation

The system performs automatic reconciliation:

```
Sum of configured treasury balances
+ Distributor balance
+ Liquidity positions
+ Unclassified known balance
≈ Total Supply
```

Warnings are generated for:
- Config mismatches
- Duplicate addresses
- Stale/unavailable reads
- Snapshot/distributor mismatches
- DB/chain mismatches

---

## Data Freshness

| Metric | Source | Refresh |
|--------|--------|---------|
| Total Supply | RPC | Real-time |
| Account Balances | RPC | Real-time |
| Genesis Stats | Database | Real-time |
| Treasury Config | Static | Deploy-time |

Stale data is labeled as such.

---

## Safety

- Read-only on-chain
- No signer required
- No private keys
- No token transfers
- No liquidity mutations

---

## Human Approval Required

Before publishing:

- [ ] Treasury account labels approved
- [ ] Circulating supply methodology approved
- [ ] Allocation percentages approved
- [ ] Liquidity positions verified

---

## License

SPDX-License-Identifier: GPL-3.0-only

Copyright (c) 荣景文川 2024-2026
