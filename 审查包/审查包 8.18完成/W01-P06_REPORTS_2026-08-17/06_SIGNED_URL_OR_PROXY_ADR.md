# 06 — ADR: Signed URL vs Streaming Proxy

**W01-P06 · 2026-08-17 · 状态：DECIDED（契约层）/ 部署 BLOCKED**

## Problem

Android 应如何接收一个 READY render 的可播放入口？

## Option A — Signed Object URL

**Benefits**
- 更低 API 带宽（大文件直连对象存储/CDN）
- One Song 路径更简单
- 对象存储支持时原生 range/seek

**Costs/Risks**
- URL 过期管理
- 签名 query 泄露风险（日志/抓包）
- 间接暴露对象存储语义
- **现实约束：OSS NOT_PROVISIONED（P03 S-09）**——暂无对象存储可签

## Option B — API Streaming Proxy

**Benefits**
- 授权完全集中在 API
- 隐藏存储细节

**Costs/Risks**
- API 带宽（音频大文件全走 BFF）
- range/seek 需自行实现
- 多一层故障点

## 现实约束（决定因素）

1. **OSS 未开通**（P03 `OSSAdapter` 占位 raise `OSS_WRITE_BLOCKED`）→ 经典「OSS 签名 URL」当前无落地载体。
2. **现状交付 = LA `music-media` 静态 host**（`https://rongjinwenchuan.xyz/audio/<key>`，NW-03 current 无鉴权）。
3. 任务书 §5 决策原则：**最小可运行、最少新基础设施、最少带宽重复搬运**。

## Selected

- **decision**：**混合演进式 —— 「服务端签发短 TTL 授权定位符（Signed Entry）」为原则**，底层载体分两阶段：
  - **P06 契约层（本包）**：`DeliveryService` 签发 HMAC 短 TTL 签名定位符（`moodify://deliver/`，Track/URL 解耦）。**这是原则决策：走 Option A 的「签发限时入口」思想，而非 Option B 的全代理。**
  - **部署层（BLOCKED，待基础设施）**：把签名定位符映射为真实可播放 URL。落地点二选一，由基础设施就绪度决定：
    - **A1**：OSS 开通后 → OSS 签名 URL（P03 既定方向）。
    - **A2**：OSS 未开通前 → 现有 `music-media` host 加**限时签名 query**（如 nginx secure_link / BFF 签发 token），把 NW-03 从「无鉴权静态」升级为「限时签名」。
  - **不选 Option B 全代理**作为默认：带宽与 range 复杂度代价高，违背「最少带宽重复搬运」。仅当安全审计要求完全隐藏存储时再评估。

- **evidence**：P02 NW-03 target（BFF 签发限时 URL）、P03 S-09（OSS 服务端 only）、`delivery.py` 签名实现、TST-04（过期刷新）。
- **reason**：满足「最少新基础设施」同时把「无鉴权静态 URL」演进为「限时签名入口」；抽象 scheme 使 A1/A2 落地可互换而不改客户端契约。
- **TTL**：3600s（`URI_TTL_SECONDS`），可随安全评审收紧。
- **refresh**：过期 → 重新 `GET /tracks/{id}/playback` → 新 URI，同 identity（TST-04/10）。
- **fallback**：契约层无 fallback；Android 现状保留静态 CDN 兜底直至真实签发端点上线（01 报告 §7「remove later」）。
- **revisit trigger**：OSS 开通 / 安全审计要求隐藏存储 / 多区域 CDN 引入 / 付费墙需强鉴权。

## 不做（本包边界）

- 不实现 API 流式代理（Option B）。
- 不部署真实签名端点（BLOCKED，需基础设施 + 人类授权）。
- 不引入第二套交付/鉴权系统。
