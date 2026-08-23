# Moodify Windows Desktop Completion — W05 Queue 播放队列

**Package ID:** `MFY-WIN-W05-QUEUE-001`  
**日期：** 2026-08-21  
**阶段：** Windows Desktop Completion / 05 of 12  
**任务类型：** Core implementation / Playback Queue  
**CANON_CHANGE：** `NO`  
**VISUAL_REDESIGN：** `FORBIDDEN`  
**前置依赖：** W04 `W05_GATE = PASS`  
**下一包：** W06 — Library Experience 音乐管理体验

---

## 1. W05 的目标

W05 解决的是：

> “现在正在听什么，接下来听什么，以及用户如何控制接下来的播放顺序。”

建立完整链路：

```text
Library / Playlist / User Action
→ Queue Materialization
→ Current Queue Item
→ Play Now
→ Play Next
→ Append
→ Reorder
→ Remove
→ Ended Advance
→ Error Advance
→ Clear
```

W05 完成后，Moodify Windows 才真正具备连续听歌能力。

---

## 2. 强制前置门槛

执行前必须读取：

```text
artifacts/windows/w04/W04_IMPLEMENTATION_REPORT.md
artifacts/windows/w04/playback-authority.md
artifacts/windows/w04/playback-state-contract.md
artifacts/windows/w04/ended-error-policy.md
artifacts/windows/w04/W05_HANDOFF.md
```

必须确认：

```text
W04_STATUS = PASS
W05_GATE = PASS
```

否则：

```text
W05_STATUS = BLOCKED
```

禁止在 Playback authority 未稳定时自行绕开 Player 建第二套播放逻辑。

---

## 3. 核心边界

### Queue 是短期播放意图

```text
Playlist = 长期组织
Queue = 当前会话播放顺序
```

Queue 可以由 Playlist 生成，但不能反向覆盖 Playlist 顺序。

### QueueItem 引用 Track

推荐：

```text
Queue
 ├── current_index
 └── QueueItem
       └── track_id → Track
```

QueueItem 不复制 Track metadata 作为第二套 truth。

### Playback 仍归 W04

W05 决定：

```text
next Track is which
```

W04 决定：

```text
how this Track is loaded / played
```

因此：

```text
Queue = sequencing authority
Playback = playback authority
```

---

## 4. 本包要做

- 唯一 Queue authority
- 从 Playlist 生成 Queue
- 从 Library 直接播放生成 Queue context
- current Queue item
- Play Now
- Play Next
- Add to Queue / Append
- Previous / Next 与 Queue 接轨
- Ended 自动前进
- Error safe-skip
- Queue remove
- Queue reorder
- Queue clear
- current item 删除行为
- duplicate Track policy
- Queue 与 Playlist 解耦
- UI 最小 Queue panel / popover
- tests
- evidence
- 为 W08 恢复留 persistence seam

### 不做

- Queue 跨设备同步
- Cloud playlist sync
- social queue
- party mode
- smart recommendation
- autoplay recommendation
- shuffle/repeat 完整产品化
- crossfade
- DSP
- skin/community
- Windows media keys
- release hardening

---

## 5. 最终用户行为

至少稳定完成：

```text
打开歌单
→ 播放第一首
→ 自动生成 Queue
→ 下一首
→ 上一首
→ 右键另一首“下一首播放”
→ Queue 更新
→ 调整队列顺序
→ 当前歌曲结束
→ 自动播放新的下一首
```

并且：

```text
从 Queue 删除歌曲
≠
从 Playlist 删除
≠
从 Library 删除
≠
删除原文件
```
