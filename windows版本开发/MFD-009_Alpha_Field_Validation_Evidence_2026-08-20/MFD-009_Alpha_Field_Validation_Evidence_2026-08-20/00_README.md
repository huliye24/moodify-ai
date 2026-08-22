# MFD-009 — Alpha Field Validation & Evidence

**项目：** Moodify  
**阶段：** Moodify Desktop Alpha Validation  
**任务包编号：** MFD-009  
**日期：** 2026-08-20  
**执行对象：** Codex  
**性质：** 受控 Alpha 验证 / 真实使用证据 / 可靠性与听感证据收集  
**优先级：** P0  
**前置任务：** MFD-008 — Alpha Release Gate  
**后续任务：** MFD-010 — Alpha Entropy Reduction & Fix Prioritization

---

## 1. 这一包为什么存在

MFD-008 如果通过，只能证明：

> **Moodify Desktop 达到了可以进入 Alpha 的最低工程标准。**

它还不能证明：

- 用户会不会真的使用；
- 用户能不能理解 Play；
- 哪些故障只会在真实环境发生；
- 不同 Windows 设备 / 声卡 / 耳机下是否稳定；
- “用 Moodify 听起来更好”是否真的能被人感知；
- 哪些功能用户根本不需要；
- 下一阶段应该增加什么、删除什么。

因此 MFD-009 的核心不是开发，而是：

> **让真实使用产生证据。**

---

## 2. Alpha Validation 的目标

建立四类证据：

```text
Reliability Evidence
Playback Evidence
Listening Evidence
Usage Evidence
```

然后回答：

```text
什么坏了？
什么没人用？
什么让用户困惑？
什么真的产生价值？
```

---

## 3. 核心原则

### Evidence before roadmap

先看证据，再决定 Phase 2。

### Controlled cohort

Alpha 不是无限公开扩散。

### Minimal telemetry

只采集真正用于改进产品的技术事实。

### Listening is not a vanity metric

“更好听”必须通过受控听感反馈逐渐建立证据。

### No feature creep

MFD-009 禁止因为收到反馈就立即开发大量新功能。

---

## 4. 验收句

MFD-009 完成后，应能够说：

> **我们已经知道 Moodify Desktop 在真实用户、真实设备、真实网络和真实听觉环境中，最主要的问题与最主要的价值分别是什么。**
