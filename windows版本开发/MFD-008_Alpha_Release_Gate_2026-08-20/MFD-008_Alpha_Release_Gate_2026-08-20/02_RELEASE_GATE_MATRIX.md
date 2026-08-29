# MFD-008 Release Gate Matrix

| Gate | Required | Result |
|---|---:|---|
| RC Freeze | YES | |
| Clean Build | YES | |
| Installer | YES | |
| Fresh Install | YES | |
| First Launch | YES | |
| Auth | YES | |
| Library Authorization | YES | |
| Real Playback | YES | |
| Human Audible Check | YES | |
| Pause / Resume | YES | |
| Seek | YES | |
| Next / Previous | YES | |
| Manifest Expiry | YES | |
| Network Recovery | YES | |
| Normal Restart | YES | |
| Forced Kill Recovery | YES | |
| Corrupt State Recovery | YES | |
| Rapid Interaction | YES | |
| Single Instance | YES | |
| Tray / Background | YES | |
| Media Controls | TARGET | |
| Upgrade | YES | |
| Uninstall | YES | |
| Packaged Logging | YES | |
| Secret Audit | YES | |
| Electron Security | YES | |
| Update Boundary | YES | |
| Signing Status Known | YES | |
| Windows Compatibility | YES / truthful UNVERIFIED | |
| Resource Sanity | YES | |
| Release Artifacts | YES | |
| Rollback | YES | |

---

## Hard blockers

以下任何一项 FAIL 默认阻塞：

```text
Installer
Auth/Authorization
Real Playback
Human Audible Check
Security
Secret Audit
Restart/Recovery
Upgrade integrity
```
