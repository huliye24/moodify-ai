# Recovery Snapshot Contract

LocalState schema v5 contains one `recovery` object with inner `schema_version = 1`:

```text
playback { current_track_id, position_ms, volume, last_status }
queue { items[id, track_id, origin_type, origin_id, inserted_at], current_item_id, source_context, updated_at }
navigation { active_view, active_playlist_id }
timestamps { saved_at }
```

Window bounds remain in the existing `LocalState.window` authority rather than being duplicated. All references are stable IDs; no URLs, paths, engines, callbacks, DOM/File objects, selections, drag/menu state or generations are stored.
