# W02-P00 — Wave 02 Re-entry Gate

**Wave:** Moodify Cognitive Wave 02  
**Package:** W02-P00  
**性质:** 第二轮重入门 / Reality Revalidation / Human Decision Gate  
**日期:** 2026-08-17  
**执行对象:** Codex + 人类最终决策  
**前置依赖:** W01-P09 已实际执行并完成 Wave 01 Closeout  
**后继任务:** 仅在人类明确选择 Wave 02 候选后生成  
**原子任务数:** 3  
**核心目标:** 不继承“我们以为 Wave 01 做完了”的假设，而是重新确认 Wave 01 的最终现实、当前运行状态和真实未解决问题，再由人类决定 Wave 02 是否启动、以及只启动哪一个主问题。

---

# 0. 为什么 Wave 02 不能直接从功能开发开始

Wave 01 的理论原则是：

```text
Reality
→ Canon
→ Build
→ Cases
→ Evidence
→ Distill
```

因此 Wave 02 的起点不能是：

> “继续做下一个功能。”

它必须重新回到：

> **Reality。**

原因很简单：

- P09 可能改变 Canon；
- P09 可能删除或降级规则；
- P09 可能把重复操作变成工具；
- P09 可能发现真正的瓶颈不在我们原先预想的位置；
- Wave 01 执行结束与 Wave 02 开始之间，服务器、部署、PR、数据量都可能发生变化；
- 甚至 P09 可能给出 `NO_NEW_WAVE_YET`。

所以 W02-P00 不是重复 P00。

它是：

> **在已经完成第一次认知蒸馏以后，验证新的“河床”是否真实存在。**

---

# 1. 三个原子任务

## T02-00-1 — Verify Wave 01 Closeout Reality

重新核验：

- Wave 01 Closeout Verdict
- Current Project Snapshot
- Agent Cold Start
- Current Canon
- actual main commit
- deployed commits
- current cloud services
- current database/object storage
- current Golden Case
- current Pilot Evidence
- open blockers/debt
- P09 automation/tool promotions 是否真的存在

目的：

> 区分“P09 写下了什么”与“项目现在真的是什么”。

---

## T02-00-2 — Validate the New Cognitive Riverbed

检查 P09 宣称已经消除的认知摩擦，是否真的被消除。

至少抽测：

- 新 Agent 是否可 cold start；
- deployment identity 是否可直接获取；
- server role 是否无需重新考古；
- Track/Job/Object identity 是否仍唯一；
- Job state authority 是否仍唯一；
- known failures 是否已有 guard/recovery；
- Golden Case regression 是否可执行；
- pilot evidence 是否仍可追溯；
- P09 新增 tool/automation 是否可运行；
- legacy docs 是否仍会误导 Agent。

如果 P09 宣称“已消除”，但实际仍需重复支付：

标记：

`DISTILLATION_NOT_CAPITALIZED`

---

## T02-00-3 — Human Wave 02 Selection Gate

只从真实未解决问题中生成最多 3 个候选。

每个候选必须回答：

- problem
- evidence
- current user impact
- current system impact
- why now
- why not later
- dependencies
- expected cognitive cost
- expected product value
- risk
- stop condition
- what not to build

最终由人类明确选择：

- `SELECT_CANDIDATE_1`
- `SELECT_CANDIDATE_2`
- `SELECT_CANDIDATE_3`
- `NO_NEW_WAVE_YET`

Codex 不得自动选择。

---

# 2. Hard Gate

如果 W01-P09 没有真实执行结果：

> `STOP — W01_CLOSEOUT_NOT_AVAILABLE`

禁止用 W01-P09 的“任务模板”当成“执行结果”。

必须读取真实产物：

- `WAVE_01_CLOSEOUT`
- `CURRENT_PROJECT_SNAPSHOT`
- `AGENT_COLD_START`
- `DISTILLATION_REGISTER`
- `COGNITIVE_DEBT_REGISTER`
- `FAILURE_CAPITALIZATION_REGISTER`
- `COLD_AGENT_TEST_REPORT`
- `WAVE_02_DECISION_BRIEF`
- `P09_ACCEPTANCE_REPORT`

---

# 3. Reality Revalidation

W02-P00 必须重新检查至少以下现实。

## 3.1 Repository

- current main
- open PR
- branch drift
- unmerged deployed code
- current AGENTS
- current Canon
- current tests
- current deployment scripts

## 3.2 Runtime

- control/API node
- worker node
- DB
- OSS
- deployed commits
- running services
- health
- queue/job counts
- stale jobs
- current versions

## 3.3 Data

- current Track count
- current Job count
- current Object count
- current Evidence count
- Golden Case references
- Pilot Case references
- orphan/missing object state

## 3.4 Product

- Android current build/version
- READY → PLAY still works
- Golden Song regression still works
- current external product identity still matches Canon

---

# 4. Riverbed Validation

P09 可能将某些重复认知成本升级为：

- D5 Test
- D6 Tool
- D7 Infrastructure

W02-P00 必须逐项验证：

| Distillation | Claimed Level | Artifact | Runs? | Removes Repetition? | Result |
|---|---|---|---:|---:|---|

Result:

- `CAPITALIZED`
- `PARTIALLY_CAPITALIZED`
- `NOT_CAPITALIZED`
- `REGRESSED`
- `UNKNOWN`

---

# 5. Cold Start Re-test

必须再次执行一个真实 Cold Agent Test。

与 P09 不同：

P09 是蒸馏结束时的测试。

W02-P00 是：

> **让一个新的执行者在下一轮真正开始之前，再次验证。**

最关键问题：

1. Moodify 对外是什么？
2. 当前 main 是什么？
3. 当前部署版本是什么？
4. 哪台机器做什么？
5. Track/Job/Object authority 是什么？
6. 当前 Job 状态权威是什么？
7. 当前 Pipeline version 是什么？
8. READY → PLAY 怎么走？
9. Golden Case 当前状态？
10. 当前最重要的未解决问题？

如果需要大量翻旧 Wave 01 包才能回答：

> `COLD_START_REGRESSION`

---

# 6. No Automatic Carry-over

Wave 01 的“下一步建议”不能自动变成 Wave 02 的任务。

必须经过：

```text
P09 Suggestion
  ↓
W02 Reality Revalidation
  ↓
Evidence Still Valid?
  ↓
Human Selection
  ↓
Wave 02 Package Design
```

这是为了防止：

> 计划因为曾经写下，就自动获得永久权威。

---

# 7. Candidate Construction Rules

最多 3 个候选。

每个候选必须是一个“真实问题”，而不是一个技术名词。

错误：

- Redis
- GPU
- iOS
- Hardware
- AI Model

正确：

- “完整歌曲平均处理时间过长，导致 10-song pilot 中等待成为主要瓶颈”
- “Android READY playback 在弱网下失败率高，阻碍真实日常使用”
- “听觉干预在多数歌曲上没有稳定收益，需要重新研究判断/处理策略”

---

# 8. Candidate Score

建议只做辅助，不自动排序。

维度：

- evidence strength
- user impact
- main-river impact
- urgency
- reversibility
- dependency readiness
- cognitive leverage
- cost

每项 0–2。

总分只作为讨论材料。

人类仍有最终权威。

---

# 9. Possible Wave 02 Directions

W02-P00 不预设，但候选可能来自：

## A. Product Reliability
如果 PLAY/Delivery/Android 是真实瓶颈。

## B. Audio Quality Generalization
如果 Pilot 显示干预收益不稳定。

## C. Operational Efficiency
如果 repeated manual/cloud friction 仍显著。

## D. Data/Learning Loop
如果已有足够真实 case，需要把 human evidence 变成学习资产。

## E. Hardware/Listening Environment
只有在 Wave 01 证据证明软件链已经稳定，而且硬件是当前真实产品瓶颈时才进入。

以上只是分类，不是自动任务。

---

# 10. Wave 02 Scope Rule

一旦人类选定一个候选：

Wave 02 只围绕**一个主问题**展开。

禁止同时：

- 做音质泛化；
- 做硬件；
- 做 iOS；
- 做社区；
- 做大规模增长；
- 做新模型；
- 做商业化。

除非这些是同一个主问题不可分割的依赖。

---

# 11. Evidence Freshness

所有 Wave 02 候选必须基于：

- W01 frozen evidence
- W02 current revalidation

如果两者冲突：

> 当前 Reality 优先。

例如：

P08 说 worker 内存是瓶颈，但 W02 已换机器。

那么：

不能继续把旧内存问题当 Wave 02 主问题。

---

# 12. Required Outputs

至少：

1. `00_W02P00_EXECUTIVE_SUMMARY.md`
2. `01_W01_CLOSEOUT_INTAKE.md`
3. `02_CURRENT_REALITY_REVALIDATION.md`
4. `03_RIVERBED_CAPITALIZATION_CHECK.md`
5. `04_COLD_START_RETEST.md`
6. `05_REGRESSION_AND_DRIFT_REPORT.md`
7. `06_CURRENT_DEBT_AND_UNKNOWNS.md`
8. `07_WAVE_02_CANDIDATES.md`
9. `08_CANDIDATE_SCORECARD.csv`
10. `09_HUMAN_SELECTION_GATE.md`
11. `10_SELECTED_WAVE_02_PROBLEM.md`
12. `11_W02P00_ACCEPTANCE_REPORT.md`

---

# 13. What May Change

W02-P00 默认只读。

允许：

- 生成报告；
- 更新 Reality Snapshot 草案；
- 标记 drift；
- 生成候选；
- 运行只读 validation；
- 运行 Golden regression（若安全且已授权）。

禁止：

- 开发候选功能；
- 迁移；
- 部署；
- 新开服务器；
- 新模型；
- 改状态机；
- 改 Pipeline；
- 改 Android；
- 自动启动 Wave 02。

---

# 14. Human Selection Gate

最终文件：

`HUMAN_SELECTION_GATE.md`

必须包含：

```text
Candidate 1:
Candidate 2:
Candidate 3:

Human decision:
[ ] SELECT_CANDIDATE_1
[ ] SELECT_CANDIDATE_2
[ ] SELECT_CANDIDATE_3
[ ] NO_NEW_WAVE_YET
```

只有人类明确选择后，才允许生成 W02-P01。

---

# 15. Acceptance

- [ ] W01-P09 实际执行结果可用
- [ ] Current Reality 已重新核验
- [ ] repository/runtime/data/product 四类现实已复查
- [ ] P09 D5/D6/D7 promotions 已验证
- [ ] Cold Start re-test 完成
- [ ] drift/regression 已记录
- [ ] current debt/unknowns 已重新排序
- [ ] 候选不超过 3 个
- [ ] 每个候选有 Evidence
- [ ] 每个候选是“问题”，不是技术名词
- [ ] 没有自动选择 Wave 02
- [ ] 没有开始开发
- [ ] Human Selection Gate 已生成
- [ ] 未经人类选择，不生成 W02-P01

---

# 16. 最终执行口令

> 执行 W02-P00 — Wave 02 Re-entry Gate。  
> 不得把 W01-P09 的任务模板当成执行结果；若没有真实 Wave 01 Closeout，则 STOP — W01_CLOSEOUT_NOT_AVAILABLE。  
> 重新核验 repository、runtime、data、product 现实，并验证 P09 声称已经下沉到 D5/D6/D7 的认知资产是否真的减少了重复理解与操作成本。  
> 再次执行 Cold Agent Test，识别 regression、drift、debt 与 unknown。  
> 只从当前真实问题中生成最多 3 个 Wave 02 候选，每个候选必须有证据、用户/主河道影响、成本、风险、依赖与 stop condition。  
> 不自动选择、不自动开发、不自动部署。  
> 最终等待人类在 Human Selection Gate 中选择一个候选，或明确 NO_NEW_WAVE_YET。
