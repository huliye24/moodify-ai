# Product Model Assessment

| Entity | Decision | Basis / target boundary |
|---|---|---|
| CloudTrack | KEEP | BFF `Track` DTO and server ID are stable cloud references |
| Queue | KEEP | One in-memory `PlaybackQueue`; later persistence may reference Track IDs |
| Playback engine | KEEP | Single service/engine path with tested transitions |
| AppState | REPAIR | Versioned atomic JSON exists, but read/wiring and renderer access are incomplete |
| Track | MIGRATE | Split source-specific locator from durable client Track identity; preserve cloud IDs |
| Library | MIGRATE | Currently absent; create one durable collection authority in W02 |
| Playlist | REPAIR | Preserve existing `{id,name}` records while moving them from unversioned localStorage |
| PlaylistItem | MIGRATE | Absent; introduce ordered relation to durable Track IDs, not paths/blob URLs |
| Favorite | REPAIR later | API exists but Desktop UI/authority is incomplete |
| History | REPAIR later | play event support exists; no local/history surface closure |

Migration must be adapter-based: import existing playlist-name JSON into the existing versioned main-process persistence boundary. Do not add another state machine/store. A local source needs an explicit availability state so move/delete does not erase Library or PlaylistItem identity. Roll back by retaining the old localStorage key until post-migration verification.
