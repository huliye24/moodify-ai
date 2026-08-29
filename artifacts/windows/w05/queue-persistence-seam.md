# Queue Persistence Seam for W08

`QueueService.snapshot()` returns serializable:

```text
items[id, track_id, origin_type, origin_id, inserted_at]
current_item_id
source_context
updated_at
```

W08 may decide whether and how to restore this snapshot, current item, playback position and paused status. W05 does not persist engine objects, source URLs, callbacks, component state or playback generation, and does not auto-start sound after restart.
