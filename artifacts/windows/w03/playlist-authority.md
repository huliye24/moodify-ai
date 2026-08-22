# Playlist Authority

The unique authority is LocalState schema v3:

- `playlists: Playlist[]`
- `playlistItems: PlaylistItem[]`

`PlaylistService` is the only mutation boundary. Renderer state is a read projection obtained over allowlisted IPC. Create, rename, delete, add/batch-add, remove and reorder all flush atomically through the existing `LocalStateStore`; no new persistence system or Queue authority was created.

Duplicate playlist names are allowed and distinguished by stable UUID. Names are trimmed, non-empty and limited to 100 characters.
