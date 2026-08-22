# MFD-006 — Reliability & Local State

**项目：** Moodify  
**阶段：** Moodify Desktop Phase 1 — Windows Alpha  
**任务包编号：** MFD-006  
**日期：** 2026-08-20  
**执行对象：** Codex  
**性质：** 稳定性 / 恢复 / 本地状态 / 缓存边界 / 会话可靠性  
**优先级：** P0  
**前置任务：** MFD-005 — Moodify Minimal Player  
**后续任务：** MFD-007 — Windows Productization

---

## 1. 本包目的

MFD-005 完成后，Moodify Desktop 已经应该具备：

```text
打开
→ 看见 Moodify
→ 选择 / 恢复一首歌
→ Play
→ Pause
→ Seek
→ Next / Previous
```

但“可以演示”不等于“可以长期使用”。

MFD-006 的目标是：

> **让 Moodify Desktop 在重启、断网、会话过期、播放 URL 失效、异常退出和用户重复操作下仍然保持可理解、可恢复、不会污染 Cloud 权威的行为。**

---

## 2. 本包不增加产品面

本包不增加：

- 新页面
- 新音乐功能
- 新社区功能
- 新音频能力
- 新推荐能力

本包主要改变的是：

> **软件在坏情况下如何表现。**

---

## 3. 核心原则

### Cloud remains authority

Desktop 本地状态不是第二数据库。

### Recoverable by default

能恢复的错误，不应该变成永久失败。

### Minimal persistence

只保存真正需要跨重启保留的状态。

### No secret leakage

任何 auth / signed URL / private metadata 都必须有明确生命周期。

### Deterministic state

同一个事件只能导致一套明确状态转换。

---

## 4. MFD-006 完成后的用户体验

用户应该可以：

```text
关闭 Moodify
→ 再打开
→ 回到上次听的歌
→ 恢复合理播放位置
→ 音量仍然正常
```

如果网络断开：

```text
不崩溃
→ 显示可理解状态
→ 网络回来
→ 用户可以继续播放
```

如果播放 URL 过期：

```text
自动或受控刷新 manifest
→ 恢复播放
```

如果 session 过期：

```text
清楚地进入重新认证 / 恢复会话流程
```

---

## 5. 本包明确不做

- 正式 installer
- code signing
- auto-update
- tray
- Windows media keys
- notification integration
- mini player
- native audio
- WASAPI
- offline full library
- background mass download
- upload
- local music import
- complex analytics
- crash reporting SaaS
- sync across devices
- recommendation
- playlist product expansion

---

## 6. 验收句

MFD-006 通过后，应能说：

> **Moodify Desktop 不再只是一次性演示播放器，而是具备基础恢复能力和可信本地状态边界的 Alpha 软件。**
