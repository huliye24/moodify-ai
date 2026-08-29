# W08 Handoff Gate — Recovery & Resilience

W08 将解决：

> 关闭、崩溃、重启后，Moodify 能不能回到一个可靠状态？

## Required

- [ ] W07_STATUS = PASS
- [ ] Track/Library stable
- [ ] Playlist stable
- [ ] Playback stable
- [ ] Queue stable
- [ ] Library views stable
- [ ] desktop interaction stable
- [ ] no interaction-created shadow state
- [ ] playback persistence seam exists
- [ ] queue persistence seam exists
- [ ] AppState/window/navigation reality identifiable

## W08 Will Build

```text
restore current Track
restore position
restore Queue
restore active Playlist/view
restore volume
restore window state
recover after abnormal exit
handle missing source after restart
safe schema/version recovery
```

## W08 Must Not Persist

```text
DOM refs
component instances
raw audio engine
callbacks
drag state
temporary context menu state
```

## Gate

```text
W08_GATE = PASS | BLOCKED
```
