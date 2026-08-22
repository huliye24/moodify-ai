# W09 Preflight

```text
W08_STATUS = PASS
W09_GATE = PASS
DESKTOP_RUNTIME = Electron + Chromium renderer + React
NATIVE_BRIDGE = context-isolated allowlisted preload/IPC
PLAYBACK_AUTHORITY = PlaybackService (W04)
QUEUE_AUTHORITY = QueueService (W05)
TRACK_AUTHORITY = LibraryTrack / LibraryService (W02)
WINDOW_LIFECYCLE = Electron main createWindow + W08 bounds restore/flush
SINGLE_INSTANCE_REALITY = requestSingleInstanceLock existed; second launch only focused window
MEDIA_CONTROL_REALITY = globalShortcut media keys existed; no system metadata/session projection
TRAY_REALITY = Electron Tray existed; no Next and stale playback label
OPEN_FILE_REALITY = MISSING
```

W08 recovery and W04/W05 authority artifacts passed. W09 replaces the broad global shortcut approach with the platform Media Session adapter.
