# Import Pipeline

```text
Add Songs / Empty State
-> one native multi-file dialog
-> extension allowlist
-> readable regular-file and non-zero checks
-> lightweight container/header validation
-> normalized-path lookup
-> embedded ID3v2 metadata or WAV duration when available
-> safe filename / unknown-artist fallback
-> LibraryTrack creation or ALREADY_EXISTS
-> atomic LocalStateStore write
-> renderer refresh
-> source resolution by Track ID
-> existing PlaybackService
```

Per-file results are `IMPORTED`, `ALREADY_EXISTS`, `UNSUPPORTED`, `INVALID`, or `FAILED`; batch counters are returned over IPC. A bad file does not roll back successful siblings and never creates a half-record.

Supported extensions and validated headers: MP3, WAV, FLAC, M4A, AAC and OGG. The lightweight reader extracts ID3v2 title/artist/album and WAV duration; unsupported or malformed metadata falls back safely. Full codec decoding remains the Chromium playback engine's final capability check.
