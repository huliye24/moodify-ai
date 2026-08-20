# Package 03 — Before Company Home

**Captured:** 2026-08-19

**Branch:** `codex/moodify-classic-reconstruction-001`

**Commit:** `4ce407bb`

**Production:** `https://rongjingwenchuan.com/` (HTTPS 200)

## Current production surface

- Title: `Moodify — Auditory Intelligence Infrastructure`
- Description: `Moodify — Auditory Intelligence Infrastructure. Give machines the ability to hear.`
- Primary brand: Moodify, not 荣景文川
- Navigation: Playground / API / Developers / Research / Status
- Primary CTA: Open Moodify Ear / Try Moodify / Build with Moodify
- Hero: `Give machines the ability to hear.`
- Technical showcase: Listen / Compare / Rank / Detect plus `/v1/*` endpoint examples and SDK quickstart
- ACU section: `Free access. Governed compute.`
- Research: `Can machines learn to hear?`
- Footer: Moodify / API / Developers / Research / Status
- Product outbound: `https://rongjingmusic.com`
- Contact on live Home: none found

## Source and deployment

- The live HTML references `./styles.css`, `./app.js`, `./assets/favicon-32.png` and `./assets/moodify-symbol.png`.
- No tracked copy of those Company Home files was found in the repository.
- nginx expects `/var/www/rongjingwenchuan.com/current`.
- cloudflared maps the hostname to nginx.
- `deploy_static_origins.sh` fetches the already-live site; it is not a repository-source publisher.
- Classification: `EXTERNAL_DEPLOYMENT` until original source provenance is supplied.
