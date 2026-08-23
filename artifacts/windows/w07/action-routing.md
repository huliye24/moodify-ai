# Action Routing

Library-derived rows use one callback surface: play, Play Next, append Queue, add Playlist, favorite/unfavorite, reveal and remove Library. Playlist/Queue add only collection-scoped remove/play commands. UI never edits durable state arrays.

```text
PLAY -> PlaybackService
PLAY_NEXT / ADD_TO_QUEUE -> PlaybackService -> QueueService
ADD_TO_PLAYLIST -> PlaylistService IPC
FAVORITE / UNFAVORITE -> LibraryExperienceService IPC
REVEAL -> LibraryService track resolver -> Electron shell.showItemInFolder
REMOVE_LIBRARY -> LibraryService IPC
```
