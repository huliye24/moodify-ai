# Settings Schema

LocalState advances v5 → v6 and adds Settings schema v1:

```text
playback {
  preferred_output_device = SYSTEM_DEFAULT
  restore_volume = true
  autoplay_policy = OFF_ON_APP_LAUNCH
}
app {
  close_behavior = QUIT
  launch_at_startup = false
}
```

Validation limits device IDs, defaults invalid enums/types and rejects future Settings versions to safe defaults. Migration is idempotent and preserves durable collections. Settings corruption does not clear Library/Playlist/Favorite/History. Cloud/cache/storage fields are omitted because those capabilities are not live.
