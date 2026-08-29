# MFD-001 — Moodify Desktop Authority & Boundary

**项目：** Moodify  
**阶段：** Moodify Desktop Phase 1 — Windows Alpha  
**任务包编号：** MFD-001  
**日期：** 2026-08-20  
**执行对象：** Codex  
**性质：** 权威重建 / 只读审计 / 文档级收敛  
**优先级：** P0  
**前置任务：** 无  
**后续任务：** MFD-002 — Electron Foundation

---

## 1. 本包的唯一目的

在写任何 Electron / Windows 客户端代码之前，先把 Moodify 当前真实状态与最新产品决策对齐，建立一套不会让后续 AI Agent、工程师或仓库文档继续发生“产品身份漂移”的权威结构。

本包不是 Windows 功能开发包。

本包结束时，我们需要回答清楚：

1. Moodify 对外到底是什么产品？
2. Moodify Ear 现在处于什么位置？
3. Moodify Cloud 处于什么位置？
4. Android、Desktop、未来 iOS 的关系是什么？
5. 现有 `moodify-ai` 仓库哪些内容仍然是权威，哪些已经属于旧产品叙事？
6. Desktop 应该进入现有仓库，还是建立独立 `moodify-desktop` 仓库？
7. Desktop 与 Cloud / Player / Ear 之间的权限和数据边界是什么？
8. 下一包 MFD-002 可以安全从哪里开始？

---

## 2. 人类已经确认的最新产品决策

以下不是待讨论假设，而是本任务的上位输入：

> **Moodify 对外唯一产品是 Moodify Player / Moodify Music。**

用户面对的是播放产品，而不是内部听觉智能研究系统。

产品体验的核心承诺是：

> **让音乐更好听。**

核心体验是：

> **一首歌进入 Moodify，内部经过必要的扫描、分析、分轨、后处理和专属播放决策，用户最终只需要 Play。**

Moodify Ear：

> **保留为内部听觉智能、研究、判断、验证与学习系统，不再作为当前公开产品独立上线。**

Moodify Cloud：

> **承担用户不可见的云端处理、资产、播放版本、内部智能和服务能力。**

客户端：

```text
Moodify Player
├── Android          已有产品线
├── Desktop
│   └── Windows      当前开发阶段
└── iOS              延后，待具备 Mac 开发条件
```

Desktop 技术方向已经确定：

> **Electron。**

但 MFD-001 禁止开始 Electron 功能实现。

---

## 3. 当前已知仓库冲突

执行前已知 `huliye24/moodify-ai` 主仓库的根权威仍然把 Moodify 定义为：

> “The Ear of AI — an Auditory Intelligence System.”

现有根 `AGENTS.md` 还明确要求不要把 Moodify 退回为 post-processing / preset / DSP 产品。

`docs/REPOSITORY_STATUS.md` 也仍将 Auditory Intelligence System 作为 Canonical Identity，并将 Cloud runtime 与 App integration 标记为 UNRESOLVED。

因此：

**不能直接在旧权威体系下面增加一个 Electron 目录。**

否则后续 Agent 会同时收到两套互相冲突的产品定义。

---

## 4. 本包目录

- `00_README.md`：入口
- `01_MFD-001_TASK.md`：Codex 完整执行任务书
- `02_HUMAN_AUTHORITY_BASELINE.md`：不可被旧文档覆盖的人类最新决策
- `03_AUDIT_CHECKLIST.md`：扫描清单
- `04_DELIVERABLE_CONTRACT.md`：最终交付格式
- `05_ACCEPTANCE_GATE.md`：人工验收门
- `CODEX_START_PROMPT.md`：可直接交给 Codex 的起始指令
- `manifest.json`：任务包机器可读清单

---

## 5. 执行原则

```text
先认清系统
→ 再确定权威
→ 再画边界
→ 再决定仓库
→ 最后才允许进入 MFD-002
```

不要把“完成任务”理解为增加代码量。

MFD-001 最好的结果，是减少冲突、删除歧义、建立主河道。
