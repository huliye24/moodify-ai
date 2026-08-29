# Package 03 — After Company Home

**Implemented:** 2026-08-19

**New reviewable source:** `ops/web_origin/site/rongjingwenchuan/`

## New Company Home

- Company identity: 荣景文川 / Rongjing Wenchuan
- Hero: `We build things worth hearing.`
- Description: `An independent company building products and research.`
- Belief: `Every voice deserves to be heard.` / `每一种声音，都值得被世界听见。`
- Primary work: Moodify / `Listen. Then Play.`
- Moodify link contract: Header, Hero, Primary Work, Company facts and Footer point to `https://rongjingmusic.com/`
- Research: `Can machines learn to hear?` presented as research beneath the product
- Company facts: only verified public name, primary product, research question and contact
- Contact: `hello@rongjingwenchuan.com`
- Privacy: real static `/privacy.html`
- Sitemap: only Company Home and privacy page; no API/Developers/ACU route

## Removed from the new primary surface

- Auditory Intelligence Infrastructure
- Give machines the ability to hear.
- Build with Moodify
- Playground / API / Developers / Status navigation
- ACU commercial identity
- `/v1/listen`, `/v1/compare`, `/v1/rank`, `/v1/detect` showcase

No backend API, legacy route, nginx rule, DNS or cloudflared mapping was deleted or changed.

## Visual verification

- Desktop: `screenshots/after-company-desktop.png`
- Mobile emulation (~390 CSS px): `screenshots/after-company-mobile-emulated-390.png`

## Deployment status

Not deployed. The original live source and a repository-to-server publish procedure remain unavailable; see `BLOCKERS.md`.
