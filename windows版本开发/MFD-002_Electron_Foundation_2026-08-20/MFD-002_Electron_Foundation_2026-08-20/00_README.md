# MFD-002 — Electron Foundation

**项目：** Moodify  
**阶段：** Moodify Desktop Phase 1 — Windows Alpha  
**任务包编号：** MFD-002  
**日期：** 2026-08-20  
**执行对象：** Codex  
**性质：** Desktop 工程地基 / Electron 安全骨架 / 构建基线  
**优先级：** P0  
**前置任务：** MFD-001 — Moodify Desktop Authority & Boundary  
**后续任务：** MFD-003 — Desktop–Cloud Contract

---

## 1. 本包目的

建立 Moodify Desktop 的第一套可运行、可测试、可构建、可继续扩展的 Electron 工程骨架。

本包不负责接 Moodify Cloud，不负责播放真实云端歌曲，不负责设计最终 UI。

本包只建立：

```text
Electron Main
    ↓
Preload
    ↓
Typed IPC
    ↓
Renderer
```

以及：

- TypeScript
- React
- Vite
- Electron Forge
- 基础测试
- lint / format / typecheck
- Windows 本地构建
- 安全默认值
- 日志与错误边界
- 配置与 secrets 边界
- 未来 Playback / Cloud 模块的占位接口

完成后，应得到一个：

> **安全、干净、没有业务污染的 Moodify Desktop 空壳。**

---

## 2. 硬前置

Codex 开始本包前必须确认：

```text
MFD-001 = GO
或
MFD-001 = CONDITIONAL GO 且所有阻塞 MFD-002 的条件已关闭
```

如果 MFD-001 仍是 NO-GO：

> **立即停止 MFD-002。**

不得自行绕过。

---

## 3. 本包明确不做

- 不连接真实 Moodify Cloud
- 不使用生产 service key
- 不实现登录
- 不实现真实 library
- 不实现真实 playback manifest
- 不实现云端音乐播放
- 不做 Audio DSP
- 不做 WASAPI
- 不做 native addon
- 不做 Audiolla / LALAL 接入
- 不做歌曲上传
- 不做分轨
- 不做最终 UI
- 不做皮肤系统
- 不做自动更新生产配置
- 不做代码签名
- 不发布正式 Release

---

## 4. 验收目标

最终必须满足：

```text
npm/pnpm install
→ dev 启动
→ Electron 窗口正常显示
→ renderer 无 Node 权限
→ preload 只暴露最小 typed bridge
→ typecheck 通过
→ lint 通过
→ test 通过
→ package Windows app 成功
→ 无 secret
→ 无生产 API 依赖
```

如果以上任一项没有证据，不算完成。
