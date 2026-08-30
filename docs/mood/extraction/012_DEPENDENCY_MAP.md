# MOOD FOUNDATION 012 — Dependency Map

**Purpose:** record which 009 modules depend on which other 009 modules, and which dependencies carry MOOD-token coupling. Consumers (015, 016, 021, 013) use this map to decide what to import without re-reading 009.

**Notation:**

```text
->      imports the symbol(s) listed
*       wildcard / implicit dependency
P       imports the entire namespace
TX      the import / usage is MOOD-token-coupled (TX = "token-coupled")
```

Every dependency recorded here is observed in 009 source. This is not an aspirational design — it is a snapshot of the actual graph at `ed6aae9b`.

---

## 1. Identity / wallet graph

```text
apps/web/lib/evm-address.ts
  (no external imports; self-contained Keccak-256 + EIP-55)
  ↓ used by
apps/web/lib/wallet.ts                 [TX]
apps/web/lib/genesis-message.ts        [TX via genesis-config]
app/api/genesis/nonce/route.ts        [TX via genesis-service]
app/api/genesis/register/route.ts     [TX via genesis-service]
app/genesis/page.tsx                  [TX]
app/token/WalletConnect.tsx           [TX]

apps/web/lib/genesis-message.ts        [TX]
  -> GENESIS_CONFIG                    [TX]
  -> keccak256 (self-contained)

apps/web/lib/genesis-config.ts         [TX]
  -> MOOD_TOKEN                        [TX]   <-- contract address + officialSite

apps/web/lib/wallet.ts                 [TX]
  -> getBalance, formatMood (mood-chain) [TX]
  -> createWalletClient, custom, publicActions (viem)
  -> bsc (viem/chains)
```

**Token-coupled edges:** every edge in this graph eventually touches `MOOD_TOKEN`. Foundation extraction (015) must either:

- accept the BSC chain id as a runtime parameter (chain-agnostic), OR
- keep BSC as default but remove the `moodBalance` field from `WalletAccount` and stop rendering it under `foundation` (per `moodLaunchFeatures.showWalletTokenBalance = false`).

---

## 2. Contribution graph

```text
apps/web/lib/contribution-service.ts
  -> getDb
  -> contributionReviewEvents, contributionSubmissions, contributionTasks,
     genesisParticipants, reputationEvents, rewardEvents    (schema)
  -> ApiError (lib/api)
  -> fromAtomicUnits, toAtomicUnits       (lib/genesis-distribution)   [TX names]
  -> CONTRIBUTION_CONFIG, isAllowedSubmissionTransition,
     isContributionCategory, isPublicTaskStatus, isSubmissionStatus,
     isTaskStatus, normalizeEvidenceUrl,
     SubmissionStatus, TaskStatus          (lib/contribution-config)

apps/web/lib/contribution-config.ts        [TX: imports MOOD_TOKEN]
  -> MOOD_TOKEN                            [TX]

app/api/contribution/admin/**              (10 routes)
  -> requireAdminActor (lib/admin-auth)
  -> getDb
  -> contribution* / reputation_events / reward_events (schema)
  -> ApiError

app/api/contribution/submissions/route.ts
  -> requireMusicUser (lib/api)             [shared with Moodify Music auth]
  -> contribution-service
  -> ApiError

app/api/contribution/tasks/route.ts
  -> contribution-service
  -> ApiError

app/api/contribution/me/route.ts
  -> requireMusicUser
  -> contribution-service
  -> ApiError

app/contribute/page.tsx
  -> contribution-service (public task listing)

apps/web/lib/admin-auth.ts
  -> requireMusicUser (lib/api)
  -> getDb, users (schema)
  -> ApiError
```

**Token-coupled edges:**

- `contribution-config.ts` -> `MOOD_TOKEN` is the only direct import. The constants it reads are `decimals` (used in display formatting via `formatMood`) and `symbol` (display only). The integer math itself uses `fromAtomicUnits(MOOD_TOKEN.decimals)` and does NOT depend on the contract address.
- `genesis-distribution.ts` (TX names) is imported by `contribution-service.ts`. Its API is integer-only; renaming the file (or wrapping it) does not change the protocol contract.

**Identity edge:** `contribution-service.ts` reads `genesisParticipants.walletAddressNormalized` for actor identity. This is fine for foundation: identity is wallet-address-based and pre-dates the airdrop enrollment. 015 should normalize this to a `residentIdentities` view so that 016 does not accidentally treat airdrop fields as identity.

---

## 3. Reputation / Reward graph

```text
apps/web/lib/contribution-service.ts
  -> writes to reputation_events        (append-only)
  -> writes to reward_events            (status = "pending" / "cancelled")
  -> updates genesis_participants.contributionScore + reputationScore
     in the same transaction that writes the event
```

**Token-coupled edges:** `reward_events.amountMood` / `amountAtomic` are integer columns. No on-chain transfer is ever performed by `contribution-service.ts` (verified by reading the file: only Drizzle insert / select / update operations are present; no viem wallet client, no signer).

**Invariant held at runtime:** pending reward is accounting only; conversion to token is a *separate* operation gated by 024/025. The launch gate `moodLaunchFeatures.allowTokenRewardSettlement = false` makes this explicit at the type level.

---

## 4. Transparency / Treasury graph

```text
app/api/protocol/transparency/route.ts
  -> getDb
  -> TREASURY_CONFIG                    [TX]
  -> genesis_participants / reputation_events (for provenance counts)
  -> system version constants

app/transparency/page.tsx
  -> fetch /api/protocol/transparency

apps/web/lib/mood-treasury.ts           [TX]
  -> MOOD_TOKEN                          [TX]

apps/web/lib/mood-chain.ts              [TX]
  -> MOOD_TOKEN                          [TX]
  -> bsc, viem publicActions
```

**Token-coupled edges:** every transparency edge that touches a token number is gated behind `moodLaunchFeatures.showTreasuryTokenBalance`. Under `foundation`, the page renders provenance + policy + system version, but the treasury balance card is suppressed at the API layer (021 owns that change).

---

## 5. Launch gate (012 output)

```text
apps/web/lib/mood-launch-state.ts
  (no external imports; pure constant + helpers)

  consumers (future):
    app/token/page.tsx                    -> guarded by showTokenInfoPage
    app/token/WalletConnect.tsx           -> guarded by showWalletTokenBalance
    app/genesis/page.tsx                  -> guarded by showTokenCTAs
    app/airdrop/page.tsx                  -> guarded by showTokenCTAs
    app/api/genesis/register/route.ts     -> guarded by assertMoodLaunchState
    app/api/airdrop/eligibility/route.ts  -> guarded by assertMoodLaunchState
    app/transparency/page.tsx              -> guarded by showTreasuryTokenBalance
    app/api/protocol/transparency/route.ts
                                          -> guarded by showTreasuryTokenBalance
```

The launch gate is the **only** module 012 introduces. It must be the only place launch state is computed.

---

## 6. Cycle analysis

009 has no import cycles among the foundation candidates. The only indirect cycle is:

```text
contribution-config -> MOOD_TOKEN
contribution-service -> contribution-config
contribution-service -> genesis-distribution
genesis-distribution -> (no further deps; pure math)
```

which terminates at `MOOD_TOKEN` and `genesis-distribution`. Both are FREEZE or rename targets; breaking the cycle is a 016 task, not 012's.

---

## 7. Foundation-only contract surface (for 015 / 016 / 021 / 013)

| Contract | Module | Notes |
|---|---|---|
| `MoodLaunchState` | `apps/web/lib/mood-launch-state.ts` | 012 introduces |
| `getMoodLaunchState()` | same | public |
| `isFoundation()` | same | public |
| `mayExposePublicToken()` | same | public |
| `moodLaunchFeatures` | same | frozen object |
| `normalizeMoodLaunchState(unknown)` | same | fail-closed |
| `assertMoodLaunchState(allowed, context)` | same | throws `LAUNCH_STATE_FORBIDDEN` |

The remaining foundation contracts (`WalletSession`, `ResidentIdentitySeed`, `ContributionTask`, `ContributionSubmission`, `ReputationSnapshot`, `TransparencySnapshot`) are 015 / 016 / 021 deliverables. 012 records the expected shapes from the HANDOFF_013.md contract text:

```ts
// 015 — Wallet + Passport
type WalletSession = {
  address: string;            // normalized
  chainId: number;
  status: "connected" | "disconnected" | "wrongNetwork";
  // NO token balance under foundation
};

type ResidentIdentitySeed = {
  walletAddressNormalized: string;
  signatureVersion: string;
  joinedAt: string;           // ISO 8601
};

// 016 — Contribution Network
type ContributionTask = {
  id: string;
  slug: string;
  category: ContributionCategory;
  status: TaskStatus;
  // …
};

type ContributionSubmission = {
  id: string;
  taskId: string;
  submitterWallet: string;    // normalized
  status: SubmissionStatus;
  evidence: { … };
};

// 016 — Reputation
type ReputationSnapshot = {
  walletAddressNormalized: string;
  score: number;              // derived from reputation_events
  lastEventAt: string;
};

// 021 — Transparency
type TransparencySnapshot = {
  generatedAt: string;
  contributionCount: number;
  residentCount: number;
  // token-related fields OMITTED under foundation
};
```

013 consumes these via the route contract in `docs/portal/013_ROUTE_CONTRACT.md` (to be authored by 013).

---

## 8. Why this map matters

015 / 016 / 021 / 013 will each look at 009 and want to copy. The map tells them:

- what they can copy without renegotiating,
- what they have to rename (`genesis-distribution` → `unit-conversion` or similar),
- what they must NOT copy (`MOOD_TOKEN`, `MoodGenesisDistributor.sol`, `/airdrop`, `/token` UI),
- which DB columns are coupled so they know what to migrate later (016) and what to leave (012).

If a dependency not in this map ever appears in a foundation code path, that is a violation of INV-012-08 and must be added to `012_LEGACY_TOKEN_SEAMS.md`.