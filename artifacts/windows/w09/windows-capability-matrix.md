# Windows Capability Matrix

| Capability | Status | Implementation/decision |
|---|---|---|
| media keys | SUPPORTED_WITH_ADAPTER | Chromium Media Session action handlers |
| system media controls | SUPPORTED_WITH_ADAPTER | `navigator.mediaSession` |
| playback state projection | SUPPORTED | playing/paused/none |
| title/artist/album | SUPPORTED | Track authority + W06 fallback |
| timeline/seek | SUPPORTED_WITH_ADAPTER | position state + seekto → Playback.seek |
| previous/next | SUPPORTED | Media Session/tray → PlaybackService → Queue |
| tray | SUPPORTED | Open, Play/Pause, Next, Quit |
| taskbar identity | SUPPORTED | existing executable metadata/icon/window activation |
| single instance | SUPPORTED | Electron instance lock |
| second-instance args | SUPPORTED | structured argv array, no string splitting |
| open file | SUPPORTED_WITH_ADAPTER | W02 import → stable Track IDs → W05/W04 |
| file association registration | INSTALLER_REQUIRED | deferred to W12 |
| lock-screen metadata | SUPPORTED_WITH_ADAPTER | OS-dependent Media Session projection |
| artwork | RUNTIME_BLOCKED | no reliable canonical artwork asset; omitted |
