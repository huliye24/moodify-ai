# Legacy Player Route Matrix

**Date:** 2026-08-19
**Package:** 04 - Web Player Migration
**Origin:** `rongjinwenchuan.xyz` (legacy)

---

## Route Inventory

| # | Route | Type | Auth | Creator | Public Face | Current Traffic | External Dep | Recommended Action | Actual Action |
|---|---|---|---|---|---|---|---|---|
| 1 | `/` | Page | No | No | ✅ Main player | Unknown | None | **keep** — core surface | keep |
| 2 | `/library` | Page | Yes | No | ✅ User library | Unknown | None | **keep** — moved to drawer entry | keep |
| 3 | `/playlists` | Page | Yes | No | ⚠️ P2 feature | Unknown | None | **keep** — accessible via URL | keep |
| 4 | `/studio` | Page | Yes | Yes | ❌ Creator surface | Unknown | Upload dep | **hide from first layer** → drawer | **done** — moved to drawer |
| 5 | `/drafts` | Page | Yes | Yes | ❌ Creator surface | Unknown | Studio dep | **hide from first layer** → drawer | **done** — moved to drawer |
| 6 | `/console` | Page | Yes | Admin | ❌ Admin surface | Unknown | Admin only | **keep gated** — no nav exposure | keep (no change) |
| 7 | `/inbox` | Page | Yes | Yes | ❌ Creator surface | Unknown | License dep | **hide from first layer** → drawer | **done** — moved to drawer |
| 8 | `/offline` | Page | No | No | ⚠️ Utility | Unknown | SW dep | **keep** — PWA utility | keep |
| 9 | `/design` | Page | No | No | ❌ Dev/debug | Unknown | None | **keep but no nav link** | keep (no change) |
| 10 | `/beta-login` | Page | No | No | ⚠️ Auth flow | Unknown | OAuth dep | **keep** — auth required | keep |
| 11 | `/track/[id]` | Page | No | No | ✅ Track page | Unknown | Redirects to /t/[id] | **keep redirect** | keep |
| 12 | `/t/[id]` | Page | No | No | ✅ Track play | Unknown | Audio dep | **keep** — deep link | keep |
| 13 | `/c/[handle]` | Page | No | No | ✅ Creator profile | Unknown | API dep | **keep** — public profile | keep |
| 14 | `GET /api/v1/tracks` | API | Varies | No | Backend | Unknown | D1 | **keep** — data API | keep |
| 15 | `GET/PUT /api/v1/tracks/[id]` | API | Varies | No | Backend | Unknown | D1+R2 | **keep** — data API | keep |
| 16 | `GET /api/v1/tracks/[id]/audio` | API | No | No | **Audio stream** | Unknown | R2 Range | **keep critical** — media | keep |
| 17 | `POST /api/v1/tracks/[id]/publish` | API | Yes | Yes | Backend | Unknown | Workflow | **keep** — creator action | keep |
| 18 | `GET /api/v1/creators/[handle]` | API | No | No | Backend | Unknown | D1 | **keep** — data API | keep |
| 19 | `GET /api/v1/me/creator` | API | Yes | No | Backend | Unknown | D1 | **keep** — user data | keep |

---

## Action Summary

### Surface Changes (Applied)

| Route | Previous Visibility | New Visibility |
|---|---|---|
| `/studio` | Sidebar nav group + header button | Drawer menu (conditional) |
| `/drafts` | Direct URL only | Drawer menu (conditional) |
| `/inbox` | Direct URL only | Drawer menu (conditional) |

### Routes Unchanged

All other routes remain at same URL and access level. No routes were deleted. No backend code was modified.

---

## Notes

- **No route deletion performed.** Per spec: "隐藏不等于删除后端数据"
- **External traffic evidence unavailable.** All traffic marked "Unknown" — requires analytics access
- **Deep links preserved.** `/t/[id]` and `/c/[handle]` continue to work
- **Audio streaming untouched.** `/api/v1/tracks/[id]/audio` remains the critical path
