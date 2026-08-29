# Screenshot Index — 64A-R2 evidence

**Date:** 2026-08-15
**Method:** Playwright 1.62.1 (npx cache) driving system Chrome (Google Chrome for Windows), viewport 1440×900 and 390×844; real URLs recorded in `screenshot-evidence.json`; screenshots stored in `screenshots/`.
**Servers used:** official website + Ear workbench served as static sites (python http.server 8080/8081); Music served by `MOODIFY_SELF_HOSTED=1` vite dev (localhost:5173) with `/api/v1/music/bootstrap` route-intercepted to model identities (browser-side mock, no server change).

| File | Surface | Identity | URL | Notes |
|---|---|---|---|---|
| `site-home-1440x900.png` | Official Website | anonymous | http://localhost:8080/ | 3-item nav: Home / Moodify Music / Evidence |
| `site-home-mobile-390x844.png` | Official Website | anonymous | http://localhost:8080/ | mobile viewport |
| `site-music-1440x900.png` | Official Website music page | anonymous | http://localhost:8080/music.html | Library·Track·Now Playing·Play axis |
| `ear-index-operator-1440x900.png` | Ear workbench (INTERNAL) | operator | http://localhost:8081/ | INTERNAL OPERATOR SYSTEM; **not a public product screenshot** |
| `music-home-anonymous-1440x900.png` | Music Web | anonymous | http://localhost:5173/ | no Library/Studio/upload entries |
| `music-home-anonymous-mobile-390x844.png` | Music Web | anonymous | http://localhost:5173/ | mobile |
| `music-home-listener-1440x900.png` | Music Web | listener (account_actions) | http://localhost:5173/ | Library visible only |
| `music-home-listener-mobile-390x844.png` | Music Web | listener | http://localhost:5173/ | mobile (sidebar hidden by layout) |
| `music-home-creator-1440x900.png` | Music Web | creator (both caps) | http://localhost:5173/ | Library + Studio + upload visible |
| `music-home-creator-mobile-390x844.png` | Music Web | creator | http://localhost:5173/ | mobile |

Identity matrix (DOM-observed, from `screenshot-evidence.json`):

| Entry | anonymous | listener | creator |
|---|---|---|---|
| Library `/library` | none | visible | visible |
| Studio `/studio` | none | none | visible |
| Upload (header) | none | none | visible |
| Inbox `/inbox` | none | none | none |

Ear workbench sidebar nav (all 8 pages, contract-checked): Home / New Listening Case / Evidence Library / System Status (4 items, identical across pages); Human Review is deep-link only.
