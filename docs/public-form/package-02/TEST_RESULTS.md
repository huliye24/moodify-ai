# Package 02 Test Results

**Date:** 2026-08-19

| Check | Result | Evidence |
|---|---|---|
| Package SHA-256 manifest | PASS | All 12 package files match `MANIFEST.sha256`. |
| Static Product Home suite | PASS | `node --test ops/web_origin/site/check_site.mjs`: 11/11. |
| Canon guard | PASS | `python scripts/canon_guard.py`: `CANON GUARD PASSED`. |
| Android 2.0 APK URL | PASS | HTTPS HEAD 200. |
| Android 2.0 release ZIP URL | PASS | HTTPS HEAD 200. |
| Android 3.1 expected URL | BLOCKED | HTTPS HEAD 404; not advertised. |
| Audio public rights/fairness | BLOCKED SAFE | No public grant; no audio source wired. |
| Desktop render | PASS | `screenshots/after-desktop.png`. |
| Mobile render | PASS | `screenshots/after-mobile-emulated-390.png`. |
| Keyboard/focus/reduced motion | PASS (static) | Skip link, `:focus-visible`, semantic links, reduced-motion media query. |
| Production deployment | NOT PERFORMED | Existing deploy script is not a local-source publisher. |

No new dependency, secret, DNS, Cloudflare, API, database, App or audio-processing change was introduced.
