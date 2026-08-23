# Add Track Flow

```text
Library Track right-click or + action
-> choose canonical Playlist projection
-> playlist:addTrack IPC
-> PlaylistService.addTrack(playlist_id, track_id)
-> validate both authorities
-> idempotency check
-> append position
-> atomic persistence
-> refresh UI snapshot
```

Batch add is available through the same service/IPC contract and preserves input order. If there are no playlists, the interaction opens the existing minimal create dialog. Playlist playback resolves the referenced Library Track and calls the existing Player.
