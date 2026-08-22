# 02 — Delivery Architecture

**W01-P06 · 2026-08-17**

## 目标主链

```text
READY (P04 Job, ready_object_id)
   │
   │  Android: GET PlaybackMetadata
   ▼
Moodify Delivery Authority (服务端)
   │
   ├── verify READY          (DLV-INV-01)
   ├── verify access scope   (DLV-INV-05)
   ├── verify object exists  (DLV-INV-12 反 orphan)
   └── issue playable entry  (short-TTL signed URI / session)
            │
            ▼
      Object Delivery  (render object, byte-range)
            │
            ▼
      Media3 / ExoPlayer
            │
            ▼
           PLAY
```

## 已实现（代码，本地验证）

服务端交付层 `moodify-core-package/src/moodify/data_plane/delivery.py`：

- `DeliveryService.playback_metadata(track_id, user_scope, ...)` = 逻辑接口 `GET /tracks/{track_id}/playback` 等价物。
- `_ready_render()`：READY guard——查 authoritative `jobs.current_state='READY' AND ready_object_id IS NOT NULL`（最新），再核 `objects` 行与对象存储 `head()` 存在性。
- `_check_access()`：按 `track.owner_scope` 做访问域校验（DLV-INV-05）。
- `_sign_uri()` / `_verify_uri()`：HMAC-SHA256 短 TTL 签名定位符（`moodify://deliver/...` 抽象 scheme），含 `expires/nonce/sig`。
- `PlaybackSession`：轻量会话（非第二套任务系统），用于交付排障与证据关联。
- `refresh()`：过期刷新，不重处理、不重传、不失 identity（DLV-INV-06）。
- `resolve_object()`：签名定位符 → `(bucket, object_key)`，供交付 adapter 取字节。

> 设计要点：`playback_uri` 用**抽象 `moodify://deliver/` scheme** 而非写死 CDN/OSS URL——Track identity 与具体交付 URL 解耦（DLV-INV-03/04），把「签名 URL vs 代理」的落地推迟到 ADR（06 报告）与真实基础设施。

## 边界（Boundary）

Android 客户端**知道**：

- track identity（`track_id`）
- playback metadata
- playable URI / session
- playback state（客户端态，非 Job 态）

Android 客户端**不需要知道**：

- stem refs / 处理链 / 内部 judgment / Ear
- database credentials / object-store credentials
- pipeline_version / profile_version / 内部 object identity（服务端可追溯即可，客户端隐藏）

内部处理复杂度（P05 pipeline / Ear / DSP）**不进入客户端**（DLV-INV-08，对外产品面只暴露 PLAY）。

## 与现实拓扑的对应（P02 Network Matrix）

- NW-02：Android → LA `music-bff`（playback URL / metadata）。现状无鉴权；**目标 = API 签发**。
- NW-03：Android → LA `music-media` 静态音频（resolveUrl）。现状无鉴权静态 URL；**目标 = BFF 签发限时 URL（P06 范围）**。
- 交付 Authority 逻辑上属 BFF/控制面一侧；OSS 为 P03 规划的对象存储（**NOT_PROVISIONED**）。

## 部署现状（事实，不虚构）

- `DeliveryService` 为**库内服务 + 本地对象存储验证**；**未接进任何运行中的 HTTP 端点**。
- 真实 BFF `/tracks/{id}/playback` 路由、真实签名 CDN URL / 代理、真实 OSS：**均未部署 → BLOCKED**（见 06 ADR、11 安全、14 验收）。
