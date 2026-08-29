# 04 — Playback Metadata Contract

**W01-P06 · 2026-08-17 · 实现：`delivery.py::PlaybackMetadata`**

## Server-side canonical fields（服务端全量，可追溯）

| field | 来源 | 说明 |
|---|---|---|
| `track_id` | P03 tracks | 稳定 Track 身份（`trk_<uuid7>`），**永不可用 URL 替代** |
| `playback_version` | object.pipeline_version | 播放版本标识 |
| `render_object_id` | P05 ready_object_id | 内部 final render 身份（traceability） |
| `title` | tracks | 标题 |
| `duration_ms` | VALIDATE metrics | 时长（**当前 0 = 未持久化**，见「已知缺口」） |
| `container` | object.mime_type | 首阶段 `wav`（P05 Render Contract） |
| `codec` | 派生 | `pcm_s16le`（wav） |
| `sample_rate` | VALIDATE | 当前 0 = 未提供 |
| `channels` | VALIDATE | 当前 0 = 未提供 |
| `content_length` | object.byte_size | 字节数 |
| `playback_uri` | 签发 | 临时授权 URI（可替换） |
| `uri_expires_at` | 签发 | 过期时间（ISO8601） |
| `supports_range` | 固定 true | seek 支持 |
| `etag` | object.content_hash[:16] | 缓存校验 |
| `ready_at` | job.finished_at | READY 时间 |
| `pipeline_version` | object | 内部（客户端隐藏） |
| `profile_version` | object.artifact_role | 内部（客户端隐藏） |

## Client-safe fields（对客户端隐藏内部字段）

隐藏：`pipeline_version`、`profile_version`、`render_object_id`（内部 object identity）。
理由：DLV-INV-08（内部复杂度不外泄）。服务端仍可追溯（DLV-INV-11）。

建议客户端 payload：

```json
{
  "track_id": "trk_...",
  "title": "Track",
  "duration_ms": 123000,
  "playback_uri": "https://.../signed",
  "uri_expires_at": "2026-08-17T09:00:00Z",
  "supports_range": true,
  "etag": "\"abc123\"",
  "container": "wav",
  "codec": "pcm_s16le"
}
```

## Rule

- **永远不要把 `playback_uri` 当作持久 Track 身份**（DLV-INV-03/04）。
- 客户端隐藏字段不代表服务端丢失——`render_object_id/pipeline_version` 服务端留存用于追溯。

## 已知缺口（事实，不虚构）

1. `duration_ms / sample_rate / channels` 当前为 **0**：P05 VALIDATE/VERIFY metrics 尚未按 object 持久化（`delivery.py::_duration_ms` 注释「persisted per-object TBD in P07」）。**→ P07 补。**
2. `playback_uri` 当前是**抽象 `moodify://deliver/` scheme**，不是可直接喂给 ExoPlayer 的 `https://` URL；抽象→真实 URL 的映射取决于 ADR（06）与交付 adapter 部署（BLOCKED）。
3. 播放格式首阶段为 WAV/PCM16/44.1k（P05 Render Contract）。WAV 无压缩、体积大，移动流式不友好；**是否引入压缩流式格式（m4a/aac）= HUMAN_DECISION_REQUIRED**（P05 §12「自有格式/流式：P06+ 评估」），本包不擅自转码（P06 不重转码，任务书 §7）。
