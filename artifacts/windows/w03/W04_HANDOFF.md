# W04 Handoff

```text
W03_STATUS = PASS
W04_GATE = PASS
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
QUEUE_AUTHORITY_NOT_CREATED = YES
```

W04 must reuse `LibraryTrack`, `Playlist`, `PlaylistItem`, `LocalStateStore` v3, `LibraryService` source resolution and the existing `PlaybackService`/engine. Ordered playlist context is `playlistItems` sorted by persisted `position`, joined to Library Tracks by `track_id`.

W04 must not rebuild Track, Library, Playlist, PlaylistItem or persistence. Playlist mutation remains independent from the current playback session.
