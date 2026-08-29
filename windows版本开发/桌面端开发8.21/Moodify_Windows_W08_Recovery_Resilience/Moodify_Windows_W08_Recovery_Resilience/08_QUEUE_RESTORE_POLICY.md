# Queue Restore Policy

## Restore Fields

```text
QueueItem IDs
track_ids
ordering
current_queue_item_id
origin/context
```

## Invalid Item

如果某一个 QueueItem：
- malformed
- Track not found
- invalid ID

推荐：

```text
drop that item
preserve remaining valid queue
```

## Current Item Missing

推荐：

```text
if current Track still valid:
    restore as detached/current state
else:
    choose no current item
```

不要偷偷跳到随机歌曲。

## Duplicate Tracks

允许，只要 QueueItem ID 不同。

## Playback Link

Queue 恢复后不直接 play。

只建立 sequencing state。
