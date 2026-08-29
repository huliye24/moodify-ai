# W08 Handoff

```text
W07_STATUS = PASS
W08_GATE = PASS
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```

W08 may persist current Track, playback position, volume, Queue snapshot, active Library/Playlist view and window/navigation state through existing authority seams. It must not persist selected IDs, anchors, focus, open context menus, drag/drop highlights, batch messages, DOM/File objects, callbacks or component instances.

Reuse LocalStateStore schema migration, PlaybackService snapshot, QueueService snapshot and stable Track/Playlist IDs. Do not let interaction state become recovery authority.
