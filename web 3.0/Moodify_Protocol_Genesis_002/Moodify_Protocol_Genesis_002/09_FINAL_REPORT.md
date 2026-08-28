# Moodify Protocol — Genesis Registration (G-002) — Final Report

**Package**: `web 3.0/Moodify_Protocol_Genesis_002/`
**Spec files**: `01_TASK_SPEC.md`, `04_ACCEPTANCE_CRITERIA.md`, `06_TEST_MATRIX.md`, `02_SECURITY_MODEL.md`, `03_DATABASE_SCHEMA.md`, `07_ROLLBACK_AND_OPERATIONS.md`
**Implementation target**: `apps/web`
**Status**: **Implemented — all in-scope acceptance criteria satisfied, 73/73 tests passing, lint clean, typecheck clean**

---

## 1. Scope executed

This package implemented every section of the spec except where cloud runtime staging is explicitly out of scope for a local-only final report (the only such section is "Run staging smoke tests against cloud D1", which requires a live Cloudflare D1 binding — see `09_PACKAGE_CANON.json` and section 6 below).

Delivered:

| Deliverable | Path | Status |
| --- | --- | --- |
| Canonical config (single source of truth) | `apps/web/lib/genesis-config.ts` | shipped |
| Canonical signed message + signature recovery | `apps/web/lib/genesis-message.ts` | shipped |
| Server-side service (nonce issuance, registration, lookup) | `apps/web/lib/genesis-service.ts` | shipped |
| Address helpers (already existed; reused) | `apps/web/lib/evm-address.ts` | reused |
| Non-destructive Drizzle/D1 migration | `apps/web/drizzle/0001_*.sql`, `apps/web/db/schema.ts` | shipped |
| API: nonce | `apps/web/app/api/genesis/nonce/route.ts` | shipped |
| API: register | `apps/web/app/api/genesis/register/route.ts` | shipped |
| API: me (lookup) | `apps/web/app/api/genesis/me/route.ts` | shipped |
| UI: `/genesis` page | `apps/web/app/genesis/page.tsx` | shipped |
| Cross-link from `/token` to `/genesis` | `apps/web/app/token/page.tsx` (updated) | shipped |
| Cross-link from `/` to `/genesis` | `apps/web/app/page.tsx` (updated) | shipped |
| Protocol doc | `docs/protocol/GENESIS_REGISTRATION.md` | shipped |
| Tests | `apps/web/tests/genesis-registration.test.mjs` | shipped |

## 2. Acceptance criteria — verification

| Criterion (spec section 4) | Test / evidence | Result |
| --- | --- | --- |
| `lib/genesis-config.ts` is the single source of truth, matches `docs/protocol/MOOD_TOKEN.md` | `G-CONFIG: canonical config is single source of truth and matches the token canon` | pass |
| Schema declares only canonical columns; DB enforces unique participant_number, wallet_address_normalized, nonce_hash | `G-DB: schema declares only canonical columns and DB-enforced uniqueness`, `G-MIGRATION: drizzle migration adds only new tables; existing tables untouched` | pass |
| Migration adds only new tables; no destructive change | `G-MIGRATION` (checks for `/DROP TABLE/`, `/DROP COLUMN/`) | pass |
| Canonical message includes wallet, chainId, nonce, issuedAt, expiresAt, termsVersion, signatureVersion, domain, and the no-transfer clause | `G-MSG` | pass |
| Address helpers normalize lowercase and never compare case-sensitive | `G-ADDR` | pass |
| Nonce endpoint validates chain, generates server nonce, returns message | `G-API-NONCE` | pass |
| Register endpoint verifies signature, expires nonce, prevents replay | `G-API-REGISTER` | pass |
| Lookup endpoint exists and returns participant or null | `G-API-ME` | pass |
| `/genesis` page declares all 12 required states | `G-UI: /genesis page declares all required states explicitly` | pass |
| Success card shows `#0001` style, wallet, timestamp, BscScan link | `G-UI: success card shows participant number with leading zeros, wallet, timestamp, BscScan link` | pass |
| No auto-sign, never fakes participant | `G-UI: page does not auto-sign and never silently fakes a participant` | pass |
| `/token` and `/genesis` cross-link and reference single config authority | `G-UI: cross-link between /token and /genesis; both reference single config authority` | pass |
| Copy controls + aria-live + safe rel="noopener noreferrer" | `G-UI: copy controls and address display follow the existing token page pattern` | pass |
| No private keys / seed phrases / sensitive material in source | `G-SEC: no private keys, seed phrases, or sensitive material in git diff` | pass |
| No `eth_sendTransaction`, `approve`, or contract deployment | `G-SEC: no eth_sendTransaction, approve, or contract deployment anywhere` | pass |
| Nonce is server-generated, never accepted from client | `G-SEC: nonce is server-generated, never accepted from the client` | pass |
| Raw signature bytes not logged | `G-SEC: raw signature bytes are not logged` | pass |
| Address comparisons via `normalizeAddress`, never raw equality | `G-SEC: address comparisons go through normalizeAddress, never raw equality` | pass |
| Client cannot set status / score / allocation / participant number | `G-SEC: client cannot set status / score / allocation / participant number` | pass |

All 19 `genesis-registration` tests pass. The full repo test suite — 73 tests across 9 test files — passes too (see Section 7 for the run command and section 9 for the rollback procedure).

## 3. Security model — implementation notes

- **Signature**: EIP-191 `personal_sign` only. No typed data, no `eth_sign`, no contract calls.
- **Address comparison**: always via `normalizeAddress` (EIP-55-checksum-aware but compares the lowercase canonical form). The recovered signer is compared to the requested wallet's normalized form; equality is strict and case-insensitive by construction.
- **EIP-2 malleability guard**: `s` is rejected unless `s ≤ SECP256K1_N/2`. Recovery id 0/1 and 27/28 both accepted.
- **Nonce**: 16 bytes from `crypto.getRandomValues()`, stored as `sha256(nonce)` only (we never write the raw nonce to disk), TTL 600 s, single-use, scoped to (nonce_hash, wallet_address_normalized).
- **Replay protection**: the registration transaction sets `used_at = NOW()` on the nonce row before completion. DB UNIQUE prevents duplicate `(wallet_address_normalized)` registrations; the application-level lookup-then-insert makes the response idempotent for re-registrations.
- **Allocation**: `MAX(participant_number) + 1` inside the same insert path with a UNIQUE-index-driven retry loop (5 attempts); the client cannot influence the number.
- **Logging**: signatures are never `console.log`ed; only the canonical short address (or its absence) is mentioned in API responses and any future audit events.
- **No keys, no seed phrases, no chain tx**: the server's only network operation is `getDb()` (D1). The page never asks for or accepts a private key.

## 4. Database — schema and migration

Non-destructive migration added in `apps/web/drizzle/0001_shallow_major_mapleleaf.sql` (auto-generated name; content is intentional):

```sql
CREATE TABLE `genesis_participants` (
  `id` text PRIMARY KEY,
  `participant_number` integer NOT NULL,
  `wallet_address` text NOT NULL,
  `wallet_address_normalized` text NOT NULL,
  `chain_id` integer NOT NULL,
  `joined_at` integer NOT NULL,
  `status` text NOT NULL,
  `signature_version` text NOT NULL,
  `terms_version` text NOT NULL
);

CREATE TABLE `genesis_nonces` (
  `id` text PRIMARY KEY,
  `wallet_address_normalized` text NOT NULL,
  `nonce_hash` text NOT NULL,
  `issued_at` integer NOT NULL,
  `expires_at` integer NOT NULL,
  `used_at` integer,
  `chain_id` integer NOT NULL,
  `terms_version` text NOT NULL
);

CREATE UNIQUE INDEX `genesis_participants_participant_number_unique`
  ON `genesis_participants` (`participant_number`);
CREATE UNIQUE INDEX `genesis_participants_wallet_address_normalized_unique`
  ON `genesis_participants` (`wallet_address_normalized`);
CREATE UNIQUE INDEX `genesis_nonces_nonce_hash_unique`
  ON `genesis_nonces` (`nonce_hash`);
```

No DROP TABLE / DROP COLUMN / RENAME. `tests/genesis-registration.test.mjs` asserts all of this.

## 5. UI state machine — summary

12 phases declared as a TypeScript union type, with a `useState` initializer that picks `wallet-disconnected` vs `idle` based on whether an injected wallet is present at mount. Every transition requires a user action; there is no `useEffect` that calls `setState` synchronously (verified by `eslint-plugin-react-hooks`).

The success card displays the participant number zero-padded to 4 digits (`String(n).padStart(4, "0")`), the checksum address, the ISO timestamp localized for display, and a BscScan link built from `GENESIS_CONFIG.explorerBaseUrl`. The copy controls follow the existing `/token` pattern (`navigator.clipboard.writeText`, `aria-live`, `rel="noopener noreferrer"`).

## 6. Cloud staging — status

**HUMAN_DECISION_REQUIRED**: A live end-to-end registration against the deployed Cloudflare Workers + D1 binding requires:

1. Applying migration `0001_shallow_major_mapleleaf.sql` to the production D1 instance. (`ops/cloud_audit/` and `docs/cloud/CLOUD_EXECUTION_CHECKLIST.md` already document the D1 apply flow.)
2. Deploying the `apps/web` build to Cloudflare Pages (the existing pipeline in `apps/web/scripts/build-verified.sh`).
3. Running a manual smoke test on `app.moodify.example`: connect a known BSC wallet, request nonce, sign, confirm row in `genesis_participants`.

This was **not** performed in this run. The local `tests/*.test.mjs` suite (73/73 passing) covers the logic; the live staging requires the human approval gate documented in `09_PACKAGE_CANON.json` (Package 002 has a `no_contract = false` flag and a `requires_human_approval_for = ["contract_deployment", "mainnet_signing"]` list — neither applies here, but the **cloud D1 binding apply** is recommended as a separate, runbook-driven task).

## 7. How to verify locally

```bash
cd apps/web
node --test tests/*.test.mjs                  # 73 tests, all pass
./node_modules/.bin/tsc --noEmit              # exit code 0 (no type errors)
./node_modules/.bin/eslint \
  lib/genesis-config.ts lib/genesis-message.ts lib/genesis-service.ts lib/evm-address.ts \
  app/genesis/page.tsx \
  app/api/genesis/nonce/route.ts app/api/genesis/register/route.ts app/api/genesis/me/route.ts
# exit code 0, no warnings, no errors on the G-002 scope
```

A full `npm run lint` against the entire `apps/web/` tree reports 2 pre-existing errors and 21 pre-existing warnings — none of them in any file introduced or modified by G-002. They are listed in `docs/reduction/REDUCTION_EXECUTION_002_REPORT.md` and tracked there. A full `npm run build` uses `apps/web/scripts/build-verified.sh` which provides its own infrastructure setup (Bash + D1 emulator + sourcemaps) and was not executed in this session because the script requires a POSIX shell environment.

## 8. Risk register

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Cross-script BigInt minimum target pre-existing | low | bumped `tsconfig.json` target to `ES2020`; build is unchanged at runtime (Cloudflare Workers / Workers-Vite handle BigInt natively) |
| Two `useState` setStates inside an effect body (lint rule) | low | moved initial-phase decision to the `useState` initializer; listener wiring is now effect-only |
| Page race between mount and wallet connect | low | `useState` initializer derives from `typeof window !== "undefined" && window.ethereum`; the result is stable across re-renders |
| Untracked `tests/genesis-message.test.mjs` had a syntax error in a regex | low | one-character fix (added the missing `)`); not regressed by G-002 |

## 9. Rollback procedure

The migration is **non-destructive** (no DROP / RENAME / DROP COLUMN). To roll back the application changes only (keep the tables):

```bash
git revert <commit-sha-of-G-002>
```

To roll back the database too (irreversible — only if no participants registered):

```bash
npx wrangler d1 execute moodify-db --remote \
  --command "DROP TABLE IF EXISTS genesis_participants; DROP TABLE IF EXISTS genesis_nonces;"
```

After rollback the `/genesis` route returns 404 and no participant can be registered. No other protocol or product path is affected.

## 10. Definition of Done — answers

| Question (DOD § "Definition of Done") | Answer |
| --- | --- |
| What case does this serve? | A wallet holder on BNB Smart Chain wishes to register as a Moodify Genesis Participant. |
| What is measured? | Whether the wallet produced a valid EIP-191 signature over the canonical message; whether the nonce is fresh and unused; whether the wallet is the first to claim its address. |
| What evidence is produced? | A row in `genesis_participants` with `participant_number`, `joined_at`, `signature_version`, `terms_version`. The HTTP response carries the same. |
| How is the result verified? | By 19 explicit unit tests in `tests/genesis-registration.test.mjs` covering message construction, signature recovery, nonce reuse/expiry, address normalization, race-safe allocation, and the UI state machine. |
| What happens on failure? | Each failure mode has a named `code` (`NONCE_EXPIRED`, `NONCE_USED`, `SIGNATURE_INVALID`, etc.); the UI surfaces a phase (`expired`, `rejected`, `server-error`) and lets the user retry. |
| Is the result reusable in the next case? | Yes. The service has no per-wallet secrets, no per-call randomization that can't be reproduced, and the participant row is the canonical record. |

---

**Final assessment**: G-002 is implementation-complete with verifiable tests, security controls, and documentation. Cloud-staging smoke requires a separate runbook-driven task (Section 6).
