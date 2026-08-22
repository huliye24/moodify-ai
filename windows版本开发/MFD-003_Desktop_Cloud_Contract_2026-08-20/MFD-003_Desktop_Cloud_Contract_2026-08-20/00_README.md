# MFD-003 — Desktop–Cloud Contract

**项目：** Moodify  
**阶段：** Moodify Desktop Phase 1 — Windows Alpha  
**任务包编号：** MFD-003  
**日期：** 2026-08-20  
**执行对象：** Codex  
**性质：** Client–Cloud 协议 / 公共 API 边界 / 认证与播放清单契约  
**优先级：** P0  
**前置任务：** MFD-002 — Electron Foundation  
**后续任务：** MFD-004 — Playback Vertical Slice

---

## 1. 本包目的

本包第一次让 Moodify Desktop 接触真实 Moodify 后端。

但本包的目标不是“把歌播放出来”，而是：

> **建立 Desktop 可以安全依赖、Cloud 可以长期维护、且不会泄露内部实现的正式 Player API / BFF 契约。**

本包要解决四件事：

1. Desktop 如何认证；
2. Desktop 如何取得用户可见曲目；
3. Desktop 如何取得一首歌的播放清单；
4. Desktop 永远不应该知道哪些内部信息。

---

## 2. 核心架构

目标边界：

```text
Moodify Desktop
      ↓
Public Player API / BFF
      ↓
Moodify Cloud Internal Services
      ↓
DB / OSS / Processing / Ear
```

禁止：

```text
Desktop → PolarDB
Desktop → internal service-key endpoint
Desktop → Ear internal API
Desktop → Audiolla / LALAL directly
Desktop → internal filesystem
```

---

## 3. 本包不是 MFD-004

MFD-003 可以：

- 建立 API client；
- 建立 contract；
- 建立认证流程；
- 读取真实 library / tracks；
- 读取真实 playback manifest；
- 验证 stream URL 可达性；
- 验证权限和错误状态；
- 用测试请求检查音频资源头信息。

MFD-003 不应该：

- 实现正式播放状态机；
- 实现 seek / pause / next / previous 完整播放体验；
- 实现正式播放器 UI；
- 做音频 DSP；
- 做 WASAPI；
- 做缓存系统；
- 做断点续播；
- 做系统媒体键。

---

## 4. 完成后的最小结果

完成后 Desktop 应该能够在开发模式下：

```text
启动
→ 建立用户级会话
→ 请求 track/library 数据
→ 请求 PlaybackManifest
→ 得到授权后的 stream URL / asset reference
→ 验证资源可访问
```

但：

> **不要求真正从扬声器播放。**

真正的 Playback Vertical Slice 留给 MFD-004。
