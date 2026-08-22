# Previous Library Experience Audit

| Area | Before W06 | Evidence |
|---|---|---|
| Library list/import/remove | WORKING | `LibraryService`, IPC and sidebar rows |
| All Songs page | PARTIAL | Tracks were rendered directly in the sidebar; no metadata table |
| Recently Added | MISSING | `created_at` existed but no projection |
| Recently Played/history | MISSING | Cloud client DTOs were unrelated to local Library |
| Favorites | MISSING | Cloud API methods existed; no local Favorite authority |
| Search/sort | MISSING | No input, control or projection pipeline |
| Metadata rendering | PARTIAL | title/artist only; no album/duration/fallback view contract |
| Track actions | PARTIAL | play/queue/playlist/remove existed per row |
| Duplicate local state | PARTIAL | legacy playlist localStorage migration exists; no W06 shadow state added |
| Performance | UNKNOWN | no large-Library evidence before W06 |

The main player remained PLAY-focused. W06 adds only secondary Library views.
