# Referential Safety Contract

W03 的最大风险不是“功能不能点”，而是错误删除关系和数据。

## Delete Playlist

必须：

```text
Playlist gone
PlaylistItems gone
Tracks remain
Files remain
Other Playlists remain
```

## Remove PlaylistItem

必须：

```text
Target PlaylistItem gone
Track remains
File remains
Other PlaylistItems remain
```

## Track Missing

必须：

```text
PlaylistItem may remain
Track remains
availability changes
```

## Remove Track from Library

W03 不重新定义 W02 行为。

如果 W02 允许 Library membership 删除但 Track entity 仍为 relation 保留：
复用。

如果 W02 会阻止删除被 Playlist 引用的 Track：
复用。

若行为不明确：
标 `BLOCKER`，不要自造 cascade。

## Foreign Keys / Relations

如果 persistence 支持 FK：

- 禁止 accidental cascade 删除 Track
- cascade Playlist → PlaylistItem 可以合理使用
- Track → PlaylistItem cascade 需要产品决策，不应默认开启

## File Deletion

W03 中：

```text
filesystem delete = FORBIDDEN
```
