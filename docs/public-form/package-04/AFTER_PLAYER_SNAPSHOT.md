# After Player Snapshot

**Date:** 2026-08-19
**Package:** 04 - Web Player Migration
**Status:** Code changes applied (awaiting `play.rongjingmusic.com` origin creation)

---

## 1. Changes Applied

### 1.1 Surface Convergence (`app/page.tsx`)

| Change | Before | After |
|---|---|---|
| **Brand area** | Static logo + text | Clickable link -> `rongjingmusic.com` (About Moodify) |
| **Menu button** | ❌ None | ✅ ☰ button in sidebar brand + mobile header |
| **Creator Center (sidebar)** | Visible in `nav-group` section | **Moved to Drawer** (conditional on `creator_writes`) |
| **Upload (mobile header)** | Visible as "上传作品" link | **Removed from header** (moved to Drawer) |
| **Drawer / Menu** | ❌ Not present | ✅ Slide-in drawer with: Library, Creator tools, About links |
| **Player utilities** | Only `◉` icon | Added "About" link -> `rongjingmusic.com` |

### 1.2 New Drawer Contents

```
┌─ Menu ──────────────✕ ┐
│                         │
│  ▥ 我的音乐             │  (if authenticated)
│  ─────────────────────  │
│  你的音乐               │  (if creator)
│  ＋ 创作者中心           │
│  📄 草稿                │
│  ─────────────────────  │
│  关于                   │
│  🏠 Moodify 官网       │  -> rongjingmusic.com
│  🏢 荣景文川            │  -> rongjingwenchuan.com
│  ─────────────────────  │
│  📥 授权收件箱          │  (if authenticated)
└─────────────────────────┘
```

### 1.3 SEO / Metadata (`app/layout.tsx`)

| Field | Before | After |
|---|---|---|
| `<title>` | "Moodify Music" | "Moodify — Play" |
| `<meta description>` | "听见此刻与你更接近的音乐。" | "正在播放。Moodify 让每一种声音都值得被世界听见。" |
| canonical | Not set | `https://play.rongjingmusic.com/` |

### 1.4 CSS (`app/globals.css`)

New styles added:
- `.brand-link` — Brand click area styling
- `.menu-toggle` — Hamburger button (sidebar + mobile)
- `.drawer-overlay` — Backdrop overlay
- `.drawer` — Slide-in panel (right side, 300px / 80vw)
- `.drawer-header` — Close button row
- `.drawer-label` — Section labels
- `.drawer-item` — Navigation items
- `.drawer-divider` — Horizontal rules
- Mobile: drawer goes full-width at ≤760px

### 1.5 Audio URL Comments (4 files)

All hard-coded `.xyz` fallback URLs annotated with:
> `Package 04: Legacy fallback — replace after play.rongjingmusic.com origin is live.`

Files annotated:
- `app/page.tsx` (line 17)
- `app/library/page.tsx` (line 51)
- `app/t/[id]/page.tsx` (line 6)
- `app/c/[handle]/page.tsx` (line 7)

---

## 2. Current Navigation (Post-Change)

### Desktop Sidebar

```
┌─────────────────────────────┐
│ [🎵 Moodify]          [☰]  │  ← Brand links to Product Home
│                             │
│  ◉ 发现音乐                 │
│  ⌕ 搜索 [____________]      │
│  ▥ 我的音乐                 │  (authenticated)
│                             │
│  👤 M                       │
│    Moodify | 创作者/聆听者   │
└─────────────────────────────┘
```

**Key change:** No more "创作者中心" in sidebar. It's now inside ☰ menu.

### Mobile Header

```
[Moodify→]    [‹][›]   [☰]
```

**Key change:** No more "上传作品" button. Clean header.

---

## 3. Cross-Link Status (Post-Change)

| From | To | Status |
|---|---|---|
| Player brand -> Product Home | `rongjingmusic.com` | ✅ Added |
| Player drawer -> Product Home | `rongjingmusic.com` | ✅ Added |
| Player drawer -> Company Home | `rongjingwenchuan.com` | ✅ Added |
| Player bar "About" -> Product Home | `rongjingmusic.com` | ✅ Added |

---

## 4. Files Modified

```
M  apps/music-web/app/page.tsx        (+38 lines: menu state, drawer JSX, brand link, utility link)
M  apps/music-web/app/layout.tsx       (+2 lines: canonical, updated title/description)
M  apps/music-web/app/globals.css     (+22 lines: drawer styles)
M  apps/music-web/app/library/page.tsx (+1 line: migration comment)
M  apps/music-web/app/t/[id]/page.tsx  (+1 line: migration comment)
M  apps/music-web/app/c/[handle]/page.tsx (+1 line: migration comment)
```

**Total: 6 files changed, ~65 lines added**

---

## 5. What Was NOT Changed (Intentional)

| Item | Reason |
|---|---|
| Backend API routes | Out of scope — surface convergence only |
| Audio streaming endpoint | Works independently of UI |
| Auth / session mechanism | Preserved as-is per spec |
| Service worker | Requires separate origin migration step |
| R2 / D1 configuration | Infrastructure, not surface |
| `/studio`, `/drafts`, `/console` routes | Still accessible via drawer or direct URL |
| Search functionality | Preserved in sidebar |
| Track listing | Preserved in content area |
| Vinyl / player core | Unchanged — already matches spec |

---

## 6. Remaining Work (Blocked on External)

1. **DNS / Cloudflare route for `play.rongjingmusic.com`** — not in repo
2. **TLS certificate** for new origin
3. **CORS update** for new origin on API/audio endpoints
4. **Service Worker re-registration** for new origin scope
5. **OAuth callback URL update** (if ChatGPT auth used)
6. **Production deployment** of these changes
7. **Android app URL update** (separate repo)
