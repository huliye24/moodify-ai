# MFD-007 Windows Productization Test Matrix

## Install

- [ ] fresh install
- [ ] expected install location
- [ ] Start Menu
- [ ] shortcut if configured
- [ ] correct icon
- [ ] correct publisher metadata if signed
- [ ] launch

## Single instance

- [ ] launch once
- [ ] launch second time
- [ ] existing window focused
- [ ] no duplicate playback

## Window / tray

- [ ] minimize
- [ ] hide/close behavior
- [ ] tray restore
- [ ] tray play/pause
- [ ] tray quit
- [ ] no orphan background process after quit

## Background playback

- [ ] minimize while playing
- [ ] hide to tray while playing if policy
- [ ] switch applications
- [ ] lock screen if feasible

## Media controls

- [ ] play
- [ ] pause
- [ ] next
- [ ] previous
- [ ] metadata
- [ ] UI state sync

## Logs

- [ ] packaged log created
- [ ] size bounded
- [ ] no token
- [ ] no signed URL
- [ ] no auth header
- [ ] version present

## Update

- [ ] update disabled safely if not configured
- [ ] update check failure non-fatal
- [ ] channel correct
- [ ] feed URL controlled
- [ ] first-run condition handled
- [ ] mocked/staging update path verified

## Upgrade

- [ ] install old Alpha
- [ ] create local state
- [ ] install newer Alpha
- [ ] state survives/migrates
- [ ] session behavior correct
- [ ] playback still works

## Uninstall

- [ ] uninstall succeeds
- [ ] shortcuts removed
- [ ] running process handled
- [ ] secret session data cleared according to policy

## Security

- [ ] no service key
- [ ] no DB key
- [ ] no signing private key
- [ ] no prod secret
- [ ] contextIsolation retained
- [ ] nodeIntegration off
- [ ] update origin allowlisted
