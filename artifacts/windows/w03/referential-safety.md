# Referential Safety

- Delete Playlist deletes only its PlaylistItems and Playlist.
- Remove PlaylistItem preserves Library Track and original file.
- Other playlists are unchanged.
- Deleting a playlist does not stop or mutate current playback.
- Unavailable Track and its PlaylistItem remain visible and ordered.
- W02 Library removal is now refused while any PlaylistItem references the Track, preventing dangling relations.
- No Playlist operation calls filesystem deletion.

Once all referencing PlaylistItems are removed, normal W02 non-destructive Library removal is available again.
