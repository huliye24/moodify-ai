# MOOD FOUNDATION 012 — Extraction Manifest

**Source:** `codex/mood-mainnet-integration-009` @ `ed6aae9b33f76e6d3ff6b2dfa1727c3921b9704e`
**Target:** `codex/mood-foundation-012` (forked from `codex/mood-foundation-011` @ `429fbbb34abcbaf11be0cce16987bc3d0102296f`)
**Output of:** 012 TASK.md Phase C

This document lists every candidate asset from 009 and the per-asset Action. The Action vocabulary follows the 012 EXTRACTION_MATRIX guidance:

- **EXTRACT** — copy the source's logic into the target unchanged. No semantic edits.
- **ADAPT** — copy with a small documented change (rename, narrow surface, drop a token-specific field). The adaptation must NOT change the protocol-level contract.
- **LEAVE** — leave the asset in the source branch. Do NOT copy. The target branch will not reference it.
- **FREEZE** — leave the asset in the source branch AND mark it as not to be activated until 024/025 (per `docs/mood/TOKEN_LAUNCH_GATE.md`).
- **REWRITE_MINIMAL** — copy with a deliberate semantic change in the target (e.g., decouple from `MOOD_TOKEN`). Reserved for assets whose current shape is wrong for foundation.
- **HUMAN_DECISION_REQUIRED** — Codex cannot decide; record here for review.

Per 011 `docs/mood/ASSET_CLASSIFICATION.md`, the KEEP / KEEP-BUT-DARK / FREEZE / SEPARATE classes are honored here. 012 does not re-litigate 011's classifications; it only adds EXTRACT/ADAPT/REWRITE_MINIMAL where foundation code needs to surface.

---

## 1. Asset-by-asset manifest

### 1.1 Identity / wallet

| Asset | Source Branch | Source Path | Classification (011) | Action | Token Coupling | Tests on 009 |
|---|---|---|---|---|---|---|
| EVM address utilities | `codex/mood-mainnet-integration-009` | `apps/web/lib/evm-address.ts` | KEEP | **EXTRACT** (to a future 015 worktree; for 012: document only) | none | none on 009 |
| EIP-191 signature message builder | `codex/mood-mainnet-integration-009` | `apps/web/lib/genesis-message.ts` | KEEP | **EXTRACT** (015) | nominal — `GENESIS_CONFIG.chainId` | `tests/genesis-message.test.mjs` |
| Genesis signature config | `codex/mood-mainnet-integration-009` | `apps/web/lib/genesis-config.ts` | KEEP | **ADAPT** when 015 lands — split into `wallet-config.ts` (chainId, signatureVersion) and `identity-policy.ts` (termsVersion). 012 documents only. | imports `MOOD_TOKEN` for chainId + officialSite | covered by genesis-message tests |
| Wallet React hook | `codex/mood-mainnet-integration-009` | `apps/web/lib/wallet.ts` | KEEP | **REWRITE_MINIMAL** when 015 lands — `chainId` parameter becomes a runtime option (default BSC = 56 is fine, but `moodBalance` must be optional). 012 documents only. | hard-codes BSC, fetches MOOD balance | none on 009 |
| `genesis_participants` table | `codex/mood-mainnet-integration-009` | `apps/web/db/schema.ts` (lines around `genesis_participants`) | KEEP (identity fields) / KEEP-BUT-DARK (airdrop fields) | **ADAPT** at next migration — split identity-bearing fields (`walletAddressNormalized`, `signatureVersion`, `joinedAt`) from airdrop-bearing fields (`allocationMood`, `allocationAtomic`, `contributionScore`). 012: do not migrate; record in 012_DEPENDENCY_MAP. | dual: identity is foundation; allocation is token | `tests/genesis-registration.test.mjs` |
| `genesis_nonces` table | `codex/mood-mainnet-integration-009` | `apps/web/db/schema.ts` | KEEP | **EXTRACT** (015) | stores `chainId` only | genesis-registration tests |

### 1.2 Contribution / Reputation / Reward

| Asset | Source Branch | Source Path | Classification (011) | Action | Token Coupling | Tests on 009 |
|---|---|---|---|---|---|---|
| Contribution config | `codex/mood-mainnet-integration-009` | `apps/web/lib/contribution-config.ts` | KEEP | **EXTRACT** | imports `MOOD_TOKEN` for arithmetic; arithmetic is on integer `units`, not tokens | none directly |
| Contribution service | `codex/mood-mainnet-integration-009` | `apps/web/lib/contribution-service.ts` | KEEP | **EXTRACT** | reads `genesisParticipants` for actor identity; no token transfer / no signer | `tests/contribution-network.test.mjs` |
| Contribution export script | `codex/mood-mainnet-integration-009` | `apps/web/scripts/contributions-rewards-export.ts` | KEEP | **LEAVE** in source until 016 consumes it; record here for 016 | emits `reward_events` rows | none |
| `contribution_tasks` table | `codex/mood-mainnet-integration-009` | `apps/web/db/schema.ts` | KEEP | **EXTRACT** | none | contribution-network tests |
| `contribution_submissions` table | `codex/mood-mainnet-integration-009` | `apps/web/db/schema.ts` | KEEP | **EXTRACT** | none | contribution-network tests |
| `contribution_review_events` table | `codex/mood-mainnet-integration-009` | `apps/web/db/schema.ts` | KEEP | **EXTRACT** | none | contribution-network tests |
| `reputation_events` table | `codex/mood-mainnet-integration-009` | `apps/web/db/schema.ts` | KEEP | **EXTRACT** | schema-only integer `points_delta` | contribution-network tests |
| `reward_events` table | `codex/mood-mainnet-integration-009` | `apps/web/db/schema.ts` | KEEP-BUT-DARK | **ADAPT** — schema retained; semantic renamed in docs: `pending_reward_units` accounting only. No schema migration in 012. | `status: "pending" \| "included_in_snapshot" \| "distributed" \| "cancelled"` — only `cancelled` / `pending` are exercisable today | contribution-network tests |

### 1.3 Transparency / Admin

| Asset | Source Branch | Source Path | Classification (011) | Action | Token Coupling | Tests on 009 |
|---|---|---|---|---|---|---|
| Admin auth (allowlist) | `codex/mood-mainnet-integration-009` | `apps/web/lib/admin-auth.ts` | KEEP | **EXTRACT** | none | covered by contribution tests |
| Transparency API route | `codex/mood-mainnet-integration-009` | `app/api/protocol/transparency/route.ts` | KEEP | **ADAPT** — guard `showTreasuryTokenBalance` behind the new launch gate (foundation = false). 012 documents only; route copy happens in 021. | currently emits treasury token balance if configured | none |
| Transparency page | `codex/mood-mainnet-integration-009` | `app/transparency/page.tsx` | KEEP | **ADAPT** (021) | renders token balance card | none |

### 1.4 Token-coupled (DO NOT extract into foundation)

| Asset | Source Branch | Source Path | Classification (011) | Action | Token Coupling | Tests on 009 |
|---|---|---|---|---|---|---|
| MOOD token fact table | `codex/mood-mainnet-integration-009` | `apps/web/lib/mood-token.ts` | KEEP-BUT-DARK | **FREEZE** | hard-coded `address`, `totalSupply`, DEX URL | `tests/mood-token.test.mjs` |
| BSC chain reads | `codex/mood-mainnet-integration-009` | `apps/web/lib/mood-chain.ts` | KEEP-BUT-DARK | **FREEZE** | imports `MOOD_TOKEN` | none directly |
| Treasury config | `codex/mood-mainnet-integration-009` | `apps/web/lib/mood-treasury.ts` | KEEP-BUT-DARK | **FREEZE** | imports `MOOD_TOKEN` | none directly |
| Token page | `codex/mood-mainnet-integration-009` | `app/token/page.tsx` | KEEP-BUT-DARK | **FREEZE** | renders CA + DEX | none |
| WalletConnect UI | `codex/mood-mainnet-integration-009` | `app/token/WalletConnect.tsx` | KEEP-BUT-DARK | **FREEZE** | renders MOOD balance | none |
| Genesis registration page | `codex/mood-mainnet-integration-009` | `app/genesis/page.tsx` | KEEP-BUT-DARK | **FREEZE** until 015 re-skins it | enrollment UI | none |
| Genesis registration APIs | `codex/mood-mainnet-integration-009` | `app/api/genesis/{me,nonce,register}/route.ts` | KEEP-BUT-DARK | **FREEZE** | registration endpoint | `tests/genesis-registration.test.mjs` |
| Airdrop page | `codex/mood-mainnet-integration-009` | `app/airdrop/page.tsx` | FREEZE | **FREEZE** | airdrop UI | none |
| Airdrop eligibility API | `codex/mood-mainnet-integration-009` | `app/api/airdrop/eligibility/route.ts` | FREEZE | **FREEZE** | airdrop eligibility | none |
| Genesis distributor contract | `codex/mood-mainnet-integration-009` | `apps/web/contracts/protocol/MoodGenesisDistributor.sol` | FREEZE | **FREEZE** | BEP-20 distributor | `tests/MoodGenesisDistributor.t.sol` |
| Genesis distribution helpers | `codex/mood-mainnet-integration-009` | `apps/web/lib/genesis-distribution.ts` | KEEP-BUT-DARK | **LEAVE** for now — `fromAtomicUnits` / `toAtomicUnits` are pure integer math but their names bind them to the MOOD token. 012 documents the rename candidates; does not edit. | names only | `tests/genesis-distribution.test.mjs` |
| Genesis snapshot script | `codex/mood-mainnet-integration-009` | `apps/web/scripts/genesis-snapshot.ts` | KEEP-BUT-DARK | **LEAVE** for 025 | snapshot + Merkle | none |
| Genesis distribution deploy scripts | `codex/mood-mainnet-integration-009` | `apps/web/contracts/script/{DeployLocal,DeployProduction}.s.sol` | FREEZE | **FREEZE** | production deploy script | covered by foundry tests |

### 1.5 Documentation

| Asset | Source Branch | Source Path | Classification (011) | Action | Token Coupling | Tests on 009 |
|---|---|---|---|---|---|---|
| Contribution network spec | `codex/mood-mainnet-integration-009` | `apps/web/docs/protocol/CONTRIBUTION_NETWORK.md` | KEEP / REFERENCE | **REFERENCE** in 012_DEPENDENCY_MAP; copy verbatim if 016 needs it | none | n/a |
| Transparency spec | `codex/mood-mainnet-integration-009` | `apps/web/docs/protocol/TRANSPARENCY.md` | KEEP / REFERENCE | **REFERENCE** in 012_DEPENDENCY_MAP | light | n/a |
| Genesis docs (`GENESIS_AIRDROP.md`, `GENESIS_AIRDROP_RUNBOOK.md`, `GENESIS_DISTRIBUTION.md`, `GENESIS_LAUNCH_RUNBOOK.md`) | `codex/mood-mainnet-integration-009` | `apps/web/docs/protocol/GENESIS_*.md` | FREEZE | **FREEZE** | heavy | n/a |
| Treasury doc | `codex/mood-mainnet-integration-009` | `apps/web/docs/protocol/TREASURY.md` | FREEZE | **FREEZE** | heavy | n/a |
| Genesis V1 RC | `codex/mood-mainnet-integration-009` | `apps/web/docs/releases/GENESIS_V1_RC.md` | FREEZE | **FREEZE** | heavy | n/a |
| Security docs (`GENESIS_INCIDENT_RESPONSE.md`, `GENESIS_PRIVACY_REVIEW.md`, `GENESIS_SECURITY_REVIEW.md`, `GENESIS_THREAT_MODEL.md`) | `codex/mood-mainnet-integration-009` | `apps/web/docs/security/GENESIS_*.md` | EXTRACT/REFERENCE | **REFERENCE** in 022 handoff | light | n/a |

---

## 2. Counts

```text
EXTRACT          : 11   (identity, contribution, reputation, admin)
ADAPT            :  7   (015 will refactor genesis-config + wallet hook;
                        016 will rename genesis-distribution;
                        021 will gate transparency)
LEAVE            :  2   (genesis-distribution, genesis-snapshot)
FREEZE           : 13   (token-coupled UI / contracts / docs)
REWRITE_MINIMAL  :  1   (wallet hook when 015 lands)
HUMAN_DECISION_REQUIRED :
                  1   (renaming `pending_mood` to `pending_reward_units` —
                       see §4)
```

---

## 3. Decision rules applied

1. **Token coupling is the gating question.** Any asset whose public contract references `MOOD_TOKEN.address`, DEX URLs, `totalSupply`, or `pending_mood` is FREEZE'd by default. Foundation consumers (015 / 016 / 021) must read the launch gate (`apps/web/lib/mood-launch-state.ts`) and either render nothing, or render a stub, when the state is `foundation`.
2. **Schema migration is deferred.** 012 deliberately does not introduce a Drizzle migration to rename `pending_mood` or split `genesis_participants`. The freeze list names a *target* package (015, 016, 021) that owns the schema migration when the relevant gate passes. Migration-by-stealth is forbidden.
3. **Test porting is per asset.** Tests on 009 (`tests/contribution-network.test.mjs`, `tests/genesis-message.test.mjs`, `tests/genesis-registration.test.mjs`, `tests/genesis-distribution.test.mjs`, `tests/mood-token.test.mjs`) are NOT brought into 011/012. They continue to live on 009 so that 016 / 021 can pick them up under their own migration packages without dragging in the FREEZE assets.
4. **No whole-009 import.** `apps/web/contracts/`, `app/genesis`, `app/airdrop`, `app/token`, and the corresponding lib/ files are NEVER imported from the foundation. Any cross-import is a contract violation that the launch gate would catch (via INV-012-08).

---

## 4. HUMAN_DECISION_REQUIRED

### 4.1 Rename `pending_mood` → `pending_reward_units`?

The `reward_events` table on 009 has `amountMood` / `amountAtomic` integer columns whose **schema names** imply on-chain MOOD allocation. The table's `status` field already includes `"pending"` (not `"settled"`), and 011 explicitly forbids auto-conversion to token. So the column names are misleading but not contractually wrong.

Options:

- **A.** Leave schema names. Document in `012_LEGACY_TOKEN_SEAMS.md`. Cost: zero migration risk. Risk: future readers assume the table is a token ledger.
- **B.** Rename columns in 016 with a Drizzle migration. Cost: ~1 hour + a separate code change in contribution service. Risk: low. The semantic intent matches `pending_reward_units` from 012 TASK.md Phase D.

012 itself does not decide. This is recorded for 016 to resolve when it opens its own migration.

### 4.2 Split `genesis_participants` identity vs airdrop?

The table holds both foundation-grade fields (`walletAddressNormalized`, `signatureVersion`, `joinedAt`) and airdrop-grade fields (`allocationMood`, `allocationAtomic`, `contributionScore`, `reputationScore`).

- 015 Passport may want a `resident_identities` table (new) and a view or join to `genesis_participants` for legacy wallets.
- 016 Contribution Network may want `reputation_events` as the source of truth for `contributionScore` / `reputationScore` cached aggregates.

012 documents both options and lets 015 / 016 pick.

---

## 5. Cross-check with HANDOFF_013

013 needs (per `HANDOFF_013.md`):

```text
WalletSession                  -> supplied by 015; 012 documents boundary
ResidentIdentitySeed           -> supplied by 015; 012 documents boundary
ContributionTask               -> EXTRACT (016)
ContributionSubmission         -> EXTRACT (016)
ReputationSnapshot / ReputationEvents -> EXTRACT (016)
TransparencySnapshot           -> ADAPT (021)
LaunchState                    -> 012 introduces; documented here
```

013 MUST NOT directly import any FREEZE asset from 009. 013 reads only:

- `apps/web/lib/mood-launch-state.ts` (012 output)
- The TypeScript contracts recorded in `012_DEPENDENCY_MAP.md`
- The `LibraryDocument` shape recorded in 013 HANDOFF_014 (future contract)

`012_LEGACY_TOKEN_SEAMS.md` records the explicit "do not import" list for 013.