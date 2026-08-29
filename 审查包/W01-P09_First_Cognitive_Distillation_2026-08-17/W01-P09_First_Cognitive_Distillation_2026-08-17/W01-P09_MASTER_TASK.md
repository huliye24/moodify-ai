# W01-P09 — First Cognitive Distillation

**Wave:** Moodify Cognitive Wave 01  
**Package:** W01-P09  
**性质:** 第一次全项目认知蒸馏 / Wave Closeout / Canon & Infrastructure Compression  
**日期:** 2026-08-17  
**执行对象:** Codex + 人类最终审核  
**前置依赖:** W01-P00 ~ W01-P08 已完成；P08 Pilot Evidence Index 已冻结  
**后继任务:** 无自动后继；由人类审核后决定 Wave 02  
**原子任务数:** 1  
**核心目标:** 将 Wave 01 产生的事实、失败、重复劳动、规则、测试与架构经验进行第一次正式蒸馏，使下一位 Agent 不再重复支付已经支付过的认知成本。

---

# 0. 这是 Wave 01 的最后一个包

P00–P08 分别完成了：

- Reality
- Canon
- Cloud Topology
- Data Plane
- Control Plane
- Compute Pipeline
- Delivery + PLAY
- Golden Song
- 3 → 10 Song Pilot

P09 不再继续增加功能。

P09 也不再增加样本。

P09 唯一的问题是：

> **这一整个 Wave 结束以后，哪些认知成本不应该在下一轮被重新支付？**

这意味着：

- 哪些经验应该变成 Canon；
- 哪些经验只适合作为 SOP；
- 哪些重复错误应该变成 test；
- 哪些重复命令应该变成 tool；
- 哪些稳定规则应该下沉进 infrastructure；
- 哪些文档已经过期；
- 哪些规则应该降级；
- 哪些东西应该删除；
- 哪些未知项必须继续保持未知；
- 下一位 Agent 最少需要读什么，才能进入真实主河道。

---

# 1. P09 的单一原子任务

# T09-1 — Wave 01 Cognitive Distillation

将整个 Wave 01 的 Evidence 从：

```text
D0 Raw Logs / Raw Evidence
        ↓
D1 Observation
        ↓
D2 Lesson
        ↓
D3 Rule
        ↓
D4 SOP
        ↓
D5 Test / Guard
        ↓
D6 Tool / Automation
        ↓
D7 Infrastructure / Default Path
```

逐项蒸馏。

同时对现有知识资产执行：

```text
KEEP
REWRITE
DOWNGRADE
MERGE
DELETE_CANDIDATE
AUTOMATE
HARDEN
HUMAN_DECISION_REQUIRED
```

最终形成新的：

- Current Reality
- Current Canon
- Current Architecture
- Current Known Failures
- Golden Case Baseline
- Pilot Baseline
- Agent Cold Start
- Task Grammar
- Cognitive Debt Register
- Next-Wave Decision Brief

---

# 2. P09 不允许凭回忆进行

必须优先读取：

## P00
- Reality Summary
- Truth Table
- Conflict/Unknown List
- System Map
- Evidence Index

## P01
- Canonical Decision Register
- Current Canon
- Product Boundary
- Authority Order
- Canon Changelog

## P02
- Node Role Assignment
- Network Matrix
- Secret Ownership
- Failure Domain
- Capacity Contract
- Architecture Decisions

## P03
- Data Identity Contract
- Data Plane Invariants
- Migration status
- Data Plane Test Report

## P04
- Authoritative State Machine
- Lease / Retry / Recovery / Idempotency
- Failure Taxonomy
- Control Plane Test Report

## P05
- Capability Map
- Pipeline Contract
- BYPASS Policy
- Render/Verify
- Pipeline Test Report

## P06
- Delivery Contract
- Android Playback Reality
- Security Review
- Playback Test Report

## P07
- Golden Case Evidence Pack
- Blocker Register
- Final Verdict
- Regression Baseline

## P08
- Pilot Version Freeze
- Case Verdicts
- Resource/Cost
- Failure Distribution
- Repeated Friction Log
- Integrity Report
- Traceability Coverage
- Aggregate
- W01 Pilot Evidence Index

若证据缺失：

> `DISTILLATION_INPUT_INCOMPLETE`

P09 可以记录缺失，但不得用推测补齐。

---

# 3. Evidence Before Interpretation

P09 必须先输出：

`W01_EVIDENCE_INTAKE.md`

每个重要输入记录：

- source package
- file/ref
- version/date
- hash if available
- confidence
- whether current
- whether superseded
- whether conflicting

原则：

> **先证明我们从什么事实出发，再做蒸馏。**

---

# 4. Distillation Unit

任何蒸馏项都必须是一个独立 `Distillation Unit`。

至少包含：

- distillation_id
- source evidence
- repeated occurrence count
- problem/friction
- why it matters
- current handling
- proposed D-level
- target artifact
- expected future cognitive cost eliminated
- risk of over-hardening
- reversibility
- owner
- review trigger
- decision

---

# 5. D0 → D7 的严格含义

## D0 — Raw Evidence

包括：

- logs
- case records
- traces
- metrics
- failure reports
- human review text
- command outputs
- raw screenshots/refs

D0 不直接进入 Canon。

---

## D1 — Observation

对事实的最小抽象。

例如：

> 10 个 case 中有 4 次需要人工重新确认同一服务器部署 commit。

它仍然是“观察”，不是规则。

---

## D2 — Lesson

从多个 Observation 中提炼：

> 部署身份没有成为低成本可见信息，导致 Agent 反复查询。

Lesson 仍然可能被未来证据推翻。

---

## D3 — Rule

适合稳定约束：

> 每个运行服务必须暴露 build/commit identity。

Rule 必须：

- 有 evidence；
- 有 scope；
- 有 exception；
- 有 review trigger。

---

## D4 — SOP

适合一段仍需人为执行的稳定流程：

> Golden Case 前执行 deployment identity preflight。

如果完全可以自动化，不要长期停在 SOP。

---

## D5 — Test / Guard

将重复错误变成自动拒绝：

- Canon drift guard
- provenance test
- READY guard
- no-client-secret scan
- state transition test
- Golden Case regression

---

## D6 — Tool / Automation

将重复认知或重复操作压缩为工具：

- reality scanner
- pilot aggregator
- deployment identity reporter
- integrity reconciler
- evidence pack generator

只有重复且稳定的动作才自动化。

---

## D7 — Infrastructure / Default Path

最高层蒸馏：

> 正确行为成为默认低摩擦路径。

例如：

- durable object 注册自动绑定 provenance；
- worker claim 天生带 lease/fencing；
- delivery API 天生只签发 READY；
- Agent 冷启动自动读取唯一 current snapshot。

D7 不意味着“最复杂”。

而意味着：

> 不再需要每个 Agent 重新记住一条规则。

---

# 6. 最小充分蒸馏原则

不是所有发现都应该升到 D7。

必须使用：

`MINIMUM_SUFFICIENT_DISTILLATION`

问题：

> **消除这项重复认知成本所需的最低持久层级是什么？**

例如：

- 一次性异常 → D1
- 重复两三次但环境特定 → D2/D4
- 稳定风险 → D3/D5
- 高频机械重复 → D6
- 核心不变量 → D7

禁止：

> 为了“成熟”而把所有事情变成基础设施。

---

# 7. KEEP / REWRITE / DOWNGRADE / DELETE

P09 必须对高权威和高频资产做一次生命周期裁决。

## KEEP

当前正确、低摩擦、仍有价值。

## REWRITE

概念仍有价值，但表述/结构造成误解。

## DOWNGRADE

保留历史/研究价值，但不应继续作为高权威入口。

## MERGE

多个重复文档/规则可以合并为一个 authority。

## DELETE_CANDIDATE

已经：

- 错误；
- 重复；
- 被自动化完全替代；
- 频繁误导 Agent；
- 无历史保留价值；

但 P09 默认先标候选。

大规模删除仍需人类审核。

## AUTOMATE

从人工说明下沉到 tool。

## HARDEN

从 rule/SOP 下沉到 test/infrastructure。

---

# 8. Rule Lifecycle

每条 Canon Rule 必须有：

- rule_id
- statement
- evidence
- scope
- owner
- created_at
- status
- exception
- challenge condition
- review trigger

状态：

- ACTIVE
- EXPERIMENTAL
- CHALLENGED
- DEPRECATED
- SUPERSEDED
- REMOVED

这样避免：

> 熵减一次以后，规则无限累积造成第二次熵增。

---

# 9. Cognitive Debt Register

必须建立：

`COGNITIVE_DEBT_REGISTER.md`

机器认知债务定义：

> 当前为了快速推进而把未来理解、判断、迁移或验证成本向后转移的结构。

至少记录：

- debt_id
- source
- current shortcut
- future cost
- affected agents
- evidence
- severity
- payoff action
- earliest sensible payoff
- can defer?
- owner

典型债务：

- duplicate docs
- unmerged but deployed code
- undocumented server config
- ambiguous version authority
- manual evidence assembly
- hidden filesystem assumptions
- legacy branch dependencies
- undocumented recovery step

---

# 10. Cognitive Friction Register

必须区分：

## Necessary Friction

不能消灭：

- rights check
- security authorization
- human listening judgment where required
- destructive migration review
- uncertainty review

这些是必要审慎。

## Avoidable Friction

应该降低：

- repeated context lookup
- repeated identity confirmation
- repeated server path search
- repeated known error diagnosis
- repeated command assembly
- duplicate authority resolution
- repeated evidence stitching

原则：

> **低摩擦不是最少思考，而是最少重复支付。**

---

# 11. Failure Capitalization

P09 必须检查 P07/P08 每个重复 Failure：

问题：

1. 下次还会重新诊断吗？
2. 是否已经有 stable failure code？
3. 是否已有 regression test？
4. 是否已有 recovery path？
5. 是否能自动检测？
6. 是否值得下沉成 tool/infrastructure？

建立：

`FAILURE_CAPITALIZATION_REGISTER.md`

状态：

- RAW_FAILURE
- CLASSIFIED
- DOCUMENTED
- TEST_GUARDED
- AUTO_RECOVERED
- INFRASTRUCTURE_HARDENED

目标不是 0 failure。

目标是：

> **同一种 failure 的第二次成本显著下降。**

---

# 12. Human Judgment Capitalization

听觉评审不能完全自动化，但可以减少重复结构成本。

P09 检查：

- review template 是否足够；
- baseline 是否固定；
- device/environment 是否需记录；
- 什么条件触发 human review；
- 哪些判断可以自动 BYPASS；
- 哪些判断必须保留自由文本；
- 哪些指标对听感没有帮助，应该删除。

禁止：

> 为了结构化而消灭审美自由文本。

---

# 13. Canon Second Distillation

P09 必须回头检查 P01 Canon。

问题：

- P01 的哪些 Canon 已被现实验证？
- 哪些过于宽泛？
- 哪些已被代码/infrastructure 替代，文档可以缩短？
- 哪些 rules 从 D3 下沉到 D5/D7 后可从 Agent prompt 中删除？
- 哪些术语仍然造成误解？

输出：

`CANON_SECOND_DISTILLATION.md`

目标：

> Canon 更短、更稳定、更难误解。

不是更长。

---

# 14. Agent Cold Start

必须建立一个真正面向下一位 Agent 的：

`AGENT_COLD_START.md`

目标：

一个新的 Agent 不看历史对话，也能在最短路径上回答：

1. Moodify 对外是什么？
2. 当前 main/release identity 是什么？
3. 当前真实云拓扑是什么？
4. 数据在哪里？
5. Job authority 是谁？
6. Pipeline 是什么？
7. READY 如何定义？
8. Android 如何 PLAY？
9. Golden Case 是什么？
10. 当前 10-song pilot 结论是什么？
11. 哪些已知 failure 不要重复诊断？
12. 当前不能做什么？
13. 下一步真正未解决的问题是什么？

---

# 15. Current Snapshot

P09 必须生成新的：

`CURRENT_PROJECT_SNAPSHOT.md`

它不是历史回顾。

它只描述：

> **Wave 01 结束时 Moodify 真实存在的系统。**

必须区分：

- VERIFIED
- DEPLOYED_NOT_VERIFIED
- IMPLEMENTED_NOT_DEPLOYED
- EXPERIMENTAL
- BLOCKED
- UNKNOWN

Snapshot 应成为下一个 Wave 的 Reality 起点。

---

# 16. Task Grammar Distillation

基于整个 Wave，检查任务包本身。

建立：

`MOODIFY_TASK_GRAMMAR_V1.md`

建议最小 Task Grammar：

1. Intent
2. Reality Gate
3. Authority
4. Inputs
5. Scope
6. Execution
7. Evidence
8. Acceptance
9. Handoff

每个未来任务必须尽量回答：

- 真实前置是什么；
- 谁有权决定；
- 什么不做；
- 什么证据证明完成；
- 下一任务收到什么。

不要把本 Wave 的所有模板机械复制到未来每个小任务。

---

# 17. Token / Cognitive Flow Analysis

P09 可以做 Token / 认知流分析，但必须保持理论纪律。

## 17.1 不把 Token 当劳动价值

Token 只是机器认知活动与成本代理。

---

## 17.2 不把 TMR 当 KPI

可以做 post-hoc 分析：

> 哪些认知支出直接服务于最终被接受的改变？

但 TMR 只能作为分析诊断，不能成为：

- 员工考核；
- Agent 速度指标；
- “越高越好”的强制 KPI。

---

## 17.3 可分析的浪费

- 重复读取同一背景
- 重复找 authority
- 重复修同一 failure
- 重复生成已存在文档
- 重复解释 server roles
- 重复确认 data identity
- 被废弃分支带来的误导

---

# 18. Compression Test

所有新 Canon / Cold Start / Snapshot 完成后，执行一个模拟：

> **Cold Agent Test**

让一个不加载旧对话的 Agent，仅阅读：

- `AGENTS.md`
- `AGENT_COLD_START.md`
- `CURRENT_PROJECT_SNAPSHOT.md`
- 必要 Canon

回答一组固定问题。

如果还需要大规模重读历史文件：

> 蒸馏不通过。

---

# 19. Cold Agent Test Questions

至少：

1. Moodify 唯一对外产品是什么？
2. Ear 当前角色是什么？
3. 当前 PLAY 主链是什么？
4. source / metadata / objects 分别在哪里？
5. Job current state 的唯一 authority 是什么？
6. worker 如何避免双重执行？
7. BYPASS 是什么？
8. READY 必须满足什么？
9. Android 如何获得音频？
10. Golden Case 是否通过？
11. 10-song pilot 最大问题是什么？
12. 当前 Top 5 unknown/debt 是什么？
13. 下一个 Wave 最值得解决什么？
14. 哪些事情明确不应该做？

答案必须能从新 snapshot/canon 直接找到。

---

# 20. Delete Test

对于每一条候选删除资产，必须回答：

> 删除后未来 Agent 是否会失去必要证据？

如果会：

不要删。

可考虑：

- archive
- mark historical
- merge
- reference index

目标是：

> **减少 active cognitive surface，不是毁掉历史证据。**

---

# 21. Infrastructure Promotion Test

任何 D6 → D7 提议必须通过：

1. 该行为是否重复出现？
2. 规则是否稳定？
3. 自动化错误风险是否可控？
4. 是否存在重要 exception？
5. 是否真的降低未来认知成本？
6. 是否会把错误 assumption 永久固化？
7. 是否可观察、可回滚？

任一关键答案不确定：

不要升 D7。

---

# 22. Required Distillation Outputs

至少形成：

1. `00_P09_EXECUTIVE_SUMMARY.md`
2. `01_W01_EVIDENCE_INTAKE.md`
3. `02_DISTILLATION_REGISTER.md`
4. `02_DISTILLATION_REGISTER.csv`
5. `03_COGNITIVE_FRICTION_REGISTER.md`
6. `04_COGNITIVE_DEBT_REGISTER.md`
7. `05_FAILURE_CAPITALIZATION_REGISTER.md`
8. `06_RULE_LIFECYCLE_REGISTER.md`
9. `07_CANON_SECOND_DISTILLATION.md`
10. `08_AGENT_COLD_START.md`
11. `09_CURRENT_PROJECT_SNAPSHOT.md`
12. `10_MOODIFY_TASK_GRAMMAR_V1.md`
13. `11_AUTOMATION_AND_INFRASTRUCTURE_PROMOTIONS.md`
14. `12_DELETE_DOWNGRADE_MERGE_REGISTER.md`
15. `13_TOKEN_COGNITIVE_FLOW_ANALYSIS.md`
16. `14_COLD_AGENT_TEST_REPORT.md`
17. `15_WAVE_01_CLOSEOUT.md`
18. `16_WAVE_02_DECISION_BRIEF.md`
19. `17_P09_ACCEPTANCE_REPORT.md`

---

# 23. What P09 May Modify

P09 允许：

- README / AGENTS / Canon 的进一步压缩
- docs authority cleanup
- stale status docs update
- rule front matter
- test/guard additions
- small tools that directly automate repeated stable friction
- evidence indexes
- current snapshot
- cold-start document
- task grammar
- archive markers

前提：

> 每个修改都必须由 P00–P08 Evidence 支持。

---

# 24. What P09 Must Not Do

禁止：

- 新产品功能；
- 新音频模型；
- 新第三方服务；
- 新播放器；
- 新 cloud architecture；
- 新 database architecture；
- 新状态机；
- 新社交/社区/皮肤；
- iOS；
- 大规模性能扩容；
- 跑更多歌曲；
- 以“下一 Wave 可能需要”为理由提前开发；
- 把未经验证假设写成 Canon。

---

# 25. Wave 01 Closeout Verdict

最终输出：

## System Status

- `WAVE_01_ACCEPTED`
- `WAVE_01_ACCEPTED_WITH_DEBT`
- `WAVE_01_NOT_ACCEPTED`

## Cognitive Status

- repeated costs eliminated
- repeated costs still open
- debt added
- debt removed
- rules added
- rules deleted/downgraded
- tests added
- tools added
- infrastructure promotions
- unresolved human decisions

---

# 26. Wave 02 Decision Brief

P09 可以提出 Wave 02 候选，但不能自动开工。

每个候选必须回答：

- unresolved real problem
- evidence
- why now
- expected user/product value
- expected cognitive cost
- dependencies
- what not to do
- recommended priority

候选数量建议不超过 3。

必须允许：

> `NO_NEW_WAVE_YET`

如果 Wave 01 的现实系统还需要运行、积累更多数据，则“暂不开发”也是合法结论。

---

# 27. P09 Acceptance

只有满足以下条件，Wave 01 才闭环：

- [ ] P00–P08 Evidence Intake 完成
- [ ] Distillation Register 完成
- [ ] 每个重要重复 friction 有处理决策
- [ ] 必要 friction 与 avoidable friction 分离
- [ ] Cognitive Debt Register 完成
- [ ] repeated failures 已资本化评估
- [ ] rules 有 lifecycle
- [ ] Canon 进行了二次压缩
- [ ] active cognitive surface 减少
- [ ] Cold Start 文档完成
- [ ] Current Project Snapshot 完成
- [ ] Task Grammar v1 完成
- [ ] D6/D7 promotion 有证据
- [ ] delete/down-grade 有证据保护
- [ ] TMR 未被用作 KPI
- [ ] Cold Agent Test 通过
- [ ] Wave 01 Closeout Verdict 完成
- [ ] Wave 02 只输出 Decision Brief
- [ ] 未自动开始下一 Wave

---

# 28. 最终执行口令

> 执行 W01-P09 — First Cognitive Distillation。  
> 这是 Wave 01 的最后一个任务，不再开发功能，也不再扩大样本。  
> 首先完整读取 P00–P08 的 Reality、Canon、Architecture、Data、Control、Compute、Delivery、Golden Case 与 Pilot Evidence；缺失信息保持 UNKNOWN，不凭记忆补齐。  
> 使用 D0→D7 对重复事实、失败、规则、SOP、测试、工具与基础设施进行最小充分蒸馏；同时执行 KEEP / REWRITE / DOWNGRADE / MERGE / DELETE_CANDIDATE / AUTOMATE / HARDEN / HUMAN_DECISION_REQUIRED。  
> 区分必要审慎摩擦与可避免认知摩擦；建立 Cognitive Debt、Failure Capitalization、Rule Lifecycle；将稳定高频重复行为尽量下沉为 test/tool/infrastructure，同时避免过度固化。  
> 二次压缩 Canon，生成 Agent Cold Start 与新的 Current Project Snapshot，使下一位 Agent 不依赖历史对话即可进入主河道。  
> TMR 只作为事后分析工具，禁止作为 KPI。  
> 最后执行 Cold Agent Test，形成 Wave 01 Closeout Verdict 与最多 3 个 Wave 02 候选；不自动启动下一 Wave，等待人类审核。
