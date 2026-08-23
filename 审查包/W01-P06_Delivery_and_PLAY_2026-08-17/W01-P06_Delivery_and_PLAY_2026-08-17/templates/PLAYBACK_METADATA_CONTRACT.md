# Playback Metadata Contract

## Server-side canonical fields

- track_id
- render_object_id
- playback_version
- duration_ms
- container
- codec
- sample_rate
- channels
- content_length
- etag
- supports_range
- ready_at
- access_class
- pipeline_version
- profile_version

## Client-safe fields

Decision which internal fields are omitted.

Suggested client payload:

```json
{
  "track_id": "trk_...",
  "title": "Track",
  "duration_ms": 123000,
  "playback_uri": "https://...",
  "uri_expires_at": "2026-08-17T09:00:00Z",
  "supports_range": true,
  "etag": "...",
  "container": "m4a",
  "codec": "aac"
}
```

## Rule

Never use `playback_uri` as persistent Track identity.
