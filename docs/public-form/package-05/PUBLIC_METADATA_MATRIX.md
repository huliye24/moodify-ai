# Public Metadata Matrix

**Date:** 2026-08-19
**Package:** 05 - Brand Unification
**Scope:** SEO / OG / Canonical across 3 public surfaces

---

## Current State (Post-Package 02/04 Changes)

### Surface 1: Company Home (`rongjingwenchuan.com`)

| Field | Value | Source | Status |
|---|---|---|---|
| `<title>` | "荣景文川 | Rongjing Wenchuan" | Package 03 spec | ✅ Company-first |
| `<meta description>` | "We build things worth hearing." + company brief | P03 | ✅ Correct |
| `og:title` | Same as title | P03 | ✅ Consistent |
| `og:description` | Same as meta description | P03 | ✅ Consistent |
| canonical | `https://rongjingwenchuan.com/` | P03 | ✅ Set |
| `og:url` | Same as canonical | Expected | ✅ Should match |
| JSON-LD | Organization schema | P03 spec | 📝 Recommended |

### Surface 2: Product Home (`rongjingmusic.com`)

| Field | Value | Source | Status |
|---|---|---|---|
| `<title>` | "Moodify — Every voice deserves to be heard" | Package 02 | ✅ Product identity |
| `<meta description>` | "每一种声音，都值得被世界听见。Listen. Then Play." | P02 | ✅ Bilingual brand |
| `og:title` | "Moodify" or full title | P02 | ✅ |
| `og:description` | Brand belief + CTA | P02 | ✅ |
| canonical | `https://rongjingmusic.com/` | P02 | ✅ Brand primary |
| `og:url` | `https://rongjingmusic.com/` | Expected | ✅ |
| JSON-LD | Product or WebApplication schema | Recommended | 📝 Add if possible |

### Surface 3: Player (`play.rongjingmusic.com` / `.xyz`)

| Field | Value | Source | Status |
|---|---|---|---|
| `<title>` | "Moodify — Play" | **Package 04 change** | ✅ Updated |
| `<meta description>` | "正在播放。Moodify 让每一种声音都值得被世界听见。" | **P04 change** | ✅ Updated |
| canonical | `https://play.rongjingmusic.com/` | **P04 change** | ✅ Pre-configured |
| `og:title` | "Moodify — Play" | Inherits title | ✅ |
| `og:description` | Player-focused | Inherits meta | ✅ |
| manifest name | "Moodify Music" | Existing | ⚠️ May update to "Moodify Player" |
| theme-color | `#05081e` | Existing | ✅ Consistent with dark theme |

---

## Cross-Surface Conflict Check

| Potential Conflict | Status | Resolution |
|---|---|---|
| Duplicate titles? | ✅ None | Each surface has distinct title |
| Duplicate descriptions? | ✅ None | Each tailored to surface role |
| Canonical overlap? | ✅ None | Three different canonical URLs |
| OG competing for same keyword? | ✅ None | Company=org, Product=brand, Player=action |
| `.xyz` in metadata? | ✅ None | Removed from player metadata in P04 |

---

## Sitemap & Robots Status

| Item | Company | Product | Player |
|---|---|---|---|
| sitemap exists | Unknown | Unknown | Not in repo |
| robots.txt | Unknown | Unknown | Not in repo |
| noindex on any page | ❌ No | ❌ No | ❌ No |
| blocked routes | N/A | N/A | `/design`, `/console` (no nav link) |

**Note:** Sitemap/robots configuration is typically at CDN/reverse-proxy level, not in app source. Marked as external configuration.

---

## Recommendations

### Immediate (Phase 1)

1. ✅ Player metadata updated (DONE in P04)
2. ✅ Canonical URLs set (DONE in P04)
3. 📝 Consider adding JSON-LD structured data to all 3 surfaces
4. 📝 Verify OG tags render correctly in social previews (requires deploy)

### Next Iteration (After Deploy)

1. Generate sitemap.xml for all 3 origins
2. Configure robots.txt on each origin
3. Test social sharing cards (LinkedIn, Twitter, WeChat)
4. Monitor search console for indexing issues
5. Set up cross-origin referrer policy if needed

---

## Metadata Identity Summary

```
┌─────────────────────┬──────────────────────────┬─────────────────────┐
│   Company Home      │    Product Home         │     Player          │
│                     │                          │                     │
│ 荣景文川             │  Moodify                 │  Moodify — Play     │
│                     │                          │                     │
│ We build things     │  Every voice deserves    │  正在播放...        │
│ worth hearing.      │  to be heard.            │                     │
│                     │  Listen. Then Play.     │  Play.              │
│                     │                          │                     │
│ canonical:          │  canonical:              │  canonical:         │
│ rongjingwenchuan    │  rongjingmusic           │  play.rongjingmusic │
└─────────────────────┴──────────────────────────┴─────────────────────┘
```

**Three distinct identities, one coherent brand system.**
