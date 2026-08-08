# Lyric Alignment API 契约（Phase F）

任务：DSK-MFY-LYRIC-TEMPORAL-ALIGNMENT-001
日期：2026-08-08
实现：`moodify-core-package/src/moodify/api/routes/lyric_align.py`

## POST /api/v1/lyric-alignments

### 请求体

```json
{
  "audio_asset_id": "up-xxxx",
  "lyrics": "权威歌词全文",
  "language": "fr",
  "translation_lyrics": "可选翻译（行数须与歌词一致）",
  "score_asset_id": null,
  "midi_asset_id": null,
  "requested_granularity": ["line", "word"]
}
```

- `audio_asset_id`：当前解析自移动端 v1 uploads 注册表；未找到返回 `NOT_FOUND`。
- `score_asset_id` / `midi_asset_id`：Phase C 未实现，传入返回 `NOT_IMPLEMENTED`。
- 多余字段：`extra="forbid"` 拒绝（422）。

### 响应

```json
{
  "status": "PUBLISHABLE|REVIEW_REQUIRED|DRAFT_ONLY|FAILED",
  "alignment_asset_id": "al-xxxxxxxx",
  "exports": {"lrc": "lyrics.lrc", "enhanced_lrc": "lyrics.enhanced.lrc",
              "srt": "lyrics.srt", "ass": "lyrics.ass"},
  "quality": {"coverage": 0.0, "mean_confidence": 0.0, "unaligned_token_ratio": 0.0},
  "review_regions": [],
  "created_at": "ISO-8601"
}
```

- `exports` 值仅为相对文件名（不泄漏文件系统路径）。
- 当前后端固定 `heuristic`（DRAFT_ONLY）；WhisperX 生产后端需服务端安装 `moodify[ml]` 后接入。

### 错误体（与 mobile v1 契约一致）

```json
{"error": {"code": "NOT_FOUND|NOT_IMPLEMENTED|VALIDATION|SERVER_ERROR",
           "message": "...", "request_id": "..."}}
```

## 本地验证

```bash
cd moodify-core-package
python -m pytest tests/lyric_align/test_api_lyric_align.py -q
```
