# Moodify Windows W07 Implementation Report

```text
W07_STATUS = PASS
W08_GATE = PASS
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```

W07 connects native desktop input to existing W02-W06 use-cases. Library-derived views now use stable-ID single/Ctrl/Shift/Ctrl+A selection, double-click playback with the visible projection order, batch Playlist/Queue/Favorite/remove commands, internal Track-to-Playlist drag and concise context menus. Playlist Items, Queue Items and Playlists have scoped menus.

Explorer file drops use preload `webUtils.getPathForFile` and W02 import; folder recursion is intentionally unsupported. Explorer reveal accepts Track IDs only and calls `shell.showItemInFolder` after Library resolution. No unrestricted path/shell API is exposed.

Delete wording distinguishes Playlist, Queue and Library membership; no original audio deletion exists. Search reconciles visible selection, sort preserves stable IDs and view changes clear selection. Interaction feedback is limited to selection, drop highlight, menu and batch status.

Verification: typecheck PASS, lint PASS, 12/12 test files PASS, 123/123 tests PASS. Blockers: none. Unknown: packaged-window manual/visual run was not performed against the already-running Alpha instance.

Changed files: `src/shared/desktop-interaction.ts`, `src/shared/ipc-channels.ts`, `src/preload/index.ts`, `src/main/ipc/index.ts`, `src/vite-env.d.ts`, `src/renderer/components/player/MinimalPlayer.tsx`, `tests/unit/desktop-interaction.test.ts`.
