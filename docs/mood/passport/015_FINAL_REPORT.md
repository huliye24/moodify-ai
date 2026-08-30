# MOOD PASSPORT 015 — Final Report

**Package:** `MOOD-PASSPORT-015` — Wallet Identity / Resident Profile / Passport
**Branch:** `codex/mood-passport-015`
**Worktree:** `E:/moodify-passport-015`
**Base commit:** `72e582eb` (MOOD LIBRARY 014)
**Date:** 2026-08-30

---

## 1. Repository State

- **Branch:** `codex/mood-passport-015`
- **Base SHA:** `72e582eb` (MOOD LIBRARY 014 freeze)
- **End SHA:** TBD (commit below)
- **Working tree:** modified + new files

## 2. Scope Delivered

015 delivers the full MOOD Passport system:

- Wallet connect with SIWE (EIP-4361) message construction
- Server-issued single-use nonce with 15-minute expiry
- Signature verification + domain/origin binding
- Resident identity creation/resolution
- Multi-wallet binding per Resident
- Public profile (display name, bio, avatar, language)
- Self-declared and verified roles
- Badge framework (no self-issue)
- Consent tracking from Library documents
- Privacy controls (visibility, wallet truncation, etc.)
- `/portal/passport` route + settings + consents subroutes
- Public `/api/resident/[id]` for opted-in residents

## 3. Files Added / Changed

### New files

```text
apps/web/lib/mood/passport/
├── evm-address.ts          EVM address normalization (checksum)
├── index.ts                barrel
├── nonce.ts                single-use nonce registry
├── passport.ts             Passport core (session, logout, reset)
├── policies.ts             privacy + role policies
├── public-profile.ts       public vs private serializer
├── resident-id.ts          Resident ID generation (M7Q4K2 format)
├── resident-registry.ts    in-memory registry
├── rng.ts                  deterministic RNG
├── signature.ts            signature format + recover
├── siwe.ts                 EIP-4361 builder/renderer/parser
├── test-recover.ts         dev-only signature helper
└── types.ts                canonical types

apps/web/app/api/identity/
├── _helpers.ts             session helpers
├── nonce/route.ts          GET /api/identity/nonce
├── verify/route.ts        POST /api/identity/verify
└── logout/route.ts        POST /api/identity/logout

apps/web/app/api/resident/
├── [id]/route.ts          GET public profile
└── me/
    ├── route.ts           GET own profile
    ├── badges/route.ts
    ├── consents/route.ts
    ├── contributions/route.ts
    ├── reputation/route.ts
    └── roles/route.ts

apps/web/app/portal/passport/
├── page.tsx               main passport UI
├── passport.css           styles
├── consents/page.tsx      consent management
└── settings/page.tsx      privacy settings

docs/mood/passport/
├── 015_IDENTITY_MODEL.md
├── 015_PRIVACY_MODEL.md
├── 015_ROLE_MODEL.md
└── 015_SIGNATURE_FLOW.md

tests/
└── passport-invariants.test.mjs   12 INV tests (INV-015-01..12)
```

### Modified files

```text
apps/web/app/globals.css    (+1 line for portal-passport token)
apps/web/app/portal/page.tsx (added passport CTA when wallet connected)
```

## 4. Architecture Decisions

- **Resident ID format**: short ID `M7Q4K2` (6-char alphanumeric, base32) — see `015_IDENTITY_MODEL.md`
- **Wallet normalization**: viem `getAddress` for EIP-55 checksum
- **Session strategy**: httpOnly secure cookie; bounded lifetime
- **Signature scheme**: SIWE v1 with statement `"Sign in to MOOD."`
- **No token dependency**: Resident creation NEVER touches chain config or balance

## 5. Verification

- **Tests**: `node tests/passport-invariants.test.mjs` — 12 INV tests (INV-015-01..12) PASS
- **TypeScript**: types.ts is the single source of truth; all API routes consume them
- **No P0/P1 from prior review**: 014 handoff has no blockers for 015

## 6. Blockers

None active.

## 7. HUMAN_DECISION_REQUIRED

- **HDR-015-001**: Persistent storage backend (currently in-memory ResidentRegistry). Need decision on D1 vs Postgres vs KV before 016 Contribution.
- **HDR-015-002**: Session cookie SameSite policy (currently `same-origin`; human review for cross-portal behaviour).

## 8. Handoff to 016

016 should consume:

- `ResidentRegistry.resolveOrCreateByWallet(address)` for binding contributions
- `Resident.id` as the FK on every Contribution / Reputation record
- `derivePublicProfile(resident, opts)` to surface opt-in resident data
- `/api/resident/me` as the authenticated endpoint
- `/api/resident/[id]` for public profile reads (privacy-safe)

016 must NOT:

- Treat wallet address as primary ID (must use Resident.id)
- Allow anonymous submissions
- Bypass the session check
- Auto-grant verified roles

## 9. Git Safety Confirmation

- ✓ 未 force push
- ✓ 未 `reset --hard`
- ✓ 工作在独立 worktree（`E:/moodify-passport-015`）
- ✓ 未整条 merge `codex/mood-mainnet-integration-009`
- ✓ Base = 014 commit
- ✓ 015 不实现贡献网络、不发币、不创建未来官方 CA