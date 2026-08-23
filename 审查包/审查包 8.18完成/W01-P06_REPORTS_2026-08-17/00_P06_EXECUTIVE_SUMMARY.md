# 00 — P06 Executive Summary

**Package:** W01-P06 — Delivery + PLAY
**执行时间:** 2026-08-17（代码）→ 2026-08-18（验证 + 报告）
**性质:** 播放交付主链（契约 + 服务端/客户端代码 + 测试）；真实部署/真机 BLOCKED

## 唯一问题

> 一个 READY Track，怎样成为用户按下 PLAY 就稳定听到的音频。

目标主链：`READY → Playback Metadata → Authorized Delivery → Android → PLAY`。

## 两个原子任务

- **T06-1 Playback Delivery Contract**：READY guard / metadata / 授权 / 签名 URL-vs-代理 ADR / range / expiry 刷新 / 交付证据。实现于 `moodify.data_plane.delivery`。
- **T06-2 Android PLAY Integration**：`PlaybackDeliveryClient`（READY→可播放 URI、过期刷新、失败映射）+ `PlaybackController` delivery-first 解析。

## 关键决策

1. **签发短 TTL 授权入口为原则（06 ADR）**：走「服务端签发限时签名入口」思想而非全代理；底层载体分两阶段（OSS 开通后 = A1 签名 URL；开通前 = A2 现有 music-media host 加签名），抽象 `moodify://deliver/` scheme 使二者可互换、不改客户端契约。
2. **复用现有 ExoPlayer**，不重写解码器/不换框架/不扩 UI（任务书 §9）。
3. **身份与 URL 分离**：`track_id` ≠ `playback_uri`；URI 可替换、过期可刷新、不重处理（DLV-INV-03/04/06）。
4. **播放失败不污染 READY Job**：独立 delivery taxonomy，不触碰 `jobs` 状态（DLV-INV-09，TST-09）。
5. **不立即接线 Android 生产**：真实 BFF 端点未部署，接线即走兜底——不制造「假装接通」假证据；给出部署后 ≤10 行最小接线方案（08 报告）。

## 验证

- 服务端：**47/47 PASS**（delivery 10 + data_plane 9 + control 12 + pipeline 16）；P06 自有文件 ruff 全过。
- Android：**6/6 JVM 测试 PASS**（本包修复 1 个 client bug + 2 个 test bug 后）。
- 真机 E2E：**BLOCKED**（未伪造）。

## 本包修复的 Android 缺陷

`PlaybackDeliveryClient.resolve` 丢失结构化失败码（client bug）；tst04/tst07 两个 test bug。修复后全绿。

## Gate

- P06-0 / P06-1 / P06-2 三 Gate 全过（READY 契约、数据访问、Android 现状扫描）。
- 未触发 `READY_CONTRACT_INCOMPLETE` / `DELIVERY_SECURITY_INVALID`。

## 事实边界（不虚构）

1. 交付层为**库内服务 + 本地对象存储验证**；真实 BFF 端点 / OSS 签名 / 真机 PLAY **均未部署/未执行 → BLOCKED**。
2. 现状生产播放仍是**无鉴权静态 CDN URL**；签名端点上线前该风险存在（11 报告）。
3. `duration_ms/sample_rate/channels` 当前为 0（VALIDATE metrics 未按 object 持久化，P07 补）。

**完成后停止，等待人类审核，不进入 P07。**
