# W09 Handoff Gate — Windows Native Integration

W09 将把 Moodify 更深地接入 Windows。

## Required

- [ ] W08_STATUS = PASS
- [ ] playback state stable after restart
- [ ] Queue state stable after restart
- [ ] current Track stable
- [ ] window lifecycle stable
- [ ] desktop runtime identified
- [ ] native bridge security boundary stable
- [ ] abnormal exits do not corrupt core state
- [ ] no auto-play on startup

## W09 Will Build

```text
Media Keys
System Media Controls / SMTC
Taskbar integration
Tray
Single Instance
Open With / file open
File association
Lock-screen metadata where supported
Windows notifications only if useful
```

## W09 Must Reuse

```text
Playback authority
Track authority
Queue authority
Window lifecycle
Recovery hooks
```

## W09 Must Not Rebuild

```text
Player
Queue
Library
Playlist
Recovery persistence
```

## Gate

```text
W09_GATE = PASS | BLOCKED
```
