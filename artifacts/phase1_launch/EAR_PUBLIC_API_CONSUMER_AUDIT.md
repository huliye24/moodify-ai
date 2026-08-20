# Ear Public API Consumer Audit

**Package:** MFY_PUBLIC_MUSIC_INTERNAL_EAR_PROPAGATION_001 (64A-R2)
**Date:** 2026-08-15
**Status:** READ-ONLY AUDIT — no nginx, DNS, systemd or deployment changes made
**Authority:** Release Topology v1.0 (MFY-PUBLIC-INTERNAL-TOPOLOGY-001), section 3 "Public `/api/v1` Ear proxy on website host — TRANSITION RISK"

## 1. Audited proxy surface

From `ops/web_origin/nginx/moodify-sites.conf` (read-only):

| Host | Location | Upstream | Role |
|---|---|---|---|
| `rongjingmusic.com` | `= /api/v1/auditory/jobs` | `http://127.0.0.1:8000` | Ear API upload (52m, no request buffering) |
| `rongjingmusic.com` | `/api/` | `http://127.0.0.1:8000` | Ear API full proxy |
| `rongjinwenchuan.xyz` | `/audio/` | nginx media alias `/opt/moodify/music-media/audio/` | Music media delivery (Range-capable) |
| `rongjinwenchuan.xyz` | `/api/v1/music/` + `= /api/v1/music/media` | `http://127.0.0.1:8100` | Music BFF |
| `120.55.191.146` (Hangzhou) | `:8000` | Data API / worker node | not part of the website host proxy |

## 2. Real consumers of the public Ear proxy (`rongjingmusic.com /api/ -> :8000`)

### 2.1 Operator (human) — `apps/ear-workbench`

- Caller: `assets/workbench.js`, `const API = window.MOODIFY_API_BASE || "/api/v1"` — same-origin in production.
- Endpoints: `/health`, `/auditory/jobs` (POST upload), `/auditory/jobs/{id}` (status/result), `/auditory/reviews` (pending + decide), `/auditory/measurements` via result payloads.
- Identity: unauthenticated browser sessions today; `noindex` added by this package is discovery hygiene only — **not access control** (Topology §2).
- Migration: move Workbench behind authenticated/private access (private network, VPN, operator allowlist or equivalent reviewed control). Until then the proxy remains reachable publicly.
- Deletion risk if removed without migration: operator surface fully offline.

### 2.2 Service-to-service / E2E — `ops/e2e_runner.py`

- `SITE = "https://rongjingmusic.com"`; Ear read surface: `GET /api/v1/health` (stage_live_read).
- Full Ear loop (stage_local_ear): `POST /api/v1/auditory/jobs`, `GET /api/v1/auditory/jobs/{id}`, result polling — runs against an injected `api` argument (defaults to the public site).
- Identity: unauthenticated probe with browser UA (nginx 403s bare urllib).
- Migration: point `api` argument at an internal Ear address once one is authorized; low risk (read-only health + job submission).
- Deletion risk: moderate — E2E coverage of the Ear loop is lost until the internal address is wired.

### 2.3 Monitoring / probe — `ops/web_origin/probe_resources.sh`

- `probe "LA Ear API /health" 200 "$LA/api/v1/health"` — single read-only health probe per run.

### 2.4 Monitoring / soak — `ops/web_origin/soak_probe.sh`

- `BASE="${MOODIFY_E2E_BASE:-https://rongjingmusic.com}"`; `h_ear=$(curl ... "$BASE/api/v1/health")` every interval.
- Identity: unauthenticated read-only health poll.
- Migration: switch `MOODIFY_E2E_BASE` to the internal base; trivially low risk.
- Deletion risk: negligible.

### 2.5 Browser consumers (public)

- None found. Official website pages are static; no public page JS calls `/api/` on `rongjingmusic.com`.

## 3. Non-consumers verified (P0 check — Music playback must not depend on public Ear)

| Surface | Base | Ear dependency |
|---|---|---|
| `apps/music-web` | `BASE = "/api/v1/music"` (BFF) | **none** — grep of `lib/` and `app/` finds no `auditory`, `rongjingmusic.com/api`, or Ear health calls |
| `apps/music-android` | `BffClient("https://rongjinwenchuan.xyz/api/v1/music")` | **none** |
| Music media playback | `rongjinwenchuan.xyz /audio/` + `:8100` BFF | **none** |

**Result: no P0. The Music playback path is fully independent of the public Ear API proxy.**

## 4. Not via the public proxy

- `apps/android` (Ear operator client): `BaseUrlStore.DEFAULT = "http://127.0.0.1:8000"` (adb reverse local loopback; release builds only localhost) — does not traverse the public host proxy.

## 5. Migration plan sketch (not executed)

1. Keep the proxy until the Workbench has an authenticated/private access path.
2. Repoint `probe_resources.sh` / `soak_probe.sh` / `e2e_runner.py` Ear stages at the internal Ear address.
3. Remove or restrict `location /api/` and `location = /api/v1/auditory/jobs` only after (1)+(2) and explicit deployment authorization.
4. `noindex` on the Workbench does not replace steps 1–3 (Topology §5).

## 6. Evidence of read-only compliance

- No files under `ops/web_origin/nginx/` modified (git status clean for that path in this package).
- No DNS/systemd/deploy commands executed in this package.
