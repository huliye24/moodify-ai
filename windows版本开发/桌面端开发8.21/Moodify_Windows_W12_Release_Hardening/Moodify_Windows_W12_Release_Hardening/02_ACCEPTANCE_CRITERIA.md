# W12 Acceptance Criteria

## A. Scope Freeze
- [ ] no major new feature
- [ ] no new business authority
- [ ] no visual redesign
- [ ] only release blocker fixes

## B. Build
- [ ] production build works
- [ ] no dev server
- [ ] no localhost dependency
- [ ] no developer machine absolute path
- [ ] no debug bridge
- [ ] version/build identity consistent

## C. Installer
- [ ] installs cleanly
- [ ] app launches
- [ ] proper app identity/icon
- [ ] uninstall entry
- [ ] no unnecessary admin privilege
- [ ] no forced startup
- [ ] no forced default-app hijack

## D. Uninstall
- [ ] app files removed
- [ ] integrations cleaned
- [ ] user-data policy explicit
- [ ] original music never deleted
- [ ] reinstall behavior verified

## E. Upgrade / Migration
- [ ] old build → candidate tested
- [ ] Track count preserved
- [ ] Playlist count preserved
- [ ] PlaylistItem count preserved
- [ ] Favorites preserved
- [ ] History preserved
- [ ] Settings migrated
- [ ] Recovery migrated
- [ ] Cloud refs preserved
- [ ] migration idempotent
- [ ] no silent wipe

## F. Downgrade
- [ ] policy explicit
- [ ] unsafe downgrade blocked or detected
- [ ] no corruption by old schema reader

## G. Native Integrations
- [ ] file associations install/uninstall safely
- [ ] startup registration respects setting
- [ ] single instance survives upgrade
- [ ] tray/media integration survives install lifecycle

## H. Logging / Crash
- [ ] production logs
- [ ] version/build in logs
- [ ] migration errors logged
- [ ] crash artifact or equivalent
- [ ] no secret leakage
- [ ] crash-loop protection

## I. Performance
- [ ] cold start baseline
- [ ] warm start baseline
- [ ] 1000 Track render
- [ ] 5000 Track search
- [ ] playback start latency
- [ ] next-track latency
- [ ] memory soak
- [ ] no release-blocking regression

## J. Security
- [ ] no service/admin secret in client
- [ ] native IPC reviewed
- [ ] path handling reviewed
- [ ] cloud auth reviewed
- [ ] logs reviewed
- [ ] installer permissions reviewed
- [ ] update seam safe
- [ ] no arbitrary command execution

## K. Offline
- [ ] launch offline
- [ ] Library offline
- [ ] Playlist offline
- [ ] local Playback offline
- [ ] Queue offline
- [ ] Settings offline
- [ ] Cloud failure does not block app

## L. Cloud Claims
- [ ] W10 actual status reflected
- [ ] partial not described as full
- [ ] internal pipeline not exposed
- [ ] unsupported cloud capability not marketed in build

## M. Clean Machine
- [ ] no repo dependency
- [ ] no local development tool dependency
- [ ] install/launch/import/play/restart verified

## N. Release Artifacts
- [ ] installer produced
- [ ] SHA256 produced
- [ ] version recorded
- [ ] build commit recorded
- [ ] known issues recorded
- [ ] release checklist completed

## O. Beta Gate

必须：

```text
P0 = 0
P1 = 0
```

并且核心闸门全部 PASS，才允许：

```text
WINDOWS_BETA_CANDIDATE = PASS
```
