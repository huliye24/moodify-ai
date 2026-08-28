# Task Specification
## Transparency & Treasury

### 1. Mission

Build a public transparency layer for the Moodify Protocol and an internal configuration model for treasury/account classification.

The system should answer:

1. What is the official MOOD contract?
2. What is the total supply?
3. Where are major protocol-controlled balances held?
4. How much has been assigned to Genesis participants?
5. How much has been claimed/distributed?
6. How much is pending as contribution rewards?
7. What liquidity positions are publicly known?
8. What numbers are on-chain facts versus internal allocation/accounting facts?

### 2. Public route

Create:

`/transparency`

Recommended sections:

#### A. Protocol Asset Overview

Show:
- Token: Moodify / Mood
- Network: BNB Smart Chain
- Chain ID: 56
- Official contract
- Decimals
- Total supply
- BscScan link
- PancakeSwap link

All token facts must reuse Package 001 config authority.

#### B. Supply Accounting

Display clearly separated metrics:

- Total Supply
- Protocol-Controlled Balance
- Treasury/Reserve Balance
- Genesis Allocated
- Genesis Claimed/Distributed
- Contribution Rewards Pending
- Contribution Rewards Distributed
- Liquidity-Position Token Balance if verifiable
- Unclassified/Other Balance if applicable

Important:

`Wallet balance != circulating supply`

Do not calculate circulating supply with a simplistic formula unless the protocol has approved an exact methodology.

If no approved circulation methodology exists, show:

`Circulating supply methodology: not yet formally published`

#### C. Treasury Accounts

Render each publicly approved protocol account:

- label;
- purpose;
- chain;
- wallet address;
- current MOOD balance;
- percentage of total supply;
- BscScan link;
- control model if approved/public;
- status.

Possible labels:

```text
ecosystem
treasury
liquidity
contributors
team
strategic
genesis-distributor
```

Do not assign these labels to real addresses unless human-approved.

#### D. Genesis

Use Packages 002–005 data to show factual aggregate data:

- Registered Genesis Participants
- Eligible/Allocated
- Total Genesis Allocation
- Snapshot ID
- Merkle Root if publicly approved
- Claimed participants
- Claimed MOOD
- Unclaimed MOOD

Do not publish internal admin notes.

#### E. Contribution Network

Use Package 006 aggregates:

- Active tasks
- Approved contributions
- Reputation events/points issued
- Pending contribution MOOD
- Included-in-snapshot contribution MOOD
- Distributed contribution MOOD

#### F. Liquidity

Show only verifiable data.

Potentially:
- PancakeSwap pool
- fee tier
- pool contract
- liquidity position owner if public
- token balances/value if safely obtainable
- links to PancakeSwap/BscScan

Do not fabricate USD liquidity values if no reliable pricing source is integrated.

If only MOOD/WBNB balances are known, show token units rather than guessed USD values.

#### G. Methodology

Add a "How these numbers are calculated" section.

Explain:
- on-chain reads;
- database aggregates;
- snapshot artifacts;
- refresh cadence;
- limitations;
- data source authority.

### 3. Treasury configuration

Create a single treasury-account config source.

Preferred semantic path:

`src/config/mood-treasury.ts`

or existing equivalent.

Suggested type:

```ts
type TreasuryAccount = {
  id: string;
  label: string;
  purpose: string;
  chainId: 56;
  address: `0x${string}`;
  category:
    | "ecosystem"
    | "treasury"
    | "liquidity"
    | "contributors"
    | "team"
    | "strategic"
    | "genesis-distributor"
    | "other";
  public: boolean;
  controlModel?: "EOA" | "Safe" | "Contract" | "Unknown";
  notes?: string;
};
```

Do not populate unapproved addresses.

Support an empty or partially populated production config safely.

### 4. On-chain reads

Prefer existing RPC stack.

Required reads:

- MOOD `totalSupply()`;
- MOOD `balanceOf(address)` for configured public accounts;
- distributor balance if Package 005 deployed;
- claim state/events if indexed/readable;
- relevant pool/position data only if safely supported.

Use:
- read-only RPC;
- batching/multicall if existing stack supports it;
- caching appropriate to deployment.

No signer required.

### 5. Data freshness

Every public metric should expose or document:
- last refreshed timestamp;
- source;
- whether it is:
  - on-chain live/read;
  - database aggregate;
  - approved snapshot artifact;
  - manually configured metadata.

Avoid presenting stale data as real-time.

### 6. Reconciliation

Build internal reconciliation logic.

At minimum compare:

```text
configured account balances
+
known distributor balances
+
known liquidity-related balances where attributable
+
unclassified known balance
```

against total supply where methodology permits.

Do not force balances to equal total supply by inventing an "other" bucket unless the actual owner balance is discoverable.

The holder wallet containing most remaining MOOD may be labeled only after human approval.

### 7. Circulating supply

This is sensitive and often misunderstood.

Do not equate:
`totalSupply - founderWalletBalance`

with circulating supply.

Create a documented placeholder methodology interface, e.g.:

```ts
type CirculatingSupplyMethodology = {
  version: string;
  status: "draft" | "approved";
  description: string;
};
```

If not approved:
- do not emit a numeric circulating-supply claim.

### 8. Token allocation visualization

Only visualize approved allocation policy.

If allocation percentages are not yet canon:
- show actual observable balances/categories only;
- show "Token allocation policy forthcoming";
- do not reuse brainstorming percentages from chat as production facts.

### 9. Public JSON endpoint

Recommended:

`GET /api/protocol/transparency`

Return safe aggregate data:

```json
{
  "schema": "moodify-transparency-v1",
  "generatedAt": "...",
  "token": {},
  "accounts": [],
  "genesis": {},
  "contributions": {},
  "liquidity": {},
  "methodology": {}
}
```

Do not return:
- internal notes;
- raw signatures;
- nonces;
- admin identities;
- private participant data;
- secrets.

### 10. Treasury internal admin view

Optional if useful:

`/admin/treasury`

Read-only in Package 007.

Show:
- configured accounts;
- current balances;
- classification;
- missing/unclassified accounts;
- reconciliation warnings;
- stale RPC reads;
- distributor status.

No transfer buttons.

### 11. Safe / multisig readiness

Prepare architecture for future Safe-based treasury control, but do not create a Safe in this package.

Allowed:
- `controlModel: "Safe"` metadata;
- documentation for future migration;
- placeholder address support.

Not allowed:
- auto-creating Safe;
- assigning signers;
- proposing transactions.

### 12. Documentation

Create:

`docs/protocol/TREASURY.md`

`docs/protocol/TRANSPARENCY.md`

Document:

- public treasury-account classification;
- supply-accounting methodology;
- on-chain vs off-chain data;
- Genesis aggregates;
- contribution reward accounting;
- liquidity accounting;
- refresh/caching;
- future Safe governance;
- human approval requirements for wallet labels and allocation policy.

### 13. Explicit non-goals

Do not:
- move tokens;
- redistribute holdings;
- implement vesting;
- implement Safe transactions;
- claim "fully diluted valuation";
- claim market cap;
- publish an unapproved circulating supply;
- fabricate lock status;
- publish private wallet labels without approval;
- add treasury trading features.
