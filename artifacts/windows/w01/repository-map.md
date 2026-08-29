# W01 Repository Map

Audit date: 2026-08-21. `CANON_CHANGE = NO`; `VISUAL_REDESIGN = NO`.

| Area | Actual path | Finding |
|---|---|---|
| Windows app root | `E:\moodify-desktop` | Independent directory; it has no `.git` metadata |
| Package manifest | `E:\moodify-desktop\package.json` | `moodify-desktop@0.1.0-alpha.4` |
| Stack | `package.json`, `forge.config.ts` | Electron 31 + React 18 + TypeScript 5 + Vite + Electron Forge + npm |
| Bootstrap | `src/main.ts` -> `src/main/index.ts` | Electron main process |
| Window | `src/main/window.ts` | One maximized `BrowserWindow` |
| Renderer | `src/renderer/main.tsx` -> `src/renderer/App.tsx` | React; no router; `#debug` selects diagnostic UI |
| Product UI | `src/renderer/components/player/MinimalPlayer.tsx` | Single minimal player surface |
| Player | `src/domain/playback/service.ts`, `engine.ts`, `types.ts` | `PlaybackService` owns queue; `ChromiumPlaybackEngine` owns one `HTMLAudioElement` |
| Cloud data | `src/services/api/client.ts`, `dto.ts` | Public BFF only; default `/api/v1/music` endpoint |
| Local import | `MinimalPlayer.tsx:187` | Browser file input and ephemeral `blob:` URLs |
| Persistence | `src/services/state/store.ts`; renderer `localStorage` | JSON state in Electron userData plus an unversioned playlist-name key |
| IPC | `src/shared/ipc-channels.ts`, `src/preload/index.ts`, `src/main/ipc/index.ts` | Allowlisted app/telemetry/support/media-key bridge; no library/file IPC |
| Tests | `tests/unit/*.test.ts`, `vitest.config.ts` | Unit tests only; no renderer E2E/user-journey tests |
| Packaging | `forge.config.ts` | Squirrel.Windows x64 installer |
| Update | `src/main/updater.ts` | Gated service; no verified signed production feed |
| Reused web | none | Desktop calls the same public BFF contract but does not embed `apps/music-web` |

The W01 task packet lives in the main repository, but the implementation being audited is the separate `E:\moodify-desktop` working directory. Earlier MFD-001 documents saying Desktop was absent describe the pre-implementation snapshot and do not override current filesystem evidence.
