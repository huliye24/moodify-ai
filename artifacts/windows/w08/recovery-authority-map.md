# Recovery Authority Map

| State | Authority | W08 action |
|---|---|---|
| durable Library/Playlist/Favorite/History | LocalStateStore | KEEP |
| session snapshot | LocalStateStore.recovery | ADD within same authority |
| Playback runtime | PlaybackService | RESTORE, never replace |
| Queue runtime | QueueService | RESTORE validated snapshot |
| navigation | renderer route state | CHECKPOINT stable IDs/enums |
| window | LocalState.window/main process | REPAIR restore/clamp |
| legacy playlist localStorage | W03 migration only | KEEP migration; no recovery writes |

Reader/writer is `RecoveryService` over the existing LocalStateStore. IPC is an allowlisted transport, not an authority.
