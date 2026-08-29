# Source Resolution Flow

```text
LibraryTrack.id
-> window.moodify.library.resolveSource
-> LibraryService availability/readability check
-> moodify-local://track/<id>
-> privileged main-process protocol
-> normalized stored source_ref
-> ChromiumPlaybackEngine.load
```

Playlist rows provide only `track_id`; they never provide paths. Unavailable resolution invokes `PlaybackService.failSource`, producing `SOURCE_UNAVAILABLE` and ERROR while retaining Track identity. Load/decode/play failures remain typed engine errors and do not delete Library or Playlist state.
