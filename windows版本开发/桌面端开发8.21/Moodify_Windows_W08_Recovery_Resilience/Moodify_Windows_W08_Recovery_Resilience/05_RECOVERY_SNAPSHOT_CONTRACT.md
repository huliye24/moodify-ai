# Recovery Snapshot Contract

推荐结构：

```text
RecoverySnapshot {
  schema_version

  playback {
    current_track_id
    position_ms
    volume
    last_status
  }

  queue {
    items[]
    current_queue_item_id
    source_context
  }

  navigation {
    active_view
    active_playlist_id
  }

  window {
    x
    y
    width
    height
    maximized
  }

  timestamps {
    saved_at
  }
}
```

## Rules

- 所有引用必须是 stable ID
- 所有数字必须 validate/clamp
- enum 必须 validate
- 未知字段可忽略
- 缺失字段可 default
- 未来版本不得误当当前版本直接加载

## Forbidden

```text
audio engine
DOM nodes
Promise
callbacks
component refs
native handles
file handles
temporary selection
drag state
menu state
```
