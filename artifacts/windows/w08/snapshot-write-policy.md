# Snapshot Write Policy

- Track/load completion and PAUSED/READY/ERROR: checkpoint.
- Position while playing: 10-second interval, not every timeupdate.
- Queue materialize/add/reorder/remove/clear: UI action seam checkpoints; interval is fallback.
- Volume change: checkpoint after clamped command.
- Navigation/view/Playlist change: effect checkpoint.
- Window move/resize: existing LocalStateStore 2-second debounce.
- Graceful exit: main-process `before-quit` calls synchronous `flush()`.

Recovery writes share LocalStateStore's 2-second bounded debounce except explicit graceful flush.
