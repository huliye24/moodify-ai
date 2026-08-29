# Moodify Windows Desktop Completion — W04 Playback Core 播放核心

**Package ID:** `MFY-WIN-W04-PLAYBACK-CORE-001`  
**日期：** 2026-08-21  
**阶段：** Windows Desktop Completion / 04 of 12  
**任务类型：** Core implementation / Playback Engine & State  
**CANON_CHANGE：** `NO`  
**VISUAL_REDESIGN：** `FORBIDDEN`  
**前置依赖：** W03 `W04_GATE = PASS`  
**下一包：** W05 — Queue 播放队列

---

## 1. W04 的目标

W04 要把“能播放一首歌”升级成“拥有稳定、可预测、可测试的播放器”。

完成链路：

```text
Track / Playlist Context
→ Resolve Source
→ Load
→ Play
→ Pause
→ Seek
→ Previous / Next
→ Ended
→ Error
→ State Sync
→ Persistence Seam
```

本包解决的是 **Playback authority**。

不是做 UI 特效，也不是做播放队列。

---

## 2. 前置条件

执行前必须读取：

```text
artifacts/windows/w03/W03_IMPLEMENTATION_REPORT.md
artifacts/windows/w03/playlist-authority.md
artifacts/windows/w03/playlist-item-contract.md
artifacts/windows/w03/W04_HANDOFF.md
```

必须确认：

```text
W03_STATUS = PASS
W04_GATE = PASS
```

否则：

```text
W04_STATUS = BLOCKED
```

---

## 3. 本包核心结果

W04 完成后必须能稳定证明：

```text
选择 Track
→ 播放
→ 暂停
→ 恢复
→ 拖动进度
→ 上一首
→ 下一首
→ 播放结束
→ 自动进入正确下一状态
```

并且：

```text
source missing / decode error / load error
→ 不崩溃
→ 有稳定 error state
→ UI 与 audio engine 不失同步
```

---

## 4. 本包建设边界

### 要做

- 唯一 Playback authority
- current Track
- play / pause
- seek
- position / duration
- previous / next
- volume
- ended behavior
- loading / ready / playing / paused / error
- player ↔ UI state synchronization
- source resolution
- track switch
- stale event protection
- audio error handling
- unavailable Track safety
- basic playlist-context navigation
- persistence seam for W08
- tests
- evidence

### 不做

- 正式 Queue authority
- Play Next
- Queue reorder
- Shuffle / Repeat 完整产品化
- Crossfade
- EQ / DSP
- Loudness controls
- Cloud preparation pipeline
- media keys / SMTC
- tray
- auto updater
- visual redesign

---

## 5. 核心原则

### Playback 只有一个 authority

禁止出现：

```text
UI currentTrack
+ audio currentTrack
+ playlist currentTrack
+ local component currentTrack
```

四套互相竞争的状态。

必须建立明确关系：

```text
Playback Controller / Store
= playback business authority

Audio Engine
= execution authority

UI
= subscriber / command source
```

### Playlist 不是播放器状态

Playlist 只提供有序 Track context。

W04 可以基于当前 Playlist context 支持 previous / next，但不能因此把 Playlist 变成 Queue。

### Audio Event 不能直接支配业务状态

必须处理：

- stale ended event
- previous track load event
- rapid track switching
- play promise rejection
- aborted load
- out-of-order callbacks

播放器应知道某个 event 属于哪一个 active playback request。

---

## 6. 用户可感知结果

当前 Alpha 里的：

```text
上一首
播放 / 暂停
下一首
```

必须真正可用。

同时增加最小播放反馈：

```text
00:42 / 03:17
progress
volume
loading / unavailable / error
```

具体 UI 服从现有设计，不重做首页。
