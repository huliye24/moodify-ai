# MFD-009 Minimal Telemetry Schema

## Principle

Collect only what helps answer Alpha product/reliability questions.

---

## Event

```json
{
  "event_name": "track_load_failure",
  "event_time": "2026-08-20T09:00:00Z",
  "app_version": "0.1.0-alpha.1",
  "install_id": "anon_xxx",
  "platform": "win32",
  "os_version": "Windows 11",
  "track_id": "trk_xxx",
  "error_code": "MEDIA_LOAD_FAILED"
}
```

---

## Allowed events

```text
app_start
app_ready
session_refresh_success
session_refresh_failure
track_load_success
track_load_failure
play
pause
seek
next
previous
manifest_refresh_success
manifest_refresh_failure
playback_error
app_exit
```

---

## Never Include

```text
Authorization
refresh token
service key
full signed URL
DB credentials
OSS secrets
raw audio
full personal library
microphone data
browser history
```
