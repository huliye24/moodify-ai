# Current Playlist Reality

Before W03, `MinimalPlayer.tsx` loaded and wrote `localStorage['moodify.playlists']` records containing only `{id,name}`. Creation existed; rename, delete, detail, add/remove Track, ordering and relation persistence did not. Sidebar playlist buttons had no action. There was no Playlist domain type, service, IPC or automated test.

This exactly confirms the W01 root cause: Add Track stopped before the UI event because `PlaylistItem` had never been modeled.
