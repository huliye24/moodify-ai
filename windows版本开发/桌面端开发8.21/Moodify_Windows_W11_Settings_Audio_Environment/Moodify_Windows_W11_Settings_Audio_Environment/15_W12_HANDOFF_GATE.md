# W12 Handoff Gate — Release Hardening

W12 是 Windows Alpha → Beta / 可分发产品的收口包。

## Required

- [ ] W11_STATUS = PASS or acceptable PARTIAL
- [ ] W12_GATE = PASS
- [ ] Track/Library stable
- [ ] Playlist stable
- [ ] Playback stable
- [ ] Queue stable
- [ ] Library Experience stable
- [ ] Desktop Interaction stable
- [ ] Recovery stable
- [ ] Windows Native integration stable
- [ ] Cloud Bridge claims truthful
- [ ] Settings schema stable
- [ ] data/cache locations known
- [ ] installer-required native capabilities documented

## W12 Will Build

```text
Installer
Uninstaller
Upgrade
Schema migration
File association registration
Startup registration
Logging
Crash diagnostics
Performance regression
Security regression
Packaging
Signing seam
Update seam
Release checklist
Windows Alpha/Beta designation
```

## W12 Must Not

- redesign product
- add major new features
- add new business authorities
- overclaim cloud
- expose secrets
- silently wipe user data

## Gate

```text
W12_GATE = PASS | BLOCKED
```
