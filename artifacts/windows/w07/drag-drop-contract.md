# Drag & Drop Contract

Explorer `File` objects are converted with Electron `webUtils.getPathForFile` in preload, then sent through the allowlisted `library:importPaths` IPC to W02 `LibraryService.importPaths`. Single, multiple, duplicate, mixed invalid, Chinese, spaces and Unicode paths inherit W02 validation/result semantics. Rapid drops are synchronous main-process operations.

Folder recursion is `NOT_SUPPORTED_IN_W07`; a directory cannot pass the audio file importer. Renderer receives no general filesystem API.

Internal Track drags carry only JSON stable IDs under `application/x-moodify-track-ids`. Playlist drop targets call W03 `addTracks`; highlight is temporary and invalid targets do not accept the MIME type. No Playlist reorder or Queue mutation occurs.
