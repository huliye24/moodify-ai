# Codex 执行任务书 — MFY-WIN-W07-DESKTOP-INTERACTION-001

## 0. 执行模式

```text
PACKAGE = W07
FOCUS = DESKTOP_INTERACTION
CANON_CHANGE = NO
VISUAL_REDESIGN = FORBIDDEN
START_W08 = NO
```

W07 只连接既有 use-cases，不创建新的业务 authority。

---

## 1. Phase 0 — Preflight

读取 W06 产物并输出：

`artifacts/windows/w07/preflight.md`

至少确认：

```text
W06_STATUS =
W07_GATE =
TRACK_ROW_COMPONENT =
TRACK_ACTION_USE_CASES =
PLAYLIST_ACTION_USE_CASES =
QUEUE_ACTION_USE_CASES =
IMPORT_USE_CASE =
FAVORITE_USE_CASE =
REMOVE_LIBRARY_USE_CASE =
DESKTOP_RUNTIME =
NATIVE_BRIDGE =
```

若 `W07_GATE != PASS`，停止。

---

## 2. Phase 1 — Audit Existing Desktop Interactions

先定位：

- current context menu
- double-click handlers
- drag/drop support
- multi-select
- keyboard handlers
- explorer reveal
- confirmation dialogs
- native IPC
- security boundary
- duplicated action handlers

输出：

`artifacts/windows/w07/current-interaction-reality.md`

现有功能标：

```text
WORKING
PARTIAL
PLACEHOLDER
BROKEN
MISSING
UNKNOWN
```

---

## 3. Phase 2 — Unified Track Action Surface

建立统一 action adapter / menu model，复用已有 domain use-cases。

推荐语义：

```text
PLAY
PLAY_NEXT
ADD_TO_QUEUE
ADD_TO_PLAYLIST
FAVORITE
UNFAVORITE
REVEAL_IN_EXPLORER
REMOVE_FROM_LIBRARY
```

Playlist row / Queue row 可有各自相关动作，但业务入口必须复用原 use-case。

禁止每个页面复制一套 handler。

输出：

`artifacts/windows/w07/action-routing.md`

---

## 4. Phase 3 — Double Click to Play

所有 Track list view 支持：

```text
double click Track
→ Playback / Queue context
→ play
```

包括至少：

- All Songs
- Search Results
- Favorites
- Recently Played
- Playlist Detail

必须明确双击是否：

```text
build Queue from current view
```

推荐：
- Playlist view → materialize Playlist Queue
- Library-derived view → materialize current stable view order
- Search view → materialize filtered/sorted result snapshot

但必须服从 W05 Queue source policy。

---

## 5. Phase 4 — File Drag & Drop Import

支持从 Windows Explorer：

```text
drag files
→ app window
→ validate
→ W02 import pipeline
```

至少支持：

- single audio file
- multiple audio files
- mixed supported/unsupported
- duplicate files
- Chinese paths
- spaces
- Unicode
- files dropped rapidly

### Folder Drop

如果当前 runtime 安全、稳定地支持目录枚举，可支持文件夹导入。

若不支持：
明确 `NOT_SUPPORTED_IN_W07`，不要为了目录拖放引入高风险递归扫描。

### Security

禁止把 renderer 变成任意 filesystem authority。

必须复用 native bridge / file-drop event 的现有安全边界。

---

## 6. Phase 5 — Drag Track to Playlist

支持：

```text
Track row
→ drag
→ Sidebar Playlist
→ addTrackToPlaylist(...)
```

批量选中后拖拽：

```text
Selected Track IDs
→ Playlist
```

如果实现复杂，可先单 Track drag，并保留 batch through context menu。

要求：

- target highlight
- invalid target 不接收
- duplicate add policy 服从 W03
- unavailable Track 服从 W03
- Playlist reorder 不被误触发
- drag 失败不产生半 relation

---

## 7. Phase 6 — Multi-select

实现标准桌面选择语义。

最低：

```text
single click = select one
Ctrl+click = toggle item
Shift+click = range select
Ctrl+A = select all in current view
Escape = clear selection
```

具体 key 服从 runtime/OS。

### Selection Is View State

只保存：

```text
selected_track_ids / selected_row_ids
anchor
focus
```

不得成为 Track authority。

### Across Views

切换 view 后是否清空 selection 必须明确。

推荐：

```text
clear on view change
```

避免跨视图批量误操作。

---

## 8. Phase 7 — Batch Actions

多选后至少支持：

```text
Add to Playlist
Add to Queue
Favorite
Unfavorite
Remove from Library
```

### Batch Behavior

必须返回 aggregate result：

```text
total
succeeded
already_exists
skipped
failed
```

一个失败项不应默认让所有成功项回滚，除非 domain transaction 明确如此。

### Remove from Library

必须确认。

禁止删除原始文件。

---

## 9. Phase 8 — Context Menus

### Track

建议：

```text
播放
下一首播放
添加到播放队列
────────
添加到歌单 >
收藏 / 取消收藏
────────
在资源管理器中显示
从音乐库移除
```

### Playlist Item

```text
播放
下一首播放
添加到播放队列
────────
收藏 / 取消收藏
从歌单移除
```

### Queue Item

```text
播放此项
移出播放队列
```

### Playlist

```text
重命名
删除歌单
```

保持简洁，不堆无关功能。

---

## 10. Phase 9 — Keyboard Interaction

W07 只做轻量、局部键盘操作。

候选：

```text
Enter = play focused Track
Space = play/pause if focus context safe
Delete / Backspace = remove selected from current collection with confirmation
Ctrl+A = select all
Esc = clear selection
```

### Important

不得在输入框中误触发播放器快捷键。

必须识别：

```text
input
textarea
contenteditable
modal/dialog
```

W09 才做 Windows global/native media keys。

---

## 11. Phase 10 — Reveal in Explorer

若 native runtime 支持安全的：

```text
showItemInFolder
reveal
open containing folder
```

则实现：

```text
Track
→ resolved local source
→ reveal in Windows Explorer
```

要求：

- only LOCAL source
- source exists
- no shell string concatenation
- no arbitrary command execution
- unavailable source safe failure

如果当前 runtime 无安全 API：
标 `BLOCKED_FOR_NATIVE_INTEGRATION`，不要通过 `cmd.exe` 拼接路径绕过。

---

## 12. Phase 11 — Confirmation & Destructive Semantics

必须区分：

### Remove from Playlist
只删 relation。

### Remove from Queue
只删 QueueItem。

### Remove from Library
删 Moodify Library membership/reference。

### Delete Original File
W07 不实现。

所有 destructive wording 必须准确。

禁止使用模糊的：

```text
删除歌曲
```

如果实际只是从某个 collection 移除。

---

## 13. Phase 12 — Drag Visual Feedback

允许最小反馈：

- drop target highlight
- drag count
- invalid drop state
- selected row highlight

不要为了拖拽重做整个 UI。

---

## 14. Phase 13 — Selection + Search/Sort Interaction

必须测试：

```text
select tracks
→ search changes
→ sort changes
→ view changes
```

推荐策略：

- search query change：保留仍可见 selection 或清空，二选一并文档化
- sort change：保留 selection by Track ID
- view change：清空

不得按 DOM index 维护 selection。

---

## 15. Phase 14 — Drag + Queue/Playlist Referential Safety

必须验证：

```text
drag to Playlist
→ PlaylistItem only
```

```text
drag to Queue
→ QueueItem only
```

```text
file drop
→ Library import only
```

三种 drop 目标不能串线。

---

## 16. Phase 15 — Accessibility & Focus

最低要求：

- focused row 可见
- context menu 可键盘关闭
- dialog focus 不泄漏
- Escape 可取消临时 selection/menu
- mouse + keyboard interaction 不互相打架

不要求完整无障碍审计，但不能制造明显键盘陷阱。

---

## 17. Phase 16 — Tests

### Context Menu
- correct actions per view
- unavailable Track
- favorite state
- no duplicate handlers

### Double Click
- Library
- Playlist
- Search
- Favorites

### Drag Import
- one file
- batch
- duplicate
- invalid
- Unicode path

### Drag to Playlist
- one Track
- duplicate
- unavailable
- failed persistence

### Multi-select
- Ctrl
- Shift
- Ctrl+A
- view change
- sort change

### Batch
- playlist
- queue
- favorite
- remove library

### Keyboard
- Enter
- Space
- Delete
- input focus safety

### Explorer
- valid local source
- missing source
- non-local source

### Regression
- W02 import
- W03 playlist
- W04 playback
- W05 queue
- W06 search/favorite/history

---

## 18. Required Outputs

写入：

`artifacts/windows/w07/`

至少：

1. `W07_IMPLEMENTATION_REPORT.md`
2. `preflight.md`
3. `current-interaction-reality.md`
4. `action-routing.md`
5. `selection-model.md`
6. `drag-drop-contract.md`
7. `batch-action-contract.md`
8. `keyboard-interaction.md`
9. `explorer-integration.md`
10. `destructive-action-wording.md`
11. `interaction-test-report.md`
12. `evidence-manifest.json`
13. `W08_HANDOFF.md`

---

## 19. Definition of Done

必须真实证明：

```text
Double Click
+ Context Menu
+ File Drop Import
+ Track → Playlist Drag
+ Multi-select
+ Batch Actions
+ Keyboard Safety
+ Explorer Reveal
```

全部复用已有 authorities/use-cases。

最后：

```text
W07_STATUS = PASS | BLOCKED
W08_GATE = PASS | BLOCKED
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```
