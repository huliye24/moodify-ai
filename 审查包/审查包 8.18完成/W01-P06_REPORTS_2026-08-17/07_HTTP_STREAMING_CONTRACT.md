# 07 — HTTP Streaming Contract

**W01-P06 · 2026-08-17 · 状态：契约定义；真实 HTTP 行为依赖交付 adapter 部署（BLOCKED）**

## Required（服务端 / 交付 adapter 必须满足）

- **HTTPS**：生产仅 HTTPS（Android `usesCleartextTraffic="false"` 已强制）。
- **Content-Type**：与 P05 Render Contract 一致——首阶段 `audio/wav`（WAV/PCM16）。
- **Content-Length**：= `object.byte_size`（metadata `content_length`）。
- **ETag**：`"{content_hash[:16]}"`，用于缓存/一致性校验。
- **Accept-Ranges: bytes**：必须支持（DLV-INV-07）。
- **byte range semantics**：`Range: bytes=start-end` → `206 Partial Content` + `Content-Range`；不支持时 `RANGE_NOT_SUPPORTED`。
- **safe redirects**：签名 URL 若 302，须保持鉴权且不回跳泄露内部 key。
- **bounded timeout**：连接/读取超时（Android 现状 connect 10s / read 15s）。
- **retry-safe GET**：GET 幂等，可安全重试。
- **cache policy**：私有 render → `Cache-Control: private, no-store`（签名 URL 不可共享缓存）；ETag 供条件请求。
- **signed URL TTL / token TTL**：3600s，过期 `DELIVERY_URI_EXPIRED` → 刷新。

## Validation（部署后须逐项验证；当前 BLOCKED）

- [ ] first play
- [ ] seek forward
- [ ] seek backward
- [ ] resume
- [ ] partial network interruption
- [ ] expired delivery credential refresh
- [ ] object missing → OBJECT_NOT_FOUND

> 以上为真实 HTTP 行为，需交付 adapter / CDN / 对象存储就位后验证。本包只在契约层保证 `supports_range` 与 `resolve_object()` 可提供字节定位（TST-05）。

## 播放候选格式

由 P05 Render Contract 决定：**首阶段 WAV/PCM16/44.1k**。**P06 不重新转码**（任务书 §7）。
WAV 流式对移动端不友好（无压缩、体积大）；是否引入压缩流式格式 = HUMAN_DECISION_REQUIRED（见 04 报告缺口 3）。

## 现状（事实）

- 当前生产播放走 `https://rongjinwenchuan.xyz/audio/<key>` 静态 host（无鉴权、无签名、无 TTL）。
- 本契约的 range/签名/TTL 语义**尚未在任何运行端点生效** → 部署前为设计契约，部署后按上面 Validation 清单验收。
