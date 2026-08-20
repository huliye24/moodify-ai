# Music Listening Product V1 — Audit & Evidence

**Package:** MFY_MUSIC_LISTENING_PRODUCT_V1_001 (49)
**Date:** 2026-08-14

## 1. 现状审计（KEEP / ADAPT / COMPLETE / ISOLATE）

| 资产 | 分类 | 结论 |
|---|---|---|
| 首页聆听优先（hero + 五曲 cadeau10 专辑 + 播放器） | **KEEP** | 31 包成果；单 audio 元素、无自动播放、Media Session、键盘控制齐全 |
| 播放器错误恢复 | **COMPLETE（本包）** | 补 onError → 诚实错误横幅（.player-error），不再静默 |
| 搜索/库/播放列表/工作室 | **KEEP** | 32 包成果，capability false 时禁用（nav-disabled） |
| BFF 播放事实（play-events/favorites/follows） | **KEEP** | 服务端幂等 set 语义（replayed=True 无重复行）+ 客户端 Idempotency-Key |
| 媒体根 Range 服务 | **KEEP（线上验证）** | LA 音频 5/5 Range 206 ✓；seek 依赖 Range 正确 |
| music-android 薄壳 | **ISOLATE** | 未达 V1 不阻塞 Web 上线；不冒充完整可用（33 包既定） |
| 发现排序 | **KEEP** | 编辑精选/为你推荐，无 Ear 实验指标参与（静态检查固化） |

## 2. 五曲播放矩阵（真实线上媒体，LA）

| 曲目 | Range(65536-131071) | 全量 | 结果 |
|---|---|---|---|
| je-ne-veux-pas-enfermer-ton-aujourdhui | 206 / 65536B | 200 / 1.7MB | ✓ |
| ne-vivons-pas-seulement-de-souvenirs | 206 / 65536B | 200 / 13.6MB | ✓ |
| nous-pouvons-nous-reconnaitre-encore | 206 / 65536B | 200 / 13.4MB | ✓ |
| ou-es-tu-maintenant | 206 / 65536B | 200 / 8.3MB | ✓（首请求瞬时超时，重试通过） |
| vieillir-et-devenir-nouveau-avec-toi | 206 / 65536B | 200 / 3.7MB | ✓（首请求瞬时超时，重试通过） |

- 206 + 精确字节 = 浏览器 seek 可正确工作；不缓存截断（nginx 静态缓存 1h 仅限静态文件，audio 目录走 alias）。
- 媒体 SHA-256 未被 UI 改造：静态检查断言 UI 无 AudioContext/MediaRecorder/canvas 音频管线（tests/listening-product.test.mjs）。

## 3. 验收对照（49 包 P0）

| P0 | 结果 |
|---|---|
| 匿名用户能发现并开始播放公开作品 | ✓ 首页五曲真实媒体；匿名无 actor 可播放 |
| seek 与 Range 正常，不缓存截断响应 | ✓ 5/5 Range 206；sw.js 音频 pass-through 不缓存 |
| Track/Creator/Library 关键路径无假入口 | ✓ 能力假时禁用（nav-disabled），无必败写请求 |
| 登录能力与服务器事实一致 | ✓ bootstrap capability 驱动 UI（静态检查固化） |
| favorites/follows 重试无重复 | ✓ 服务端 set 语义 + 客户端幂等键（双层检查） |
| 播放器不遮挡移动内容且键盘可用 | ✓ 78px 移动播放器 + 内容 padding；aria-label 全覆盖（7/7 检查） |
| 无 Ear 实验评分和版权暗示 | ✓ 静态检查固化 |
| 公开媒体 SHA-256 未被 UI 改造改变 | ✓ 无音频处理管线（静态检查固化） |

## 4. 截图

- `home-1440.png` / `home-390.png`（本目录）— 首页桌面/移动宽度。

## 5. 事实边界

- 播放"真实出声"未在 headless 环境验证（无声卡）；证据为 Range/HTTP 矩阵 + 播放器逻辑静态检查。
- 慢网/断网场景的深度恢复记录依赖 53 包线上演练。
