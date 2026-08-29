# W09 Handoff

```text
W08_STATUS = PASS
W09_GATE = PASS
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```

After boot, PlaybackService owns a safe READY/ERROR current Track, QueueService owns the repaired Queue, and no audio auto-starts. Window lifecycle, single-instance, tray and media-key hooks remain in main. Native bridge remains context-isolated and allowlisted.

W09 may integrate SMTC/media controls, taskbar, file-open/association and tray against Playback/Queue snapshots and existing lifecycle hooks. It must not rebuild or bypass Player, Queue, Library or Recovery persistence, and must not turn restored `last_status = PLAYING` into startup autoplay.
