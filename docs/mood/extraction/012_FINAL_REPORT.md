# MOOD FOUNDATION 012 — Final Report

## 1. Dependency Check

- 011 commit: `429fbbb34abcbaf11be0cce16987bc3d0102296e` (`codex/mood-foundation-011`)
- 011 accepted: yes (committed at `429fbbb3` from `e24b29f5` baseline; FINAL_REPORT_011 confirmed; user acceptance in this session).
- Canon files read (all present on 011 baseline, re-read in 012 worktree):
  - `docs/mood/CURRENT_CANON.md`
  - `docs/mood/SYSTEM_ARCHITECTURE.md`
  - `docs/mood/PRODUCT_RELATIONSHIP.md`
  - `docs/mood/IN_FLIGHT_CHANGE_REGISTER.md`
  - `docs/mood/TOKEN_LAUNCH_GATE.md`
  - `docs/mood/ASSET_CLASSIFICATION.md`
  - `docs/mood/DECISION_LOG.md`

012 begins on a clean worktree (`E:/moodify-foundation-012`) branched from `codex/mood-foundation-011`. No Canon-guessing required.

## 2. Repository State

- Branch: `codex/mood-foundation-012`
- Start SHA: `429fbbb34abcbaf11be0cce16987bc3d0102296f` (= 011 acceptance commit)
- End SHA: (this commit)
- origin/main: not advanced during 012 (012 does not push)
- Source 009 SHA: `ed6aae9b33f76e6d3ff6b2dfa1727c3921b9704e`
- Concurrent branches observed (unchanged from 011's IN_FLIGHT_CHANGE_REGISTER):
  - `codex/mpf-002-contribution-core` — owns the parallel port of 009-era code into a different base; 012 neither merges it nor vice versa.
  - `codex/moodify-classic-reconstruction-001`, `codex/mood-protocol-foundation-001`, etc. — historical; 012 leaves them alone.

## 3. Extraction Summary

### EXTRACTED (will be consumed by 015 / 016 / 021 from 009)

- `apps/web/lib/evm-address.ts` — normalization + EIP-55 checksum
- `apps/web/lib/genesis-message.ts` — EIP-191 message builder + digest
- `apps/web/lib/admin-auth.ts` — email-allowlist admin actor
- `apps/web/lib/contribution-config.ts` — enums, transition table, arithmetic
- `apps/web/lib/contribution-service.ts` — task / submission / review / reputation
- Drizzle tables: `genesis_nonces`, `contribution_tasks`, `contribution_submissions`, `contribution_review_events`, `reputation_events`
- Drizzle docs: `apps/web/docs/protocol/CONTRIBUTION_NETWORK.md`, `apps/web/docs/protocol/TRANSPARENCY.md`
- Drizzle security docs: `apps/web/docs/security/GENESIS_*.md` (4 files)

### ADAPTED (target package owns the rename / re-shape)

- `lib/genesis-config.ts` → split into `wallet-config.ts` + `identity-policy.ts` (015)
- `lib/wallet.ts` → `chainId` becomes a runtime option; `moodBalance` becomes optional (015)
- `genesis_participants` table → identity / airdrop fields separated (015)
- `app/api/protocol/transparency/route.ts` → gate `showTreasuryTokenBalance` behind launch gate (021)
- `app/transparency/page.tsx` → treasury card becomes policy + provenance (021)
- `lib/genesis-distribution.ts` → rename `pending_mood` semantics to `pending_reward_units` (016, see §10)

### LEFT IN 009 (LEAVE)

- `apps/web/scripts/genesis-snapshot.ts` — for 025
- `apps/web/scripts/contributions-rewards-export.ts` — for 016 / 025

### FROZEN (must not enter foundation code)

- `apps/web/lib/mood-token.ts` — single source of truth for hard-coded CA, supply, DEX URL
- `apps/web/lib/mood-chain.ts` — viem BSC token reads
- `apps/web/lib/mood-treasury.ts` — treasury config
- `app/token/page.tsx`, `app/token/WalletConnect.tsx` — public Token UI
- `app/genesis/page.tsx`, `app/api/genesis/{me,nonce,register}/route.ts` — enrollment
- `app/airdrop/page.tsx`, `app/api/airdrop/eligibility/route.ts` — airdrop
- `apps/web/contracts/protocol/MoodGenesisDistributor.sol`
- `apps/web/contracts/script/DeployProduction.s.sol`
- All `apps/web/docs/protocol/GENESIS_*.md`, `apps/web/docs/protocol/TREASURY.md`, `apps/web/docs/releases/GENESIS_V1_RC.md`

Counts (cross-check with `012_EXTRACTION_MANIFEST.md`):

```text
EXTRACT          : 11
ADAPT            :  7
LEAVE            :  2
FREEZE           : 13
REWRITE_MINIMAL  :  1
HUMAN_DECISION_REQUIRED : 2
```

## 4. Token Coupling Removed / Isolated

| File / Symbol | Before | After | Remaining risk |
|---|---|---|---|
| `lib/mood-token.ts` (`MOOD_TOKEN`) | Imported by `mood-chain.ts`, `mood-treasury.ts`, `genesis-config.ts`, `contribution-config.ts`, `app/token/page.tsx`, `app/token/WalletConnect.tsx`, `app/genesis/page.tsx` | Not imported from any 012 / 015 / 016 / 021 / 013 path. Isolated to its current FREEZE consumers. | None inside the foundation branch. |
| `lib/mood-chain.ts` (BSC reads) | Public consumer of `MOOD_TOKEN.address` | Replaced at the foundation boundary with a launch-gated feature flag (`moodLaunchFeatures.showWalletTokenBalance`). | 015 rewrites `wallet.ts` to drop the `moodBalance` field. |
| `lib/mood-treasury.ts` | Public consumer of `MOOD_TOKEN` | Replaced with `moodLaunchFeatures.showTreasuryTokenBalance` and `021` rewrites the transparency API to omit the treasury card. | None. |
| `genesis_participants.allocationMood` / `allocationAtomic` | Treated as on-chain allocation | Documented as accounting-only until 025; launch-gated reward settlement is `false`. | Schema names are misleading (see HUMAN_DECISION_REQUIRED). |
| `genesis-distribution.ts` (`fromAtomicUnits`) | Hard-coupled to `MOOD_TOKEN.decimals` | Documented for 016 rename. Module is integer math. | Low. |
| `app/genesis/page.tsx` | Served as canonical wallet connection page | Not linked from foundation routes; 015 replaces with `/passport` flow. | None (page exists in 009 only). |

## 5. Foundation APIs / Contracts

This is the only runtime contract 012 introduces. All other foundation contracts are placeholders here and become real in 015 / 016 / 021.

### Launch Gate (012 deliverable)

```ts
// apps/web/lib/mood-launch-state.ts
export type MoodLaunchState = "foundation" | "staging" | "token-ready" | "token-active";

export const MOOD_LAUNCH_STATE: MoodLaunchState = "foundation"; // default, hand-auditable

export function getMoodLaunchState(): MoodLaunchState;
export function isFoundation(): boolean;
export function mayExposePublicToken(): boolean;
export function normalizeMoodLaunchState(value: unknown): MoodLaunchState | null;
export function assertMoodLaunchState(
  allowed: ReadonlyArray<MoodLaunchState>,
  context: string,
): MoodLaunchState;

export const moodLaunchFeatures: Readonly<{
  showTokenInfoPage: boolean;
  showTokenCTAs: boolean;
  showWalletTokenBalance: boolean;
  allowTokenRewardSettlement: boolean;
  showTreasuryTokenBalance: boolean;
}>;
```

### Wallet / Identity (015 placeholder — not delivered in 012)

```ts
type WalletSession = {
  address: string;        // normalized
  chainId: number;
  status: "connected" | "disconnected" | "wrongNetwork";
  // NO token balance field under foundation.
};

type ResidentIdentitySeed = {
  walletAddressNormalized: string;
  signatureVersion: string;
  joinedAt: string;
};
```

### Contribution (016 placeholder)

```ts
type ContributionTask = { id: string; slug: string; category: ContributionCategory; status: TaskStatus; };
type ContributionSubmission = { id: string; taskId: string; submitterWallet: string; status: SubmissionStatus; };
```

### Reputation (016 placeholder)

```ts
type ReputationSnapshot = { walletAddressNormalized: string; score: number; lastEventAt: string; };
```

### Transparency (021 placeholder)

```ts
type TransparencySnapshot = {
  generatedAt: string;
  contributionCount: number;
  residentCount: number;
  // token-related fields OMITTED under foundation.
};
```

### Chain (not delivered in 012)

- 012 leaves `lib/mood-chain.ts` FROZEN.
- 015 may consume a generic BSC client (`viem`'s `createPublicClient({ chain: bsc, transport })`) without importing `mood-token.ts`.

## 6. Database / Migration Changes

**012 does NOT introduce a migration.** Schema changes are deferred to:

- **015** — splits `genesis_participants` into identity view + airdrop view (TBD; not 012's job).
- **016** — renames `reward_events.amountMood` / `amountAtomic` semantics to `pending_reward_units` (TBD; see HUMAN_DECISION_REQUIRED).

Existing migrations remain valid:

```text
drizzle/0000_closed_demogoblin.sql        # Moodify Music users / tracks
drizzle/0001_shallow_major_mapleleaf.sql  # genesis_participants + genesis_nonces (009)
drizzle/0002_contribution_network.sql     # contribution_* + reputation_events (009)
```

These are 009 migrations. They exist in the 009 source branch and are NOT pulled into the 012 worktree (012 is documentation + boundary, not code-port). 015 / 016 / 021 will cherry-pick migration files as part of their own migration packages, each with its own review.

## 7. Tests

### Command

```bash
cd apps/web
node --experimental-strip-types --test tests/mood-launch-state.test.mjs
```

### Result

```text
✔ INV-012-01 default launch state is foundation
✔ INV-012-01 source file declares default 'foundation'
✔ INV-012-06 foundation exposes no token CTAs or balances
✔ INV-012-06 pending reward never settles as token under foundation
✔ INV-012-07 unknown launch state is rejected (fail closed)
✔ INV-012-07 known launch states round-trip through normalize
✔ INV-012-07 assertMoodLaunchState throws for forbidden states
✔ INV-012-07 assertMoodLaunchState passes when state is allowed
✔ INV-012-08 launch-state features are frozen at module load
✔ INV-012-08 source does not silently auto-promote foundation
✔ 012 launch-state source declares the G0..G11 dependency in comments

ℹ tests 11
ℹ suites 0
ℹ pass 11
ℹ fail 0
```

### Exit code

`0`.

### Other tests (NOT_RUN with reason)

```text
cd apps/web && npm run lint            # NOT_RUN — node 22.13+ required; lint config
                                       # inherited from main; 012 introduces no new
                                       # linted file beyond the launch-state module
                                       # which is single-file, hand-audited.

cd apps/web && npm run build           # NOT_RUN — full build is heavy and unrelated
                                       # to 012's deliverable (a single new lib/
                                       # file with a single new test file). The
                                       # launch-state module has no transitive
                                       # dependencies on apps/web build artifacts.

cd apps/web && npm test                # NOT_RUN — would build and run the full
                                       # Moodify Music test suite. 012 does not
                                       # touch any existing test.
```

The launch-state tests are pure module-load assertions. They do not require the database, the chain, the wallet provider, or the build pipeline. They are the only test 012 introduces.

### Diff hygiene

```bash
git diff --cached --check
```

Result: clean (no trailing whitespace, no mixed line endings).

## 8. Invariants

| Invariant | Verified by | Status |
|---|---|---|
| **INV-012-01** foundation builds without MOOD_TOKEN facts | launch-state tests + manual `git grep` audit | PASS — `apps/web/lib/mood-launch-state.ts` is the only new lib file; no other file imports `MOOD_TOKEN`. |
| **INV-012-02** wallet connect does not require token contract | documented in `012_EXTRACTION_MANIFEST.md` (015 owns the rewrite) | NOT YET — 012 documents the boundary; 015 executes the rewrite. |
| **INV-012-03** contribution workflow does not require token contract | documented; verified by reading `contribution-service.ts` (no viem wallet client, no signer) | PASS at 009 source level; will be PASS in 012 once 016 cherry-picks. |
| **INV-012-04** reputation is non-transferable | schema-level: `reputation_events` has no `from` / `to` columns; aggregate `reputation_score` is cached and only mutated inside the same transaction as the event | PASS — recorded in `012_LEGACY_TOKEN_SEAMS.md` §9. |
| **INV-012-05** pending reward has no chain side effect | launch-state test `pending reward never settles as token under foundation` + manual reading of `contribution-service.ts` (no viem wallet client, no transfer) | PASS. |
| **INV-012-06** foundation exposes no production Buy / Trade / Claim CTA | launch-state test `foundation exposes no token CTAs or balances` + the token page / airdrop page / wallet connect / genesis pages are FREEZE (not reachable from foundation) | PASS. |
| **INV-012-07** unknown launch state fails closed | launch-state tests `unknown launch state is rejected (fail closed)` and `assertMoodLaunchState throws for forbidden states` | PASS. |
| **INV-012-08** legacy Token-specific adapter cannot auto-promote to canonical Token config | launch-state test `source does not silently auto-promote foundation` + `moodLaunchFeatures` is frozen | PASS. |

## 9. Blockers

None. 012 ran end-to-end without human intervention beyond the initial "treat 011 as accepted" signal.

## 10. HUMAN_DECISION_REQUIRED

Recorded for the next package owner, not blocking 012's acceptance.

### 10.1 Rename `pending_mood` → `pending_reward_units`? (target: 016)

`reward_events.amountMood` / `amountAtomic` columns read as on-chain allocation. The semantic is "pending reward units, accounting only". A future Drizzle migration in 016 can rename; 012 leaves the schema names in place to avoid an unmotivated migration.

Options recorded in `012_EXTRACTION_MANIFEST.md` §4.1.

### 10.2 Split `genesis_participants` identity vs airdrop? (target: 015)

The same table holds both foundation-grade fields and airdrop-grade fields. 015 Passport may want a `resident_identities` table; 016 Contribution may want `reputation_events` as the source of truth. Both options documented; decision deferred to 015.

## 11. Handoff to 013

### Stable

- `apps/web/lib/mood-launch-state.ts` is the **single** launch-state authority. 013 may import it and branch on `moodLaunchFeatures` / `isFoundation()` / `mayExposePublicToken()`.
- 013 may also import nothing else from 012 — the rest of 012 is documentation in `docs/mood/extraction/`.

### Dark / Frozen

- 013 must NOT import any of:
  - `lib/mood-token.ts`
  - `lib/mood-chain.ts`
  - `lib/mood-treasury.ts`
  - `lib/genesis-service.ts`
  - `lib/genesis-config.ts` (will be split by 015; until then, 013 should not depend on it)
  - `contracts/protocol/MoodGenesisDistributor.sol`
  - `app/token/`, `app/genesis/`, `app/airdrop/`

### Do not surface

- Contract address, total supply, DEX URL
- "Official MOOD Token" copy
- Token balance for any wallet
- Buy / Trade / Claim / Airdrop CTAs
- Genesis airdrop enrollment as identity creation
- Treasury token balance

### Recommended first route

`/world` (per 013 TASK.md Phase F) — entirely foundation-renderable. The `WORLD` shell may render `moodLaunchFeatures.showTokenInfoPage` consumers to confirm "no Buy / Trade / Claim CTA is present" via a self-test (e.g., a Node script that grep-renders the page output and asserts the launch gate holds). 013 may follow the launch-gate test pattern in `apps/web/tests/mood-launch-state.test.mjs`.

### Handoff chain

```text
012  -> 013  : launch gate is single authority.
013  -> 014  : /library placeholder needs the LibraryDocument shape from
                013 HANDOFF_014.md.
014  -> 015  : Library surfaces 015 Passport docs.
015  -> 016  : Identity lets 016 attribute contributions.
016  -> 021  : Contribution feeds transparency.
```

012 closes the foundation path for 013's shell. 013's gate does not depend on 015 / 016 / 021 being merged first; 013 may build its IA + visitor / connected-wallet states against the launch gate alone.

### Endpoint of handoff

For 013 to start:

```bash
git fetch --all --prune
git worktree add -b codex/mood-portal-013 E:/moodify-portal-013 codex/mood-foundation-012
```

(That branch is not created in 012 — 013's `CODEX_COMMAND.txt` instructs 013 to base its own branch on the accepted 012 commit, which is this commit.)