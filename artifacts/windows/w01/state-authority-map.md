# W01 State Authority Map

| Domain | Current source of truth | Writer | Reader | Durable | Conflict / classification |
|---|---|---|---|---|---|
| Track (cloud) | BFF `Track` DTO | Public BFF | renderer + PlaybackService | Server-side, outside Desktop | KEEP as cloud catalogue identity |
| Track (local) | React `tracks` array | `handleAddSongs` | MinimalPlayer | No | Generated time/index ID; MIGRATE |
| Library | None | None | None | No | MISSING |
| Playlist | `localStorage['moodify.playlists']` array of `{id,name}` | MinimalPlayer | MinimalPlayer | Yes, renderer-local | Competes with documented `LocalStateStore` claim of “all” durable state |
| PlaylistItem | None | None | None | No | MISSING; this is the add-to-playlist break |
| Queue | `PlaybackQueue` inside `PlaybackService` | renderer calls | PlaybackService | No | Single runtime authority; KEEP then extend |
| PlaybackSession | engine state + renderer mirrors | audio events | service/UI | No | UI mirrors are subscribers, not a second player authority |
| Favorite | BFF methods only | API client | no product UI | Server if used | PLACEHOLDER in Desktop |
| History | BFF methods/play-event reporting | API client/UI events | no history UI | Server if authenticated | PARTIAL |
| AppState | `LocalStateStore` JSON | main process | main process | Yes | Not exposed to renderer; playback fields are not wired to player |
| CloudTrack | public BFF | server | BffClient | Yes, remote | KEEP |

Two persistence mechanisms exist: main-process versioned JSON and renderer `localStorage`. W02 must converge through the existing main-process store/IPC boundary, not introduce a third store.
