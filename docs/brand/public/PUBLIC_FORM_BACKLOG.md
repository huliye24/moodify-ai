# Public Form Backlog

No item below is implemented in Package 01.

## Package 02 — `rongjingmusic.com` Product Home

| Files | Purpose | Dependencies | Risks | Acceptance |
|---|---|---|---|---|
| `ops/web_origin/site/rongjingmusic/index.html`, `assets/site.css` | Lead with belief → sound → Play; reduce internal loop/Evidence prominence | Approved Public Brand authority; playable comparison assets | Removing factual proof or breaking existing CTA | 10-second comprehension test; one dominant Play action; before/after listening verified. |
| All tracked `*.html`, `sitemap.xml`, `robots.txt` | Normalize Header/Footer, titles, descriptions, canonical and OG; remove old public identity | Final Product/Company links | SEO duplication, dead links | Link crawl; canonical/OG audit; no primary Tier-D phrase. |
| `index.html`, `music.html`, nginx `/downloads/` mapping and release inventory | Reconcile Android version/download links | Human-selected release; artifact checksums | Advertising stale or missing APK | HTTP 200, checksum/release label match, device install smoke test. |
| `about.html`, `ear.html`, `evidence.html` | Move research/internal language behind product comprehension | Company Research destination | Accidental loss of evidence context | Tier rules pass; Ear remains internal; evidence claims retain limits. |

## Package 03 — `rongjingwenchuan.com` Company Home

| Files | Purpose | Dependencies | Risks | Acceptance |
|---|---|---|---|---|
| Current production source: `UNVERIFIED`; discover release source used by `deploy_static_origins.sh` and `/var/www/rongjingwenchuan.com/releases` | Put Company identity under source control before editing | Read-only server/release provenance audit | Editing a non-authoritative copy | Exact build/release provenance recorded and reproducible. |
| Discovered Company Home HTML/CSS/JS and metadata | Replace Infrastructure/API identity with Company → Moodify → Research → Contact | Source provenance; approved company facts | Unverified company claims | HTTPS, SEO/OG, navigation and claim-maturity review pass. |
| `ops/web_origin/verify_origins.sh` | Change retired string probes after new release | New stable Company marker | Probe passes while wrong content deploys | Probe asserts company identity and links to Moodify. |

## Package 04 — Web Player / `.xyz` → `play.rongjingmusic.com`

| Files | Purpose | Dependencies | Risks | Acceptance |
|---|---|---|---|---|
| `apps/music-web/app/layout.tsx`, `app/page.tsx`, `public/manifest.webmanifest` | Make Player Play-only; add Product Home return; align metadata | Package 02 URL contract | Gated features leaking into primary UX | Player opens to Play; logo returns Product Home; metadata passes Tier rules. |
| `app/studio`, `app/console`, `app/drafts`, `app/inbox`, `app/t/[id]`, related navigation | Hide/demote Creator/upload/licensing from current public journey without deleting contracts/data | Human decision on retained access; auth/capability checks | Broken creator workflows or data loss | Listener path contains no creator-first CTA; retained gated URLs tested. |
| `ops/web_origin/nginx/moodify-sites.conf`, `cloudflared/config.yml`, deployment/runbooks | Add `play.rongjingmusic.com`; decide `.xyz` redirect/compatibility only after verification | DNS/TLS authority, traffic evidence, rollback plan | Playback outage, redirect loop, broken API/audio origins | TLS, Range, API, browser-back, canonical and rollback tests pass. |
| Android/BFF hard-coded `.xyz` endpoints and contracts | Separate Player hostname migration from API/media compatibility | Endpoint inventory and staged compatibility | App playback regression | Existing app versions continue playback during migration. |
