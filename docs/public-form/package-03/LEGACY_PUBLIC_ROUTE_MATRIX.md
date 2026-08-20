# Legacy Public Route Matrix

Read-only checks were made on 2026-08-19. nginx currently falls back unknown paths to `index.html`; HTTP 200 therefore does not prove a distinct route.

| Route | Source file | Traffic evidence | External dependency | Index status | Recommended action | Package 03 action |
|---|---|---|---|---|---|---|
| `/api` | External live source, not tracked | UNVERIFIED | UNKNOWN | SPA fallback 200 | Remove from navigation; retain runtime | Not linked; not deleted |
| `/developers` | External live source, not tracked | UNVERIFIED | UNKNOWN | SPA fallback 200 | Remove from navigation; retain compatibility | Not linked; not deleted |
| `/docs` | No distinct tracked source | UNVERIFIED | UNKNOWN | SPA fallback 200 | Inventory consumers before redirect | No runtime change |
| `/acu` | No distinct tracked source | UNVERIFIED | UNKNOWN | SPA fallback 200 | Remove from Company identity | Not linked; no runtime change |
| `/v1/listen` | Backend/API ownership UNVERIFIED | UNVERIFIED | UNKNOWN | SPA fallback 200 on Company host | Preserve service; remove public showcase | No API/config change |
| `/v1/compare` | Backend/API ownership UNVERIFIED | UNVERIFIED | UNKNOWN | SPA fallback 200 on Company host | Preserve service; remove public showcase | No API/config change |
| `/v1/rank` | Backend/API ownership UNVERIFIED | UNVERIFIED | UNKNOWN | SPA fallback 200 on Company host | Preserve service; remove public showcase | No API/config change |
| `/v1/detect` | Backend/API ownership UNVERIFIED | UNVERIFIED | UNKNOWN | SPA fallback 200 on Company host | Preserve service; remove public showcase | No API/config change |
| `/research` | No distinct tracked source | UNVERIFIED | none proven | SPA fallback 200 | Use Home `#research` until a real route exists | Home anchor only |
| `/privacy` | No distinct tracked source | UNVERIFIED | none proven | SPA fallback 200 | Provide a real static privacy page | New `/privacy.html`; no redirect |
| `/contact` | No distinct tracked source | UNVERIFIED | none proven | SPA fallback 200 | Use verified email on Home | Home `#contact` + mailto |

No legacy route, API, nginx rule or cloudflared mapping is deleted or redirected in Package 03.
