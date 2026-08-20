# Before Player Snapshot

**Date:** 2026-08-19
**Package:** 04 - Web Player Migration
**Commit:** Current HEAD (pre-migration)
**Origin:** `https://rongjinwenchuan.xyz/` (legacy)

---

## 1. Current Production Headline

```
Moodify Music
听见此刻与你更接近的音乐。
```

**First visual impression:** A music discovery app with sidebar navigation, hero section featuring vinyl artwork, track listing, and a bottom player bar.

---

## 2. Current Navigation

### Desktop Sidebar

```
┌─────────────────────────────┐
│ 🎵 Moodify                  │
│                             │
│  ◉ 发现音乐                 │
│  ⌕ 搜索 [____________]      │
│  ▥ 我的音乐                 │
│                             │
│  你的音乐                   │
│  ＋ 创作者中心               │
│                             │
│  👤 M                       │
│    Moodify | 创作者/聆听者   │
└─────────────────────────────┘
```

### Mobile Header

```
[Moodify]   [‹][›]   [上传作品]
```

---

## 3. Current Primary CTA Flow

1. User lands on `/`
2. Sees "发现音乐" as active nav item
3. Hero shows current track with vinyl + play button + favorite
4. Track list below with filter tabs: 为你推荐 / Cadeau10 / 专辑 1
5. Bottom player bar: vinyl mini + controls + progress + utilities
6. Creator users see: "创作者中心" in sidebar, "上传作品" in header

---

## 4. Current Surface Elements (Pre-Migration)

| Element | Location | Visibility |
|---|---|---|
| Brand mark | Sidebar top, mobile header | Always visible |
| Discover music | Sidebar nav button | Always visible, marked active |
| Search | Sidebar nav | Always visible |
| My library | Sidebar nav | Authenticated only |
| **Creator center** | Sidebar nav group | **Authenticated creator: always visible** |
| **Upload work** | Mobile header right | **Authenticated creator: always visible** |
| Hero section | Content area | Always visible — vinyl + title + artist + play + favorite |
| Filter tabs | Content area | 3 tabs: 推荐/Cadeau10/专辑1 |
| Track list | Content area | Scrollable list with cover art |
| Player bar | Fixed bottom | Vinyl mini + title + like + prev/play/pause/next + progress |

---

## 5. Current Route Table

| Route | Type | Auth Required | Creator Only | Public Face |
|---|---|---|---|---|
| `/` | Page | No | No | ✅ Main player |
| `/library` | Page | Yes | No | ✅ User library |
| `/playlists` | Page | Yes | No | ⚠️ P2 feature |
| `/studio` | Page | Yes | Yes | ❌ **Creator surface** |
| `/drafts` | Page | Yes | Yes | ❌ Creator surface |
| `/console` | Page | Yes | Admin | ❌ Admin surface |
| `/inbox` | Page | Yes | Yes | ❌ Creator surface |
| `/offline` | Page | No | No | ⚠️ Utility |
| `/design` | Page | No | No | ❌ Dev/debug |
| `/beta-login` | Page | No | No | ⚠️ Auth flow |
| `/t/[id]` | Page | No | No | ✅ Track page |
| `/c/[handle]` | Page | No | No | ✅ Creator profile |
| `/api/v1/tracks` | API | Varies | No | Backend |
| `/api/v1/tracks/[id]` | API | Varies | No | Backend |
| `/api/v1/tracks/[id]/audio` | API | No | No | **Audio streaming** |
| `/api/v1/tracks/[id]/publish` | API | Yes | Yes | Backend |
| `/api/v1/creators/[handle]` | API | No | No | Backend |
| `/api/v1/me/creator` | API | Yes | No | Backend |

---

## 6. Current Audio URL Pattern

```
https://rongjinwenchuan.xyz/audio/{asset_key}
```

Fallback for demo album:
```
https://rongjinwenchuan.xyz/audio/cadeau10-album1/{filename}.wav
```

Environment variable override:
```
NEXT_PUBLIC_AUDIO_BASE_URL (defaults to https://rongjinwenchuan.xyz/audio)
```

---

## 7. Current SEO / OG State

```html
<title>Moodify Music</title>
<meta name="description" content="听见此刻与你更接近的音乐。" />
<meta name="theme-color" content="#05081e" />
<link rel="manifest" href="/manifest.webmanifest" />
<!-- No canonical set -->
<!-- No og:* explicitly defined -->
<!-- No robots.txt observed in source -->
<!-- No sitemap.xml observed in source -->
```

---

## 8. Current PWA Manifest

```json
{
  "name": "Moodify Music",
  "short_name": "Moodify",
  "display": "standalone",
  "background_color": "#05081e",
  "theme_color": "#05081e"
}
```

Scope: Current origin (`rongjinwenchuan.xyz`)

---

## 9. Current Service Worker

File: `public/sw.js` (2815 bytes)
- Registered via `app/sw-register.tsx`
- Caches: HTML, JS, CSS, audio
- Scope: Current origin

---

## 10. Current Cross-Link Status

| From | To | Link Type | Status |
|---|---|---|---|
| Player (.xyz) | Product Home (rongjingmusic.com) | ❌ Not present | Missing |
| Player (.xyz) | Company Home (rongjingwenchuan.com) | ❌ Not present | Missing |
| Product Home | Player (.xyz) | External link | Exists (if configured) |
| Company Home | Product Home | External link | ✅ Package 03 done |

**Gap:** Player has no return path to Product Home or Company Home.

---

## 11. Issues to Address in Migration

### P0 (Must Fix)
1. **No return link to Product Home** — Player is a dead end
2. **Creator surface in primary nav** — "创作者中心" and "上传作品" visible at first layer
3. **Hard-coded `.xyz` origin** in 6 files — blocks domain migration
4. **No canonical/OG optimization** — SEO incomplete

### P1 (Should Fix)
5. **No footer** — Missing About/Privacy/Company links
6. **No loading spinner** — Audio buffering state unclear
7. **Mobile header cluttered** — Upload button competes with navigation

### P2 (Can Defer)
8. **Filter tabs are static** — Hardcoded "为你推荐/Cadeau10/专辑1"
9. **Design route exposed** — `/design` should not be public
10. **Console route exposed** — `/console` should require stronger gates

---

## 12. Screenshots

See `screenshots/` directory:
- `before-player-desktop.png` — Full desktop render
- `before-player-mobile-emulated-390.png` — Mobile 390px render
