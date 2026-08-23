# Moodify Windows Desktop Completion — W08 Recovery & Resilience 状态恢复与韧性

**Package ID:** `MFY-WIN-W08-RECOVERY-RESILIENCE-001`  
**日期：** 2026-08-21  
**阶段：** Windows Desktop Completion / 08 of 12  
**任务类型：** Reliability / State Recovery / Resilience  
**CANON_CHANGE：** `NO`  
**VISUAL_REDESIGN：** `FORBIDDEN`  
**前置依赖：** W07 `W08_GATE = PASS`  
**下一包：** W09 — Windows Native Integration 系统融合

---

## 1. W08 的目标

W08 解决：

> Moodify 关闭、重启、异常退出之后，用户之前的听歌状态还能不能安全回来？

本包不是做“保存所有东西”，而是建立一套明确、有限、可靠的恢复边界：

```text
Runtime State
→ Snapshot
→ Persist
→ Exit / Crash
→ Restart
→ Validate
→ Restore
→ Safe Playback State
```

目标是：

```text
重启后
→ 音乐库还在
→ 歌单还在
→ Queue 还在
→ 当前歌曲还在
→ 进度大致还在
→ 音量还在
→ 上次页面/窗口状态可恢复
→ 但不会突然自动出声
```

---

## 2. 强制前置门槛

执行前必须读取：

```text
artifacts/windows/w07/W07_IMPLEMENTATION_REPORT.md
artifacts/windows/w07/W08_HANDOFF.md

artifacts/windows/w04/playback-persistence-seam.md
artifacts/windows/w05/queue-persistence-seam.md
```

必须确认：

```text
W07_STATUS = PASS
W08_GATE = PASS
```

否则：

```text
W08_STATUS = BLOCKED
```

---

## 3. W08 的核心原则

### 3.1 Restore State ≠ Auto Play

默认规则：

```text
restore current Track
restore position
restore Queue
restore context
restore volume
but
DO NOT AUTO START AUDIO
```

重启应用后不应突然播放声音。

### 3.2 只持久化可解释的产品状态

可以持久化：

```text
current_track_id
position_ms
volume
queue snapshot
current_queue_item_id
active view
active playlist id
window bounds
window maximized state
```

不要持久化：

```text
audio element
native player pointer
Promise
callback
DOM ref
component instance
drag state
context menu state
temporary selection
stale generation token
```

### 3.3 Restore 前先验证

```text
snapshot
→ schema validate
→ Track validate
→ source validate
→ relation validate
→ clamp
→ restore
```

不能把旧/坏状态直接灌回 runtime。

### 3.4 Partial Restore 优于全失败

例如：

```text
Queue valid
current Track missing
window state valid
```

应该：

```text
restore Queue
mark missing Track unavailable
restore window
do not crash
```

而不是整份 snapshot 作废。

---

## 4. 本包要做

- Playback snapshot 持久化
- Queue snapshot 持久化
- current Track 恢复
- position 恢复
- volume 恢复
- active view 恢复
- active playlist / current context 恢复
- window size / position / maximized 恢复
- graceful exit checkpoint
- periodic/debounced checkpoint
- abnormal-exit recovery
- corrupted snapshot fallback
- schema versioning
- snapshot migration
- missing-source-on-restart behavior
- missing-Track relation behavior
- restart regression tests
- crash-simulation tests
- evidence

---

## 5. 本包不做

- 自动播放恢复
- 云端同步恢复
- 跨设备同步
- 用户账号 session 恢复
- Windows media keys
- tray
- file association
- startup registration
- updater
- cloud bridge
- settings center redesign
- UI redesign

---

## 6. W08 完成后的用户体验

用户：

```text
正在播放一首歌
→ 听到 02:13
→ Queue 里还有 8 首
→ 音量 35%
→ 正在“收藏”页
→ 关闭 Moodify
→ 再打开
```

应该得到：

```text
当前歌曲仍然是那首
进度恢复到接近 02:13
Queue 仍在
音量 35%
仍在收藏页
但播放器是 PAUSED / READY
```

如果源文件被移动：

```text
Track 不消失
Queue 不崩
显示 unavailable
允许用户继续下一首
```
