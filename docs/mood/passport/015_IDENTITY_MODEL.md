# MOOD PASSPORT 015 — Identity Model

**Package:** `MOOD-PASSPORT-015`
**Authority surface:** `apps/web/lib/mood/passport/{types,resident-registry,resident-id,public-profile}.ts`
**Status:** implemented, foundation launch state

---

## 1. Core Principle

> **Wallet is a key, not the person.**

The wallet address proves *control of a key*. It is never the identity itself.
Identity is a first-class server-side record: the **Resident**.

## 2. Entities

| Entity | Purpose | Key field | Storage (foundation) |
|---|---|---|---|
| `Resident` | the person; stable record | `id` (short ID) | in-memory `ResidentRegistry` |
| `WalletIdentity` | a verified wallet bound to a Resident | `id` (UUID) | in-memory, indexed by normalized address |
| `ResidentProfile` | optional display fields | `residentId` | in-memory |
| `ResidentRoleRecord` | self-declared or verified roles | `residentId + role` | in-memory array |
| `ResidentBadge` | badges awarded by authority | `residentId` | in-memory array |
| `ResidentConsent` | per-policy-version acceptance | `residentId + policySlug + policyVersion` | in-memory array |
| `ResidentSession` | bounded session | opaque `id` | in-memory map |

One Resident may bind **multiple** wallets (`WalletIdentity[]`, one `isPrimary`).
A wallet may be bound to **at most one** active Resident at a time.

## 3. Resident ID — Decision Record

**Chosen: `M` + 6 chars of base-32 (Crockford-ish, no `0/1/I/O`), e.g. `M7Q4K2`.**

Rejected alternatives:

| Option | Verdict | Reason |
|---|---|---|
| Wallet address as primary ID | ✗ forbidden | TASK Phase D; wallet ≠ person; breaks multi-wallet future |
| Sequential `#0081` | ✗ | leaks scale; enables enumeration of `/resident/[id]` |
| Raw UUID | ✗ | ugly in UI; looks machine-generated |
| UUIDv7 | acceptable | kept as internal `WalletIdentity.id` / session IDs where humans don't look |

Properties (verified by `tests/passport-invariants.test.mjs`):

- 7 characters, prefix `M`, 32^6 ≈ 1.07B combinations
- generated from `crypto.getRandomValues`, no modulo bias (256 % 32 == 0)
- never contains `0x`, never equals a wallet address
- `isValidResidentId()` guards API boundaries

## 4. Creation / Resolution

`ResidentRegistry.resolveOrCreateByWallet(address)` is the single collision
resolver:

1. normalize address → look up existing binding → return existing Resident (`created: false`)
2. otherwise create Resident + default (all-null) profile + default-minimal privacy + bind wallet (`created: true`)

Default profile is **all-null** — no name, no email, no phone, no birthday,
no location, no government ID. Passport never requires them (TASK Phase H).

## 5. Identity Independence

- Resident creation has **zero** token-balance, holding-tier, NFT or net-worth
  inputs (INV-015-01, INV-015-10).
- The passport lib imports **no** `mood-token` / `mood-chain` FREEZE modules
  (INV-015-01b asserts this against real import specifiers).
- Suspension / deletion statuses exist (`active | suspended | deleted`);
  a wallet bound to a *deleted* resident may be re-bound, otherwise
  re-binding to another resident fails closed (`address-bound-to-other-resident`).

## 6. Reputation Linkage

`ReputationSummary` is a **read-only cache** in the registry:

- populated only by 016 (Contribution Network) via `setReputation()`
- when no data exists: `emptyReputation()` → `score: null`,
  `source: "no-contributions-yet"` — never a fabricated number (INV-015-07)

## 7. Storage Honesty

Foundation state stores residents, wallets, sessions and nonces **in memory**.
This is deliberate (no DB dependency for the foundation launch gate) and
**honestly labeled**: restart clears sessions and residents. A future
integration package moves the registry to D1; the entity model and API
surface are designed to survive that migration unchanged.
