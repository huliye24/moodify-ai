# Package 02 — Before Snapshot

**Captured:** 2026-08-19

**Branch:** `codex/moodify-classic-reconstruction-001`

**Commit:** `4ce407bb`

**Production URL:** `https://rongjingmusic.com/` (HTTPS 200 during audit)

## Public Home before change

- Headline: `LISTEN. THEN PLAY.`
- Supporting line: `Moodify 先听，再为你播放。`
- Primary navigation: Home / Moodify Music / Evidence
- Section order: Hero → sound test → six-step internal loop → product → Android download → Evidence
- Footer: `© 2024–2026 荣景文川 · Moodify — The Ear of AI`
- SEO title: `Moodify Music — Moodify listens before you do`
- SEO description: `Moodify Music is a listening experience built around one idea: Moodify listens before you do.`
- OG title: same as SEO title
- Download links: Android 2.0 APK and Android 2.0 release ZIP
- Evidence link: `/evidence.html`
- Player link: `https://rongjinwenchuan.xyz`

## Verified deployment facts

- Source directory: `ops/web_origin/site/rongjingmusic/`
- Static test/build command: `node --test ops/web_origin/site/check_site.mjs`
- Deployment root: `/var/www/rongjingmusic.com/current`
- nginx configuration: `ops/web_origin/nginx/moodify-sites.conf`
- Current static deployment script fetches the already-live site into a release directory; it does not publish local source.
- No screenshots were captured in this environment.

## Known source/production mismatches

- The repository contains Android 3.1.0 with verified SHA-256, but its expected Product Home URL returned 404.
- Android 2.0 APK and release ZIP both returned HTTP 200 and remain the only verified Product Home downloads.
- No public-demo audio has an explicit public right grant; rights records default public-demo permission to NO.
