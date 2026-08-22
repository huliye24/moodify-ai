# Playback State Contract

Statuses remain `IDLE`, `LOADING`, `READY`, `PLAYING`, `PAUSED`, `ENDED`, `ERROR`.

- Every load increments generation, clears error and position, and preserves selected Track identity.
- Position and volume are clamped in the authority projection.
- Track-scoped ended/error/load events whose `trackId` is not current are ignored.
- ERROR retains current Track and typed evidence.
- ENDED retains Track and final duration position.
- Context is `LIBRARY` or `PLAYLIST` plus an optional stable ID; it is not a Queue.
