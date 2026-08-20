# Player Origin Inventory

**Date:** 2026-08-19
**Package:** 04 - Web Player Migration
**Source:** `E:\moodify\apps\music-web\`

---

## 1. Origin Identity

| Field | Value |
|---|---|
| **Current origin** | `https://rongjinwenchuan.xyz/` |
| **Target origin** | `https://play.rongjingmusic.com/` (planned) |
| **Source directory** | `E:\moodify\apps\music-web\` |
| **Framework** | Next.js 16 (App Router) + React 19 + TypeScript |
| **Build tool** | Vite 8 + Vinext (Cloudflare adapter) |
| **Deploy target** | Cloudflare Workers (D1 + R2) |
| **Package name** | `moodify-music` |

---

## 2. Source Files Inventory

### 2.1 Entry Points

| File | Role |
|---|---|
| `app/page.tsx` | Main player page (179 lines) — sidebar + content + player bar |
| `app/layout.tsx` | Root layout — metadata, theme-color, manifest, SwRegister |
| `app/globals.css` | Global styles (~16KB) |

### 2.2 Routes (15+ pages)

| Route | File | Purpose |
|---|---|---|
| `/` | `app/page.tsx` | Main player / discover |
| `/library` | `app/library/page.tsx` | My library / favorites |
| `/playlists` | `app/playlists/page.tsx` | Playlists |
| `/studio` | `app/studio/page.tsx` | Creator center (upload) |
| `/drafts` | `app/drafts/page.tsx` | Draft management |
| `/console` | `app/console/page.tsx` | Admin console |
| `/inbox` | `app/inbox/page.tsx` | Authorization inbox |
| `/offline` | `app/offline/page.tsx` | Offline mode |
| `/design` | `app/design/page.tsx` | Design system showcase |
| `/beta-login` | `app/beta-login/page.tsx` | Beta login |
| `/track/[id]` | `app/track/[id]/page.tsx` | Track detail (redirect to /t/[id]) |
| `/t/[id]` | `app/t/[id]/page.tsx` | Track play page |
| `/c/[handle]` | `app/c/[handle]/page.tsx` | Creator profile |

### 2.3 API Routes

| Route | File | Purpose |
|---|---|---|
| `GET /api/v1/tracks` | `app/api/v1/tracks/route.ts` | Track listing |
| `GET/PUT /api/v1/tracks/[id]` | `app/api/v1/tracks/[id]/route.ts` | Single track CRUD |
| `GET /api/v1/tracks/[id]/audio` | `app/api/v1/tracks/[id]/audio/route.ts` | Audio stream proxy (R2) |
| `POST /api/v1/tracks/[id]/publish` | `app/api/v1/tracks/[id]/publish/route.ts` | Publish track |
| `GET /api/v1/creators/[handle]` | `app/api/v1/creators/[handle]/route.ts` | Creator profile API |
| `GET /api/v1/me/creator` | `app/api/v1/me/creator/route.ts` | Current user creator info |

### 2.4 Shared Components

| File | Exports |
|---|---|
| `components/ui/surfaces.tsx` | BrandMark, ProductSwitcher, NavLink, PageShell |
| `components/ui/audio.tsx` | AudioTransport (reusable player controls) |
| `components/ui/primitives.tsx` | Buttons, inputs, base primitives |
| `components/ui/data.tsx` | Lists, tables, data display |
| `components/ui/states.tsx` | Loading, error states |
| `components/ui/status.tsx` | Badges, tags, indicators |

### 2.5 Core Libraries

| File | Role |
|---|---|
| `lib/music-client.ts` | REST API client (231 lines) — bootstrap, catalogue, search, library, playlists, lifecycle, console |
| `lib/api.ts` | Server-side API helpers |
| `lib/cloudflare-workers-self-hosted.ts` | Self-hosted adapter |
| `lib/ownership.ts` | Permission verification |

### 2.6 Infrastructure

| File | Role |
|---|---|
| `worker/index.ts` | Cloudflare Worker entry point |
| `db/schema.ts` | Drizzle ORM schema (D1) |
| `db/index.ts` | D1 connection |
| `vite.config.ts` | Vite + Cloudflare Workers binding config |
| `next.config.ts` | Next.js config (empty/default) |
| `public/sw.js` | Service Worker (2815 bytes) |
| `public/manifest.webmanifest` | PWA manifest |

---

## 3. Hard-coded Origin References

| File | Line | Context | Value |
|---|---|---|---|
| `app/page.tsx` | 17 | Audio base URL fallback | `https://rongjinwenchuan.xyz/audio` |
| `app/library/page.tsx` | 51 | Audio base URL fallback | `https://rongjinwenchuan.xyz/audio` |
| `app/t/[id]/page.tsx` | 6 | Audio base URL fallback | `https://rongjinwenchuan.xyz/audio` |
| `app/c/[handle]/page.tsx` | 7 | Audio base URL fallback | `https://rongjinwenchuan.xyz/audio` |
| `assets/cadeau10-album1.json` | 5 | Album asset manifest | `https://rongjinwenchuan.xyz/audio` |
| `README.md` | 6, 13 | Documentation reference | `https://rongjinwenchuan.xyz` |

**Total: 6 files with hard-coded `.xyz` origin**

All use pattern: `process.env.NEXT_PUBLIC_AUDIO_BASE_URL ?? "https://rongjinwenchuan.xyz/audio"`

---

## 4. Navigation & Surface Elements

### Current Sidebar (`app/page.tsx` lines 144-153)

```
Brand: Moodify (logo + wordmark)
Nav:
  ◉ 发现音乐 (active)
  ⌕ 搜索 input
  ▥ 我的音乐 (conditional: account_actions)
Creator section (conditional: creator_writes):
  你的音乐
  ＋ 创作者中心 -> /studio
Profile: avatar + role label
```

### Current Mobile Header (`app/page.tsx` line 156)

```
[Moodify logo] Moodify   [‹][›]   [上传作品] (conditional)
```

### Current Footer

No dedicated footer component. Page ends at player bar.

---

## 5. P0 Surface Elements (per Package 04 spec)

| Element | Current State | Target State |
|---|---|---|
| Play/Pause | ✅ Available (hero + player bar) | Keep |
| Track metadata | ✅ Title + artist displayed | Keep |
| Progress bar | ✅ Seekable range input | Keep |
| Previous/Next | ✅ Button controls | Keep |
| Loading state | ⚠️ Implicit (no spinner) | Add visible indicator |
| Error state | ✅ `player-error` div | Keep |
| Product Home return | ❌ Missing | **Add** |
| Creator Center visibility | Visible in sidebar + header | **Hide from first surface** |
| Upload visibility | Visible in header | **Hide from first surface** |
| Discover feed | Full track list in content area | Deprioritize (keep but not primary) |

---

## 6. Auth / Session

| Item | Status | Notes |
|---|---|---|
| Auth mechanism | ChatGPT OAuth + Invite Beta | Via `app/beta-login/page.tsx` and `app/chatgpt-auth.ts` |
| Cookie details | UNVERIFIED | Server-side session via Cloudflare |
| localStorage usage | Likely (preferences, volume) | Not explicitly audited |
| CORS config | In `vite.config.ts` via worker bindings | Dev mode vs prod may differ |
| Service Worker | `public/sw.js` registered via `sw-register.tsx` | Caches HTML/JS/audio |
| OAuth callback | Configured for current origin | Will need update for new origin |

---

## 7. Media Pipeline

| Item | Value |
|---|---|
| Audio storage | Cloudflare R2 |
| Audio proxy | `GET /api/v1/tracks/[id]/audio` -> R2 get object |
| Range requests | Supported via R2 streaming |
| Fallback audio | Hardcoded album tracks from `assets/cadeau10-album1.json` |
| Audio base URL | Env-var overrideable, defaults to `.xyz` |

---

## 8. External Dependencies

| Dependency | Type | Notes |
|---|---|---|
| Cloudflare Workers | Platform | D1 database + R2 storage + edge compute |
| Cloudflare Tunnel | Network | Reverse proxy (config external to repo) |
| R2 bucket | Storage | Audio assets |
| D1 database | SQL | Tracks, creators, users, playlists |
| Android app | Client | May hard-code Web Player URL (UNVERIFIED) |

---

## 9. SEO / OG / Metadata

| Field | Current Value |
|---|---|
| `<title>` | "Moodify Music" |
| `<meta description>` | "听见此刻与你更接近的音乐。" |
| `og:title` | Not explicitly set (inherits title) |
| `og:description` | Not explicitly set |
| canonical | Not set |
| `theme-color` | `#05081e` |
| manifest name | "Moodify Music" |
| lang | `zh-CN` |

---

## 10. Build & Test

| Command | Status |
|---|---|
| `npm run dev` | Vite dev server |
| `npm run build` | `bash scripts/build-verified.sh` |
| `npm run test` | `npm run build && node --test tests/*.test.mjs` |
| `npm run db:generate` | `drizzle-kit generate` |

---

## 11. UNVERIFIED Items

| Item | Why Unverified | Impact |
|---|---|---|
| DNS / Cloudflare route config | External to repo | High — blocks origin creation |
| nginx / tunnel configuration | External to repo | High — blocks origin creation |
| Real production traffic | No analytics access | Medium — affects legacy route decisions |
| Android app hard-coded URLs | Separate repo (`apps/android`) | Medium — affects deep links |
| External dependencies on `.xyz` | Unknown | High — affects redirect timing |
| Cookie domain scope | Server-side config | High — affects auth migration |
| Production TLS certificate | External | Must be valid for new origin |

---

## 12. Rollback Plan

1. Restore `NEXT_PUBLIC_AUDIO_BASE_URL` to old value (or remove)
2. Revert navigation changes
3. Restore Product Home link target
4. Disable DNS route for `play.rongjingmusic.com`
5. Keep old `.xyz` release intact (never delete during migration)
6. Git revert commit if code changes are atomic
