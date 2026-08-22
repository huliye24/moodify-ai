# Current Player Reality

Before W04, `PlaybackService` owned an in-memory sequence and current Track, while `ChromiumPlaybackEngine` owned one lazily-created `HTMLAudioElement`. The renderer separately mirrored status, position, duration and current metadata. Raw engine events were exposed directly, so late events were not filtered at the business boundary.

- Player instances: one service/engine per mounted `App`; production root mounts one.
- Current Track: PlaybackService sequence cursor.
- Playing/time/volume execution: engine/audio element.
- Next/previous: PlaybackService context cursor.
- Ended: renderer requested `next`; final item stayed ended.
- Source errors: engine emitted typed errors; unavailable resolution previously changed UI only.
- Persistence: LocalState fields existed, but no explicit snapshot seam.
