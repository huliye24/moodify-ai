# Task Specification
## MOOD Protocol Foundation

### 1. Confirmed token facts

Use these as the initial canonical facts, but still verify all chain-readable values before implementation.

| Field | Value |
|---|---|
| Network | BNB Smart Chain |
| Chain ID | 56 |
| Token name | Moodify |
| Symbol | Mood |
| Contract | `0x1BB3115D43E397f7bb586F090831B02cA639e73E` |
| Decimals | 18 |
| Total supply | 33,000,000 MOOD |
| Primary DEX | PancakeSwap V3 |
| Primary pair | MOOD / WBNB |
| Fee tier | 1% |

### 2. Repository audit

Before changing code:

1. Read root project instructions (`AGENTS.md`, `README`, repo status, canon files if present).
2. Locate the active web app.
3. Identify:
   - framework and routing mode;
   - current design system;
   - shared layout/navigation;
   - environment/config conventions;
   - existing Web3 libraries;
   - existing RPC helpers;
   - tests;
   - build/lint/typecheck commands.
4. Report any conflict between this package and repository canon.
5. If a canon conflict exists, **stop before implementation** and report it.

Do not create duplicate architecture if equivalent primitives already exist.

### 3. Single token authority source

Create one reusable token configuration module in the existing project convention.

Preferred semantic location:

`src/config/mood-token.ts`

Equivalent existing project path is acceptable.

It must be the only application-level authority for:

- chain ID;
- network name;
- contract address;
- token name;
- symbol;
- decimals;
- total supply;
- BscScan link;
- official website;
- GitHub;
- PancakeSwap trade link;
- primary DEX metadata.

Do not hard-code the contract address in multiple UI files.

Suggested shape:

```ts
export const MOOD_TOKEN = {
  chainId: 56,
  network: "BNB Smart Chain",
  name: "Moodify",
  symbol: "Mood",
  address: "0x1BB3115D43E397f7bb586F090831B02cA639e73E",
  decimals: 18,
  totalSupply: "33000000",
  explorerUrl: "...",
  tradeUrl: "...",
  officialSite: "...",
  githubUrl: "..."
} as const;
```

Adapt types and naming to repository conventions.

### 4. Public `/token` page

Add an official MOOD token page.

Required sections:

#### Hero
- MOOD / Moodify
- concise protocol-asset description;
- BNB Smart Chain badge;
- official contract address;
- copy-address action.

#### Token facts
- network;
- chain ID;
- contract;
- decimals;
- total supply;
- primary DEX;
- pair;
- fee tier.

#### Official links
- BscScan;
- PancakeSwap;
- project website;
- GitHub.

All external links must be explicit and safe.

#### Protocol purpose
Explain MOOD as a protocol asset of the Moodify ecosystem.

Do not frame it as:
- guaranteed investment;
- security;
- guaranteed appreciation;
- fixed-return instrument.

#### Token allocation
Create a transparent placeholder structure only if allocation policy is not yet canon.

Suggested wording:
> Token allocation policy is being formalized and will be published through Moodify protocol documentation before any large-scale distribution.

Do not invent percentages in production unless already approved elsewhere in the repository.

#### Risk notice
Must communicate:
- token is newly launched;
- liquidity can be shallow;
- prices can be volatile;
- smart-contract and market risks exist;
- users should verify the contract address;
- no guaranteed return.

### 5. UX requirements

- Preserve current Moodify visual language.
- Mobile and desktop responsive.
- Contract address must be easy to copy.
- Copy feedback must be visible.
- Long addresses must not break layout.
- External links must use safe rel attributes where applicable.
- No giant crypto-dashboard redesign.
- Avoid unnecessary Web3 visual clichés.

### 6. Documentation

Create:

`docs/protocol/MOOD_TOKEN.md`

or equivalent canonical docs location.

Document:
- official contract;
- network;
- chain ID;
- decimals;
- total supply;
- explorer link;
- DEX;
- metadata authority;
- configuration authority source;
- update procedure;
- what requires human confirmation.

### 7. Tests

At minimum:

1. token config exports expected BSC chain ID;
2. contract address is exactly the approved address;
3. address is not replaced with placeholder/example data;
4. `/token` renders;
5. copy control works if component tests exist;
6. production build passes.

Use existing project test infrastructure instead of adding a new test framework unless absolutely necessary.

### 8. Build verification

Run the repository-equivalent of:

- install only if needed;
- lint;
- typecheck;
- unit tests;
- production build.

Do not hide pre-existing failures. Clearly separate:
- failures caused by this task;
- failures that existed before this task.

### 9. Output report

Codex must return:

- repository audit summary;
- files changed;
- architecture decisions;
- screenshots or local render evidence;
- test/build results;
- unresolved issues;
- exact git diff summary;
- confirmation that no contract/liquidity/production wallet action occurred.
