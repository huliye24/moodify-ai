# QueueItem Contract

```text
id            independent UUID
track_id      stable Library Track reference
origin_type   PLAYLIST | LIBRARY | MANUAL | PLAY_NEXT
origin_id     optional source collection ID
inserted_at   ISO timestamp
```

QueueItem contains no Track title, artist, path or source URL. Duplicate Tracks are allowed and distinguished by QueueItem ID. Current identity uses QueueItem ID, never Track ID or array index alone.
