# 11 — P06 Security Review

**W01-P06 · 2026-08-17 · 依据：Android 扫描（01 报告 §6）+ P02 Secret Ownership Matrix + delivery.py 实现**

## APK / Source Scan（对 `apps/music-android`）

- [x] **no OSS AccessKey** — 全仓扫描无任何 OSS 凭据（P02 S-09：OSS 未开通，凭据不落 Android）。
- [x] **no DB credential** — `BffClient` 注释明示 "Never talks to PolarDB; never holds internal service keys"。
- [x] **no processing API key** — 无外部处理 API key。
- [x] **no private key** — `SecureStore` 用本地 Keystore AES（不落盘密钥）。
- [x] **no long-lived bearer token** — V1 匿名收听，无 token；`SecureStore` 预留未用。
- [x] **no production debug endpoint** — 唯一硬编码 = 公开 BFF base + CDN host（非 debug）。

## Network

- [x] **HTTPS in production** — `usesCleartextTraffic="false"`（`AndroidManifest.xml:11`）。
- [x] **signed/proxy token bounded TTL** — 服务端 `URI_TTL_SECONDS=3600`。
- [x] **full signed URLs not retained in long-lived logs** — 契约要求（10 报告不采 signed query）；包内 `scripts/redact_delivery_url.py` 提供脱敏工具。
- [x] **object bucket not public-read by default** — P03 OSS policy 默认禁止 public-read；render 私有/受控。

## Authorization

- [x] **READY checked server-side** — `_ready_render()`（TST-01）。
- [x] **user/access scope checked server-side** — `_check_access()`（TST-07）。
- [x] **internal source/stems cannot be guessed/downloaded from client metadata** — 签名定位符绑定 `render_object_id`；客户端 metadata 隐藏内部 identity；source/stem key 不可猜（DLV-INV-12，TST-03/05）。

## Logging

- [x] **no credentials** — 客户端无凭证可记。
- [x] **no signed query strings** — 证据契约禁采完整 signed URL。
- [x] **correlation IDs available** — `PlaybackSession.correlation_id` 预留。

## 风险与遗留（事实记录，不修复）

1. **现状生产播放是无鉴权静态 CDN URL**（`rongjinwenchuan.xyz/audio/<key>`）：任何人拿到 `audioAssetKey` 即可下载。这正是 NW-03 target 要演进的；**签名端点未部署前该风险仍存在 → BLOCKED/部署后收敛**。
2. **签名密钥 `uri_signer_secret` 默认 `dev-secret`**：生产必须经服务端安全配置注入（P02 S-09 目标 Secret Manager / 服务端 env），**不得硬编码/入 Git**。当前为库默认占位。
3. **访问域为单维 `owner_scope`**：细粒度授权（账号/订阅）未实现，依赖鉴权上线（BLOCKED）。
4. 版本口径不一致（2.0.1 vs 3.1）→ HUMAN_DECISION_REQUIRED（见 01 报告 §0）。

## 结论

P06 契约与 Android 现状满足「移动端零长期云凭证、READY 服务端校验、身份与 URL 分离」。真实签名交付端点部署前，静态 CDN 无鉴权风险继续存在——这是基础设施 BLOCKED 项，不是本包能单方面关闭的。
