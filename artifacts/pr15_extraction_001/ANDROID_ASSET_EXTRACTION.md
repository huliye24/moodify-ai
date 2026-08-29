# Android Asset Extraction

| Area | Useful asset | Current assumption / risk | Action |
|---|---|---|---|
| Connection/pairing | Base URL store, token handling, classified errors | bespoke pairing/token protocol | KEEP_UI_CONCEPT, KEEP_TEST; reimplement auth contract |
| Upload/process/result | real file hash, upload, project creation, polling, result display | server auto-starts job; project/job states differ from canonical ProductionCase | REIMPLEMENT_AGAINST_CANONICAL_API |
| Playback | Media3 queue, A/B original/processed switching, error reporting | artifact/catalog URLs and token refresh are branch API-specific | KEEP_UI_CONCEPT and isolated playback tests |
| Internationalization | six locale resources, key parity, locale persistence | low domain coupling | KEEP_DATA_MODEL / KEEP_TEST; likely cherry-pickable after resource review |
| Mini-player gestures | pure gesture logic and unit tests | instrumentation idleness issue from ticker | KEEP_TEST and pure logic; rework Compose instrumentation |
| CWC/creator flows | onboarding/auth/gift/center screens | product/domain authority not established | HUMAN_DECISION / ARCHIVE until founder confirms product role |
| Works/catalog | useful browsing and result concepts | creates app-owned work/catalog domain | KEEP_UI_CONCEPT; consume canonical assets instead |

## Minimum Stable Android API

1. `GET /api/v1/health` and `GET /api/v1/capabilities` with API/client compatibility.
2. A stable authentication/session mechanism with revoke and structured errors.
3. `POST /api/v1/assets` (multipart) returning immutable asset ID, sha256, media type, and size.
4. `POST /api/v1/cases` binding source asset and objective/spec; no implicit hidden job semantics.
5. `GET /api/v1/cases/{id}` returning canonical case state, progress projection, allowed actions, and failure code.
6. Explicit approval endpoint bound to case version and plan hash.
7. Case evidence/result index returning typed artifacts with authorized download URLs.
8. Optional catalog/list endpoints that reference canonical Asset IDs rather than define a second asset model.

Android may project canonical state into UI-friendly labels, but it must not invent a second ProductionCase or Rule model.
