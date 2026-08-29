# Queue Source Policy

Playlist and Library materialization use `SNAPSHOT` policy. PlaylistItems are sorted by persisted position, then their Track IDs become independent QueueItems. Later Playlist edits do not alter the active Queue; Queue reorder/remove never alter Playlist.

The current Library UI has a stable visible canonical order, so direct Library playback materializes that supplied order with the selected Track as cursor. Manual Play Next/append operations add independent QueueItems.
