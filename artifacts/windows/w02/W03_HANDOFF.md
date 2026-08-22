# W03 Handoff

```text
W02_STATUS = PASS
W03_GATE = PASS
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```

W03 must reuse:

- `LibraryTrack.id` as PlaylistItem foreign identity;
- `LocalStateStore` v2 as the persistence authority (advance its version for PlaylistItem);
- `LibraryService` for Track lookup/availability;
- `moodify-local://` resolver and existing `PlaybackService`.

W03 must not copy Track metadata into playlist rows, persist raw path arrays, introduce another store/player/queue, or delete relations when a Track becomes unavailable.

First recommended W03 change: migrate preserved `moodify.playlists` `{id,name}` records into a versioned playlist schema and add ordered `{playlist_id, track_id}` relations, with rollback and referential tests.
