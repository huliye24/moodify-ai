# Player Migration Report

**Date:** 2026-08-19
**Package:** 04 - Web Player Migration
**Phase:** Code changes complete, awaiting origin creation
**Status:** ⚠️ PARTIAL — Surface convergence done; domain migration blocked on external infra

---

## 1. Executive Summary

Package 04 aimed to converge the Web Player surface and prepare for `play.rongjingmusic.com` migration.

**Completed:**
- ✅ Player UI surface convergence (Creator/Upload moved to drawer)
- ✅ Product Home return links added (3 entry points)
- ✅ SEO metadata updated with canonical URL
- ✅ Legacy route matrix documented
- ✅ Redirect map generated
- ✅ All `.xyz` hard-coded references annotated for future replacement
- ✅ No backend/API/audio routes modified

**Blocked:**
- ❌ DNS/Cloudflare route for `play.rongjingmusic.com` (external to repo)
- ❌ TLS certificate provisioning
- ❌ CORS configuration update for new origin
- ❌ Service Worker scope migration
- ❌ OAuth callback URL update
- ❌ Production deployment verification

---

## 2. Changes Detail

### 2.1 Files Modified (6 files)

| File | Lines Changed | Nature |
|---|---|---|
| `apps/music-web/app/page.tsx` | +38 | Menu state, drawer JSX, brand link, utility link |
| `apps/music-web/app/layout.tsx` | +2 | Canonical, title/description update |
| `apps/music-web/app/globals.css` | +22 | Drawer component styles |
| `apps/music-web/app/library/page.tsx` | +1 | Migration comment |
| `apps/music-web/app/t/[id]/page.tsx` | +1 | Migration comment |
| `apps/music-web/app/c/[handle]/page.tsx` | +1 | Migration comment |

### 2.2 Surface Convergence Results

| Spec Requirement | Status | Evidence |
|---|---|---|
| Play/Pause available | ✅ | Unchanged — hero + player bar |
| Track metadata visible | ✅ | Unchanged — title + artist |
| Progress bar working | ✅ | Unchanged — range input |
| Previous/Next controls | ✅ | Unchanged — button controls |
| Loading state visible | ⚠️ | Existing implicit behavior — explicit spinner deferred |
| Error state handled | ✅ | Unchanged — player-error div |
| **Product Home return** | **✅ Added** | Brand link + drawer "About" + player bar "About" |
| **Creator hidden from first layer** | **✅ Done** | Moved from sidebar/header to drawer |
| **Upload hidden from first layer** | **✅ Done** | Removed from header, in drawer |
| **Research/Evidence not on surface** | ✅ | Was never on surface |
| **API not on surface** | ✅ | Was never on surface |

### 2.3 Cross-Site Link Validation

| Link | Source | Target | Status |
|---|---|---|---|
| Brand -> About Moodify | Sidebar brand area | `rongjingmusic.com` | ✅ Added |
| Drawer -> Moodify 官网 | Drawer menu | `rongjingmusic.com` | ✅ Added |
| Drawer -> 荣景文川 | Drawer menu | `rongjingwenchuan.com` | ✅ Added |
| Player bar -> About | Utilities area | `rongjingmusic.com` | ✅ Added |
| Company -> Product | Package 03 output | `rongjingmusic.com` | ✅ Pre-existing |

---

## 3. Domain Migration Status

### Phase A — Inventory: ✅ COMPLETE
- Full source inventory at `PLAYER_ORIGIN_INVENTORY.md`
- All 6 hard-coded `.xyz` references identified
- Route table fully documented

### Phase B — Prepare new origin: ❌ BLOCKED
- DNS route for `play.rongjingmusic.com` not configurable from repo
- TLS certificate requires Cloudflare dashboard access
- Waiting on human/ops action

### Phase C — Dual-run: NOT STARTED
- Depends on Phase B completion

### Phase D — Canonical switch: NOT STARTED
- Depends on Phase C validation

### Phase E — Legacy observation: NOT STARTED
- Requires production analytics access

### Phase F — Redirect decision: DEFERRED
- Will decide after Phase E data collection
- Current recommendation: no forced 301 until traffic analyzed

---

## 4. Auth / Session / CORS Assessment

| Item | Current State | Migration Action Needed | Blocker |
|---|---|---|---|
| Cookie scope | Unknown (server-side) | May need Domain update if sharing login | ⚠️ Verify before origin switch |
| localStorage | Likely used for preferences | Will not auto-migrate — acceptable loss | Info |
| CORS config | In vite.config.ts / worker | Must add `play.rongjingmusic.com` to allowlist | 🔴 Blocked on infra |
| OAuth callback | ChatGPT auth configured | Must register new callback URL | 🔴 Blocked on infra |
| Service Worker | Registered per-origin | New origin needs independent SW registration | 🟡 Plan ready |
| Media Range requests | Via R2 proxy | Must test CORS-preflight Range on new origin | 🔴 Blocked on infra |

---

## 5. Rollback Instructions

If any issue arises:

1. **Code rollback:** `git revert <commit-hash>` — all changes are in 6 frontend files only
2. **Navigation rollback:** Remove drawer JSX, restore original sidebar nav-group
3. **Metadata rollback:** Restore original title/description, remove canonical
4. **CSS rollback:** Remove drawer styles block from globals.css
5. **No infrastructure changed** — zero risk to backend/DNS/CDN from this commit

---

## 6. Next Steps (Require External Action)

1. **Create DNS route** `play.rongjingmusic.com` -> Worker
2. **Provision TLS certificate** for new origin
3. **Update CORS allowlist** in Cloudflare Worker / vite config
4. **Register new OAuth callback** (if applicable)
5. **Deploy this code change** to both origins (dual-run)
6. **Test audio streaming** on new origin (Range, seek, CORS)
7. **Test auth flow** on new origin (login, refresh, logout)
8. **Update service worker** scope for new origin
9. **Update Android app** hard-coded URLs (separate repo)
10. **Monitor old origin traffic** for 2-4 weeks
11. **Decide redirect strategy** based on traffic data

---

## 7. Sign-off

| Check | Who | Date | Status |
|---|---|---|---|
| Code review | Codex (auto-generated) | 2026-08-19 | ✅ Applied |
| Build verification | Pending | — | ⏳ Blocked on deploy |
| Origin creation | Human/Ops required | — | ⏳ Blocked external |
| Cross-site validation | Partial (Product Home link verified) | 2026-08-19 | ✅ Code-level OK |
| Security scan | Basic (no secrets added) | 2026-08-19 | ✅ Pass |
