# W01 Candidate Product Model

> 本文是**候选产品契约**，不是要求 W01 直接重构。执行者必须先画出现实模型，再对照此模型给出 KEEP / REPAIR / MIGRATE。

## 1. Model Overview

```text
Library
 └── Track ───────────────┐
                          │
Playlist                  │
 └── PlaylistItem ────────┘

Queue
 └── QueueItem → Track

PlaybackSession
 └── current Track
 └── queue cursor
 └── position
 └── volume / playback mode

Favorite → Track
History  → Track + listening event

CloudTrack ↔ Track (explicit mapping only)
AppState → window/UI preferences, not business truth
```

---

## 2. Track

### Responsibility
代表“一首可被 Moodify 识别和引用的音乐资产”。

### Candidate fields

```text
id
source_kind: LOCAL | CLOUD
source_ref
title
artist
album
duration_ms
format
availability
created_at
updated_at
```

### Invariants

- `Track.id` 应稳定，不因 UI 显示名称变化而变化。
- display metadata 不能作为唯一 identity。
- Windows raw path 不宜在没有审计的情况下被当作唯一永恒 identity。
- 本地文件失效时，Track 可以进入 `UNAVAILABLE`，不应默认级联删除歌单引用。
- Local Track 与 CloudTrack 不应因为“都是一首歌”而静默共用同一个未经定义的 ID。

---

## 3. Library

### Responsibility
“用户在 Moodify 中拥有、可浏览、可引用的 Track 集合”。

Library 不是：

- 当前播放队列
- 某个歌单
- 文件选择器的临时结果

### Invariants

- import 产生 / 关联 Track 后，Library 应成为稳定用户资产视图。
- duplicate import 必须有确定行为。
- 删除 Library entry 与删除原始文件必须严格区分。

---

## 4. Playlist

### Responsibility
用户命名的长期组织结构。

Candidate fields:

```text
id
name
created_at
updated_at
sort_policy
```

Playlist 不直接承担当前播放位置。

---

## 5. PlaylistItem

### Responsibility
建立：

```text
Playlist → Track
```

的显式 relation，并保存 ordering。

Candidate fields:

```text
id
playlist_id
track_id
position
added_at
```

### Why explicit relation matters

如果 Playlist 只是复制 Track metadata 或直接保存一组绝对路径，会导致：

- Track metadata 更新难以同步
- duplicate identity 混乱
- 文件移动后引用失效
- Library / Playlist 数据互相漂移
- 后续 CloudTrack 接入困难

W01 要确认当前实现属于哪一种。

---

## 6. Queue

### Responsibility
短期播放顺序。

Queue 与 Playlist 必须在概念上区分：

```text
Playlist = 用户长期组织
Queue    = 当前一次 listening session 的短期顺序
```

播放某个歌单时可以**生成 Queue**，但不应因为 Queue 调序而反写 Playlist。

---

## 7. PlaybackSession

### Responsibility
当前播放上下文。

Candidate fields:

```text
current_track_id
queue_id / queue_snapshot
queue_cursor
position_ms
volume
repeat_mode
shuffle_state
updated_at
```

### Invariant

PlaybackSession 可以持久化用于恢复，但不应修改 Playlist 的长期 ordering。

---

## 8. Favorite

收藏是一种 relation，不应复制整首 Track。

```text
Favorite(user/local-profile, track_id, created_at)
```

Windows 1.0 是否启用由后续 W06 决定；W01 只确认当前是否已有 authority。

---

## 9. History

History 是 listening event，不是 Track 的单个 `last_played` 就能完整表示。

后续可以最小化，但 W01 先确认当前系统有没有埋下重复实现。

---

## 10. AppState

只保存 app / UI 层状态，例如：

- window geometry
- sidebar open/closed
- last route
- theme/appearance (if applicable)

业务实体不应只存在于 AppState 中。

---

## 11. CloudTrack

CloudTrack 代表服务器可播放 / 可准备的远端资产 identity。

W01 不接云端生产链路，只确认桌面层当前是否已有 CloudTrack / remote URL / media ID 之类的数据概念。

禁止把未验证的云端能力写成已上线能力。

---

## 12. Assessment Rule

对每个实体给出：

### KEEP
当前 authority 清晰、数据关系稳定，可直接复用。

### REPAIR
概念和 authority 基本正确，仅缺行为或边界。

### MIGRATE
当前结构会造成后续 W02–W08 重复 authority 或数据丢失风险。

MIGRATE 必须说明：

```text
current
target
migration
compatibility
rollback
tests
```

W01 不执行大迁移。
