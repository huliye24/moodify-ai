# W11 Acceptance Criteria

## A. Preflight
- [ ] W10_STATUS = PASS or PARTIAL
- [ ] W11_GATE = PASS
- [ ] current settings reality known
- [ ] AppState authority known
- [ ] output capability audited
- [ ] tray/startup/cache/storage capability known

## B. Settings Authority
- [ ] one Settings authority
- [ ] schema version
- [ ] defaults
- [ ] validation
- [ ] migration
- [ ] corruption fallback
- [ ] no Track/Queue/Playback duplication

## C. Output Device
- [ ] capability truthfully classified
- [ ] selector only if real support
- [ ] System Default available
- [ ] missing device fallback
- [ ] hotplug safe
- [ ] restart safe
- [ ] no 100% volume jump

## D. Volume / Autoplay
- [ ] restore-volume preference
- [ ] safe default if restore off
- [ ] app launch never auto-plays by default
- [ ] explicit Open With policy preserved
- [ ] cloud READY does not surprise-play

## E. Close / Tray
- [ ] option only if tray supported
- [ ] default Close=Quit
- [ ] minimize-to-tray optional
- [ ] explicit Quit always quits
- [ ] W08 flush on quit

## F. Startup
- [ ] only if supported
- [ ] default OFF
- [ ] no autoplay on startup
- [ ] installer dependency documented if needed

## G. Cache
- [ ] cache taxonomy explicit
- [ ] durable data separated
- [ ] size real
- [ ] clear cache safe
- [ ] original files untouched
- [ ] Library/Playlist/Favorite/History preserved

## H. Storage
- [ ] original music never silently moved
- [ ] cache target validated
- [ ] permission failure safe
- [ ] migration verified
- [ ] rollback on failure
- [ ] app-data relocation deferred unless safely supported

## I. Cloud Preferences
- [ ] only W10 verified capabilities exposed
- [ ] Manual default
- [ ] no service secret
- [ ] no provider/internal pipeline controls
- [ ] local fallback preserved

## J. Network
- [ ] only real Windows-relevant controls exposed
- [ ] no fake “Wi-Fi only” if network type unavailable
- [ ] metered policy only if supported
- [ ] background refresh bounded

## K. Reset
- [ ] reset settings only
- [ ] confirmation
- [ ] Library preserved
- [ ] Playlist preserved
- [ ] Favorites/History preserved
- [ ] original files preserved

## L. UI
- [ ] one small settings page
- [ ] unsupported settings hidden
- [ ] no engineering dashboard
- [ ] no DSP/Ear settings
- [ ] no visual redesign

## M. Regression
- [ ] W02-W10 flows
- [ ] recovery
- [ ] native integration
- [ ] cloud bridge
- [ ] no new authority conflicts

## PASS Rule

只有“少量真实设置 + 安全默认 + 不破坏主链”成立，才允许：

```text
W11_STATUS = PASS
W12_GATE = PASS
```
