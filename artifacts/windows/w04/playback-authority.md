# Playback Authority

`PlaybackService` is now the playback business authority. It owns a projected snapshot:

```text
currentTrackId, status, positionMs, durationMs, volume,
context, error, generation
```

The engine remains execution authority. UI is a command source and `onState` subscriber. Engine events pass through PlaybackService filtering before reaching UI event subscribers. Track/Playlist data remain in their W02/W03 authorities.

The existing `PlaybackQueue` class is retained only as a private ephemeral ordered context cursor. It has no persistence or product mutation APIs and is not the W05 formal Queue authority.
