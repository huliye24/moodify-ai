# Desktop Release 001 — Windows RC Packaging Report

## Scope

This change adds release engineering for the existing Moodify Studio Electron shell. It does not change product semantics, Core DSP, pipeline gating, Android identity, or Android release behavior.

`CANON_CHANGE = NO`

## Build record

| Field | Value |
| --- | --- |
| Base SHA | `01edc902d72c15010dd86390dc0511fc03fb6323` |
| Branch | `codex/desktop-release-001` |
| Product | Moodify Studio |
| Version | `1.0.0-rc.1` |
| Electron | `^33.0.0` |
| electron-builder | `26.15.3` |
| CI Node.js | 20 |
| Platform | Windows 10/11 x64 |
| Targets | NSIS installer; portable EXE |
| Signing | Unsigned |
| Runtime mode | External |

## Packaging decisions

`asar` is disabled for RC1. The desktop process executes Python scripts, loads the native `node-pty` runtime, and resolves the platform-specific `@openai/codex` executable. Keeping the application tree unpacked makes those paths real filesystem paths and is safer than an incomplete `asarUnpack` policy.

Dependency rebuilding is disabled for packaging because `node-pty` 1.1.0 ships its supported Windows x64 prebuild in the npm package. That prebuild was loaded and exercised under Electron 33 (`ELECTRON_RUN_AS_NODE=1`) by spawning `cmd.exe`; forcing electron-builder to run `node-gyp` would add an unnecessary Visual Studio Build Tools dependency and replace the vendor prebuild.

The tracked `moodify-desktop/renderer/assets/moodify_icon.ico` is a deterministic multi-resolution conversion of `brand/assets/moodify-symbol.png`. Tracking it removes image-tool variability from Windows CI and gives electron-builder a stable Windows icon source; it is not a redesign. It lives in the authoritative desktop asset tree rather than a generated `build/` directory, in accordance with the repository structure guard.

The existing Android workflow remains separate. Its `v*` tag pattern does not match the desktop namespace `desktop-v*`.

## Expected artifacts

| Artifact | Purpose |
| --- | --- |
| `Moodify_Studio_1.0.0-rc.1_Setup_x64.exe` | NSIS installer |
| `Moodify_Studio_1.0.0-rc.1_Portable_x64.exe` | Portable application |
| `RELEASE_MANIFEST.json` | Version, commit, runtime boundary, sizes and hashes |
| `SHA256SUMS.txt` | SHA-256 verification for both executables and the manifest |

Local verification at base commit produced:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `Moodify_Studio_1.0.0-rc.1_Setup_x64.exe` | 189,784,303 | `833a2bf95c383748e9f7a97e6e898a556ec454eb0ed6b99ad759e2abce2a0aa9` |
| `Moodify_Studio_1.0.0-rc.1_Portable_x64.exe` | 189,552,727 | `5b179726e257959c933d470d5f04a9fa711800eeb15771ec9ce8d6dd743d8a3b` |

CI regenerates sizes and hashes from its own exact build and commit. The local values are evidence for this verification run, not promised byte-for-byte CI output.

## Verification record

Local verification completed:

- `npm ci`: pass
- `npm test`: pass — contracts pass; pipeline 33/33; Studio 21/21
- Electron 33 `node-pty` prebuild smoke: pass — spawned `cmd.exe`
- `npm run pack:win`: pass
- `npm run dist:win`: pass
- PE header and non-zero-size checks: pass for both EXEs
- release manifest and checksum generation: pass
- Authenticode boundary: confirmed `NotSigned` for both EXEs
- `python scripts/check_repo_structure.py`: pass — 1,558 tracked files, 5 checks
- `git diff --check`: pass

## Packaged runtime inspection

The unpacked application at `dist-electron/win-unpacked/resources/app` contains:

- Electron entrypoint `src/main.js`: present
- renderer entrypoint and assets: present
- `scripts/dsp_separate.py`: present
- `scripts/midi_to_musicxml.py`: present
- `node-pty/prebuilds/win32-x64/pty.node` and `conpty.node`: present
- `@openai/codex-win32-x64/.../codex.exe`: present
- filesystem path compatibility: confirmed; `asar: false` leaves `__dirname/../scripts` and `__dirname/../node_modules` as real paths under `resources/app`

## Runtime boundary and limitations

The EXE contains the desktop shell, not a complete standalone Python audio environment. Full-pipeline use requires Python 3.10–3.12, importable Moodify Core 1.0.0-rc.1, and FFmpeg/FFprobe where required. Basic Pitch and music21 remain optional external dependencies. Quick separation remains preview-grade, and machine-generated MIDI remains evidence rather than ground truth.

## Manual check

`HUMAN_CHECK_REQUIRED`

The PR artifact must be installed and launched on Windows before any release tag is created. The human check must cover installer launch, window/icon rendering, real-audio Detect and Diagnose, quick separation, restart, portable launch, and uninstall. Exercise MIDI, Plan, and Finish when the local external runtime permits it.

The release tag `desktop-v1.0.0-rc.1` remains forbidden until PR #36, PR #37, and the desktop release PR are merged to `main`, and the manual Windows check passes.
