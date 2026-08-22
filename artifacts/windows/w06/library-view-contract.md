# Library View Contract

`LibraryService.list()` and `LocalState.library.tracks` remain the only Library truth. All Songs, Recently Added, Recently Played, Favorites and search results are `projectLibrary(...)` outputs containing references to existing stable Track IDs.

Pipeline: `Library authority -> base view -> query filter -> deterministic sort -> render`. Search and sort never write Library, Playlist or Queue order. A visible projected order is passed explicitly into Playback/Queue when a track is played.
