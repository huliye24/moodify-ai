# MOOD FOUNDATION 012 — Legacy Token Seams

**Purpose:** enumerate every place in 009 that still assumes the historic MOOD Genesis Token model, so that foundation code (015, 016, 021, 013) can route around them. Each seam is **known**, **isolated**, or **dark** — never silently inherited.

**Terminology (per 012 TASK.md Phase H):**

- **Known** — the seam is documented here. Future readers know it exists.
- **Isolated** — the seam is reachable only through a boundary module that the launch gate (`apps/web/lib/mood-launch-state.ts`) can disable.
- **Dark** — the seam is left in 009 but unreachable from the foundation because no foundation code imports it.

The target is **known → isolated → dark**. 012 does not promise dark for every seam — some are still in active use by 015 / 016 / 021 under the launch gate.

---

## 1. Hard-coded contract address

| File | Symbol | Legacy assumption | Risk | Temporary handling | Removal target package |
|---|---|---|---|---|---|
| `apps/web/lib/mood-token.ts` | `MOOD_TOKEN.address = "0x1BB3115D43E397f7bb586F090831B02cA639e73E"` | This address IS the future official MOOD CA. | High if foundation code imports `mood-token.ts`. | FREEZE — never imported from foundation. `lib/mood-launch-state.ts` returns false for `mayExposePublicToken()` under `foundation`. | 025 (Token Activation) after G0..G11 PASS. |

**Verification (manual):**

```bash
git grep -nE "0x1BB3115D43E397f7bb586F090831B02cA639e73E" apps/web
git grep -nE "MOOD_TOKEN\\.address" apps/web
```

The first grep should return hits ONLY in `mood-token.ts` and tests/docs that quote it. The second should return hits ONLY in 009-token-coupled files (which are FREEZE) and not in any 012 / 015 / 016 / 021 foundation consumer.

---

## 2. Hard-coded totalSupply

| File | Symbol | Legacy assumption | Risk | Temporary handling | Removal target package |
|---|---|---|---|---|---|
| `apps/web/lib/mood-token.ts` | `MOOD_TOKEN.totalSupply = "33000000"`, `totalSupplyDisplay = "33,000,000 MOOD"` | The historical supply number is canonical. | Medium — supply numbers in UI tend to drift. | FREEZE. The launch gate suppresses `showTokenInfoPage` under `foundation`, so the supply string is unreachable from the public surface. | 025 |

---

## 3. Hard-coded DEX URL

| File | Symbol | Legacy assumption | Risk | Temporary handling | Removal target package |
|---|---|---|---|---|---|
| `apps/web/lib/mood-token.ts` | `MOOD_TOKEN.tradeUrl = "https://pancakeswap.finance/swap?outputCurrency=0x..."` | PancakeSwap V3 is the only official DEX. | High — DEX exposure is a Buy CTA. | FREEZE. The launch gate suppresses `showTokenCTAs` under `foundation`. | 025 |

---

## 4. "Official Token" copy

| File | Symbol | Legacy assumption | Risk | Temporary handling | Removal target package |
|---|---|---|---|---|---|
| `app/token/page.tsx` | "Token · MOOD-GENESIS-001: MOOD 协议资产信息页" — page heading and CTA buttons. | The token is "official" today. | High — the word "official" implies an activation that has not happened. | FREEZE. The token page is not linked from the new foundation surface; `showTokenInfoPage = false` under foundation. | 025 (or earlier if 013/014 surfaces supersede the page). |

---

## 5. Genesis distribution

| File | Symbol | Legacy assumption | Risk | Temporary handling | Removal target package |
|---|---|---|---|---|---|
| `apps/web/lib/genesis-service.ts` | `registerGenesisParticipant`, `claimGenesisAllocation` | Genesis enrollment IS identity creation. | High — confuses wallet connection (foundation) with airdrop enrollment (token). | FREEZE. 015 replaces identity creation with `ResidentIdentitySeed` derived from signature only, never from airdrop status. | 015 + 025 |
| `app/genesis/page.tsx` | full-page enrollment UI | Genesis enrollment is the canonical entry. | High — page reads as "register for token". | FREEZE. | 025 |
| `app/api/genesis/{me,nonce,register}/route.ts` | registration endpoints | Same as above. | High. | FREEZE. 015 exposes `/api/passport/{me,nonce,register}` with a launch-gate check. | 015 + 025 |
| `apps/web/contracts/protocol/MoodGenesisDistributor.sol` | on-chain distributor | The distributor IS the launch contract. | Critical — never deploy from foundation work. | FREEZE. Deploy is gated by 024/025 G10/G11. | 025 |
| `apps/web/scripts/genesis-snapshot.ts` | snapshot generator | A snapshot is required today. | Medium. | LEAVE in 009. 016 may consume when it lands. | 025 (or earlier for offline ops) |

---

## 6. Airdrop eligibility

| File | Symbol | Legacy assumption | Risk | Temporary handling | Removal target package |
|---|---|---|---|---|---|
| `app/airdrop/page.tsx` | "AirDrop" page | Airdrop is active. | Critical. | FREEZE. Page must never link from foundation routes. | 025 |
| `app/api/airdrop/eligibility/route.ts` | eligibility endpoint | Same. | Critical. | FREEZE. Route returns 404 under foundation via launch-gate assertion. | 025 |

---

## 7. Treasury token balance

| File | Symbol | Legacy assumption | Risk | Temporary handling | Removal target package |
|---|---|---|---|---|---|
| `apps/web/lib/mood-treasury.ts` | `TREASURY_CONFIG` with token accounts | Treasury holds MOOD and reports it. | Medium. | FREEZE. `moodLaunchFeatures.showTreasuryTokenBalance = false` under foundation; the transparency API excludes token balance in its 021 adaptation. | 021 + 025 |
| `app/transparency/page.tsx` | "Treasury" card | Treasury card is part of the canonical transparency view. | Medium. | FREEZE. 021 replaces the card with policy + provenance + system version only. | 021 |

---

## 8. Automatic MOOD reward claim

| File | Symbol | Legacy assumption | Risk | Temporary handling | Removal target package |
|---|---|---|---|---|---|
| `reward_events.status = "distributed"` | reward events transition to `distributed` on its own. | Foundation converts pending reward to MOOD at submission time. | Critical. | 012 records that no code path in `contribution-service.ts` calls `update(reward_events).set({ status: "distributed" })`. The status field is set in source only as a literal `"pending"` or `"cancelled"`. The launch gate's `allowTokenRewardSettlement = false` makes this explicit. | 025 (Token Activation) when settlement becomes real; until then, `cancelled` is the only terminal state. |
| `genesis-distribution.ts` | `fromAtomicUnits` / `toAtomicUnits` use `MOOD_TOKEN.decimals` for display. | Decimal config is fixed at 18 forever. | Low. | ADAPT (016): wrap or rename to drop the MOOD-named import. | 016 |

---

## 9. Token-gated admin / identity

| File | Symbol | Legacy assumption | Risk | Temporary handling | Removal target package |
|---|---|---|---|---|---|
| `genesisParticipants.contributionScore` | admin score is "the" contribution score. | Confusing name; it's actually a cached aggregate from `reputation_events`. | Medium. | ADAPT (016): document the cache semantics in 016's contribution network spec. | 016 |
| `genesisParticipants.reputationScore` | Same. | Same. | Same. | ADAPT (016): same as above. | 016 |
| `genesisParticipants.allocationMood` / `allocationAtomic` | Cached allocation amounts. | This is on-chain MOOD allocation, not accounting. | High — the schema name implies on-chain settlement. | FREEZE. 015 does not expose allocation fields; 016 does not auto-settle. 025 owns settlement. | 025 |

---

## 10. Audit cron / scripts

| File | Symbol | Legacy assumption | Risk | Temporary handling | Removal target package |
|---|---|---|---|---|---|
| `scripts/contributions-rewards-export.ts` | Periodic reward export. | The export is the source of truth for distribution. | Low. | LEAVE in 009. 016 may adopt when it owns distribution cadence. | 016 / 025 |
| `contracts/script/DeployLocal.s.sol` | Local deploy script. | The distributor is deployable locally for testing. | Medium. | LEAVE — used by Foundry tests. | 025 |
| `contracts/script/DeployProduction.s.sol` | Production deploy script. | The distributor is deployable to BSC mainnet today. | Critical. | FREEZE. Production deploys of this contract are forbidden until 025 G10/G11 PASS. | 025 |

---

## 11. Routing seams

```text
app/token          -> FREEZE   (013 surfaces a foundation-grade "Token" placeholder only)
app/contribute     -> KEEP     (016 owns; 013 may surface as /contribute link)
app/transparency   -> KEEP     (021 owns; 013 may surface as /transparency link)
app/genesis        -> FREEZE   (015 may surface at /passport without enrollment semantics)
app/airdrop        -> FREEZE   (no foundation route)
app/admin/...      -> KEEP     (admin auth is foundation; only review surface is in scope)
```

013 / 015 / 016 / 021 routes MUST NOT 301-redirect to a FREEZE route under foundation. If a user follows an old link, the foundation surface should render an honest "this surface is currently frozen" placeholder, not a 302 to the freeze page.

---

## 12. Verification commands

Run from `codex/mood-foundation-012` worktree after 012 lands:

```bash
# 1. Foundation code must not import from FREEZE files.
git grep -nE "from.*['\"]@?/?lib/mood-token['\"]" apps/web
git grep -nE "from.*['\"]@?/?lib/mood-chain['\"]" apps/web
git grep -nE "from.*['\"]@?/?lib/mood-treasury['\"]" apps/web
git grep -nE "from.*['\"]@?/?lib/genesis-service['\"]" apps/web
# All four should return ZERO matches.

# 2. Foundation code must not import the contracts tree.
git grep -nE "from.*contracts/" apps/web/lib
# Should return ZERO matches.

# 3. Foundation code must not hard-code the historical CA.
git grep -nE "0x1BB3115D43E397f7bb586F090831B02cA639e73E" apps/web/lib
# Should return ZERO matches.

# 4. The launch gate is the only place launch state is computed.
git grep -nE "MOOD_LAUNCH_STATE\\s*=" apps/web
# Should return ONE match, in apps/web/lib/mood-launch-state.ts.
```

If any of those checks fail, add the offending file/symbol to the appropriate FREEZE row above and fix the import. Do NOT delete the FREEZE file from 009 in this package — deletion belongs to 025 or a dedicated cleanup task.

---

## 13. Status summary

| Seam | State |
|---|---|
| Contract address | KNOWN, FREEZE |
| totalSupply | KNOWN, FREEZE |
| DEX URL | KNOWN, FREEZE |
| "Official token" copy | KNOWN, FREEZE |
| Genesis distribution | KNOWN, FREEZE |
| Airdrop eligibility | KNOWN, FREEZE |
| Treasury token balance | KNOWN, ISOLATED via launch gate |
| Automatic reward claim | KNOWN, ISOLATED via launch gate + invariant |
| Token-gated admin/identity | KNOWN, FREEZE |
| Audit cron | KNOWN, LEAVE |
| Routing seams | KNOWN, FREEZE |