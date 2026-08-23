# Codex 执行任务书 — MFY-WIN-W04-PLAYBACK-CORE-001

## 0. 执行模式

```text
PACKAGE = W04
FOCUS = PLAYBACK_CORE
CANON_CHANGE = NO
VISUAL_REDESIGN = FORBIDDEN
START_W05 = NO
```

必须复用 W02/W03 已建立的：

```text
Track
Library
Playlist
PlaylistItem
Persistence
Source Resolver
```

---

## 1. Phase 0 — Gate & Reality Check

读取 W03 产物并确认：

```text
W03_STATUS =
W04_GATE =
TRACK_AUTHORITY =
PLAYLIST_AUTHORITY =
PLAYER_CURRENT_REALITY =
SOURCE_RESOLVER =
TEST_ENTRY =
```

输出：

`artifacts/windows/w04/preflight.md`

若 `W04_GATE != PASS`，停止。

---

## 2. Phase 1 — Audit Current Player

先定位真实播放实现。

必须识别：

- audio engine / library
- player singleton or multiple instances
- current Track state
- play/pause handlers
- next/previous
- seek
- volume
- timeupdate listeners
- ended listeners
- error listeners
- load metadata listeners
- UI subscriptions
- persistence hooks
- source resolver
- renderer/native ownership
- test harness

输出：

`artifacts/windows/w04/current-player-reality.md`

明确回答：

```text
How many player instances can exist?
Who owns current Track?
Who owns isPlaying?
Who owns currentTime?
Who owns volume?
Who decides next Track?
What happens on ended?
What happens on source error?
```

---

## 3. Phase 2 — Establish Playback Authority

目标概念：

```text
PlaybackState
- current_track_id
- status
- position_ms
- duration_ms
- volume
- context
- error
- request_id / generation
```

字段名服从现有技术栈。

推荐 status：

```text
IDLE
LOADING
READY
PLAYING
PAUSED
ENDED
ERROR
```

如现有实现已有等价枚举，优先复用。

禁止再建立第二个 repo-wide state machine。

这里的状态仅属于 Windows Player playback domain。

---

## 4. Phase 3 — Command Contract

播放器至少支持：

```text
load(track_id, context?)
play()
pause()
toggle()
seek(position_ms)
setVolume(value)
previous()
next()
stop()/clear()   # only if existing architecture needs it
```

UI 不直接操作 raw audio element / native engine。

所有入口统一走 Playback authority。

---

## 5. Phase 4 — Source Resolution

播放源必须来自 W02 的 Track / Source Resolver。

```text
track_id
→ Track
→ resolve source
→ validate availability
→ engine.load
```

禁止：

```text
playlist row filePath
→ <audio src>
```

绕过 Track authority。

### Required cases

- AVAILABLE local source
- UNAVAILABLE source
- malformed source
- moved/deleted file
- unsupported media
- load failure

---

## 6. Phase 5 — Play / Pause

必须处理：

### Play

```text
READY / PAUSED
→ play request
→ engine accepted
→ PLAYING
```

如果 engine reject：

```text
→ ERROR / safe paused state
```

### Pause

```text
PLAYING
→ pause
→ PAUSED
```

### Rapid toggle

连续快速点击不能导致：

- UI 显示 playing 但 engine paused
- multiple play promises
- crash
- stale state overwrite

---

## 7. Phase 6 — Track Switching

切换 Track：

```text
T1 playing
→ load T2
→ invalidate T1 events
→ resolve T2
→ load
→ optionally autoplay
```

必须处理：

- T1 `ended` 在 T2 load 后到达
- T1 `timeupdate` 污染 T2
- T1 `error` 污染 T2
- rapid T1→T2→T3

推荐使用：

```text
request_id / generation / token
```

或现有架构等价机制。

---

## 8. Phase 7 — Seek

实现：

```text
seek target
→ clamp [0, duration]
→ engine seek
→ state sync
```

处理：

- duration unknown
- before metadata loaded
- seek to end
- negative
- > duration
- unavailable source

UI 拖动时不要让高频 state write 造成明显卡顿。

---

## 9. Phase 8 — Position / Duration Sync

必须明确：

```text
engine events = telemetry
Playback authority = state projection
UI = subscriber
```

至少处理：

- loadedmetadata
- durationchange
- timeupdate / equivalent
- seeking
- seeked
- ended

不要每个 millisecond 持久化。

W08 才做正式恢复策略。

W04 只需要留清晰 persistence seam。

---

## 10. Phase 9 — Volume

实现：

```text
0.0 → 1.0
```

或现有引擎等价范围。

必须：

- clamp
- UI sync
- engine sync
- startup default
- no NaN
- no > max
- no negative

W04 可把 volume 暂存在现有 AppState 或 playback state；
正式跨重启恢复由 W08 决定，除非当前已有稳定 persistence 可安全复用。

---

## 11. Phase 10 — Previous / Next

W04 不创建 Queue。

可依据当前 context：

### Playlist context

```text
ordered PlaylistItems
current position
→ previous / next
```

### Library context

若当前 UI 支持从 Library 连续播放，可按现有 stable ordering。

如果没有稳定 context：

```text
previous / next disabled
```

不要猜排序。

---

## 12. Phase 11 — Ended Behavior

必须写成确定规则。

推荐：

```text
if next track exists in current context:
    load next
    autoplay
else:
    status = ENDED
    keep current Track visible
    position = duration
```

但如果当前产品已有明确规则，服从现有产品定义。

禁止：

- ended 后自动 clear UI
- ended 后随机选歌
- ended 后隐式创建 Queue
- ended event 多次触发 next

---

## 13. Phase 12 — Error Handling

至少区分：

```text
SOURCE_UNAVAILABLE
LOAD_FAILED
DECODE_FAILED
PLAY_REJECTED
ENGINE_ERROR
UNKNOWN
```

UI 可只显示简化文案。

内部必须保留错误类型用于 evidence。

### Error policy

单 Track 出错：

```text
no crash
no corrupted state
```

是否自动跳过到 next：

W04 可以实现 **安全 skip**，前提是：

- context 有明确 next
- 防止无限 error loop
- skip 次数 / visited track 有保护

如果架构尚不适合，先进入 ERROR，由 W05 再做 Queue-aware skip。

---

## 14. Phase 13 — UI Synchronization

当前主页仍保持简洁。

必须修正：

```text
disabled previous/play/next
```

使其随真实 player state 更新。

允许最小增加：

- progress
- elapsed / duration
- volume
- loading
- unavailable/error

禁止大规模播放器控制台。

---

## 15. Phase 14 — Concurrency / Race Protection

必须专门测试：

```text
rapid next 10x
play then immediately pause
load T1 then T2 before T1 ready
seek while loading
delete/move source during playback
playlist mutation during playback
```

任何 async callback 必须确认仍属于 active playback request。

---

## 16. Phase 15 — Persistence Seam

W04 不负责完整 restart recovery，但要定义：

`artifacts/windows/w04/playback-persistence-seam.md`

至少说明未来 W08 可持久化：

```text
current_track_id
position_ms
volume
context_ref
was_playing? (policy later)
```

W04 不得把 raw engine object 持久化。

---

## 17. Phase 16 — Tests

### Domain

- state transitions
- play/pause
- toggle
- seek clamp
- volume clamp
- next/previous
- ended
- error

### Integration

- Track → Source Resolver → Engine
- Playlist Track → Player
- player events → state → UI

### Race

- stale ended
- stale timeupdate
- rapid switching
- play promise rejection
- late error event

### Regression

- Library import
- Playlist add/remove/reorder
- unavailable Track
- no Queue authority
- no second Track authority

---

## 18. Required Outputs

写入：

`artifacts/windows/w04/`

至少：

1. `W04_IMPLEMENTATION_REPORT.md`
2. `preflight.md`
3. `current-player-reality.md`
4. `playback-authority.md`
5. `playback-state-contract.md`
6. `command-contract.md`
7. `source-resolution-flow.md`
8. `track-switch-race-control.md`
9. `ended-error-policy.md`
10. `playback-persistence-seam.md`
11. `test-report.md`
12. `evidence-manifest.json`
13. `W05_HANDOFF.md`

---

## 19. Definition of Done

必须真实证明：

```text
Load
→ Play
→ Pause
→ Resume
→ Seek
→ Volume
→ Previous
→ Next
→ Ended
→ Error
```

并且：

```text
UI state == engine reality
```

在快速切歌和异步事件下仍成立。

最后：

```text
W04_STATUS = PASS | BLOCKED
W05_GATE = PASS | BLOCKED
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```
