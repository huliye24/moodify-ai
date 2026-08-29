# Codex 执行任务书 — MFY-WIN-W06-LIBRARY-EXPERIENCE-001

## 0. 执行模式

```text
PACKAGE = W06
FOCUS = LIBRARY_EXPERIENCE
CANON_CHANGE = NO
VISUAL_REDESIGN = FORBIDDEN
START_W07 = NO
```

必须复用 W02-W05 已建立的 authorities。

## 1. Phase 0 — Preflight

读取 W05 产物，输出：

`artifacts/windows/w06/preflight.md`

至少确认：

```text
W05_STATUS =
W06_GATE =
TRACK_AUTHORITY =
LIBRARY_AUTHORITY =
PLAYLIST_AUTHORITY =
PLAYBACK_AUTHORITY =
QUEUE_AUTHORITY =
HISTORY_CURRENT_REALITY =
FAVORITE_CURRENT_REALITY =
SEARCH_CURRENT_REALITY =
SORT_CURRENT_REALITY =
```

若 `W06_GATE != PASS`，停止。

## 2. Phase 1 — Audit Existing Library Experience

先定位真实实现：

- current library route/page
- all songs view
- favorites
- history/recently played
- recently added
- search input
- sort controls
- metadata rendering
- current sidebar entries
- duplicate local state
- placeholders
- performance bottlenecks

输出：

`artifacts/windows/w06/current-library-experience.md`

现有功能统一标：

```text
WORKING
PARTIAL
PLACEHOLDER
BROKEN
MISSING
UNKNOWN
```

## 3. Phase 2 — All Songs

建立/修复 All Songs view：

```text
Library authority
→ stable Track list
→ view projection
```

最少展示：

```text
title
artist
album (if available)
duration
availability
```

测试：

- empty library
- 1 Track
- many Tracks
- unavailable Track
- metadata missing
- Chinese metadata
- long title
- duplicate names

## 4. Phase 3 — Recently Added

Recently Added 应来自稳定时间 authority：

```text
Track.created_at
or
LibraryMembership.added_at
```

禁止用 UI mount time 或临时内存顺序。

默认建议：

```text
newest first
```

## 5. Phase 4 — History / Recently Played

建立/修复最小 History authority。

候选模型：

```text
HistoryEntry
- id
- track_id
- played_at
- event_type / meaningful_play
```

必须定义“何时算播放过”。

不要简单用：

```text
点击 Play 按钮
→ 立即写 history
```

推荐使用：
- engine 确认 PLAYING
- 或超过最小播放阈值
- 或 pending → threshold commit

Recently Played 推荐为：

```text
History
→ sort played_at desc
→ unique by track_id
```

输出：

`artifacts/windows/w06/history-event-policy.md`

## 6. Phase 5 — Favorites

建立/修复：

```text
Favorite
- track_id
- created_at
```

要求：

- favorite
- unfavorite
- idempotent
- restart persistence
- unavailable Track 可保留
- no Track metadata copy
- remove-from-library interaction 明确

## 7. Phase 6 — Search

最低搜索字段：

```text
title
artist
album
```

要求：

- trim whitespace
- Unicode-safe
- Chinese
- case-insensitive where valid
- partial match
- empty query returns base view
- rapid typing stable
- null metadata safe

Search result 只能引用现有 Track，不建立新 Track copies。

## 8. Phase 7 — Sort

最少支持：

```text
Title
Artist
Recently Added
Duration
```

若现有 metadata 不足，可明确缩减，但必须记录。

要求：

- deterministic
- stable tie-breaker
- null metadata rule
- unavailable Track safe
- 不写回 Playlist/Queue order

## 9. Phase 8 — Combined Search + Sort

统一 pipeline：

```text
Authority
→ Base View
→ Search Filter
→ Sort Projection
→ Render
```

例如：

```text
Favorites
→ search "blue"
→ sort by artist
```

不得产生第二套 collection authority。

## 10. Phase 9 — Track Actions Integration

所有 view 复用同一 Track actions：

```text
播放
下一首播放
添加到播放队列
添加到歌单 >
收藏 / 取消收藏
在资源管理器中显示（如安全支持）
从音乐库移除
```

不同 view 禁止各自实现不同业务逻辑。

## 11. Phase 10 — Recently Played Integration

History 写入必须由 Playback authority 的稳定事件驱动。

至少处理：

- play accepted
- immediate pause
- seek
- track switch
- ended
- error
- same Track repeated
- Queue advance

## 12. Phase 11 — Empty States

### All Songs
```text
还没有音乐
添加本地歌曲
```

### Favorites
```text
还没有收藏
```

### Recently Played
```text
还没有播放记录
```

### Search
```text
没有找到匹配的歌曲
```

保持极简，不增加教学卡片。

## 13. Phase 12 — Metadata Safety

处理：

```text
null title
null artist
null album
0 duration
invalid duration
very long text
Unicode
emoji
```

Fallback 推荐：

```text
title → filename stem
artist → 未知艺术家
album → 未知专辑 / omit
duration → --:--
```

## 14. Phase 13 — Performance Baseline

至少测试：

```text
100 tracks
1,000 tracks
5,000 tracks
```

允许 synthetic metadata，不需要私人音乐。

观察：

- first render
- search typing
- sort
- favorite toggle
- view switching
- memory trend
- rerender behavior

只有有证据时才引入 virtualization/index。

输出：

`artifacts/windows/w06/performance-baseline.md`

## 15. Phase 14 — Persistence

必须持久化：

```text
Favorites
History
```

Search query 不必持久化。

Sort preference 可以：
- 放入现有 AppState
- 或每次恢复默认

但必须写清。

## 16. Phase 15 — Removal Interactions

从 Library 移除 Track 后：

### Favorite
行为必须明确。

### History
推荐保留历史事件，但 projection 必须安全。

最终以 W02 Track lifecycle 为准，不得制造 referential corruption。

## 17. Phase 16 — Tests

### All Songs
- empty
- metadata fallback
- unavailable
- ordering

### Favorite
- favorite
- unfavorite
- idempotency
- restart

### History
- meaningful play
- repeated play
- restart
- error
- Queue advance

### Search
- title / artist / album
- Chinese
- partial
- empty
- null

### Sort
- title / artist / added / duration
- null
- ties

### Integration
- search → play
- favorite → queue
- recent → playlist

### Performance
- 100 / 1000 / 5000

### Regression
- Library
- Playlist
- Playback
- Queue
- no second Track authority

## 18. Required Outputs

写入：

`artifacts/windows/w06/`

至少：

1. `W06_IMPLEMENTATION_REPORT.md`
2. `preflight.md`
3. `current-library-experience.md`
4. `library-view-contract.md`
5. `favorite-authority.md`
6. `history-authority.md`
7. `history-event-policy.md`
8. `search-contract.md`
9. `sort-contract.md`
10. `metadata-fallback-policy.md`
11. `performance-baseline.md`
12. `test-report.md`
13. `evidence-manifest.json`
14. `W07_HANDOFF.md`

## 19. Definition of Done

必须真实证明：

```text
All Songs
+ Recently Added
+ Recently Played
+ Favorites
+ Search
+ Sort
+ Track Actions
+ Persistence
```

并且它们全部复用同一 Track / Library authority。

最后：

```text
W06_STATUS = PASS | BLOCKED
W07_GATE = PASS | BLOCKED
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```
