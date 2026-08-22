# W02 Preflight

```text
W01_STATUS = PASS
W02_GATE = PASS
TRACK_AUTHORITY = Cloud BFF Track for cloud sources; LocalStateStore v2 LibraryTrack for local sources
LIBRARY_AUTHORITY = LocalStateStore v2 library.tracks
PERSISTENCE_AUTHORITY = <Electron userData>/moodify/local-state.json
PLAYER_AUTHORITY = PlaybackService + PlaybackQueue + ChromiumPlaybackEngine
MIGRATION_REQUIRED = YES (v1 -> v2; playlist-name localStorage preserved for W03)
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```

Implementation root: `E:\moodify-desktop`. The directory has no `.git`, so changes are evidenced by file paths and tests rather than a Desktop commit SHA.
