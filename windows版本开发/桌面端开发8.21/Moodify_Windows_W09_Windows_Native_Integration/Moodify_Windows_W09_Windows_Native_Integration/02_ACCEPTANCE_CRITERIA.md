# W09 Acceptance Criteria

## Preflight
- [ ] W08_STATUS = PASS
- [ ] W09_GATE = PASS
- [ ] actual runtime known
- [ ] native bridge known
- [ ] W04 Playback reused
- [ ] W05 Queue reused
- [ ] W08 Recovery reused

## Media Controls
- [ ] Play
- [ ] Pause
- [ ] Toggle
- [ ] Previous
- [ ] Next
- [ ] background safe
- [ ] no Track safe
- [ ] rapid input stable
- [ ] no second player

## System State / Metadata
- [ ] playing/paused projection
- [ ] title
- [ ] artist
- [ ] album if available
- [ ] Unicode
- [ ] W06 fallback
- [ ] track-switch update
- [ ] no path/internal-state leakage
- [ ] system session cleared on quit

## Single Instance
- [ ] one primary
- [ ] second launch handoff
- [ ] explicit launch activates primary
- [ ] file args handed off
- [ ] rapid launches safe
- [ ] no concurrent persistence writers

## Open File
- [ ] one file
- [ ] multiple files
- [ ] deterministic order
- [ ] duplicate safe
- [ ] unsupported safe
- [ ] W02 import reused
- [ ] W05/W04 playback path reused
- [ ] Chinese/space/Unicode paths safe

## File Association
- [ ] extensions from real capability
- [ ] installer needs documented
- [ ] unregister plan
- [ ] upgrade plan
- [ ] user default-app choice respected
- [ ] no forced hijack

## Tray / Taskbar
- [ ] only if supported/useful
- [ ] Open Moodify
- [ ] Play/Pause if implemented
- [ ] Next if implemented
- [ ] Quit flushes W08 state
- [ ] no ghost tray icon
- [ ] Close semantics unchanged unless explicitly configured

## Security
- [ ] narrow native adapter
- [ ] IPC allowlist
- [ ] structured payload
- [ ] safe argv parsing
- [ ] no shell string concatenation
- [ ] no arbitrary command execution
- [ ] metacharacter paths tested

## Regression
- [ ] Library
- [ ] Playlist
- [ ] Playback
- [ ] Queue
- [ ] Library Experience
- [ ] Desktop Interaction
- [ ] Recovery

## PASS

只有“Windows 控制 Moodify，但不成为另一套 Moodify”成立，才允许：

```text
W09_STATUS = PASS
W10_GATE = PASS
```
