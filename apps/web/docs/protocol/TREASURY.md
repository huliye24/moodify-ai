# Treasury Configuration

**Package:** MOOD-GENESIS-007  
**Purpose:** Treasury account classification and configuration

---

## Overview

The treasury configuration provides a single source of truth for protocol-controlled accounts. It supports:

- Account classification by category
- Public/private designation
- Control model documentation
- Safe empty-state handling

---

## Configuration File

**Location:** `lib/mood-treasury.ts`

### TreasuryAccount Type

```typescript
interface TreasuryAccount {
  id: string;                    // Unique identifier
  label: string;                 // Human-readable label
  purpose: string;               // Purpose description
  chainId: 56;                   // BNB Smart Chain
  address: `0x${string}`;        // Wallet address
  category: TreasuryCategory;    // Classification
  public: boolean;               // Publicly disclosed
  controlModel?: ControlModel;   // EOA | Safe | Contract | Unknown
  notes?: string;                // Public notes
}
```

### Categories

| Category | Description |
|----------|-------------|
| `ecosystem` | Ecosystem development funds |
| `treasury` | General treasury reserve |
| `liquidity` | Liquidity provision |
| `contributors` | Contributor rewards |
| `team` | Team allocation |
| `strategic` | Strategic partnerships |
| `genesis-distributor` | Genesis airdrop distributor |
| `other` | Uncategorized |

### Control Models

| Model | Description |
|-------|-------------|
| `EOA` | Externally owned account |
| `Safe` | Gnosis Safe multisig |
| `Contract` | Smart contract controlled |
| `Unknown` | Control model not disclosed |

---

## Adding Treasury Accounts

### Requirements

1. **Human approval required** before adding any account
2. **Address must be valid** EVM address
3. **No duplicates allowed**
4. **Category must be approved**

### Example

```typescript
// In lib/mood-treasury.ts
accounts: [
  {
    id: "genesis-distributor-001",
    label: "Genesis Distributor",
    purpose: "MOOD-GENESIS-005 airdrop distribution",
    chainId: 56,
    address: "0x...",
    category: "genesis-distributor",
    public: true,
    controlModel: "Contract",
    notes: "Immutable Merkle distributor deployed from Package 005"
  }
]
```

---

## Circulating Supply Methodology

### Status Values

| Status | Description |
|--------|-------------|
| `draft` | Methodology in development |
| `approved` | Methodology approved and active |
| `not_published` | No methodology published |

### Current Status

```typescript
circulatingSupply: {
  version: "v0.1",
  status: "not_published",
  description: "Circulating supply methodology not yet formally published."
}
```

---

## Validation

### Duplicate Detection

```typescript
const duplicates = findDuplicateAddresses();
// Returns array of duplicate addresses
```

### Address Validation

```typescript
const isValid = isValidTreasuryAddress(address);
// Validates EVM address format
```

### Lookup

```typescript
const account = getTreasuryAccountByAddress(address);
// Returns account or undefined
```

---

## RPC Configuration

```typescript
rpcEndpoint: "https://bsc-dataseed.binance.org"
```

---

## Safety

- Read-only configuration
- No private keys stored
- No transfer capabilities
- Human approval required for changes

---

## License

SPDX-License-Identifier: GPL-3.0-only

Copyright (c) 荣景文川 2024-2026
