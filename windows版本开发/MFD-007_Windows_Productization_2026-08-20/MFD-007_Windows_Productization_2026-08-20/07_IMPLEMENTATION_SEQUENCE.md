# MFD-007 Implementation Sequence

## Step 1 — Gate

- [ ] MFD-006 GO
- [ ] repo clean
- [ ] packaging baseline known
- [ ] identity known
- [ ] signing status known

## Step 2 — Identity

- [ ] product name
- [ ] package id
- [ ] exe
- [ ] icon
- [ ] version source

## Step 3 — Installer

- [ ] maker
- [ ] metadata
- [ ] shortcut
- [ ] install
- [ ] uninstall
- [ ] Squirrel lifecycle if used

## Step 4 — OS behavior

- [ ] single instance packaged
- [ ] minimize/close policy
- [ ] tray
- [ ] background playback

## Step 5 — Media integration

- [ ] media metadata
- [ ] play/pause
- [ ] next/previous
- [ ] state synchronization

## Step 6 — Packaged reliability

- [ ] logging
- [ ] crash-safe boot
- [ ] secret redaction
- [ ] no dev server dependency

## Step 7 — Update boundary

- [ ] UpdateService
- [ ] channels
- [ ] feed allowlist
- [ ] disabled-safe state
- [ ] first-run handling

## Step 8 — Signing

- [ ] status
- [ ] configure if available
- [ ] verify signature if available
- [ ] otherwise mark internal-only

## Step 9 — Release engineering

- [ ] clean package
- [ ] artifact naming
- [ ] build info
- [ ] checksums
- [ ] release notes

## Step 10 — Product tests

- [ ] fresh install
- [ ] second launch
- [ ] tray
- [ ] media controls
- [ ] upgrade
- [ ] uninstall

## Step 11 — Security audit

- [ ] bundled files
- [ ] config
- [ ] secrets
- [ ] update origin
- [ ] Electron security flags

## Step 12 — Evidence / Gate

- [ ] evidence complete
- [ ] MFD-008 readiness
