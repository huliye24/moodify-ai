# W07 Handoff

```text
W06_STATUS = PASS
W07_GATE = PASS
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```

W07 must reuse `LibraryTrack`, `LibraryService`, `LibraryExperienceService`, `projectLibrary`, `PlaylistService`, `PlaybackService` and `QueueService`. Track rows use stable `track.id`; shared callbacks already provide play, Play Next, append Queue, add Playlist, favorite and remove seams.

Context menus, drag/drop, multi-select, batch actions, confirmation and reveal-in-Explorer may extend these seams. Do not create alternate Library/Favorite/History collections, do not write search/sort order into Queue or Playlist, and do not record history from click intent.
