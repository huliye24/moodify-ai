# MOOD PASSPORT 015 — Privacy Model

**Package:** `MOOD-PASSPORT-015`
**Authority surface:** `apps/web/lib/mood/passport/{public-profile,types}.ts` + `apps/web/app/portal/passport/settings/page.tsx`

---

## 1. Posture

> **Privacy by default. Minimal collection. No KYC.**

Passport collects the minimum needed to render a Resident identity:
one wallet address (user-provided) plus optional display fields.

## 2. Collected vs Never Collected

| Collected (optional) | Never collected |
|---|---|
| wallet address (required, cryptographic proof) | real name |
| display name (≤ 32 chars, optional) | email |
| short bio (≤ 280 chars, optional) | phone number |
| avatar URL (≤ 256 chars, optional) | birthday |
| preferred language (`zh` / `en`) | geolocation / IP-based profiling |
| self-declared role interests | government IDs / KYC documents |

Future compliance-driven data collection must open its **own package**
(it must not be smuggled into 015).

## 3. Defaults

| Setting | Default |
|---|---|
| `profileVisibility` | `minimal` |
| `showFullWalletAddress` | `false` (truncated `0xABCD…1234`) |
| `showContributionHistory` | `true` (renders nothing until 016 exists) |
| `showRoles` | `true` |
| `showReputation` | `true` (renders "No contributions yet") |

## 4. Public / Private Field Split

**Public (only when the Resident opts in, and only via the derived
`PublicResidentProfile`):**

- resident short ID (e.g. `M7Q4K2`)
- display name (or null)
- roles (self-declared + verified), badges
- joined **month** (e.g. "Aug 2026" — not the exact date)
- reputation summary + contribution count (subject to toggles)

**Never public (private by default, no toggle):**

- full wallet address (truncated everywhere unless explicitly enabled)
- session records / cookies
- consent records (slug / version / timestamps)
- internal wallet / DB UUIDs
- admin flags, suspension status details
- exact join timestamp (month granularity only)

`derivePublicProfile()` is the **only** code path that builds a public view;
`profileVisibility: "private"` returns `null` outright. Verified by
INV-015-08: the serialized public profile contains no wallet address, no
wallet objects, no consent or session records.

## 5. Public Passport Route

`GET /api/resident/[id]` (and a future `/resident/[id]` page) is:

- **disabled by default**: unless `MOOD_PASSPORT_PUBLIC_PROFILE=1`, the route
  404s (privacy hard-OFF in foundation state, TASK Phase N)
- even when enabled, only residents with `profileVisibility: "public"` are
  served; `minimal`/`private` → 403/404
- responses come exclusively from `derivePublicProfile()`

## 6. Resident Controls (`/portal/passport/settings`)

- profile visibility: public / minimal / private
- show full wallet address: on/off
- show contribution history: on/off
- show roles: on/off
- show reputation: on/off
- disconnect wallet (revokes all sessions)
- revoke session (sign out)
- soft-delete request path documented; v1 implements status field, actual
  deletion workflow deferred to governance (see THREAT_REVIEW §retention)

## 7. Anti-Enumeration

- short random Resident IDs (no sequential numbering)
- public route disabled by default
- lookup failures return uniform 404s (no distinction between "private
  resident" and "nonexistent resident" at the API surface where feasible)
