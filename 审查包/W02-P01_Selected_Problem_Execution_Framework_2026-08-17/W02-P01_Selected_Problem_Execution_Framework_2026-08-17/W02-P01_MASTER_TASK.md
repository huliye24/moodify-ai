# W02-P01 — Selected Problem Execution Framework

**Wave:** Moodify Cognitive Wave 02  
**Package:** W02-P01  
**性质:** 选择后执行框架 / Selected-Problem Execution / Evidence-Bound Build  
**日期:** 2026-08-17  
**执行对象:** Codex  
**前置依赖:** W02-P00 已实际执行；Human Selection Gate 已明确选择一个 Wave 02 主问题  
**后继任务:** 由本包执行结果决定  
**原子任务数:** 4  
**核心目标:** 将人类已经明确选择的一个真实问题，转化为一条受 Reality、Authority、Evidence、Stop Condition 约束的最小执行主线。

---

# 0. 这不是一个预设功能包

W02-P01 的内容不能在 W02-P00 之前被“猜出来”。

因此本包不是：

- 音质优化包；
- Android 优化包；
- GPU 包；
- iOS 包；
- 硬件包；
- 数据学习包。

它是一个**执行框架**。

只有当 W02-P00 真实输出：

```text
SELECT_CANDIDATE_1
or
SELECT_CANDIDATE_2
or
SELECT_CANDIDATE_3
```

并写出：

`SELECTED_WAVE_02_PROBLEM.md`

以后，本包才允许进入执行。

若没有人类选择：

> `STOP — W02_PROBLEM_NOT_SELECTED`

---

# 1. 四个原子任务

## T02-01-1 — Problem Freeze

将人类选择的问题冻结为一个不可随意扩张的 Problem Contract。

必须回答：

- 当前真实问题是什么；
- 用户/产品为什么会被它影响；
- 它在主河道哪个位置；
- 证据是什么；
- 当前基线是什么；
- 成功条件是什么；
- 停止条件是什么；
- 明确不做什么；
- 什么变化需要重新回到人类决策。

输出：

`SELECTED_PROBLEM_CONTRACT.md`

---

## T02-01-2 — Minimal Intervention Design

只设计解决该问题所需的最小改变。

必须区分：

- MUST
- SHOULD
- MAY
- NOT_IN_WAVE

任何 proposed change 都必须回答：

> 它如何直接改变被选中的问题？

回答不了：

> `OUT_OF_SCOPE`

---

## T02-01-3 — Execute with Evidence

按最小 changeset 执行。

每个修改必须绑定：

- problem evidence
- expected effect
- test
- runtime evidence
- rollback
- regression risk

禁止“先做再解释”。

---

## T02-01-4 — Re-measure & Decide

执行后必须重新测量同一问题。

比较：

```text
Baseline
→ Intervention
→ Re-measurement
```

最终只允许：

- `PROBLEM_IMPROVED`
- `PROBLEM_RESOLVED`
- `NO_MEANINGFUL_IMPROVEMENT`
- `REGRESSED`
- `EVIDENCE_INSUFFICIENT`

不能因为代码合并/测试通过就自动宣布问题解决。

---

# 2. Hard Gate

必须读取：

## W02-P00

- Current Reality Revalidation
- Riverbed Capitalization Check
- Cold Start Re-test
- Regression & Drift Report
- Current Debt & Unknowns
- Wave 02 Candidates
- Human Selection Gate
- Selected Wave 02 Problem
- W02-P00 Acceptance Report

必须满足：

```text
Human Decision = SELECT_CANDIDATE_X
```

如果：

- 未选择；
- 选择文件为空；
- candidate 无 Evidence；
- candidate 只是技术名词；

则：

> `STOP — W02_PROBLEM_NOT_SELECTED_OR_INVALID`

---

# 3. Problem Contract

必须冻结：

## 3.1 Problem Statement

格式：

> 在 [当前真实场景] 中，因为 [可观察机制/缺口]，导致 [用户/主河道影响]。

错误：

> “我们需要 GPU。”

正确：

> “P08 的 10-song cohort 中，完整歌曲处理 wall-clock 的主要瓶颈来自 stem 阶段，导致一首歌完成时间超过当前可接受等待窗口。”

---

## 3.2 Evidence

必须列：

- source
- sample/case
- metric/observation
- confidence
- freshness

至少一个当前 W02 reality evidence。

不能只靠 W01 历史证据。

---

## 3.3 Baseline

必须有可重新测量的基线。

可能是：

- error rate
- playback failure rate
- median processing time
- first-pass acceptance
- listening verdict pattern
- manual steps count
- repeated friction occurrence
- human review burden
- recovery time

如果没有 baseline：

> 先补 measurement，不直接开发。

---

# 4. Scope Lock

必须生成：

`SCOPE_LOCK.md`

至少：

## In Scope

仅直接服务主问题。

## Out of Scope

明确写出最容易顺手扩张的邻近事项。

## Forbidden

- product identity changes
- unrelated architecture changes
- unrelated refactor
- new service unless evidence requires
- new model unless problem directly demands
- iOS unless selected problem is iOS
- hardware unless selected problem is hardware
- community/skin unless selected problem is that
- scale work unless selected problem is capacity/reliability

---

# 5. Change Budget

Wave 02 开始引入：

`CHANGE_BUDGET`

目的不是限制优秀工程，而是防止一个问题变成一次大重构。

必须记录：

- max primary modules touched
- max new persistent services
- max new authoritative data models
- max new public API surfaces
- expected migration count
- expected rollback unit

默认建议：

- 新 authoritative state machine = 0
- 新数据库 = 0
- 新长期 service = 0 或 1（必须证明）
- 新公开产品面 = 0

---

# 6. Dependency Reuse First

任何执行都必须先问：

1. 当前系统是否已经有能力？
2. 是否只是没有被正确接入？
3. 是否只是配置/观测/恢复问题？
4. 是否可以通过 D5/D6/D7 已有资产解决？
5. 是否真的需要新 dependency？

优先级：

```text
Reuse
→ Reconfigure
→ Extend
→ Replace
→ Add New
```

---

# 7. Architecture Change Gate

如果解决主问题需要改变：

- Track/Job/Object identity
- Job state authority
- queue authority
- pipeline semantics
- READY semantics
- delivery authority
- product Canon

必须标：

`CANONICAL_ARCHITECTURE_CHANGE = YES`

并返回人类审核。

W02-P01 不允许静默突破 Wave 01 的河床。

---

# 8. Minimum Intervention Plan

必须输出：

`MINIMUM_INTERVENTION_PLAN.md`

每项：

- intervention_id
- evidence
- target mechanism
- exact change
- affected files/services
- expected result
- test
- runtime validation
- rollback
- risk
- priority

优先顺序：

1. instrumentation gap
2. configuration defect
3. local code defect
4. contract defect
5. dependency issue
6. architectural issue

不要从第 6 层开始。

---

# 9. Pre-change Measurement

在改动前必须保存：

`BASELINE_MEASUREMENT.md`

要求：

- same scenario
- same version identity
- same metric definition
- timestamp
- sample/case refs
- environment
- known confounders

如果问题是听觉质量：

必须保留 source/render review evidence。

如果问题是 runtime：

保留 timings/failures/resources。

---

# 10. Execution Ledger

每个实际变化进入：

`EXECUTION_LEDGER.csv`

字段：

- change_id
- problem_ref
- commit
- files
- services
- migration
- test
- deploy status
- evidence
- rollback
- result

这样下一位 Agent 不需要重新问：

> “这次为了解决什么改了这些？”

---

# 11. Test Strategy

必须至少包含：

## Contract Test
被选择的问题对应契约是否被满足。

## Regression Test
Wave 01 主河道不能因本次修改被破坏。

至少保护：

- Golden Case
- Data identity
- Job authority
- READY
- PLAY

## Failure Test
如果主问题涉及 failure/recovery，必须模拟失败。

## Before/After Test
同一 baseline 条件下重新运行。

---

# 12. Golden Case Guard

无论 Wave 02 主问题是什么，只要修改影响主河道：

必须运行 Golden Case regression。

结果：

- PASS
- FAIL
- NOT_APPLICABLE（必须解释）

Golden Case FAIL：

> 不允许宣布 W02-P01 成功。

---

# 13. Pilot Subset Guard

如果修改影响：

- compute
- judgment
- render
- delivery
- playback

至少从 P08 中选 3 个代表 case 做回归。

目的：

> 防止只在 Golden Song 上过拟合。

---

# 14. Evidence of Improvement

最终必须回答：

## Before
问题有多严重？

## After
同一定义下变成什么？

## Delta
变化是多少？

## Cost
代价是什么？

## Trade-off
引入了什么新问题？

## Confidence
证据强度如何？

不能只写：

> “Tests passed.”

---

# 15. No Metric Gaming

如果选中的主问题是：

- speed
- cost
- listening score
- failure rate

不能通过改变口径“改善”。

例如：

- 忽略失败 case
- 缩短歌曲
- 降低音质
- 跳过 verify
- 去掉 human review
- 不记录 retry

都必须视为无效改善，除非人类明确批准新的产品契约。

---

# 16. Runtime Deployment Gate

如果 W02-P01 需要部署：

必须：

- identify target node
- deployed commit
- config diff
- health check
- rollback command
- post-deploy evidence
- no secret leakage

生产部署若未授权：

> `W02P01_DEPLOY_BLOCKED`

仍可完成 code/test/staging evidence。

---

# 17. Stop Conditions

立即停止并返回人类：

- 发现主问题定义错误；
- 当前 evidence 与 W02-P00 相反；
- 解决需要改 Canon；
- 解决需要第二套 authority；
- 需要不可逆数据迁移；
- 需要显著扩大 scope；
- Golden regression fail；
- 出现 security/data integrity risk；
- intervention 无 meaningful improvement；
- 新增复杂度明显大于收益。

---

# 18. Completion Verdict

最终只允许：

## `PROBLEM_RESOLVED`

达到预先冻结的 success criteria。

## `PROBLEM_IMPROVED`

有实证改善，但仍有明确剩余问题。

## `NO_MEANINGFUL_IMPROVEMENT`

改动存在，但基线问题没有显著改善。

## `REGRESSED`

更差或破坏主河道。

## `EVIDENCE_INSUFFICIENT`

无法可靠判断。

---

# 19. Required Outputs

至少：

1. `00_W02P01_EXECUTIVE_SUMMARY.md`
2. `01_SELECTED_PROBLEM_CONTRACT.md`
3. `02_BASELINE_MEASUREMENT.md`
4. `03_SCOPE_LOCK.md`
5. `04_CHANGE_BUDGET.md`
6. `05_MINIMUM_INTERVENTION_PLAN.md`
7. `06_EXECUTION_LEDGER.csv`
8. `07_TEST_AND_REGRESSION_REPORT.md`
9. `08_GOLDEN_CASE_REGRESSION.md`
10. `09_PILOT_SUBSET_REGRESSION.md`
11. `10_AFTER_MEASUREMENT.md`
12. `11_BEFORE_AFTER_EVIDENCE.md`
13. `12_NEW_DEBT_AND_TRADEOFFS.md`
14. `13_COMPLETION_VERDICT.md`
15. `14_NEXT_DECISION_GATE.md`
16. `15_W02P01_ACCEPTANCE_REPORT.md`

---

# 20. Next Decision Gate

W02-P01 完成后，不自动生成 W02-P02。

必须根据 Verdict：

### PROBLEM_RESOLVED
可能：
- close mini-cycle
- operate and observe
- distill

### PROBLEM_IMPROVED
可能：
- one more focused package

### NO_MEANINGFUL_IMPROVEMENT
必须：
- revisit problem model
- do not keep stacking changes

### REGRESSED
必须：
- rollback / recovery

### EVIDENCE_INSUFFICIENT
必须：
- improve measurement, not add features

---

# 21. Acceptance

- [ ] W02-P00 human-selected problem exists
- [ ] Problem Contract frozen
- [ ] current W02 evidence cited
- [ ] baseline measurable
- [ ] scope locked
- [ ] change budget explicit
- [ ] reuse-first analysis complete
- [ ] architecture change gate respected
- [ ] minimum intervention plan complete
- [ ] changes linked to problem evidence
- [ ] tests include regression
- [ ] Golden Case protected where applicable
- [ ] 3-case pilot subset protected where applicable
- [ ] after measurement uses same definition
- [ ] debt/trade-offs recorded
- [ ] completion verdict evidence-based
- [ ] no automatic W02-P02
- [ ] next human decision gate generated

---

# 22. 最终执行口令

> 执行 W02-P01 — Selected Problem Execution Framework。  
> 只有 W02-P00 已实际执行且人类明确选择一个 Wave 02 Candidate 才能开始；否则 STOP — W02_PROBLEM_NOT_SELECTED。  
> 首先冻结 Selected Problem Contract、Baseline、Scope Lock 与 Change Budget。  
> 优先复用 Wave 01 已形成的 D5/D6/D7 资产，从 instrumentation/configuration/local defect 开始寻找最小干预，不从新架构开始。  
> 每一个变化必须直接绑定问题 Evidence、预期结果、测试、runtime validation 与 rollback；任何 Canon/authority/identity 变化必须回到人类审批。  
> 执行后在相同定义下重新测量 Before/After，并运行 Golden Case 与必要的 3-case Pilot subset regression。  
> 最终只能输出 PROBLEM_RESOLVED / PROBLEM_IMPROVED / NO_MEANINGFUL_IMPROVEMENT / REGRESSED / EVIDENCE_INSUFFICIENT。  
> 不因代码完成或测试通过自动宣布问题解决，不自动生成 W02-P02，等待下一次人类决策。
