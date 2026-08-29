# Moodify Windows Beta Release Checklist

## Build
- [ ] version frozen
- [ ] production build passes
- [ ] no dev dependency
- [ ] installer generated
- [ ] SHA256 generated

## Install
- [ ] clean install
- [ ] first launch
- [ ] import
- [ ] play
- [ ] restart

## Upgrade
- [ ] previous build prepared
- [ ] upgrade install
- [ ] migrations pass
- [ ] data counts verified
- [ ] settings verified

## Uninstall
- [ ] uninstall pass
- [ ] integrations cleaned
- [ ] original audio preserved
- [ ] user-data policy verified
- [ ] reinstall pass

## Core Regression
- [ ] Library
- [ ] Playlist
- [ ] Playback
- [ ] Queue
- [ ] Search/Favorite/History
- [ ] Desktop Interaction
- [ ] Recovery
- [ ] Windows Native
- [ ] Cloud Bridge
- [ ] Settings

## Security
- [ ] no secrets
- [ ] native IPC safe
- [ ] path safety
- [ ] installer permissions
- [ ] logs privacy
- [ ] update seam safe

## Performance
- [ ] start time
- [ ] 1000 library
- [ ] 5000 search
- [ ] playback latency
- [ ] memory soak

## Offline
- [ ] launch
- [ ] local playback
- [ ] queue
- [ ] settings
- [ ] cloud failure safe

## Release Truth
- [ ] W10 claims audited
- [ ] known issues updated
- [ ] P0 = 0
- [ ] P1 = 0

## Signing
- [ ] signed and verified
or
- [ ] unsigned status explicitly accepted for this Beta

## Final
- [ ] artifact manifest complete
- [ ] WINDOWS_BETA_CANDIDATE = PASS
