# MFD-007 Acceptance Gate

## A. Installer

- [ ] Windows installer exists
- [ ] clean install works
- [ ] correct name/icon
- [ ] Start Menu works
- [ ] launch works
- [ ] uninstall works

## B. App identity

- [ ] package id stable
- [ ] exe stable
- [ ] version is single-source
- [ ] build commit recorded

## C. Runtime

- [ ] single instance
- [ ] no duplicate playback
- [ ] minimize behavior consistent
- [ ] close behavior consistent
- [ ] tray works
- [ ] background playback works
- [ ] quit fully exits

## D. Windows media integration

- [ ] play/pause
- [ ] next/previous
- [ ] product-safe metadata
- [ ] system/UI state synchronized

If current standard API cannot satisfy a requirement:
- [ ] evidence-based blocker documented
- [ ] no premature native addon

## E. Packaged reliability

- [ ] local-state restore
- [ ] session restore
- [ ] expired manifest recovery
- [ ] offline startup non-fatal
- [ ] packaged logging
- [ ] log redaction

## F. Update

- [ ] UpdateService boundary
- [ ] channel policy
- [ ] controlled feed
- [ ] update failure non-fatal
- [ ] first-run handling
- [ ] real auto-update disabled if release prerequisites absent

## G. Signing

One must be true:

- [ ] signed installer verified

OR

- [ ] unsigned internal Alpha explicitly marked
- [ ] public release blocked

## H. Release engineering

- [ ] reproducible build command
- [ ] lockfile
- [ ] artifact naming
- [ ] SHA256
- [ ] BUILD_INFO
- [ ] RELEASE_NOTES
- [ ] test evidence

## I. Upgrade

- [ ] old → new install path tested
- [ ] state migration works
- [ ] session behavior safe
- [ ] playback survives upgrade

## J. Security

- [ ] no service key
- [ ] no DB credential
- [ ] no OSS secret
- [ ] no signing secret
- [ ] no unsafe Electron setting
- [ ] no uncontrolled update origin

## K. Scope discipline

- [ ] no WASAPI
- [ ] no native audio
- [ ] no DSP/EQ
- [ ] no offline full library
- [ ] no new product complexity
- [ ] no public publishing without authorization

---

全部通过：

> **MFD-008 = GO**
