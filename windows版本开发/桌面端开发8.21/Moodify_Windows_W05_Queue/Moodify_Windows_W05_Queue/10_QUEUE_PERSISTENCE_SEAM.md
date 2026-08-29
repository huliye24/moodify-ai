# Queue Persistence Seam for W08

W05 不完成 restart restore。

但必须让 Queue 可快照化。

## Candidate Snapshot

```text
queue_items [
  queue_item_id
  track_id
  origin
]
current_queue_item_id
source_context
updated_at
```

## W08 Future Restore

W08 将决定：

- restart 后是否恢复 Queue
- 是否恢复 current item
- 是否恢复 position
- 是否恢复 paused state
- 是否自动播放

通常：

```text
restore state
but do not auto-start sound
```

## Do Not Persist

- player objects
- callbacks
- renderer component refs
- audio element
- generation token as durable session identity
