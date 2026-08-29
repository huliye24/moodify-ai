# Playback Command Contract

Supported commands:

- load cloud/local context at a stable index;
- `play`, `pause`, serialized `togglePlayPause`;
- clamped `seek` through the engine;
- clamped finite `setVolume`;
- serialized `previous` and `next` within current context;
- `stop`/dispose for lifecycle;
- `failSource` for resolver failures;
- `getPlaybackSnapshot` / `onState`.

At context boundaries previous/next are deterministic no-ops. Rapid next/toggle commands serialize so their final state matches engine reality.
