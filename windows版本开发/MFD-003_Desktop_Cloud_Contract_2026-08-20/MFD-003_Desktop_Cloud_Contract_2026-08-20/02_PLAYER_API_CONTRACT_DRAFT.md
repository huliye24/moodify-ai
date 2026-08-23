# Moodify Player API — Contract Draft v0.1

本文件是 MFD-003 的目标形状，不代表 endpoint 已存在。

Codex 必须根据真实后端校准。

---

## Base

建议：

```text
/api/player/v1
```

---

## 1. Session

### `GET /session`

Response:

```json
{
  "user": {
    "id": "usr_xxx",
    "display_name": "..."
  },
  "session": {
    "expires_at": "2026-08-20T10:00:00Z"
  }
}
```

---

## 2. Library

### `GET /library/tracks`

Response:

```json
{
  "items": [
    {
      "id": "trk_xxx",
      "title": "Track",
      "artist": "Artist",
      "duration_ms": 180000,
      "playback_status": "READY",
      "version": "v1"
    }
  ],
  "next_cursor": null
}
```

---

## 3. Track

### `GET /tracks/{track_id}`

只返回用户产品层需要的信息。

---

## 4. Playback Manifest

### `GET /tracks/{track_id}/playback`

Response:

```json
{
  "track_id": "trk_xxx",
  "playback_id": "pb_xxx",
  "asset_version": "asset_v3",
  "stream_url": "https://...",
  "expires_at": "2026-08-20T10:10:00Z",
  "mime_type": "audio/flac",
  "duration_ms": 180000,
  "playback_policy": {
    "allow_seek": true,
    "allow_cache": false,
    "requires_online": true
  }
}
```

---

## 5. Errors

```json
{
  "error": {
    "code": "PLAYBACK_NOT_READY",
    "message": "Playback asset is not ready.",
    "retryable": true,
    "request_id": "req_xxx"
  }
}
```

---

## 6. 不应暴露的字段

以下默认禁止进入 Player API：

```text
internal_file_path
worker_id
service_key
bucket_secret
processing_graph
stems
raw_measurements
diagnosis
ear_judgment
preset_internal_parameters
model_trace
audit_internal
database_primary_key not intended for product
```

---

## 7. Status 建议

Track playback status：

```text
READY
PROCESSING
UNAVAILABLE
FAILED
```

不要把内部 16 态状态机完整暴露给客户端。

产品层状态应该是对用户行为有意义的压缩状态。
