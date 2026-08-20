# Public Surface Inventory — Package 01

**Audit date:** 2026-08-19

**Method:** tracked repository inspection plus read-only HTTPS fetches. No DNS or production configuration was changed.

## Inventory

| Domain / surface | Repository directory | Deployment entry | Home / metadata | Public routes and entry points | Current first definition | Verification |
|---|---|---|---|---|---|---|
| `rongjingmusic.com` | `ops/web_origin/site/rongjingmusic/` | `ops/web_origin/deploy_static_origins.sh`; nginx root `/var/www/rongjingmusic.com/current`; cloudflared hostname mapping | `index.html`; title/description, canonical and OG present | Header: Home, Moodify Music, Evidence. Footer: About, Contact, Privacy. Player CTA → `.xyz`. APK/ZIP download links. Research/Ear content at `about.html`, `ear.html`, `evidence.html`. | `Moodify Music — Moodify listens before you do`; Hero `LISTEN. THEN PLAY.`; footer still says `The Ear of AI`. | Repository VERIFIED; HTTPS 200 VERIFIED on audit date. |
| `rongjingwenchuan.com` | Production page source absent from tracked repository; deployment/test references under `ops/web_origin/` | nginx root `/var/www/rongjingwenchuan.com/current`; cloudflared hostname mapping; `deploy_static_origins.sh` fetches a release rather than building tracked source | Tracked home file: `UNVERIFIED`. Live title/description verified. OG: not found in fetched home. | Live surface exposes Developers/API/ACU and `Build with Moodify`; exact complete route list and Header/Footer source: `UNVERIFIED`. | `Moodify — Auditory Intelligence Infrastructure`; `Give machines the ability to hear.` | HTTPS 200 and phrases VERIFIED; source provenance UNVERIFIED. |
| `rongjinwenchuan.xyz` | `apps/music-web/` (Next.js/PWA); service contracts in `moodify-music-package/` | nginx proxies `/` to `127.0.0.1:3000`, `/api/v1/music/` to BFF `:8100`, `/audio/` to static media; cloudflared hostname mapping | `apps/music-web/app/layout.tsx`, `app/page.tsx`, `public/manifest.webmanifest` | Player at `/`; library; track and creator pages; gated `/studio`, `/console`, `/drafts`, `/inbox`; upload and licensing flows; no verified logo link back to product home. | `Moodify Music`; description `听见此刻与你更接近的音乐。` | Repository VERIFIED; HTTPS 200 VERIFIED. |
| `play.rongjingmusic.com` | No source/deployment hostname found | No nginx/cloudflared entry found | `UNVERIFIED` | Target player migration only | No current public definition | TLS connection failed during read-only fetch; migration status `UNVERIFIED`. |
| Android public download | App source: `apps/music-android/`; public links in `ops/web_origin/site/rongjingmusic/index.html` and `music.html`; releases under `deliverables/releases/` | Static `/downloads/` alias in nginx | Main-site links label Moodify Music 2.0; repository status/README mention 3.1; live download availability/version consistency not exhaustively verified | APK and release ZIP links | `Moodify Music` | Naming VERIFIED; advertised-version consistency requires Package 02 verification. |

## Header, footer, SEO and OG findings

- Product Home has tracked Header/Footer and per-page title/description/canonical. Home has OG title/description/url; secondary pages have partial OG metadata.
- Product Home footer repeats `Moodify — The Ear of AI` across tracked pages.
- Company Home's live title and description encode the retired Infrastructure identity. Its tracked production source is missing, so file-level remediation cannot yet be named beyond deployment/release discovery.
- Player metadata identifies Moodify Music but has no canonical/OG metadata in `app/layout.tsx`, and its manifest description still says `先听，再发现，然后创作`.
- `play.rongjingmusic.com` is not represented in tracked nginx/cloudflared configuration.

## Fourth/fifth public definitions found

1. Older `docs/product-framework/TERMINOLOGY_AND_CLAIMS.md` defines Moodify publicly as `The Ear of AI`.
2. `docs/product-framework/04_MOODIFY_MUSIC_PRODUCT_FRAMEWORK.md` and public Music pages retain a listening-and-publishing / creator-platform definition.
3. `docs/contracts/product-boundary.md` retains historical domain roles that conflict with the new Company/Product/Player split.

These remain useful history or engineering context but no longer own public-brand authority.
