# W06 Handoff

```text
W05_STATUS = PASS
W06_GATE = PASS
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```

W06 must reuse LibraryTrack/LibraryService, Playlist/PlaylistItem, PlaybackService and QueueService. If W06 adds search/sort views, it must explicitly pass the visible stable Track order when materializing a Library Queue; it must not make Queue the Library authority.

Favorites, history and browsing projections must reference stable Track IDs and must not copy or rebuild Track, Playlist, Playback or Queue truth.
