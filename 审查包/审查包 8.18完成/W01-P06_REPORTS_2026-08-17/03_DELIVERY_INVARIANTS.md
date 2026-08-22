# 03 — Delivery Plane Invariants

**W01-P06 · 2026-08-17**

每条 invariant 标注：**实现位置 / 验证证据 / 状态**。`delivery.py` = `moodify-core-package/src/moodify/data_plane/delivery.py`；`test_delivery.py` = `moodify-core-package/tests/test_delivery.py`。

## DLV-INV-01 — READY Only
客户端只能获得 READY 对象的正式播放入口。
- 实现：`DeliveryService._ready_render()`（查 `jobs.current_state='READY' AND ready_object_id IS NOT NULL`）。
- 证据：TST-01（非 READY → `TRACK_NOT_READY`）。**状态：已实现+测试。**

## DLV-INV-02 — No Long-Lived Cloud Secret
移动端不持有长期 OSS / DB 凭证。
- 实现：客户端只收短 TTL 签名 URI（`URI_TTL_SECONDS=3600`）；签名密钥 `uri_signer_secret` 仅在服务端。
- 证据：TST-08（metadata JSON 无 accesskey/secret）；Android 扫描确认 APK 无云凭证（01 报告 §6）。**状态：已实现+测试（服务端）；APK 侧已扫描确认。**

## DLV-INV-03 — Playback URI Is Replaceable
客户端不能把临时签名 URL 当永久 Track identity。
- 实现：URI 含 `expires/nonce/sig`，过期即失效；`refresh()` 发新 URI。**状态：已实现+测试（TST-04/10）。**

## DLV-INV-04 — Track ID != URL
Track identity 独立于具体 CDN/OSS URL。
- 实现：`track_id`（`trk_<uuid7>`）与 `playback_uri`（`moodify://deliver/...`）分离；身份用 ID，不用 URL。**状态：已实现+测试（TST-10）。**

## DLV-INV-05 — Delivery Is Authorized
每次播放入口必须受用户/产品访问策略约束。
- 实现：`_check_access()` 按 `owner_scope` 校验。**状态：已实现+测试（TST-07）。**

## DLV-INV-06 — Expiry Is Recoverable
签名 URL 过期后可刷新，不必重新处理音频。
- 实现：`refresh()` 重新走 `playback_metadata`，不动 pipeline / 不重传 source / 不重 Render。**状态：已实现+测试（TST-04/06）。**

## DLV-INV-07 — Range-Friendly
长音频播放必须支持合理的 byte-range / streaming behavior。
- 实现：`PlaybackMetadata.supports_range=True`；`resolve_object()` 返回 `(bucket,key)` 供 adapter 按 range 取字节。
- 证据：TST-05。**状态：契约已实现+测试；真实 HTTP range 行为依赖交付 adapter/部署（BLOCKED，见 07 报告）。**

## DLV-INV-08 — Internal Complexity Hidden
客户端不需要知道 stem / analysis / Ear / DSP / pipeline 内部结构。
- 实现：客户端 metadata 隐藏 `pipeline_version/profile_version/render_object_id`（见 04 报告 client-safe 字段）。**状态：契约已实现。**

## DLV-INV-09 — Playback Failure != Compute Failure
播放失败不能把已经 READY 的 Job 重新变成 processing failure。
- 实现：`delivery.py` **不触碰 jobs 状态**（独立 `DeliveryError` taxonomy）。
- 证据：TST-09（delivery 失败后 `jobs.current_state` 仍为 READY）。**状态：已实现+测试。**

## DLV-INV-10 — Delivery Evidence Is Separate
播放事件可记录，但不能反向篡改生产 Evidence。
- 实现：playback evidence 用独立事件模型（10 报告），与 P03/P05 生产 evidence 分离、只读关联。**状态：契约已定义。**

## DLV-INV-11 — Final Render Version Is Visible Internally
播放会话必须能追溯到 render object/version。
- 实现：`PlaybackSession.render_object_id` + `PlaybackMetadata.render_object_id/pipeline_version`。**状态：已实现（服务端可追溯）。**

## DLV-INV-12 — Source Is Never Accidentally Exposed
若用户只应播放处理后的 render，不能因为 URL 设计错误暴露内部 source/stems。
- 实现：READY guard 只解析 `ready_object_id`（render）；签名定位符绑定具体 `render_object_id`，客户端无法凭 metadata 猜 source/stem key。**状态：已实现+测试（TST-03/05 反 orphan/越权）。**
