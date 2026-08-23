# W01 Playback Flow

Cloud path:

```text
MinimalPlayer mount -> BffClient.playableCatalogue()
-> GET catalogue + per-track detail -> Track DTO
-> PlaybackService.loadQueue() -> PlaybackQueue
-> Track.audio_asset_key -> BffClient.mediaUrl()
-> ChromiumPlaybackEngine.load() -> one HTMLAudioElement
-> play/pause/seek/ended/error events
-> PlaybackService subscribers -> React display state
```

Local path:

```text
file input -> File objects -> generated local Track IDs
-> URL.createObjectURL(File) -> PlaybackService.loadLocalQueue()
-> PlaybackQueue -> ChromiumPlaybackEngine -> UI events
```

`PlaybackService` is the queue/current-track authority. `ChromiumPlaybackEngine` is the playback-state and timing authority. Ended advances through the service; next/previous use the in-memory queue. The queue, current item, position, and volume are not restored from `LocalStateStore`, despite fields existing in its schema. Local blob URLs are revoked on replacement/unmount and cannot survive restart.
