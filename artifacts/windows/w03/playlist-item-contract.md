# PlaylistItem Contract

```text
PlaylistItem
- id: stable relation UUID
- playlist_id: Playlist.id
- track_id: LibraryTrack.id
- position: contiguous zero-based persisted order
- added_at: ISO timestamp
```

No title, artist, path, duration or other Track metadata is copied. Same Playlist + Track is unique by policy: repeated add returns `ALREADY_IN_PLAYLIST`. Unavailable Tracks remain valid references. Invalid playlist/track references return explicit domain results.
