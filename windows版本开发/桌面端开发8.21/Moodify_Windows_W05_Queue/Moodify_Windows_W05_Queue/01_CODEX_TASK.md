# Codex 执行任务书 — MFY-WIN-W05-QUEUE-001

## 0. 执行模式

```text
PACKAGE = W05
FOCUS = PLAYBACK_QUEUE
CANON_CHANGE = NO
VISUAL_REDESIGN = FORBIDDEN
START_W06 = NO
```

必须复用：

```text
Track
Library
Playlist
PlaylistItem
Playback authority
Source Resolver
```

---

## 1. Phase 0 — Preflight

读取 W04 产物并输出：

`artifacts/windows/w05/preflight.md`

至少：

```text
W04_STATUS =
W05_GATE =
PLAYBACK_AUTHORITY =
CURRENT_TRACK_AUTHORITY =
ENDED_SEAM =
ERROR_SEAM =
PLAYLIST_ORDER_SOURCE =
QUEUE_CURRENT_REALITY =
```

若 `W05_GATE != PASS`，停止。

---

## 2. Phase 1 — Audit Existing Queue Reality

先查真实代码：

- 是否已有 queue model
- 是否只是临时 array
- 是否 next/previous 直接读 playlist
- 是否 player 内藏 queue
- 是否 UI 有 “当前播放”
- 是否有 play next / add to queue
- 是否已有 queue persistence
- 是否有 duplicate policy

输出：

`artifacts/windows/w05/current-queue-reality.md`

如果现有 Queue 可 REPAIR，则修复；不要重建第二套。

---

## 3. Phase 2 — Queue Contract

推荐语义：

```text
Queue
- items
- current_item_id / current_index
- source_context
- created_at / updated_at

QueueItem
- id
- track_id
- origin
- inserted_at
```

字段名可适配现有实现。

### Required invariants

1. Queue authority 唯一。
2. QueueItem 引用 Track ID。
3. Queue 不复制 Track truth。
4. Queue 顺序独立于 Playlist。
5. Queue reorder 不改变 Playlist。
6. Queue remove 不改变 Playlist。
7. Queue clear 不改变 Library。
8. Playback current Track 与 current Queue item 可明确映射。
9. stale ended 不能推进错误的 Queue。
10. current item mutation 有确定行为。

---

## 4. Phase 3 — Materialize Queue from Playlist

实现：

```text
Play Playlist
→ ordered PlaylistItems
→ Queue snapshot/materialization
→ current item
→ Playback.load(track)
```

默认建议：

```text
current Queue = playlist order snapshot
```

之后用户 reorder Queue：

```text
Playlist remains unchanged
```

如果 Playlist 后续被修改，Queue 是否实时跟随必须明确。

推荐 W05：

```text
Queue is snapshot after materialization
```

避免播放中 Playlist 编辑导致顺序漂移。

---

## 5. Phase 4 — Play Track from Library

从 Library 点某一首播放时，需要确定上下文。

推荐：

```text
Library current ordering
→ build Queue
→ cursor = selected Track
```

如果当前 Library 没有稳定排序，就：

```text
Queue = [selected Track]
```

不要猜排序。

---

## 6. Phase 5 — Play Now

定义：

```text
Play Now(track)
```

推荐行为：

```text
replace current active playback target
keep remaining queue unless product rule says replace all
```

但必须明确产品语义。

如果 UI 只有普通“播放”，可以把当前 Track 设为 current item，并保留 Queue 后续。

不要让 Play Now 与 “清空后只播这一首” 混为一谈，除非现有产品就是如此。

---

## 7. Phase 6 — Play Next

实现：

```text
Play Next(track)
```

目标：

```text
insert directly after current Queue item
```

如果无 current item：

```text
becomes first/current item
```

### Duplicate policy

W05 必须明确：

同一 Track 是否允许 Queue 中多次出现。

推荐 Queue：

```text
ALLOW
```

因为用户可能真的想连续听同一首多次。

这与 Playlist duplicate policy 可以不同。

QueueItem 因此应优先有自己稳定 ID。

---

## 8. Phase 7 — Add to Queue / Append

实现：

```text
Add to Queue(track)
→ append to tail
```

批量添加时：

```text
preserve selection order
```

如果当前 Queue 为空：

```text
queue becomes populated
```

是否立即播放由用户动作语义决定。

---

## 9. Phase 8 — Previous / Next Integration

W04 的：

```text
previous()
next()
```

必须改为优先使用 Queue sequencing authority。

### Next

```text
current item
→ next QueueItem
→ Playback.load(track)
```

### Previous

推荐基础规则：

```text
if position > restart_threshold:
    seek(0)
else:
    previous QueueItem
```

但如果现有产品已有规则，服从现有定义。

建议 threshold：

```text
~3 seconds
```

只是候选，不强制；必须写清最终规则。

---

## 10. Phase 9 — Ended Advance

W04 ended seam 接入 Queue：

```text
Playback ended
→ Queue.advance()
→ next QueueItem
→ Playback.load
→ autoplay
```

没有 next：

```text
Playback = ENDED
Queue current remains final item
```

必须防：

- ended duplicate
- stale generation
- double advance
- deleted current item race

---

## 11. Phase 10 — Error Advance

如果当前 Track 出错：

推荐：

```text
mark current attempt failed
→ advance to next QueueItem
```

但必须有：

- max consecutive skips
- visited item protection
- final failure state

不能无限循环。

如果无 next：

```text
Playback ERROR
Queue remains inspectable
```

---

## 12. Phase 11 — Remove Queue Item

### Remove non-current item

```text
remove
→ compact ordering
```

### Remove current item while playing

必须定义。

推荐：

```text
current audio continues
QueueItem removed from future sequencing
on ended → advance using nearest surviving successor
```

或：

```text
immediately advance
```

二选一，但要稳定。

建议优先：

> 当前正在听的歌不被突然打断。

除非用户选择的是显式 `Skip/Next`。

---

## 13. Phase 12 — Reorder Queue

实现：

```text
drag/drop
or minimal reorder action
```

必须保证：

- current item identity 稳定
- reorder 前后 current Track 不突然换
- next target 根据新顺序更新
- QueueItem ID 不因 reorder 改变
- Playlist 不受影响

至少测试：

```text
move future item
move current item
move item before current
move item after current
rapid reorder
```

---

## 14. Phase 13 — Clear Queue

定义：

```text
Clear Queue
```

推荐：

```text
remove future items
keep current playing item until it ends/stops
```

避免清空队列就突然切断音乐。

也可以提供：

```text
Clear All / Stop
```

但 W05 不要求额外 UI。

必须保证：

```text
Library / Playlist untouched
```

---

## 15. Phase 14 — Queue UI

当前视觉保持不变。

允许最小 Queue surface：

- `当前播放`
- `接下来播放`
- 当前 Track
- 后续 Track 列表
- drag reorder
- remove
- clear

可以放：

- sidebar secondary panel
- drawer
- popover
- secondary page

不要重做首页。

### Track context menu

W05 可补：

```text
播放
下一首播放
添加到播放队列
添加到歌单 >
```

---

## 16. Phase 15 — Queue Snapshot vs Live Playlist

必须在：

`artifacts/windows/w05/queue-source-policy.md`

明确：

```text
Playlist → Queue
```

是 snapshot 还是 live view。

推荐：

```text
SNAPSHOT
```

原因：

- 播放顺序稳定
- Queue 可独立 reorder
- Playlist 编辑不污染当前会话
- 更符合 Queue 的短期会话语义

---

## 17. Phase 16 — Persistence Seam for W08

W05 不要求 Queue restart recovery 完整落地。

但必须定义：

```text
Queue snapshot
Queue current item
Queue order
Queue origin/context
```

未来 W08 可以恢复。

输出：

`artifacts/windows/w05/queue-persistence-seam.md`

禁止持久化 engine object / callback / raw component state。

---

## 18. Phase 17 — Tests

### Domain

- materialize from Playlist
- play next
- append
- remove
- reorder
- clear
- duplicate items
- current cursor
- advance

### Integration

- Queue → Playback.load
- ended → advance
- error → safe skip
- previous/next → Queue

### Referential Safety

- Queue remove keeps Playlist
- Queue reorder keeps Playlist
- Queue clear keeps Library
- original files untouched

### Race

- duplicate ended
- rapid next
- remove current during ended
- reorder during playback
- play-next during loading

### Regression

- W04 Playback stable
- W03 Playlist stable
- W02 Library stable
- no second Playback authority

---

## 19. Required Outputs

写入：

`artifacts/windows/w05/`

至少：

1. `W05_IMPLEMENTATION_REPORT.md`
2. `preflight.md`
3. `current-queue-reality.md`
4. `queue-authority.md`
5. `queue-item-contract.md`
6. `queue-source-policy.md`
7. `previous-next-policy.md`
8. `ended-error-integration.md`
9. `queue-mutation-policy.md`
10. `queue-persistence-seam.md`
11. `test-report.md`
12. `evidence-manifest.json`
13. `W06_HANDOFF.md`

---

## 20. Definition of Done

必须真实证明：

```text
Playlist / Library
→ Queue
→ Current Item
→ Play
→ Play Next
→ Append
→ Reorder
→ Remove
→ Next / Previous
→ Ended Advance
→ Error Advance
→ Clear
```

并且：

```text
Queue mutation does not mutate Playlist/Library
```

最后：

```text
W05_STATUS = PASS | BLOCKED
W06_GATE = PASS | BLOCKED
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```
