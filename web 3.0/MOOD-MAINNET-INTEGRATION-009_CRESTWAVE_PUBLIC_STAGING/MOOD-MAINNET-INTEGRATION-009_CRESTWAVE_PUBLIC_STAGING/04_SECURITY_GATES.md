# Security Gates

## Security Posture

Package 009 is intentionally a **read-only mainnet staging package**.

The goal is to prove connectivity before any asset-moving feature is enabled.

---

## P0 — Immediate Stop Conditions

### P0.1 Secret Exposure

Stop if any of the following are found in tracked files, browser bundle, logs, CI output, or committed history:

- private key;
- seed phrase;
- deployer secret;
- treasury signing key;
- admin wallet signing key;
- API secret that permits asset movement.

### P0.2 Contract Address Conflict

Stop if active production code references a different MOOD contract from:

`0x1BB3115D43E397f7bb586F090831B02cA639e73E`

Historic docs may differ only if clearly archival.

### P0.3 Write Path Enabled

Stop if public staging can execute:

- token transfer;
- approve;
- distributor funding;
- claim;
- Merkle root mutation;
- ownership transfer.

### P0.4 Production Data Collision

Stop if staging deployment requires mutating an existing production D1 database without explicit human approval.

---

## P1 — Must Resolve Before Public Validation

- localhost RPC remains in runtime configuration;
- chain values silently fall back to config;
- wrong-network handling is absent;
- public wallet balance reads fail;
- BscScan link points to wrong chain/address;
- Cloudflare environment variables are incomplete;
- browser bundle contains non-public RPC credentials;
- stale mock eligibility is presented as real eligibility.

---

## Key Principle

A public staging failure is acceptable.

A misleading or asset-moving staging deployment is not.

Prefer:

`UNAVAILABLE`

over invented or stale chain data.

Prefer:

`CLAIMS DISABLED`

over a partially working claim flow.
