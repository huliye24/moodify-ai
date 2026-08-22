# W08 Preflight

```text
W07_STATUS = PASS
W08_GATE = PASS
APP_STATE_AUTHORITY = LocalStateStore/local-state.json
PLAYBACK_SNAPSHOT_SEAM = PlaybackService.getPlaybackSnapshot()
QUEUE_SNAPSHOT_SEAM = PlaybackService.getQueueSnapshot() / QueueService.snapshot()
PERSISTENCE_TECH = versioned human-readable JSON, temp + atomic rename
WINDOW_STATE_CURRENT_REALITY = persisted but previously not restored; window always maximized
CRASH_RECOVERY_CURRENT_REALITY = atomic temp rename existed; no LKG fallback
SCHEMA_VERSION_CURRENT_REALITY = LocalState v4 before W08
```

W04/W05 persistence seam documents and W07 handoff were read. Gate passed.
