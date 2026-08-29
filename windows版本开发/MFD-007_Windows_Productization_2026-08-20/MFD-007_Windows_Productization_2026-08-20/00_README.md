# MFD-007 — Windows Productization

**项目：** Moodify  
**阶段：** Moodify Desktop Phase 1 — Windows Alpha  
**任务包编号：** MFD-007  
**日期：** 2026-08-20  
**执行对象：** Codex  
**性质：** Windows 产品化 / 安装 / OS 集成 / 更新边界 / 发布工程  
**优先级：** P0  
**前置任务：** MFD-006 — Reliability & Local State  
**后续任务：** MFD-008 — Alpha Release Gate

---

## 1. 本包目的

MFD-006 完成以后，Moodify Desktop 应该已经是：

> 可以播放、可以恢复、基础可靠的 Electron Alpha 软件。

但如果用户仍然必须执行：

```text
git clone
npm install
npm run dev
```

它就还不是一个真正的 Windows 产品。

MFD-007 的目标是：

> **把 Moodify Desktop 变成可以安装、启动、卸载、识别版本、与 Windows 基础媒体能力协作，并具备可重复发行路径的软件。**

---

## 2. 本包的产品化边界

本包进入：

- Windows installer；
- application identity；
- icon / executable naming；
- Start Menu / shortcut；
- single instance；
- tray；
- minimize/background playback；
- OS media controls；
- release versioning；
- packaged logging；
- crash-safe startup；
- update architecture；
- code-signing readiness；
- build/release reproducibility；
- release artifacts / checksums。

本包仍然不进入：

- 新播放算法；
- WASAPI；
- DSP；
- offline library；
- 社区；
- 推荐；
- 皮肤市场；
- macOS；
- Linux。

---

## 3. Release 分层

必须区分：

### Internal Alpha

允许：

```text
unsigned build
private/internal distribution
manual warning acknowledged
```

### Public Alpha / External Distribution

目标：

```text
signed installer
verified publisher identity
controlled update source
release notes
checksums
rollback path
```

不要为了缺少签名证书阻塞内部工程验证。

但：

> **不得把 unsigned internal build 误称为 production-ready public release。**

---

## 4. Windows 第一发行格式

默认优先评估：

> **Electron Forge + Squirrel.Windows**

如 MFD-002 已经确定其他 maker，则遵守现有唯一打包主线，不并存两个 installer authority。

---

## 5. 本包完成后的结果

至少得到：

```text
Moodify Setup.exe
```

或者当前 Forge maker 对应的标准安装 artifact。

用户应该能够：

```text
下载安装
→ 安装
→ 从 Start Menu / shortcut 启动
→ Play
→ 最小化后继续播放
→ 使用系统媒体控制
→ 退出
→ 再启动
→ 卸载
```

---

## 6. 验收句

MFD-007 通过后，应能说：

> **Moodify Desktop 已经从开发项目变成具有 Windows 安装、运行与发行边界的软件产品候选版本。**
