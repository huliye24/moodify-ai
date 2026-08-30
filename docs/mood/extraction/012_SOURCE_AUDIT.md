# MOOD FOUNDATION 012 — Source Audit

**Source branch:** `codex/mood-mainnet-integration-009`
**Source SHA at audit time:** `ed6aae9b33f76e6d3ff6b2dfa1727c3921b9704e`
**Target branch:** `codex/mood-foundation-012`
**Base commit (011):** `429fbbb34abcbaf11be0cce16987bc3d0102296f`

This document records what is actually present on `codex/mood-mainnet-integration-009` (009) and which domains in 009 are relevant to 012. The audit is selective — 009 is a large commit graph and 012 is concerned only with foundation extraction, not with copying or merging the whole branch.

Per 012 GIT_SAFETY: 012 NEVER merges 009. 012 cherry-picks nothing blindly. This document is the input to `012_EXTRACTION_MANIFEST.md`.

---

## 1. 009 commit inventory (relevant only)

| SHA | Title | Relevance |
|---|---|---|
| `b3f0d71c` | feat(web3): MOOD Protocol Genesis v1.0 — Complete 8-Package Implementation | First drop of MOOD code on the web app. Includes all lib/, app/, db schema additions, contracts, scripts. |
| `ed6aae9b` | feat(web3): Package 009 Gates A-C — viem BSC integration + wallet | Tightens BSC integration; introduces the BSC-coupled `wallet.ts` and the typed viem client. |
| `8dced568` | sync: merge origin/main and commit local workspace changes | Pre-009 sync commit; carries the baseline used by 009. |

Later commits (`d59875a4` Cloudflare worker deployment, `90c9258b` protocol docs migrations, etc.) are NOT on 009 itself but are visible in the parallel `codex/mpf-002-contribution-core` branch. They are out of scope for 012 source-of-truth (009 is the explicit dependency named in PACKAGE_MANIFEST.json).

---

## 2. File inventory on 009 vs 011/012 baseline

The 011/012 baseline (`codex/mood-foundation-011`) was forked at `e24b29f5`. That baseline has:

```text
apps/web/lib/
  api.ts                              # email-based music user auth + ApiError
  cloudflare-workers-self-hosted.ts
  music-client.ts
  ownership.ts

apps/web/db/
  index.ts
  schema.ts                            # users, creatorProfiles, tracks, etc.
                                       # NO contribution/genesis tables
```

After `git diff e24b29f5..ed6aae9b -- apps/web`, 009 ADDED (relative to 011/012 baseline):

### 2.1 apps/web/lib (NEW on 009)

```text
contribution-config.ts          # enums + transitions + arithmetic config
contribution-export.ts          # rewards export utility
contribution-service.ts         # task / submission / review / reputation
                                # service layer
evm-address.ts                  # normalization + EIP-55 checksum
genesis-config.ts               # signatureVersion + nonce TTL
genesis-distribution.ts         # atomic / display conversion helpers
genesis-message.ts              # EIP-191 personal_sign digest + build
genesis-service.ts              # participant registration service
mood-chain.ts                   # viem BSC client + token reads
mood-token.ts                   # SINGLE SOURCE OF TRUTH: chainId, address,
                                # supply, DEX URLs, official CA
mood-treasury.ts                # treasury config + circulating supply methodology
wallet.ts                       # react hook (useWallet) with BSC coupling
admin-auth.ts                   # MOODIFY_ADMIN_EMAILS allowlist (ChatGPT auth)
```

### 2.2 apps/web/app (NEW on 009)

Public surface:

```text
app/token/page.tsx              # reads MOOD_TOKEN, getTotalSupply, etc.
app/token/WalletConnect.tsx     # React wallet UI tied to MOOD_TOKEN
app/contribute/page.tsx         # public contribution tasks view
app/transparency/page.tsx       # public transparency report
app/genesis/page.tsx            # registration page (KEEP BUT DARK per 011)
app/airdrop/page.tsx            # airdrop page (FREEZE per 011)
```

API routes:

```text
app/api/contribution/admin/metrics/route.ts
app/api/contribution/admin/overview/route.ts
app/api/contribution/admin/submissions/[id]/note/route.ts
app/api/contribution/admin/submissions/[id]/route.ts
app/api/contribution/admin/submissions/[id]/transition/route.ts
app/api/contribution/admin/submissions/route.ts
app/api/contribution/admin/tasks/[idOrSlug]/route.ts
app/api/contribution/admin/tasks/route.ts
app/api/contribution/me/route.ts
app/api/contribution/submissions/route.ts
app/api/contribution/tasks/[idOrSlug]/route.ts
app/api/contribution/tasks/route.ts
app/api/genesis/me/route.ts
app/api/genesis/nonce/route.ts
app/api/genesis/register/route.ts
app/api/protocol/transparency/route.ts
app/api/airdrop/eligibility/route.ts
```

Admin surface:

```text
app/admin/contributions/page.tsx
```

### 2.3 apps/web/db (MODIFIED on 009)

```text
db/schema.ts        # extended with:
                    #   genesis_participants
                    #   genesis_nonces
                    #   contribution_tasks
                    #   contribution_submissions
                    #   contribution_review_events
                    #   reputation_events
                    #   reward_events
                    # All snake_case table + column names, all additive.

drizzle/
  0001_shallow_major_mapleleaf.sql   # genesis tables
  0002_contribution_network.sql       # contribution / reputation tables
  + corresponding meta snapshots
```

### 2.4 apps/web/docs (NEW on 009)

```text
docs/protocol/CONTRIBUTION_NETWORK.md
docs/protocol/GENESIS_AIRDROP.md
docs/protocol/GENESIS_AIRDROP_RUNBOOK.md
docs/protocol/GENESIS_DISTRIBUTION.md
docs/protocol/GENESIS_LAUNCH_RUNBOOK.md
docs/protocol/TRANSPARENCY.md
docs/protocol/TREASURY.md
docs/releases/GENESIS_V1_RC.md
docs/security/GENESIS_INCIDENT_RESPONSE.md
docs/security/GENESIS_PRIVACY_REVIEW.md
docs/security/GENESIS_SECURITY_REVIEW.md
docs/security/GENESIS_THREAT_MODEL.md
docs/security/GENESIS_SECURITY_REVIEW.md
```

### 2.5 apps/web/contracts (NEW on 009)

```text
contracts/protocol/MoodGenesisDistributor.sol       # BEP-20 distributor
contracts/script/DeployLocal.s.sol
contracts/script/DeployProduction.s.sol
contracts/test/MoodGenesisDistributor.t.sol
contracts/test/Package004Compatibility.t.sol
```

### 2.6 apps/web/tests (NEW on 009)

```text
tests/contribution-network.test.mjs
tests/genesis-distribution.test.mjs
tests/genesis-message.test.mjs
tests/genesis-registration.test.mjs
tests/mood-token.test.mjs
```

### 2.7 apps/web/scripts (NEW on 009)

```text
scripts/contributions-rewards-export.ts
scripts/genesis-snapshot.ts
```

---

## 3. Domain classification

Per `EXTRACTION_MATRIX.md` initial guidance and the 011 `docs/mood/ASSET_CLASSIFICATION.md`:

### 3.1 Foundation (extract or adapt)

These are token-independent or only nominally token-coupled:

| Domain | 009 file(s) | Token coupling |
|---|---|---|
| EVM address normalization | `lib/evm-address.ts` | none |
| Wallet hook skeleton | `lib/wallet.ts` | coupled via BSC chain id and `moodBalance` field |
| EIP-191 signature primitives | `lib/genesis-message.ts` | coupled to `genesis-config.ts` which pulls `MOOD_TOKEN.chainId` |
| Genesis nonce / signature schema (DB) | `db/schema.ts` (`genesis_nonces`) | minimal; only stores `chainId` |
| Contribution config | `lib/contribution-config.ts` | imports `MOOD_TOKEN` only for arithmetic constants (`fromAtomicUnits` lives in `genesis-distribution.ts`) |
| Contribution service | `lib/contribution-service.ts` | reads `genesisParticipants` for actor identity |
| Reputation events | `db/schema.ts` (`reputation_events`) | schema-only; values are integer `points_delta` |
| Reward events (accounting) | `db/schema.ts` (`reward_events`) | schema-only; values are integer amounts |
| Admin auth | `lib/admin-auth.ts` | none |
| Transparency API | `app/api/protocol/transparency/route.ts` | reports MOOD-token-free metrics by default |
| Security docs | `docs/security/GENESIS_*` | reference docs only |

### 3.2 Token-coupled (FREEZE / KEEP BUT DARK per 011)

| Domain | 009 file(s) | Coupling |
|---|---|---|
| Token fact table | `lib/mood-token.ts` | hard-coded CA, supply, DEX URLs |
| BSC chain reads | `lib/mood-chain.ts` | imports `MOOD_TOKEN.address` |
| Treasury token config | `lib/mood-treasury.ts` | imports `MOOD_TOKEN` |
| Token page UI | `app/token/page.tsx` | reads `MOOD_TOKEN` |
| Wallet connect UI | `app/token/WalletConnect.tsx` | renders MOOD balance |
| Genesis registration page | `app/genesis/page.tsx` | tied to genesis airdrop enrollment |
| Airdrop page | `app/airdrop/page.tsx` | FREEZE |
| Airdrop eligibility API | `app/api/airdrop/eligibility/route.ts` | FREEZE |
| Genesis registration APIs | `app/api/genesis/*` | coupled to airdrop flow |
| Genesis distributor contract | `contracts/protocol/MoodGenesisDistributor.sol` | FREEZE; not deployed by 012 |
| `genesis_participants` table | `db/schema.ts` | dual-use: identity (extract) and airdrop enrollment (freeze) |

### 3.3 Out-of-scope (already on main, not 009-specific)

- `apps/web/lib/api.ts` — already in 011 baseline; untouched.
- `apps/web/lib/cloudflare-workers-self-hosted.ts`, `music-client.ts`, `ownership.ts` — already in 011 baseline.
- `apps/web/lib/genesis-distribution.ts` — `fromAtomicUnits` / `toAtomicUnits` are pure integer math; flagged here as `ADAPT` (rename `mood` → `unit`) but 012 LEAVES the names in place per "preserve names where migration cost > benefit".

---

## 4. 011 / 012 baseline delta

012 begins with 011's `docs/mood/` already present. The 011 baseline also carries `AGENTS.md`, `README.md`, `docs/canon/CANON_CHANGELOG.md`, and `scripts/canon_guard.py` modifications from 011's commit `429fbbb3`.

012 must NOT re-create any of 011's outputs. 012 builds on top of them.

012's own additions are:

```text
NEW:
  apps/web/lib/mood-launch-state.ts
  apps/web/tests/mood-launch-state.test.mjs
  docs/mood/extraction/012_SOURCE_AUDIT.md           (this file)
  docs/mood/extraction/012_EXTRACTION_MANIFEST.md
  docs/mood/extraction/012_DEPENDENCY_MAP.md
  docs/mood/extraction/012_LEGACY_TOKEN_SEAMS.md
  docs/mood/extraction/012_FINAL_REPORT.md
```

012 deliberately does NOT touch any 009 file. The foundation extraction in 012 is a documentation + boundary exercise. Code movement into the 011/012 worktree is left to the packages that consume the extracted contracts (015 Passport, 016 Contribution, 017 Network, 019 Nodes, 021 Transparency).

---

## 5. Why not just merge 009?

Per 011 `docs/mood/ASSET_CLASSIFICATION.md`, the 009 branch mixes:

- token-launch-coupled UI (`/token`, `/genesis`, `/airdrop`)
- token-coupled chain adapter (`mood-token.ts`, `mood-chain.ts`)
- foundation-grade contribution / reputation work
- a production-bound Solidity distributor

Merging the whole branch would:

1. activate Token UI under `MOOD_TOKEN.address` exposure — i.e., un-freeze the FREEZE list before G0..G11 PASS;
2. bundle token-coupled commits with foundation commits, making rollback impossible;
3. violate 011 § "011 does not merge `codex/mood-mainnet-integration-009` wholesale".

Therefore 012 is an extraction, not a merge. Each domain in §3 is treated independently in `012_EXTRACTION_MANIFEST.md`.