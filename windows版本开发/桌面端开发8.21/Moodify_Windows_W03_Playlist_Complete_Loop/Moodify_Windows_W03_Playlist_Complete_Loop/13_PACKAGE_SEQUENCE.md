# Windows Desktop Completion Sequence

```text
W01 现状审计 / 产品模型 / 开发冻结
↓
W02 Music Library
↓
W03 Playlist                       ← 当前包
↓
W04 Playback Core
↓
W05 Queue
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

## W03 为什么在 W04 之前

因为 Playback Core 需要稳定知道：

```text
当前 Track 是谁
来自哪个长期集合
这个集合的顺序是什么
```

如果 Playlist 本身还只是临时数组，W04 的 previous / next / ended behavior 就会再次建立一套隐式列表逻辑。

所以顺序是：

```text
Track
→ Library
→ Playlist
→ Playback
→ Queue
```
