# QueueItem Contract

推荐：

```text
QueueItem {
  id
  track_id
  origin_type
  origin_id
  inserted_at
}
```

字段名可适配现有实现。

## Why QueueItem ID Matters

如果 Queue 允许：

```text
T1
T2
T1
```

那么仅靠 `track_id` 无法区分两个 T1。

因此：

```text
QueueItem.id != Track.id
```

## Origin

可选但推荐：

```text
PLAYLIST
LIBRARY
MANUAL
PLAY_NEXT
```

只用于解释来源 / analytics / future UI。

Origin 不能反向成为 Playlist authority。

## Current Identity

优先：

```text
current_queue_item_id
```

而不是只存 current index。

index 可作为派生值。

## Deletion

QueueItem 删除：

```text
Track remains
Playlist remains
File remains
```
