# Canonical Mainnet Fact Model

`mainnet.template.json` is a safe starting point only. It intentionally contains unresolved values and must never be presented as a live mainnet configuration.

Codex should copy/adapt it into repository-root `protocol/mainnet.json`, then replace fields only with evidence-backed facts.

## Chain-family rules

### EVM

- `chain.family = "evm"`
- `chain.chainId` must be a positive integer
- `chain.cluster = null`
- token/address identifiers must use 20-byte `0x...` address form

### Solana

- `chain.family = "solana"`
- `chain.chainId = null`
- `chain.cluster` must identify the cluster/network
- token/address identifiers must use valid base58 public-key form

### Other

Use `other` only during draft discovery or if an intentionally supported chain family is added with explicit validation. A locked config should not use `other` unless the validator has explicit rules for it.

## Supply rule

Always store total supply in **atomic/base units** as a decimal string:

```json
"totalSupplyAtomic": "1000000000000000000"
```

Never store a JavaScript floating-point token quantity as protocol authority.
