# W07 Preflight

```text
W06_STATUS = PASS
W07_GATE = PASS
TRACK_ROW_COMPONENT = LibraryPage / PlaylistDetail / QueuePanel
TRACK_ACTION_USE_CASES = PlaybackService + LibraryService + LibraryExperienceService
PLAYLIST_ACTION_USE_CASES = PlaylistService IPC
QUEUE_ACTION_USE_CASES = PlaybackService -> QueueService
IMPORT_USE_CASE = LibraryService.importPaths
FAVORITE_USE_CASE = LibraryExperienceService.setFavorite
REMOVE_LIBRARY_USE_CASE = LibraryService.remove
DESKTOP_RUNTIME = Electron + React + context-isolated preload
NATIVE_BRIDGE = allowlisted contextBridge/IPC only
```

No Canon or visual direction change.
