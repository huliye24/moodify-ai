# W01-P08 — 3 → 10 Song Pilot

**Wave:** Moodify Cognitive Wave 01  
**Package:** W01-P08  
**性质:** 小规模实证 / Pilot / Stability & Variability Validation  
**日期:** 2026-08-17  
**执行对象:** Codex + 人类听觉评审  
**前置依赖:** W01-P07 Golden Song 001 已完成，且 P08 Gate = OPEN  
**后继任务:** W01-P09 — First Cognitive Distillation  
**原子任务数:** 2  
**核心目标:** 在不扩功能、不追求规模化的前提下，将已经通过 Golden Song 的同一套 Moodify 系统从 1 首扩展到 3 首，再扩展到 10 首，观察它在不同歌曲上的稳定性、失败模式、资源成本、听觉结果与重复认知摩擦。

---

# 0. P08 的问题不是“能不能批量跑”

P07 已经证明：

> 一首真实歌曲是否可以完整走通 Moodify。

P08 进一步问：

> **同一套系统，在面对不同歌曲时是否仍然成立？**

因此 P08 不是批处理性能竞赛。

也不是“跑得越多越好”。

更不是开始规模化。

本包只做：

```text
1 Golden Song
      ↓
3-song smoke pilot
      ↓
Gate
      ↓
10-song pilot
      ↓
Evidence Freeze
```

---

# 1. 两个原子任务

## T08-1 — 3-Song Smoke Pilot

选择 3 首具有明显差异的合法、熟悉或可评审歌曲。

目的：

- 验证 Golden Song 不是偶然；
- 验证不同音频结构不会立刻击穿系统；
- 验证 job/control/data/compute/delivery 在连续 case 中稳定；
- 暴露最明显的 pipeline/profile/generalization 问题；
- 在进入 10 首前发现低成本问题。

只有 3 首全部通过 3-song Gate，才能进入 T08-2。

---

## T08-2 — 10-Song Pilot

在冻结系统版本后，将样本扩展到 10 首。

收集：

- 工程成功率；
- failure 分布；
- retry/recovery；
- wall-clock；
- compute/resource；
- external API 使用；
- storage；
- human review；
- BYPASS/INTERVENE 分布；
- playback success；
- blocker；
- repeated friction observations；
- version stability；
- traceability completeness。

最终冻结：

> **W01 10-SONG PILOT EVIDENCE SET**

作为 P09 第一次认知蒸馏的直接输入。

---

# 2. 硬 Gate：P07 必须真正通过

P08 执行前必须读取：

- P07 Final Verdict
- P08 Gate Report
- Golden Source Identity
- Golden Run Ledger
- Blocker Register
- Resource & Cost Report
- Human Listening Review
- Regression Baseline
- Traceability Proof
- P08 Handoff

只有：

```text
P08_GATE_OPEN
```

才能继续。

否则：

> `STOP — P08_GATE_CLOSED`

Codex 不得自行绕过。

---

# 3. Pilot 期间禁止继续“建设系统”

P08 是验证期。

禁止：

- 新功能；
- 新产品面；
- 新模型；
- 新播放器；
- 新数据库；
- 新 queue；
- 新状态机；
- 新对象身份；
- 新 UI；
- iOS；
- skin/community；
- recommendation；
- “顺便重构”；
- 为某一首歌定制硬编码逻辑。

---

# 4. Version Freeze

P08 必须先生成：

`PILOT_VERSION_FREEZE.md`

至少固定：

- repository commit
- control-plane version
- schema version
- worker version
- pipeline version
- profile/preset versions
- external adapter versions
- render policy
- verification policy
- delivery version
- Android app version

## 原则

3-song smoke 必须尽量运行在同一组版本上。

进入 10-song pilot 前：

> 再冻结一次正式 Pilot Version。

---

# 5. Pilot 中出现代码修改怎么办

这是 P08 最重要的控制规则之一。

## 5.1 在 3-song 阶段

如果发现真正阻塞问题：

允许最小修复。

但必须：

1. 进入 `PILOT_BLOCKER_REGISTER`;
2. 增加 regression test；
3. bump 相关版本；
4. 重新运行受影响的 3-song case；
5. 重新冻结版本；
6. Gate 重新评估。

---

## 5.2 在 10-song 阶段

默认不修改系统。

只有：

- data integrity risk
- security risk
- B3/B4 full-chain blocker

才允许修复。

一旦发生会改变生产语义的修改：

> 当前 cohort 必须标记 `VERSION_SPLIT`

然后由人类选择：

- `RESTART_10_SONG_COHORT`
- `CONTINUE_AS_TWO_COHORTS`
- `STOP_PILOT`

不得把不同版本的数据假装成同一批结果。

---

# 6. Song Selection Strategy

P08 不随机抓 10 首歌。

必须形成：

`PILOT_COHORT_SELECTION.md`

目标是**最大化问题覆盖，而不是最大化数量**。

---

## 6.1 3-Song Smoke

除 Golden Song 外，建议 3 首覆盖至少 3 种明显差异：

例如：

- vocal-centered / sparse
- dense pop/rock
- ambient/instrumental
- bass-heavy
- rap/spoken
- AI-generated
- older/technically limited recording
- dynamic acoustic

最终由真实授权资产决定。

---

## 6.2 10-Song Pilot

10 首应尽量覆盖：

- vocal vs instrumental
- sparse vs dense
- old vs modern
- high vs low dynamic range
- strong low-frequency vs light low-frequency
- synthetic/AI vs conventional recording（若合法样本存在）
- easy vs difficult separation
- obvious processing opportunity vs likely BYPASS
- different durations where current capacity allows

---

## 6.3 不追求统计代表性

10 首不足以支持市场总体结论。

本包只能称：

> **engineering pilot / small empirical cohort**

禁止输出：

- “Moodify 对所有音乐有效”
- “平均提升 X% 所以产品已证明”
- “行业领先”
- “统计显著”

除非未来有正式实验设计支持。

---

# 7. Cohort Registry

每首歌必须有：

- pilot_case_id
- track_id
- source_object_id
- source_hash
- rights class
- category tags
- duration
- sample rate
- channels
- familiarity level
- human reviewer
- pipeline version
- profile policy
- selection reason

禁止将真实音频本体放进 Git。

---

# 8. 每首歌统一运行协议

所有 Pilot Case 统一执行：

```text
Source Identity
  ↓
Track Registration
  ↓
Job
  ↓
Queue / Claim / Attempt
  ↓
Compute Pipeline
  ↓
Verify
  ↓
READY
  ↓
Delivery
  ↓
Android PLAY
  ↓
Human A/B Review
  ↓
Case Verdict
```

不能为了让某首歌通过，而人工跳过关键基础设施。

---

# 9. Case Verdict

每首歌必须有两个 Verdict。

## Engineering Verdict

- `PASS`
- `PASS_WITH_RECOVERY`
- `PASS_WITH_BLOCKER_FIX`
- `FAIL`

## Listening Verdict

- `RENDER_PREFERRED`
- `SOURCE_PREFERRED`
- `NO_MEANINGFUL_DIFFERENCE`
- `MIXED_TRADEOFF`
- `BYPASS_CORRECT`
- `INVALID_REVIEW`

---

# 10. 3-Song Gate

必须形成：

`THREE_SONG_GATE_REPORT.md`

建议最低条件：

- 3/3 无 B4；
- 3/3 数据 provenance 完整；
- 3/3 Job state 合法；
- 3/3 可得到明确工程 Verdict；
- 至少 2/3 完整到 Android PLAY；
- 若有失败，必须是已理解且不表明系统主链失稳；
- 没有重复出现的严重 silent corruption；
- 没有泄漏 Secret；
- 没有未解决的状态机双权威；
- 没有孤立 READY；
- pipeline version 可以正式冻结。

最终：

- `TEN_SONG_GATE_OPEN`
- `TEN_SONG_GATE_CLOSED`

如果关闭：

> 停止，不跑 10 首。

---

# 11. 10-Song Pilot Measurement

P08 必须收集真实观测，不做猜测。

---

## 11.1 Engineering

- cases attempted
- engineering pass
- pass with recovery
- pass with blocker fix
- failed
- first-pass completion
- retries
- attempts
- stale lease incidents
- orphan object incidents
- missing object incidents
- READY guard rejections
- playback failures
- traceability completeness

---

## 11.2 Compute / Cost

每首：

- queue wait
- total wall-clock
- active compute time
- stem time
- analysis time
- render time
- verify time
- external API time
- human review time
- CPU
- RAM peak
- swap peak
- scratch peak
- input bytes
- output bytes
- external usage/cost

---

## 11.3 Listening

统计只做描述性汇总：

- RENDER_PREFERRED
- SOURCE_PREFERRED
- NO_MEANINGFUL_DIFFERENCE
- MIXED_TRADEOFF
- BYPASS_CORRECT
- INVALID_REVIEW

并保存每首的自由文本。

禁止只保留平均分。

---

## 11.4 Intervention

记录：

- intervention count
- bypass count
- human-review-required count
- profile distribution
- verify fail count
- re-render count

重要：

> BYPASS 高不等于系统差。

如果歌曲不需要处理，正确 BYPASS 反而是系统判断能力。

---

# 12. Repeated Friction Observation

P08 不进行最终蒸馏，但必须开始收集 P09 的原始材料。

建立：

`REPEATED_FRICTION_LOG.md`

每当出现重复现象：

- 同样上下文反复查询；
- 同样服务器路径反复确认；
- 同样 error 反复诊断；
- 同样 command 人工重复；
- 同样 evidence 手工拼接；
- 同样 human review 结构反复解释；
- 同样 deployment state 反复确认；

记录：

- friction_id
- occurrence_count
- affected cases
- repeated cognitive cost
- current workaround
- candidate D0-D7 level
- **不在 P08 直接蒸馏**

P09 才决定 KEEP / RULE / TEST / TOOL / INFRASTRUCTURE / DELETE。

---

# 13. Failure Distribution

建立：

`PILOT_FAILURE_DISTRIBUTION.md`

必须把失败按现有 taxonomy 聚类。

关注：

- 单次异常
- 重复异常
- 系统性异常
- 音频类型相关异常
- 外部 API 相关
- 资源相关
- 数据完整性相关
- playback 相关

禁止一遇失败就增加新的顶层 failure class。

---

# 14. Human Listening Protocol

为了让 10 首结果可比较，尽量固定：

- reviewer
- device
- environment
- approximate loudness matching
- review template
- source/render order strategy

如果换 reviewer/device：

记录，不伪装为完全一致条件。

---

# 15. Listening Review 负担控制

每首至少：

- source baseline note
- render note
- verdict
- key improvement
- key regression
- artifact check
- whether intervention was worth it

不要求每首写长篇文章。

P09 需要的是：

> 可比较、可回看、有自由文本证据。

---

# 16. First-Pass Acceptance

P08 引入一个重要观测：

`first_pass_acceptance`

定义：

> 一个 case 在不发生代码修复、不发生 retry、不需要人工修复数据的情况下，是否一次完整走到目标状态。

取值：

- YES
- NO

它比“最终能跑通”更能揭示系统摩擦。

---

# 17. Recovery Observation

对所有发生 recovery 的 case 记录：

- trigger
- automatic/manual
- time to recovery
- lost work
- duplicated work
- evidence preserved
- state correct after recovery

目标：

不是追求 0 failure。

而是：

> failure 发生后是否仍然可解释、可恢复。

---

# 18. Traceability Coverage

每个 case 必须检查：

```text
Playback
→ Render
→ READY Job
→ Attempt
→ Pipeline
→ Inputs
→ Source
```

标记：

- COMPLETE
- PARTIAL
- BROKEN

任何 BROKEN 都不能隐藏在“歌曲可以听”后面。

---

# 19. Data Integrity Checks

每 3 首 / 10 首阶段后执行：

- orphan object scan
- missing object scan
- duplicate logical job scan
- invalid terminal transition scan
- stale RUNNING/lease scan
- object hash verification sample
- READY without object scan
- Evidence missing subject scan

---

# 20. Pilot Stop Conditions

出现以下任一情况，立即暂停：

- B4 security issue
- source ownership/rights issue
- source overwrite
- database corruption
- object identity collision
- Job state double authority
- stale worker can overwrite valid result
- READY without valid render
- secret exposure
- repeated unexplained audio corruption
- version provenance lost

输出：

`PILOT_STOP_EVENT`

不得为了凑够 10 首继续。

---

# 21. Pilot Aggregate Report

必须形成：

`TEN_SONG_PILOT_AGGREGATE.md`

至少包含：

## Cohort
- attempted
- completed
- failed
- categories
- durations

## Engineering
- first-pass acceptance
- final pass
- retries
- blocker fixes
- recovery
- traceability

## Compute
- median / range where meaningful
- not fake precision
- external dependency usage

## Listening
- verdict distribution
- major recurring improvements
- major recurring regressions
- artifact patterns

## System Friction
- repeated issues
- repeated manual steps
- repeated context retrieval
- candidate distillation items

## Limits
- small sample
- human review subjectivity
- version changes
- external service variability
- no population-level claims

---

# 22. P09 Evidence Freeze

P08 完成后必须冻结一个：

`W01_PILOT_EVIDENCE_INDEX.md`

所有 P09 蒸馏结论只能引用：

- P00 reality
- P01 canon changes
- P02 architecture decisions
- P03 data evidence
- P04 control evidence
- P05 compute evidence
- P06 playback evidence
- P07 Golden Case
- P08 3/10 pilot

P09 不应该重新凭印象讨论整个 Wave。

---

# 23. 必须输出的文件

至少：

1. `00_P08_EXECUTIVE_SUMMARY.md`
2. `01_PILOT_VERSION_FREEZE.md`
3. `02_PILOT_COHORT_SELECTION.md`
4. `03_PILOT_COHORT_REGISTRY.csv`
5. `04_THREE_SONG_RUN_LEDGER.csv`
6. `05_THREE_SONG_GATE_REPORT.md`
7. `06_TEN_SONG_RUN_LEDGER.csv`
8. `07_CASE_VERDICTS.csv`
9. `08_RESOURCE_COST_MATRIX.csv`
10. `09_LISTENING_REVIEW_MATRIX.csv`
11. `10_PILOT_BLOCKER_REGISTER.md`
12. `11_PILOT_FAILURE_DISTRIBUTION.md`
13. `12_REPEATED_FRICTION_LOG.md`
14. `13_DATA_INTEGRITY_REPORT.md`
15. `14_RECOVERY_REPORT.md`
16. `15_TRACEABILITY_COVERAGE.md`
17. `16_TEN_SONG_PILOT_AGGREGATE.md`
18. `17_W01_PILOT_EVIDENCE_INDEX.md`
19. `18_P09_HANDOFF.md`
20. `19_P08_ACCEPTANCE_REPORT.md`

---

# 24. P09 Handoff

P09 是第一次真正的项目认知蒸馏。

P08 不替 P09下结论。

P09 接收：

- version freeze
- all case ledgers
- blocker register
- failure distribution
- resource/cost matrix
- listening matrix
- repeated friction log
- data integrity
- recovery
- traceability
- pilot aggregate
- evidence index

P09 唯一问题：

> **这一整个 Wave 结束后，哪些已经支付过的认知成本，应该被永久消除？**

---

# 25. 验收标准

## Gate
- [ ] P07 Gate = OPEN
- [ ] Pilot Version Freeze 完成

## 3-Song
- [ ] cohort selected
- [ ] rights clear
- [ ] 3 cases executed
- [ ] case verdicts complete
- [ ] integrity scan
- [ ] Three-Song Gate completed

## 10-Song
- [ ] Gate open before execution
- [ ] version cohort clear
- [ ] 10 cases attempted according to plan
- [ ] no hidden version mixing
- [ ] every case has engineering verdict
- [ ] every valid case has listening verdict
- [ ] every case has traceability status

## Evidence
- [ ] resource/cost matrix
- [ ] failure distribution
- [ ] blocker register
- [ ] recovery report
- [ ] repeated friction log
- [ ] data integrity report
- [ ] aggregate report
- [ ] evidence index

## Discipline
- [ ] no feature expansion
- [ ] no unsupported population claims
- [ ] BYPASS not treated as automatic failure
- [ ] version-changing fixes explicitly split/restart cohort
- [ ] Pilot Stop Conditions respected

## Handoff
- [ ] P09 handoff complete
- [ ] stop after P08
- [ ] do not begin distillation automatically

---

# 26. 最终执行口令

> 执行 W01-P08 — 3 → 10 Song Pilot。  
> 只有 P07 明确输出 P08_GATE_OPEN 才能开始。  
> 先冻结完整 Pilot Version，然后选择具有差异性的合法 3-song smoke cohort；统一运行完整 Source → Job → Compute → READY → Android PLAY → Human Review 主链。  
> 只有 THREE_SONG_GATE_OPEN 才能扩展至 10-song pilot。  
> Pilot 期间禁止功能扩张和顺手重构；3-song 阶段如遇真实 blocker，只做最小修复、加回归测试、重新冻结并重跑受影响 case；10-song 阶段若发生生产语义版本变化，必须 VERSION_SPLIT 并由人类决定重启或拆 cohort。  
> 收集工程成功、first-pass acceptance、retry/recovery、资源成本、external usage、BYPASS/INTERVENE、人耳 verdict、traceability、failure distribution、data integrity 与 repeated friction。  
> 不把 10 首结果包装成总体统计结论。  
> 完成 W01 Pilot Evidence Index 与 P09 Handoff 后停止，等待人类审核，不自动进入蒸馏。
