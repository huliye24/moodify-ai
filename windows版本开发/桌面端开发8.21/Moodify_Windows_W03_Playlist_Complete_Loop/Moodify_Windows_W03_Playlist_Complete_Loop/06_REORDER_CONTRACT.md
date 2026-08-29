# Playlist Reorder Contract

## 1. Goal

用户调整歌单顺序后，顺序成为长期歌单状态。

## 2. Domain Form

可采用：

```text
PlaylistItem.position
```

或现有系统等价结构。

## 3. Required Properties

- deterministic
- persisted
- restart-stable
- no duplicate positions
- no lost items
- safe after add/remove
- no dependency on current DOM order as sole truth

## 4. Operation

推荐接口：

```text
reorderPlaylist(
  playlist_id,
  ordered_track_ids / ordered_item_ids
)
```

如果同一 Track 未来允许重复，应优先使用 PlaylistItem ID，而非 Track ID。

## 5. Atomicity

一次 reorder 应尽量原子提交。

不要出现：

```text
position 1 updated
position 2 failed
→ half-reordered playlist
```

## 6. Unavailable Track

Unavailable Track 仍参与 ordering。

## 7. Playback

W03 只保证 UI / Playlist 顺序稳定。

正式把 Playlist 转换成 Queue 的行为留给 W05。
