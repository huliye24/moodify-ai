# Playlist Invariants

## P-01 Playlist ≠ Queue

Playlist 是长期组织，Queue 是播放会话顺序。

W03 不建立正式 Queue authority。

## P-02 PlaylistItem References Track

推荐：

```text
PlaylistItem.track_id → Track.id
```

禁止复制：

```text
title
artist
path
duration
...
```

形成第二份 Track truth。

## P-03 Stable Ordering

排序必须在 domain / persistence 层有稳定 representation。

## P-04 Delete Playlist Is Non-destructive

删除歌单：

```text
delete Playlist
delete PlaylistItems
keep Tracks
keep files
```

## P-05 Remove Item Is Non-destructive

从歌单删歌：

```text
delete relation
keep Track
keep file
```

## P-06 Unavailable Track Can Remain

本地文件失效：

```text
PlaylistItem remains
Track remains
Track.availability = UNAVAILABLE
```

## P-07 Rename Preserves Identity

重命名歌单不能改变 Playlist ID。

## P-08 Duplicate Add Is Deterministic

推荐：

```text
same playlist + same track
→ ALREADY_IN_PLAYLIST
```

若产品确实允许重复，必须显式建模，而不是 accidental duplicates。

## P-09 Restart Is Hard Boundary

任何只存在内存的 Playlist 修改都不算完成。

## P-10 No Hidden Rebuild

不要为了修“添加歌曲”而新建：

- second playlist store
- second persistence
- UI-only playlist arrays
- player-owned playlist state

## P-11 Current Playback Survives Playlist Mutation

用户删歌单或移除其他 Track 时，不应使当前播放器崩溃。

## P-12 No Original File Deletion

任何 Playlist 操作都不得删除用户原始音频文件。
