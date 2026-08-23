# Codex 执行任务书 — MFY-WIN-W03-PLAYLIST-001

## 0. 执行模式

```text
PACKAGE = W03
FOCUS = PLAYLIST_COMPLETE_LOOP
CANON_CHANGE = NO
VISUAL_REDESIGN = FORBIDDEN
START_W04 = NO
```

本包必须复用 W02 建立的 Track / Library / Persistence authority。

---

## 1. Phase 0 — Gate Check

读取：

- `artifacts/windows/w02/W02_IMPLEMENTATION_REPORT.md`
- `artifacts/windows/w02/track-identity.md`
- `artifacts/windows/w02/library-authority.md`
- `artifacts/windows/w02/persistence-change.md`
- `artifacts/windows/w02/W03_HANDOFF.md`

输出：

`artifacts/windows/w03/preflight.md`

至少包含：

```text
W02_STATUS =
W03_GATE =
TRACK_AUTHORITY =
LIBRARY_AUTHORITY =
PERSISTENCE_AUTHORITY =
PLAYLIST_CURRENT_STATE =
MIGRATION_REQUIRED =
```

如果 `W03_GATE != PASS`，停止实现。

---

## 2. Phase 1 — Audit Existing Playlist Code

不要假设 Playlist 是空白功能。

先定位：

- playlist model/type
- create handler
- rename handler
- delete handler
- add-track handler
- remove-track handler
- reorder handler
- persistence
- UI list
- playlist detail
- any mock/local state
- any legacy schema

输出：

`artifacts/windows/w03/current-playlist-reality.md`

重点对照 W01 的 `playlist-add-root-cause.md`。

---

## 3. Phase 2 — Playlist Contract

实现或修复唯一 Playlist authority。

候选语义：

```text
Playlist
- id
- name
- created_at
- updated_at

PlaylistItem
- id
- playlist_id
- track_id
- position
- added_at
```

字段名可服从现有实现。

### Required invariants

1. Playlist ID 稳定。
2. PlaylistItem 必须引用稳定 Track ID。
3. PlaylistItem 不复制整份 Track truth。
4. Playlist 删除时只删除 Playlist / PlaylistItem relation。
5. Track 仍保留在 Library。
6. 原始文件永不因删歌单而删除。
7. 排序保存在 PlaylistItem relation 层。
8. restart 后顺序不变。
9. unavailable Track 可保留在歌单中。
10. Player 不成为 Playlist authority。

---

## 4. Phase 3 — Create Playlist

实现 / 修复：

```text
User
→ + 我的歌单
→ input name
→ validate
→ persist Playlist
→ sidebar update
```

### Validation

至少：

- empty
- whitespace-only
- too long
- duplicate name
- Unicode / 中文
- emoji

duplicate name 是否允许可以服从现有产品规则。

若允许重复名称，必须依赖 Playlist ID 区分。

---

## 5. Phase 4 — Rename Playlist

实现：

```text
Playlist
→ Rename
→ Validate
→ Persist
→ UI Update
→ Restart
→ Still Renamed
```

禁止通过“删旧建新”实现，因为会破坏 PlaylistItem relation。

---

## 6. Phase 5 — Add Track to Playlist

这是 W03 的最高优先级功能。

支持：

```text
Single Track
→ Add to Playlist
```

以及：

```text
Selected Tracks
→ Add to Playlist
```

如果 UI 暂无 multi-select，可先实现 domain/use-case 批量接口，UI 可只暴露单曲。

### Required behavior

- 已在歌单内的 Track 再次添加
- unavailable Track
- deleted-from-library Track（若业务仍允许引用）
- multiple playlists
- rapid repeated clicks
- restart persistence

### Duplicate policy

W03 必须明确：

```text
同一 Track 在同一 Playlist 是否允许重复？
```

推荐默认：

```text
NO
```

除非现有产品已有相反规则。

如果不允许重复：

```text
add existing track
→ idempotent no-op / ALREADY_IN_PLAYLIST
```

不要 silently append duplicate rows。

---

## 7. Phase 6 — Track Context Action

复用 Library Track context menu，加入：

```text
添加到歌单 >
```

子菜单列出已有歌单。

若无歌单：

```text
新建歌单…
```

可以作为轻量 shortcut，但不要把 context menu 做成复杂管理器。

需要确保：

- submenu 来源于唯一 Playlist authority
- 不维护 UI 私有 playlist copy
- add action 走同一 domain use-case

---

## 8. Phase 7 — Playlist Detail View

复用当前视觉方向。

最小展示：

```text
Playlist Name
Track Count
Track List
Play action
Context action
```

Track row 至少能表示：

- title
- artist
- availability
- ordering
- play
- remove

禁止新增密集工程列。

---

## 9. Phase 8 — Remove Track from Playlist

实现：

```text
PlaylistItem
→ Remove
→ Persist
→ Reindex / preserve ordering
→ UI update
→ restart
```

必须保证：

```text
Track remains in Library
Original file untouched
Other playlists untouched
```

---

## 10. Phase 9 — Reorder

实现稳定 reorder：

```text
drag/drop
or
move up/down
```

具体交互服从当前技术能力。

Domain 必须支持：

```text
playlist_id
ordered track references
```

### Required tests

- move first to last
- last to first
- middle reorder
- repeated reorder
- restart
- unavailable Track in sequence
- remove after reorder
- add after reorder

排序字段不能依赖 React array index 或临时 DOM 顺序作为唯一 truth。

---

## 11. Phase 10 — Delete Playlist

实现：

```text
Delete Playlist
→ confirmation
→ delete PlaylistItems
→ delete Playlist
→ UI update
→ restart
```

必须验证：

- Library Track 未删除
- original files 未删除
- other playlists 不受影响
- current route gracefully returns
- current playback 不应因为删除列表而崩溃

如果当前正在播放来自该 Playlist 的歌曲：
W03 只要求安全，不要求完整 Queue 行为。

推荐：

```text
current track continues playing
playlist context disappears
```

Queue 由 W05 接管。

---

## 12. Phase 11 — Start Playback from Playlist

本包允许最小播放集成：

```text
Double click Track
or
Play Track action
→ existing Player
```

以及：

```text
Play Playlist
```

如果当前架构没有 Queue，不要在 W03 偷偷造正式 Queue。

可以临时调用现有 player next-context，但必须明确：

```text
QUEUE_AUTHORITY_NOT_CREATED
```

完整顺序播放由 W04/W05 完成。

---

## 13. Phase 12 — Unavailable Track in Playlist

Unavailable Track 不应自动从歌单消失。

显示最小状态，例如：

```text
无法找到本地文件
```

允许：

- remove from playlist
- inspect
- future relink seam

不允许：

- crash
- silent delete
- sequence corruption

---

## 14. Phase 13 — Persistence / Migration

若已有旧 Playlist 数据：

- 保留
- 迁移
- 验证 relation count
- 验证 ordering
- 验证 Track foreign/reference identity

禁止：

```text
schema mismatch → reset playlists
```

任何 migration 必须可重复、可验证、可回滚或至少可恢复。

---

## 15. Phase 14 — Tests

### Domain

- create
- rename
- delete
- add
- duplicate add
- remove
- reorder
- track reference
- unavailable Track

### Persistence

- create → restart
- add → restart
- reorder → restart
- rename → restart
- delete → restart

### Referential safety

- delete playlist leaves Track
- remove item leaves Track
- delete library Track interaction clarified
- original file untouched

### UI integration

- `+ 我的歌单`
- context `添加到歌单`
- playlist detail
- remove
- reorder
- play

### Regression

- Library still works
- import still works
- existing player still works
- no second Track authority
- no second Playlist authority

---

## 16. Required Outputs

写入：

`artifacts/windows/w03/`

至少：

1. `W03_IMPLEMENTATION_REPORT.md`
2. `preflight.md`
3. `current-playlist-reality.md`
4. `playlist-authority.md`
5. `playlist-item-contract.md`
6. `add-track-flow.md`
7. `reorder-behavior.md`
8. `persistence-migration.md`
9. `referential-safety.md`
10. `test-report.md`
11. `evidence-manifest.json`
12. `W04_HANDOFF.md`

---

## 17. Definition of Done

必须真实证明：

```text
Create Playlist
→ Add Track
→ Persist
→ Reorder
→ Remove
→ Rename
→ Restart
→ State Still Correct
```

以及：

```text
Delete Playlist
→ Track remains
→ original file remains
```

最后：

```text
W03_STATUS = PASS | BLOCKED
W04_GATE = PASS | BLOCKED
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```
