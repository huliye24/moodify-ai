# W04 Handoff Gate — Playback Core

W04 将建设真正稳定的播放核心，因此 W03 需要提供可靠的 Playlist 上下文。

## W04 Required

- [ ] W03_STATUS = PASS
- [ ] Playlist authority 唯一
- [ ] PlaylistItem relation 稳定
- [ ] Track authority 仍唯一
- [ ] Playlist ordering 持久化
- [ ] Playlist Track 可调用 existing Player
- [ ] unavailable Track 行为安全
- [ ] 删除 Playlist 不破坏 current Player
- [ ] restart 后 Playlist / ordering 正确
- [ ] 未创建正式 Queue authority
- [ ] W04 可读取：
  - current Track
  - ordered Playlist Tracks
  - source resolver

## W04 Can Now Build

```text
Play / Pause
Seek
Duration
Previous / Next
End-of-track
Error skip
Volume
Playback state synchronization
```

## W04 Must Not Rebuild

```text
Track
Library
Playlist
PlaylistItem
Persistence
```

## Gate

```text
W04_GATE = PASS | BLOCKED
```
