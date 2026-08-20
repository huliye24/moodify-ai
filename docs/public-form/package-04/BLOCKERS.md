# Package 04 Blockers

**Date:** 2026-08-19
**Package:** 04 - Web Player Migration

---

## BLOCKER 1: EXTERNAL_DEPLOYMENT — DNS/Cloudflare Route

`play.rongjingmusic.com` does not yet exist as a routable origin.

**Required action:**
1. Add DNS record for `play` subdomain on `rongjingmusic.com`
2. Configure Cloudflare Tunnel / Worker route to point to existing Player deployment
3. Provision TLS certificate (automatic via Cloudflare if DNS is correct)

**Who can resolve:** Cloudflare account owner / DevOps
**Impact:** Blocks Phases B-F of migration
**Risk:** HIGH — entire domain migration depends on this

---

## BLOCKER 2: CORS_CONFIGURATION_UPDATE

New origin `https://play.rongjingmusic.com` must be added to CORS allowlist for:
- API endpoints (`/api/v1/*`)
- Audio streaming (`/api/v1/tracks/[id]/audio`)
- Any other cross-origin resource

**Current state:** CORS config likely in `vite.config.ts` or Worker entry. Not verified without build environment.

**Who can resolve:** Developer with repo access + Cloudflare dashboard
**Impact:** Audio streaming and API calls will fail on new origin
**Risk:** HIGH — core functionality broken without this

---

## BLOCKER 3: OAUTH_CALLBACK_UPDATE

If ChatGPT OAuth (or any OAuth provider) is configured with a callback URL, the new origin must be registered.

**Current state:** `app/beta-login/page.tsx` and `app/chatgpt-auth.ts` exist but callback URL configuration is external.

**Who can resolve:** OAuth provider dashboard access (ChatGPT/Google/etc.)
**Impact:** Login flow breaks on new origin
**Risk:** MEDIUM — only affects authenticated users

---

## BLOCKER 4: SERVICE_WORKER_SCOPE

Current Service Worker (`public/sw.js`) is scoped to `rongjinwenchuan.xyz`. New origin needs independent SW registration.

**Required action:**
1. Update `public/manifest.webmanifest` `scope` and `start_url` for new origin
2. Verify SW cache versioning doesn't conflict between origins
3. Test offline behavior on new origin

**Who can resolve:** Developer with repo access
**Impact:** PWA install, offline mode, caching behavior
**Risk:** MEDIUM — degrades experience but doesn't break core playback

---

## BLOCKER 5: ANDROID_APP_HARD_CODED_URLS

Android app (`apps/android/`) may contain hard-coded references to `rongjinwenchuan.xyz`.

**Current state:** Not audited — separate codebase.
**Discovery needed:** Search Android source for `.xyz` references.

**Who can resolve:** Android developer
**Impact:** Deep links from app may break or point to old origin
**Risk:** LOW-MEDIUM — affects mobile app users only

---

## Non-Blockers (Recorded But Not Blocking Code Changes)

| Item | Status | Why Not Blocker |
|---|---|---|
| Analytics/traffic data unavailable | Info | Needed for redirect decisions, not for code changes |
| Production TLS certificate | Auto-resolves | Cloudflare auto-provisions when DNS is correct |
| Cookie domain scope | Deferred | Can test after origin exists; current session model may work |
| localStorage migration | Acceptable loss | Preferences will reset on new origin — expected behavior |
| PWA manifest update | Trivial | Quick change once origin confirmed |

---

## Resolution Path

```
Blocker 1 (DNS) ──┐
                  ├──> Phase B: Origin created ──> Resolve Blockers 2-4 simultaneously
Blocker 2 (CORS) ─┤                                  │
                  ├──> Phase C: Dual-run test ──> Validate ──> Phase D: Switch
Blocker 3 (OAuth)─┤
                  │
Blocker 4 (SW)   ──┘

Blocker 5 (Android) ──> Independent track, can parallelize
```

**Estimated unblocked timeline:** 2-4 hours once Blocker 1 is resolved (assuming single developer has all access)
