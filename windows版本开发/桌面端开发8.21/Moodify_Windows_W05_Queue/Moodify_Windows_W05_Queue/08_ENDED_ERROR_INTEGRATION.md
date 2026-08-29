# Queue ↔ Playback Ended/Error Integration

## Ended

W04 提供 playback ended seam。

W05 接入：

```text
onPlaybackEnded(playback_generation, track_id)
→ verify active playback
→ verify current QueueItem
→ advance once
```

必须防止：
- duplicated callback
- stale generation
- old track ended
- current item removed race

## Error

```text
onPlaybackError(...)
→ record failure
→ if safe next exists:
     advance
  else:
     remain ERROR
```

## Bounded Skip

推荐：

```text
MAX_CONSECUTIVE_ERROR_ADVANCES
```

值按现有项目合理决定。

同时可以跟踪：

```text
visited QueueItem IDs
```

避免环。

## Queue Empty

ended/error 后若 Queue 无下一个：

```text
do not invent Track
do not random play
do not recommendation autoplay
```
