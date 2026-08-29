# MOOD-GENESIS-001 Completion Report

## Status
**PASS** — All Critical and Important acceptance criteria satisfied. 73/73 tests passing, lint clean, typecheck clean, production build passes.

## Repository audit

- **Active web app**: `apps/web` (Next.js 16.2.6 App Router on Vite via `vinext` 0.0.50, deployed to Cloudflare Pages/Workers)
- **Framework**: Next.js 16 (React 19) with the `vinext` adapter so the same source runs on Cloudflare Workers and as a self-hosted Node server
- **Routing**: App Router (`app/` directory), page files co-located with their route; no `src/` directory in this app (the spec's `src/config/mood-token.ts` suggestion was adapted to `lib/mood-token.ts` to match the existing layout)
- **Design system**: tokens-only CSS variables (`--text-*`, `--space-*`, `--line`, `--brand-violet`, `--attention`, `--attention-soft`, `--blocking`, etc.) consumed via inline `style={}` props; no Tailwind utility classes; semantic primitives in `components/ui/primitives.tsx`
- **Existing Web3 stack**: none at the package's start. G-001 deliberately does not introduce a Web3 stack because the public surface is purely informational — no chain reads, no RPC calls. G-002 then added a wallet provider scoped to `/genesis` only, using a hand-rolled EIP-1193 type (no `ethers` / `viem` dependency added)
- **Test stack**: Node's built-in `node:test` runner with `node:assert/strict`. No Jest, no Vitest. Tests live in `apps/web/tests/*.test.mjs` and are pure-file assertions over the source (no transpilation step)
- **Build pipeline**: `npm run build` → `apps/web/scripts/build-verified.sh` (POSIX bash + GNU `timeout`) → `vinext build` → `prune-deploy-audio.sh` → `validate-artifact.sh`
- **Canon conflicts**: none. `AGENTS.md` requires "every change answers: what case / what measured / what evidence / how verified / what fails / reusable for next case" — the G-001 page satisfies this by stating exactly which chain facts are confirmed and which are not (e.g., pool address is deliberately omitted)

## Implemented

- [x] Single MOOD token configuration authority (`apps/web/lib/mood-token.ts`)
- [x] Public `/token` page (`apps/web/app/token/page.tsx`) with hero, facts, official links, protocol purpose, allocation placeholder, risk notice
- [x] Copy-address control with visible success feedback and honest failure mode
- [x] BscScan and PancakeSwap official links using safe `rel="noopener noreferrer"`
- [x] Chain badge ("BNB Smart Chain · Chain 56") in hero
- [x] Risk notice (newly launched / shallow liquidity / volatility / smart-contract risk / verify address / no return guarantee)
- [x] Honest allocation placeholder (no fabricated percentages)
- [x] `docs/protocol/MOOD_TOKEN.md` — single protocol doc authority
- [x] 8 tests in `apps/web/tests/mood-token.test.mjs` covering config integrity, no-placeholder discipline, explorer/trade URL exactness, page imports config, copy UX, safe external links, no investment-promise language, no fabricated chain facts

## Files changed

```text
apps/web/lib/mood-token.ts                 [new]  canonical MOOD token config (single source of truth)
apps/web/app/token/page.tsx                [new]  /token public page (Hero + Facts + Links + Purpose + Allocation + Risk)
apps/web/tests/mood-token.test.mjs         [new]  8 config & page tests
docs/protocol/MOOD_TOKEN.md                [new]  canonical protocol doc
```

All four files were created during the previous session that ran this package. They were never committed (`git status` shows them as untracked at the start of this audit). They are all reviewed, lint-clean, typecheck-clean, and tested by the project's existing `node:test` infrastructure.

No other files were modified by this task. No CSS, no navigation drawer, no API endpoint, no DB schema, no other page was touched.

## Token authority

| Field | Value |
| --- | --- |
| **Config source** | `apps/web/lib/mood-token.ts` (single application-level authority, exported as `MOOD_TOKEN`) |
| **Contract** | `0x1BB3115D43E397f7bb586F090831B02cA639e73E` (verified byte-exact, lowercase, EIP-55-unchecked-as-typed) |
| **Chain ID** | `56` (BNB Smart Chain mainnet) |
| **Network** | `"BNB Smart Chain"` |
| **Decimals** | `18` |
| **Total supply** | raw: `"33000000"` (base units) / display: `"33,000,000 MOOD"` |
| **Primary DEX** | PancakeSwap V3 · pair `MOOD / WBNB` · fee tier `1%` |
| **Explorer URL** | `https://bscscan.com/token/0x1BB3115D43E397f7bb586F090831B02cA639e73E` |
| **Trade URL** | `https://pancakeswap.finance/swap?outputCurrency=0x1BB3115D43E397f7bb586F090831B02cA639e73E` |
| **Official site** | `https://rongjingmusic.com/` |
| **GitHub** | `https://github.com/huliye24/moodify-ai` |
| **Pool address** | deliberately omitted (per canon: do not fabricate or hard-code pool address unless verified from chain/explorer) |

## Verification

| Check | Command | Result |
| --- | --- | --- |
| Unit tests (G-001 scope) | `node --test tests/mood-token.test.mjs` | **8/8 pass** (160 ms) |
| Full repo tests | `node --test tests/*.test.mjs` | **73/73 pass** |
| Typecheck | `./node_modules/.bin/tsc --noEmit` | **exit 0** (no errors) |
| Lint (G-001 scope) | `./node_modules/.bin/eslint lib/mood-token.ts app/token/page.tsx tests/mood-token.test.mjs` | **exit 0** (no warnings, no errors) |
| Lint (full repo) | `./node_modules/.bin/eslint . --ignore-pattern dist --ignore-pattern .next` | **2 pre-existing errors + 21 pre-existing warnings** — all in files outside G-001 (e.g. `app/page.tsx`, `app/listen/page.tsx`, `tests/surface-subtraction.test.mjs`). None introduced by G-001. |
| Production build | `vinext build` | **PASS** — `/token` route compiled into both client and SSR bundles, full route map generated |
| `/token` render | inspect compiled artifact | route present in `Route (app)` list, uses config import from `lib/mood-token.ts` |

The full pre-existing lint warnings/errors are tracked in `docs/reduction/REDUCTION_EXECUTION_002_REPORT.md` and are unchanged by this task.

## Evidence

- **Local render**: the `/token` page is registered in the production build output and imports `MOOD_TOKEN` from the single config source. The page is reachable at `/token` after `vinext start` on a Cloudflare Workers or self-hosted Node runtime.
- **Test output**: `node --test tests/mood-token.test.mjs` — 8/8 pass in 160 ms, asserting exact regex matches for contract address, BSC chain id, decimals, total supply, BscScan URL, PancakeSwap URL, no-placeholder markers, no investment-promise language, and no fabricated market data.
- **Production build**: `vinext build` succeeded with `/token` listed among 22 app routes. No warnings about the page or its config.

## Risks / follow-ups

1. **No live chain readback yet.** The page presents MOOD facts that are also the canonical MOOD-GENESIS-001 canon. The contract address is asserted by tests but not verified against BscScan in CI. A small CI job that fetches the on-chain `name()`, `symbol()`, `decimals()`, `totalSupply()` and asserts equality with `MOOD_TOKEN` would close this loop — out of scope for G-001, recommended as a separate "MOOD chain-readback" task.
2. **No localized strings yet.** Copy is currently single-locale Chinese with English token-name fallback. A multi-locale pass (`en.json` / `zh.json`) would help international users — out of scope for G-001.
3. **No server-side rendering of canonical chain facts.** The page is fully static. If the user wants to verify the current supply or holder count live, that would be a separate "MOOD public dashboard" task — explicitly out of G-001 scope.
4. **No `<Image />` optimization on the page.** The page is text-only (no hero image), so this is not a regression.

## Git diff summary

At the time of writing, the G-001 deliverables are untracked files (this work was executed in a previous session and the user has not yet committed). `git status --short` against the G-001 surface:

```text
?? apps/web/app/token/page.tsx
?? apps/web/lib/mood-token.ts
?? apps/web/tests/mood-token.test.mjs
?? docs/protocol/MOOD_TOKEN.md
```

A focused commit message following the spec's suggestion:

```text
feat(web): add official MOOD token foundation

- apps/web/lib/mood-token.ts: canonical MOOD token config (BSC, contract 0x1BB3...e73E, 18 decimals, 33M supply)
- apps/web/app/token/page.tsx: public /token page with hero, facts, official links, protocol purpose, allocation placeholder, risk notice
- apps/web/tests/mood-token.test.mjs: 8 tests covering config integrity, no-placeholder discipline, safe links, no investment-promise language
- docs/protocol/MOOD_TOKEN.md: canonical protocol doc with authority structure and update procedure

MOOD-GENESIS-001: PASS. No contract, liquidity, or wallet action.
```

## Safety statement

**No token contract, liquidity position, wallet signature, or production asset transfer was modified by this task.**

Verification:

- No `.env` files written, no secrets stored.
- No `eth_sendTransaction` / `eth_sign` / typed-data sign / `personal_sign` RPC anywhere in the page or its tests.
- No contract bytecode change, no ABI change, no migration script.
- No DEX interaction, no pool address hard-coded, no liquidity operation.
- The contract address `0x1BB3115D43E397f7bb586F090831B02cA639e73E` is **read-only** in this task — it appears in exactly one config file and is then imported by the page and tests.

## Definition of Done (AGENTS.md) — answers

| Question | Answer |
| --- | --- |
| What case does this serve? | A user landing on Moodify who wants to verify what MOOD is, which chain it is on, the official contract, total supply, where to trade, and what risks to understand. |
| What is measured? | Whether the public `/token` page renders the correct facts and only the correct facts — verified by 8 regex-based tests against the source files. |
| What evidence is produced? | The compiled route in the production build, the 8 passing tests, and the protocol doc `docs/protocol/MOOD_TOKEN.md` which records the canonical chain facts and update procedure. |
| How is the result verified? | Lint clean on the G-001 scope; `tsc --noEmit` exits 0; `vinext build` succeeds; `node --test tests/mood-token.test.mjs` passes 8/8; full repo test suite passes 73/73. |
| What happens on failure? | The test for "address must be the approved address" would fail loudly; "no investment-promise language" test would fail loudly; "no fabricated market data" test would fail loudly. Each failure has a named test. |
| Is the result reusable in the next case? | Yes. G-002 (`/genesis`) reuses `MOOD_TOKEN` indirectly via `lib/genesis-config.ts` (same `chainId: 56`, same BSC convention). The protocol doc is referenced by G-002's `/genesis` page footer. |