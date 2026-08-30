# MOOD PASSPORT 015 — Signature Flow (SIWE / EIP-4361)

**Package:** `MOOD-PASSPORT-015`
**Authority surface:** `apps/web/lib/mood/passport/{siwe,signature,nonce,passport}.ts` + `apps/web/app/api/identity/*`

---

## 1. Standard Choice

MOOD Passport adopts **SIWE (EIP-4361)** message format, signed via
`personal_sign` (EIP-191). Rationale:

- human-readable → prevents blind-signing / phishing-style messages
- contains domain, URI, chain ID, nonce, issued-at, expiration → full replay
  protection surface
- industry standard, wallet-native rendering

Deviations from strict EIP-4361 in v1 (documented, acceptable):

- addresses are compared in **normalized lowercase** (no keccak256 EIP-55
  checksum in the dep-free foundation build — see §6)
- signature recovery is **pluggable** (`RecoverAddressFn`), fail-closed

## 2. Flow

```text
Connect Wallet
  ↓
GET  /api/identity/nonce?address=0x…
  ↓  issues single-use nonce (bound to address, 15 min TTL)
Build human-readable SIWE message (server-side)
  ↓
Wallet signs message (personal_sign)
  ↓
POST /api/identity/verify { messageText, signature }
  ↓
Server:
  1. same-origin check (Origin header must match host)
  2. re-parse message text (strict SIWE parser)
  3. domain / URI / chain-ID binding check — fail closed on mismatch
  4. signature format check (65 bytes, v ∈ {0,1,27,28})
  5. recover signer address — fail closed if impossible
  6. recovered address MUST equal message address AND claimed address
  7. consume nonce (single-use, address-bound, expiry-checked)
  8. resolve or create Resident
  9. issue bounded session (1 h TTL)
  ↓
Set-Cookie: mood_session (HttpOnly, SameSite=Lax, Secure-when-HTTPS)
```

## 3. Signed Message Contents

Every message contains, at minimum:

| Field | Purpose |
|---|---|
| Domain | binds the message to this site (anti-phishing) |
| Statement | fixed: "Sign in to MOOD." — never token/DEX/claim language |
| Wallet Address | the key being proven |
| Nonce | single-use, server-issued |
| Issued At / Expiration Time | stale-signature rejection (15 min window) |
| Chain ID | 56 (BSC) — informational, never a Token gate |
| URI | canonical origin of the Passport route |
| Request ID | opaque correlation ID |

## 4. Replay / Abuse Protection (TASK Phase F)

| Requirement | Enforcement | Test |
|---|---|---|
| nonce single-use | `NonceRegistry.consume` marks used; second use → `already-used` | INV-015-02 |
| nonce expiry | 15 min TTL, `now > expiresAt` → `expired` | INV-015-03 |
| address-bound nonce | nonce record carries the bound normalized address | INV-015-02/05 |
| domain/origin binding | message must start with `<host> wants you to sign in`; request Origin must match host | INV-015-12 |
| URI / chain binding | `URI:` and `Chain ID:` lines must match server expectations | INV-015-12 |
| verification fail closed | no recoverer / bad shape / wrong recovered address → 401, never a partial success | INV-015-04 |
| stale signature rejection | expiration window in message + nonce TTL | INV-015-03 |
| replay rejection | nonce consumed exactly once; replay → `nonce-already-used` | INV-015-12 (step 5) |
| session expiry | sessions carry `expiresAt`; expired lookups return null | INV-015-06 |
| CSRF / same-site | session cookie is `HttpOnly; SameSite=Lax`; verify route rejects cross-origin Origin | INV-015-12 |

Forbidden states (absent by construction): permanent nonces, reusable
signatures, arbitrary-message acceptance, front-end-only verification.

Rate limiting: v1 relies on same-origin checks + nonce issuance caps
(`maxEntries` 10k with sweep). A dedicated rate limiter is deferred to the
integration/022 package — flagged in THREAT_REVIEW §rate-limiting.

## 5. Session

- opaque UUID session ID in an HttpOnly cookie
- 1 hour TTL, `lastActiveAt` tracked
- logout (`POST /api/identity/logout`) revokes the session and clears the cookie
- `revokeAllSessions(residentId)` supports disconnect-wallet / soft-delete

## 6. Signature Recovery — Foundation Compromise (honest disclosure)

Real recovery requires keccak256 + secp256k1. 015 deliberately does **not**
couple the passport path to `viem` (012 froze `mood-chain.ts` /
`mood-token.ts`; the foundation launch gate requires Passport to work with
zero token/chain dependencies). Therefore:

- `Passport` accepts an injected `RecoverAddressFn`.
- Production default: `FAIL_CLOSED_RECOVER` → always null → 401.
  **Until an integration package wires a real recoverer, wallet sign-in
  cannot complete in production. This is intentional fail-closed, not a bug.**
- Development (`MOOD_PASSPORT_DEV_MODE=1`): `FAKE_RECOVER_FOR_TEST`
  consults a registered (messageText, signature) → address table.
  It can never forge an address that wasn't registered.

Filling the real recoverer is a **015 → integration handoff item** (see
015_FINAL_REPORT §Blockers-constraints).

## 7. API Surface

| Route | Method | Auth | Purpose |
|---|---|---|---|
| `/api/identity/nonce` | GET | none (address query param) | issue nonce + SIWE message |
| `/api/identity/verify` | POST | none (signature is the proof) | complete sign-in, set session cookie |
| `/api/identity/logout` | POST | session | revoke session, clear cookie |
