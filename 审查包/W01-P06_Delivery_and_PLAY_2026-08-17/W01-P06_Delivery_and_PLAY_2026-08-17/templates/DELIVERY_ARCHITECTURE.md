# Delivery Architecture

```text
Android
   │
   │ GET PlaybackMetadata
   ▼
Moodify API / Delivery Authority
   │
   ├── verify READY
   ├── verify access
   └── issue playable entry
            │
            ▼
      Object Delivery
            │
            ▼
      Media3 / ExoPlayer
            │
            ▼
           PLAY
```

## Boundary

The Android client knows:

- track identity
- playback metadata
- playable URI/session
- playback state

The Android client does not need:

- stem refs
- processing chain
- internal judgment
- database credentials
- object-store credentials
