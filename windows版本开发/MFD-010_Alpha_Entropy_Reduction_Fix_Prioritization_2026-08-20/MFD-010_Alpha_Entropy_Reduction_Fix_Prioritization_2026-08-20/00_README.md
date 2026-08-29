# MFD-010 — Alpha Entropy Reduction & Fix Prioritization

**项目：** Moodify  
**阶段：** Moodify Desktop Alpha Validation  
**任务包编号：** MFD-010  
**日期：** 2026-08-20  
**执行对象：** Codex  
**性质：** Alpha 熵减 / 问题归并 / 修复优先级 / Phase 2 输入收敛  
**优先级：** P0  
**前置任务：** MFD-009 — Alpha Field Validation & Evidence  
**后续任务：** MFD-FIX 系列或 Moodify Desktop Phase 2 Definition

---

## 1. 本包目的

MFD-009 会产生很多东西：

- Bug
- 播放失败
- 设备差异
- 用户困惑
- 听感反馈
- 第二次打开信号
- Feature Requests
- 日志
- Support Bundles
- 新未知问题

如果把这些东西直接全部变成开发任务：

> Moodify 会重新进入功能膨胀。

MFD-010 的唯一目的：

> **对 Alpha 产生的认知进行熵减，只留下真正值得消耗工程资源的问题。**

---

## 2. 不要把“用户说了”当成“应该做”

用户可能会要求：

```text
歌词
搜索
EQ
本地音乐
皮肤
离线
播放列表
可视化
更多按钮
```

这些都只能首先被视为：

> **Signal**

而不是：

> **Roadmap**

必须经过：

```text
Evidence
→ Frequency
→ Severity
→ Product Fit
→ Core Value
→ Cost
→ Complexity
→ Decision
```

---

## 3. 本包最终应该输出

```text
Raw Alpha Evidence
        ↓
Deduplication
        ↓
Root Cause Grouping
        ↓
Evidence Strength
        ↓
Core / Non-core Classification
        ↓
Fix / Observe / Reject / Defer
        ↓
Ranked Engineering Backlog
```

最终只留下少量真正值得开发的工作。

---

## 4. 核心问题

MFD-010 必须回答：

1. 哪些问题真正阻碍 Play？
2. 哪些问题只是偶发噪音？
3. 哪些问题来自同一个根因？
4. 哪些 feature request 与 Moodify 核心无关？
5. 哪些需求虽然高频，但会让产品变复杂？
6. 哪些听感差异值得继续研究？
7. 哪些设备/系统组合最容易失败？
8. Alpha 的最大技术风险是什么？
9. Alpha 的最大产品风险是什么？
10. 下一轮应该做得更多，还是做得更少？

---

## 5. 验收句

MFD-010 完成后，应能说：

> **我们已经把 Alpha 的噪音压缩成一张极小、极清晰、可以直接指导下一轮工程的决策表。**
