# MFD-001 Desktop–Cloud 就绪度

**生成时间:** 2026-08-20
**任务:** MFD-001 阶段 A5 — Cloud/Playback 接口盘点

---

## 接口就绪度矩阵

| 能力 | 状态 | 证据路径 | Desktop 适用性 |
|---|---|---|---|
| **公开 API (HTTP)** | EXISTS_AND_VERIFIED | BffClient.kt + bff/main.py | ✅ 直接可用 |
| **内部 API** | EXISTS_BUT_INTERNAL | moodify-api :8000 (service-key) | ❌ Desktop 不使用 |
| **BFF** | EXISTS_AND_VERIFIED | moodify-music-bff :8100 | ✅ Desktop 主要接口 |
| **Auth (公开)** | DOCUMENTED_ONLY | routes_auth.py | ⚠️ 需确认是否强制 |
| **Users** | PARTIAL | routes_users.py | ⚠️ Alpha 可能不需要 |
| **Tracks** | EXISTS_AND_VERIFIED | routes_tracks.py + BffClient | ✅ 核心 |
| **Albums** | UNKNOWN | 需进一步检查 | ℹ️ 低优先级 |
| **Playlists** | EXISTS | routes_playlists.py | ⚠️ MFD-004+ |
| **Queue** | MISSING | 无专用 queue endpoint | 🔶 MFD-004 用 local queue |
| **Playback/Media** | PARTIAL | bff/media.py | ⚠️ 需验证 signed URL |
| **Upload** | EXISTS | routes_intents.py | ❌ Desktop 不做 |
| **Processing Status** | INTERNAL | core-package | ❌ Desktop 不接触 |
| **Service-key** | INTERNAL | 杭州 API | ❌ Desktop 不持有 |
| **CORS** | UNKNOWN | nginx/cloudflared 配置 | ⚠️ 需验证 |
| **Origin Assumptions** | UNKNOWN | rongjinwenchuan.xyz | ⚠️ 需验证 |

## 详细分析

### 1. 公开 API (Player API)

**状态: EXISTS_AND_VERIFIED**

Android 已成功调用以下端点：

```
GET https://rongjinwenchuan.xyz/api/v1/music/bootstrap
GET https://rongjinwenchuan.xyz/api/v1/music/catalogue
GET https://rongjinwenchuan.xyz/api/v1/music/tracks/{id}
```

这些是 Desktop 的主要数据源。

### 2. 认证 (Auth)

**状态: DOCUMENTED_ONLY (可能可选)**

观察：
- `BffClient.kt` 没有 Authorization header
- 注释明确说 "public /api/v1/music only"
- 但 `routes_auth.py` 存在

**结论:** Alpha 阶段可能不需要用户认证，或使用非常简单的机制。MFD-003 需要确认。

### 3. Track 元数据

**状态: EXISTS_AND_VERIFIED**

从 `routes_tracks.py` (21161 bytes) 和 `models.py` (18571 bytes) 看：
- Track 模型完善
- 支持 versioning, playback status
- 有 audioAssetKey 字段用于媒体交付

### 4. Playback / Media URL

**状态: PARTIAL (需验证)**

关键问题：
- `audioAssetKey` 如何转换为实际音频 URL?
- 是否有 signed URL 机制?
- 是否支持 range request?

**证据:**
- `bff/media.py` 存在 (2534 bytes)
- Android 通过某种方式获取可播放 URL

**阻塞风险:** 🔶 **MEDIUM** — MFD-003 必须解决

### 5. Session 管理

**状态: MISSING (公开 API)**

当前没有看到:
- 用户 session endpoint
- Token refresh mechanism
- Session expiry handling

**Alpha 影响:** 可能暂不需要，但 MFD-003 需要明确策略。

### 6. CORS / Origin

**状态: UNKNOWN**

需要验证：
- Electron renderer 发起的请求是否能被 BFF 接受
- 是否需要特殊 CORS header
- cloudflared 隧道是否有 origin 限制

**阻塞风险:** 🔶 **MEDIUM** — 可能影响开发

---

## 总结

### 已就绪 (Desktop 可直接使用)
- [x] 公开 BFF 端点 (bootstrap/catalogue/tracks)
- [x] Track 数据模型
- [x] 错误响应格式

### 需要在 MFD-003 确认/建立
- [ ] Media URL 交付机制 (signed URL?)
- [ ] Auth 策略 (是否必须)
- [ ] CORS 配置
- [ ] PlaybackManifest 概念是否已存在
- [ ] Range request 支持

### Desktop 不需要
- [ ] Internal API (service-key)
- [ ] Ear internal endpoints
- [ ] Processing pipeline
- [ ] Database direct access

---

*本评估基于代码阅读和 Android 实现分析。所有网络相关能力需要在 MFD-003 进行真实请求验证。*
