# Windows Desktop Completion Sequence

```text
W01 现状审计 / 产品模型 / 开发冻结
↓
W02 Music Library
↓
W03 Playlist
↓
W04 Playback Core
↓
W05 Queue                            ← 当前包
↓
W06 Library Experience
↓
W07 Desktop Interaction
↓
W08 Recovery & Resilience
↓
W09 Windows Native Integration
↓
W10 Cloud Bridge
↓
W11 Settings & Audio Environment
↓
W12 Release Hardening
```

## W05 的位置

W04 回答：

> 这首歌怎样稳定播放？

W05 回答：

> 接下来播放哪一首？

当这两层分开之后，播放器才不会把：

```text
Playlist
Queue
Player
UI array
```

混成同一个东西。
