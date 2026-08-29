# Codex 执行任务书 — MFY-WIN-W08-RECOVERY-RESILIENCE-001

## 0. 执行模式

```text
PACKAGE = W08
FOCUS = RECOVERY_RESILIENCE
CANON_CHANGE = NO
VISUAL_REDESIGN = FORBIDDEN
START_W09 = NO
```

W08 只建立恢复系统，不改业务 authority。

---

## 1. Phase 0 — Preflight

读取：

```text
artifacts/windows/w07/W07_IMPLEMENTATION_REPORT.md
artifacts/windows/w07/W08_HANDOFF.md
artifacts/windows/w04/playback-persistence-seam.md
artifacts/windows/w05/queue-persistence-seam.md
```

输出：

`artifacts/windows/w08/preflight.md`

至少：

```text
W07_STATUS =
W08_GATE =
APP_STATE_AUTHORITY =
PLAYBACK_SNAPSHOT_SEAM =
QUEUE_SNAPSHOT_SEAM =
PERSISTENCE_TECH =
WINDOW_STATE_CURRENT_REALITY =
CRASH_RECOVERY_CURRENT_REALITY =
SCHEMA_VERSION_CURRENT_REALITY =
```

若 `W08_GATE != PASS`，停止。

---

## 2. Phase 1 — Audit Current Persistence Reality

定位真实实现：

- AppState persistence
- playback snapshot
- queue snapshot
- active route/view
- window bounds persistence
- graceful shutdown hooks
- abnormal exit detection
- schema/version
- existing migrations
- recovery logs
- stale state cleanup

输出：

`artifacts/windows/w08/current-recovery-reality.md`

分类：

```text
WORKING
PARTIAL
PLACEHOLDER
BROKEN
MISSING
UNKNOWN
```

---

## 3. Phase 2 — Define Recovery Snapshot Contract

建立或修复一个明确 snapshot contract。

推荐语义：

```text
RecoverySnapshot {
  schema_version

  playback {
    current_track_id
    position_ms
    volume
    last_status
  }

  queue {
    items
    current_queue_item_id
    source_context
  }

  navigation {
    active_view
    active_playlist_id
  }

  window {
    x
    y
    width
    height
    maximized
  }

  timestamps {
    saved_at
  }
}
```

字段服从现有技术栈。

### Required

- versioned
- serializable
- human-inspectable where practical
- no engine object
- no raw UI instance
- no circular references

输出：

`artifacts/windows/w08/recovery-snapshot-contract.md`

---

## 4. Phase 3 — Snapshot Authority

必须明确：

```text
Who writes snapshot?
Who reads snapshot?
Where is it stored?
When is it written?
What makes it valid?
```

禁止：

```text
Playback store writes one file
Queue store writes another
UI writes localStorage
window process writes a third competing app state
```

如果已有多个 persistence sources，W08 必须做 authority map 并明确：

```text
KEEP
REPAIR
MIGRATE
```

不能再加第四套。

---

## 5. Phase 4 — Write Policy

不能每次 timeupdate 都同步写磁盘。

推荐：

```text
dirty state
→ debounce/throttle
→ checkpoint
```

至少在这些时机写：

- track switch
- pause
- queue mutation
- volume settled
- route/view change
- window move/resize settled
- graceful app close
- periodic checkpoint

### Position

推荐：

```text
throttle 5–15 seconds
```

具体值按现有 runtime 和性能决定。

---

## 6. Phase 5 — Graceful Exit

应用正常关闭时：

```text
capture latest snapshot
→ flush persistence
→ confirm/await completion where runtime supports
→ exit
```

要求：

- 不无限阻塞退出
- 不因一个字段失败导致全 app hang
- failure 有日志
- snapshot atomic or transaction-safe

如果 runtime 不允许 async shutdown flush，使用当前技术栈最安全方案。

---

## 7. Phase 6 — Abnormal Exit / Crash Recovery

W08 要至少能处理：

```text
process crash
forced kill
power loss approximation
renderer crash
partial previous write
```

具体能模拟多少取决于 runtime。

推荐：

```text
last known valid snapshot
```

或：

```text
atomic temp file
→ fsync/commit
→ rename
```

若 persistence 是 DB，则使用事务。

禁止：

```text
write directly to canonical JSON
→ half-written file
→ next boot crash
```

---

## 8. Phase 7 — Restore Pipeline

启动时：

```text
load snapshot
→ parse
→ schema validate
→ migrate if needed
→ validate relations
→ validate Track
→ validate Queue
→ clamp values
→ apply safe state
```

### Restore Order

推荐：

```text
1. Library/Track authority ready
2. Playlist/History/Favorite ready
3. Queue snapshot restore
4. Playback current Track restore
5. Position/volume restore
6. Navigation
7. Window state
```

不要在 Track authority 尚未就绪时提前恢复 Playback。

---

## 9. Phase 8 — Playback Restore

默认目标：

```text
current_track_id restored
position restored
volume restored
status restored as PAUSED/READY
```

### Never

```text
was PLAYING
→ app launches
→ immediately outputs audio
```

除非未来产品明确改变。

### Position Validation

```text
position < 0 → 0
position > duration → clamp
duration unknown → defer seek
```

### Track Missing

如果 Track entity 存在但 source unavailable：

```text
restore Track identity
status = safe unavailable/error
queue remains
```

---

## 10. Phase 9 — Queue Restore

恢复：

```text
QueueItem IDs
Track refs
order
current item
origin/context
```

必须处理：

- Track removed
- Track unavailable
- duplicate Track QueueItems
- current item missing
- invalid item ID
- partial queue corruption

推荐：

```text
drop only invalid QueueItem
preserve valid items
```

同时输出 recovery summary evidence。

---

## 11. Phase 10 — Navigation Restore

允许恢复：

```text
active view
active playlist
```

如果目标已不存在：

```text
fallback to safe default
```

推荐：

```text
All Songs
or Home
```

不要 crash / blank screen。

Search query 一般不恢复。

临时 selection 不恢复。

---

## 12. Phase 11 — Window State Restore

如果 desktop runtime 支持：

持久化：

```text
x
y
width
height
maximized
```

必须验证：

- multi-monitor
- monitor removed
- resolution changed
- off-screen coordinates
- minimum size
- maximized state

启动时：

```text
clamp into visible work area
```

不能把窗口恢复到用户看不见的位置。

---

## 13. Phase 12 — Schema Versioning

Recovery snapshot 必须有：

```text
schema_version
```

并建立：

```text
vN
→ vN+1 migration
```

至少：

- unknown future version
- old version
- missing version
- malformed fields

行为必须明确。

禁止：

```text
version mismatch
→ clear all app data
```

---

## 14. Phase 13 — Corrupted Snapshot Fallback

至少测试：

- empty file
- truncated JSON / record
- invalid types
- missing fields
- impossible position
- unknown Track ID
- malformed QueueItem

目标：

```text
app starts
valid durable data remains
recovery snapshot can be ignored/partially repaired
```

Recovery snapshot 损坏不能导致 Library/Playlist 数据被清空。

---

## 15. Phase 14 — Last Known Good

如果当前 persistence 技术适合，推荐引入：

```text
current snapshot
last-known-good snapshot
```

或 DB transaction equivalent。

当 current snapshot corrupted：

```text
fallback to LKG
```

若成本太高，可记录不做，但必须解释为何当前 atomic write 已足够。

---

## 16. Phase 15 — Recovery UI

不增加复杂恢复页面。

允许极简：

```text
上次播放
```

或：

```text
无法恢复上次播放状态
```

但默认恢复应尽量静默。

不要显示：
- schema version
- raw JSON
- stack trace
- internal recovery flags

---

## 17. Phase 16 — Recovery Logging

内部日志至少记录：

```text
snapshot save success/fail
snapshot load result
schema version
migration result
partial repair
dropped invalid queue items
missing current track
window clamp
```

日志不可包含：
- user private audio content
- secrets
- tokens

路径也尽量避免不必要全量输出。

---

## 18. Phase 17 — Tests

### Snapshot
- serialize
- deserialize
- version
- unknown field
- missing field

### Playback
- current Track
- position
- volume
- no autoplay
- missing source

### Queue
- order
- duplicates
- current item
- invalid item
- partial repair

### Navigation
- valid view
- deleted playlist fallback

### Window
- valid bounds
- off-screen
- monitor change
- maximized

### Crash
- truncated snapshot
- interrupted write
- forced restart simulation

### Migration
- old version
- repeated migration
- future version

### Regression
- Library
- Playlist
- Playback
- Queue
- Favorite/History
- Desktop interaction

---

## 19. Required Outputs

写入：

`artifacts/windows/w08/`

至少：

1. `W08_IMPLEMENTATION_REPORT.md`
2. `preflight.md`
3. `current-recovery-reality.md`
4. `recovery-snapshot-contract.md`
5. `recovery-authority-map.md`
6. `snapshot-write-policy.md`
7. `restore-order.md`
8. `playback-restore-policy.md`
9. `queue-restore-policy.md`
10. `window-restore-policy.md`
11. `schema-migration.md`
12. `corruption-recovery.md`
13. `crash-test-report.md`
14. `test-report.md`
15. `evidence-manifest.json`
16. `W09_HANDOFF.md`

---

## 20. Definition of Done

必须真实证明：

```text
Normal Exit
→ Restart
→ State Restored
```

以及：

```text
Abnormal Exit / Corrupted Snapshot
→ App Still Starts
→ Durable User Data Preserved
→ Recovery Is Safe
```

并且：

```text
Restore != Auto Play
```

最后：

```text
W08_STATUS = PASS | BLOCKED
W09_GATE = PASS | BLOCKED
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```
