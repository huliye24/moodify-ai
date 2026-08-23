# Migration Matrix

| Component | Old | New | Migration | Fallback / verification |
|---|---:|---:|---|---|
| LocalState | 0–5 | 6 | sequential, idempotent | `.vN.bak` + LKG; unit tested |
| Library/Playlist/Favorite/History | prior fields | 6 | sanitize and preserve valid records | relation tests pass |
| Queue/Recovery | absent/1 | 1 | repair valid references | silent empty session for invalid/future data |
| Settings | absent/1 | 1 | safe defaults + validation | reset settings only |
| CloudPreparation | absent | absent | none | W10 BLOCKED; no invented state |
| File association | none | pending | not implemented | Beta blocker |
| Startup | OFF | OFF | none | forced OFF |
| Cache | none | none | none | no durable deletion |

143 unit tests verify migrations and no intended silent wipe; real installed-version upgrade comparison remains outstanding.
