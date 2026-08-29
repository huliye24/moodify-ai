# Library Authority

The sole durable local Library authority is `LocalStateStore.library.tracks` in schema v2. Renderer arrays are projections loaded through allowlisted IPC and are not persisted independently.

Main process responsibilities:

- native multi-file selection;
- validation, normalized-source dedupe and metadata fallback;
- atomic persistence and availability refresh;
- non-destructive remove;
- Track-ID-to-source resolution.

Renderer responsibilities:

- request imports/list/removal;
- render a minimal title/artist/availability list;
- pass resolved Library Track sources to the existing `PlaybackService`.

The old `moodify.playlists` localStorage key is deliberately untouched. W03 can migrate playlist names and create relations against stable W02 Track IDs.
