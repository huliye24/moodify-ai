# W01-P07 — Golden Song 001

**Wave:** Moodify Cognitive Wave 01  
**Package:** W01-P07  
**性质:** 单曲全链验收 / Golden Case / Reality Validation  
**日期:** 2026-08-17  
**执行对象:** Codex + 人类听觉评审  
**前置依赖:** W01-P00 ~ W01-P06 已完成并通过人类审核  
**后继任务:** W01-P08 — 3 → 10 Song Pilot  
**原子任务数:** 2  
**核心目标:** 选择一首真实、熟悉、授权的歌曲，从 Source 一直跑到 Android PLAY，并冻结一份完整、可追溯的 Golden Case Evidence Pack。

---

# 0. P07 开始以后，开发模式发生变化

P00–P06 的主要工作是：

- 扫描；
- 收敛；
- 建设；
- 契约；
- 测试。

P07 不再继续扩系统。

P07 的问题只有一个：

> **前面建立的 Moodify，能不能真的把一首歌完整、干净、可解释地跑通？**

因此 P07 的首要原则是：

# No Feature Expansion

如果过程中发现问题：

只允许修复：

> **阻塞 Golden Song 001 完成的最小问题。**

禁止：

- 顺手优化 UI；
- 顺手加入新模型；
- 顺手替换数据库；
- 顺手换播放器；
- 顺手引入新处理工具；
- 顺手重写 pipeline；
- 顺手扩展多用户系统；
- 顺手做批量处理；
- 顺手做推荐；
- 顺手加入社区/皮肤/iOS。

---

# 1. 两个原子任务

# T07-1 — Select & Run Golden Song 001

选择一首：

- 人类非常熟悉；
- 有合法处理与测试权限；
- 音频质量足以暴露系统问题；
- 时长接近真实完整歌曲；
- 具有一定动态、频谱、声部和结构复杂度；
- 能进行 source / processed A-B 评审；
- 适合未来作为回归样本之一；

的真实歌曲。

然后完整运行：

```text
Source
  ↓
Identity / Hash
  ↓
Upload / Object Registration
  ↓
Track
  ↓
Job
  ↓
Claim / Lease / Attempt
  ↓
Acquire
  ↓
Validate
  ↓
Stem (if pipeline requires)
  ↓
Analyze
  ↓
Judge
  ↓
Intervene / BYPASS
  ↓
Profile
  ↓
Render
  ↓
Verify
  ↓
READY
  ↓
Authorized Delivery
  ↓
Android
  ↓
PLAY
```

---

# T07-2 — Blocker-Only Fix + Evidence Freeze

如果链路失败：

1. 定位最小阻塞点；
2. 判断属于 P03/P04/P05/P06 哪一层；
3. 只修复该阻塞；
4. 添加回归测试；
5. 从合理断点重新运行；
6. 不把阻塞修复扩展为“下一轮重构”。

最终冻结：

> **GOLDEN_CASE_001_EVIDENCE_PACK**

作为未来 P08、P09 和后续回归测试的重要现实证据。

---

# 2. Golden Song 选择 Gate

## GATE P07-0 — Human Song Selection

Codex 不得自行从互联网下载一首歌充当 Golden Song。

必须由人类：

- 提供音频文件；或
- 指明当前项目资产中哪一个真实、合法文件作为 Golden Song。

如果没有明确输入：

> `STOP — GOLDEN_SONG_NOT_SELECTED`

---

## 2.1 权利与隐私确认

至少记录：

- source file reference
- rights/authorization class
- internal-only / distributable
- whether evidence may include waveform/metrics
- whether audio may enter cloud
- whether processed render may remain stored
- whether it may be used for future regression

不把真实音频打包进 Git 或任务包。

---

# 3. Golden Song 选择标准

必须使用 `GOLDEN_SONG_SELECTION_SCORECARD.md`。

建议维度：

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Human familiarity | unfamiliar | somewhat known | deeply familiar |
| Rights clarity | unclear | limited | clear |
| Full-song realism | synthetic fragment | partial | full real track |
| Acoustic complexity | simple | medium | representative |
| Dynamic range | flat | moderate | useful |
| Vocal/instrument interaction | absent | limited | rich |
| Processing sensitivity | low | medium | high |
| A/B usefulness | weak | moderate | strong |
| Regression usefulness | low | medium | high |

最低要求由人类/Codex共同决定，但任何 rights 不明确项都不能进入 Golden Case。

---

# 4. Freeze Input Before Run

选定后立刻生成：

`GOLDEN_SOURCE_IDENTITY.md`

必须包含：

- Golden Case ID
- Track ID
- local source reference
- source object ID
- SHA-256
- byte size
- duration
- sample rate
- channels
- codec/container
- ingest timestamp
- rights class
- selection reason

一旦冻结：

> 不允许偷偷换 source 文件继续叫 Golden Song 001。

如果 source 必须更换：

生成：

`Golden Song 002` 或明确版本升级。

---

# 5. Run Identity

每次完整尝试必须有：

- golden_case_id
- run_id
- job_id
- attempt_id
- pipeline_version
- profile_version
- production_fingerprint
- app version
- control-plane version
- worker version
- start/end timestamp

所有 run 都保留。

不允许只保留“最后成功的一次”，把前面的失败删掉。

---

# 6. Baseline Before Processing

在任何 Intervention 之前，冻结 baseline。

至少：

## Technical

- source hash
- duration
- sample rate
- channels
- peak
- loudness
- clipping
- basic spectrum/dynamic metrics
- decode health

## Human Baseline

人类用固定播放设备/环境听 source。

记录：

- clarity
- vocal/instrument relation
- low-frequency impression
- high-frequency impression
- dynamics
- space
- fatigue
- overall character
- specific known weaknesses
- things that must not be lost

不要强迫量化全部审美。

自由文本必须保留。

---

# 7. Stage-by-Stage Evidence

每个执行 stage 都必须进入 Run Ledger。

至少：

| Stage | Start | End | Status | Input | Output | Evidence | Duration | Notes |
|---|---|---|---|---|---|---|---|---|

状态：

- SUCCEEDED
- BYPASSED
- FAILED
- HUMAN_REVIEW_REQUIRED

---

# 8. Cost & Resource Evidence

P07 必须记录真实成本，而不是未来估算。

至少：

- total wall-clock time
- queue wait
- compute time
- stem external time
- external API usage
- external API cost（如果可得）
- CPU peak/average（合理采集）
- RAM peak
- swap peak
- scratch peak
- source bytes
- output bytes
- retry count
- number of attempts
- human review time

如果成本无法精确获得：

> 标 `UNKNOWN`，不要猜。

---

# 9. Blocker Policy

发现问题时进入：

`BLOCKER_REGISTER.md`

每个 blocker：

- blocker_id
- layer
- symptom
- evidence
- root cause
- blocks golden song? yes/no
- minimum fix
- files changed
- regression test
- rerun point
- resolution
- introduced new capability? must be NO

只有：

`blocks_golden_song = YES`

才能在 P07 修。

否则：

> `DEFER_TO_P09_OR_NEXT_WAVE`

---

# 10. Blocker Severity

## B0 — Cosmetic / Non-blocking

不修。

## B1 — Evidence inconvenience

如果不影响可追溯性，可以 defer。

## B2 — Partial functional blocker

阻碍主链的一部分；允许最小修复。

## B3 — Full chain blocker

必须修复或停止 Golden Case。

## B4 — Safety / data integrity / security risk

立即停止运行：

> `STOP — GOLDEN_CASE_SAFETY_BLOCK`

先修复风险，再继续。

---

# 11. Human Listening Review

P07 的人耳不是装饰。

这是第一次把系统输出与人类实际听感放到同一个 Evidence Pack。

至少进行：

- source
- final render

A/B。

如果可能：

- 音量匹配；
- 同一设备；
- 同一环境；
- 随机化 A/B 标签（可选）；
- 记录首次感受；
- 再记录集中比较。

---

## 11.1 评审维度

建议：

- clarity
- tonal balance
- low-end control
- vocal presence
- transient quality
- dynamics
- stereo space
- separation
- fatigue
- emotional integrity
- artifacts
- overall preference

评分可以使用 1–5。

但最终结论必须允许：

- source preferred
- render preferred
- no meaningful difference
- mixed / trade-off
- invalid comparison

---

## 11.2 Moodify Success 不等于“必须更好”

Golden Song 成功分两层：

### Engineering Success
整条系统正确跑通、可追溯、可恢复、可播放。

### Auditory Success
处理后的版本是否真的值得使用。

因此完全允许：

```text
Engineering = PASS
Auditory = BYPASS / SOURCE_PREFERRED
```

这不是失败。

它说明 Moodify 学会了：

> **不应该改的时候不改。**

---

# 12. Golden Case Verdict

最终必须形成两个独立 Verdict：

## System Verdict

- PASS
- PASS_WITH_BLOCKER_FIXES
- FAIL

## Listening Verdict

- RENDER_PREFERRED
- SOURCE_PREFERRED
- NO_MEANINGFUL_DIFFERENCE
- MIXED_TRADEOFF
- INVALID_REVIEW

不能用一个“总分”把两类结论混在一起。

---

# 13. PLAY Acceptance

真正完成必须在 Android 上听。

不能只在服务器上：

> “文件生成成功。”

最低动作：

```text
Open Moodify
→ load Golden Track
→ PLAY
→ pause
→ resume
→ seek
→ finish / sufficient listening
```

如果当前产品范围含上下切歌：

可测试 Golden Track 与一个测试邻接 Track 的切换。

但不因 P07 创建新 playlist 系统。

---

# 14. End-to-End Traceability

最终必须从 Android Playback Event 反查：

```text
Playback Session
   ↓
Render Object
   ↓
READY Job
   ↓
Completion Candidate
   ↓
Attempt
   ↓
Pipeline Version
   ↓
Stage Results
   ↓
Input Objects
   ↓
Source Object
   ↓
SHA-256
   ↓
Golden Track
```

如果中间任意一段断裂：

> Golden Case 不能标记为完整 PASS。

---

# 15. Recovery Exercise

P07 必须至少故意验证一次恢复能力，但不得破坏生产数据。

从以下选一项：

- worker process restart in test-safe point
- temporary network interruption simulation
- expired playback URL refresh
- safe retry of a transient synthetic failure

目的：

> 证明系统不是“恰好一次跑通”，而是具备恢复语义。

如果无法安全执行：

记录：

`RECOVERY_EXERCISE_DEFERRED`

并说明原因。

---

# 16. Regression Freeze

Golden Case 通过后必须冻结：

- source hash
- expected pipeline contract
- required invariants
- final render identity
- technical verification
- listening verdict
- known tolerances
- known acceptable BYPASS behavior

未来不要求 final bytes 永远完全一样。

因为工具/model 可能升级。

但未来必须能检测：

- identity break
- provenance break
- catastrophic audio regression
- playback regression
- evidence loss
- unexpected state-machine behavior

---

# 17. Golden Case Evidence Pack

目录建议：

```text
golden_case_001/
├── 00_CASE_SUMMARY.md
├── 01_SOURCE_IDENTITY.md
├── 02_RUN_LEDGER.csv
├── 03_PIPELINE_EVIDENCE_INDEX.md
├── 04_BLOCKER_REGISTER.md
├── 05_RESOURCE_AND_COST_REPORT.md
├── 06_TECHNICAL_BEFORE_AFTER.md
├── 07_HUMAN_LISTENING_REVIEW.md
├── 08_PLAYBACK_ACCEPTANCE.md
├── 09_RECOVERY_EXERCISE.md
├── 10_TRACEABILITY_PROOF.md
├── 11_REGRESSION_BASELINE.md
└── 12_FINAL_VERDICT.md
```

音频对象本身继续留在受控对象存储，不直接塞进 Git。

Evidence Pack 只保存：

- identities
- refs
- hashes
- metrics
- screenshots/log refs where safe
- review
- verdict

---

# 18. Golden Song 失败怎么办

如果经过合理 blocker fix，仍无法完成：

不要为了“通过任务”伪造 PASS。

输出：

`GOLDEN_CASE_001 = FAIL`

并明确：

- failure layer
- blocking reason
- last valid checkpoint
- missing capability
- P08 forbidden
- recommended next action

只有 P07 Engineering Verdict 为：

- PASS
- PASS_WITH_BLOCKER_FIXES

才能进入 P08。

---

# 19. P08 Gate

P08 的 3 → 10 Pilot 只有在以下条件下打开：

- Golden source identity frozen
- complete provenance chain
- Job/control plane stable
- compute E2E complete
- READY delivery complete
- Android PLAY complete
- critical security/data integrity issue = 0
- blocker register has no B3/B4 open item
- System Verdict = PASS / PASS_WITH_BLOCKER_FIXES
- human listening review completed

否则：

> `STOP — P08_GATE_CLOSED`

---

# 20. 必须通过的测试 / 验收

## Identity
- [ ] source hash frozen
- [ ] Track ID stable
- [ ] Job/Attempt IDs traceable

## Data Plane
- [ ] source uploaded/registered
- [ ] objects registered
- [ ] no orphan/missing critical object

## Control Plane
- [ ] job enters legal states only
- [ ] attempt/lease visible
- [ ] retries/recovery auditable if used

## Compute
- [ ] stage results complete
- [ ] pipeline version frozen
- [ ] production fingerprint generated
- [ ] BYPASS/intervention decision evidenced
- [ ] render verified

## Delivery
- [ ] READY confirmed
- [ ] playback metadata valid
- [ ] Android PLAY
- [ ] pause/resume
- [ ] seek
- [ ] no client secret exposure

## Human
- [ ] source baseline listening
- [ ] render listening
- [ ] verdict
- [ ] trade-offs recorded

## Evidence
- [ ] full traceability
- [ ] resource/cost report
- [ ] blocker register
- [ ] final verdict
- [ ] regression baseline

---

# 21. 必须输出的文件

至少：

1. `00_P07_EXECUTIVE_SUMMARY.md`
2. `01_GOLDEN_SONG_SELECTION.md`
3. `02_GOLDEN_SOURCE_IDENTITY.md`
4. `03_GOLDEN_RUN_LEDGER.csv`
5. `04_BLOCKER_REGISTER.md`
6. `05_RESOURCE_AND_COST_REPORT.md`
7. `06_TECHNICAL_BEFORE_AFTER.md`
8. `07_HUMAN_LISTENING_REVIEW.md`
9. `08_PLAYBACK_ACCEPTANCE.md`
10. `09_RECOVERY_EXERCISE.md`
11. `10_TRACEABILITY_PROOF.md`
12. `11_REGRESSION_BASELINE.md`
13. `12_FINAL_VERDICT.md`
14. `13_P08_GATE_REPORT.md`
15. `14_P08_HANDOFF.md`
16. `15_P07_ACCEPTANCE_REPORT.md`

---

# 22. 允许修改

仅允许：

- 修复直接阻塞 Golden Song 的代码；
- 添加对应回归测试；
- 必要的小型配置修正；
- 必要的 instrumentation；
- Golden Case Evidence Pack。

每个修复必须进入 Blocker Register。

---

# 23. 禁止修改

- 新功能
- 新模型
- 新第三方服务（除非 P05 已决定但缺配置，且人类授权）
- 产品 Canon
- 新 UI 设计
- 大规模 refactor
- 新数据库
- 新 queue
- 新播放器框架
- iOS
- 皮肤/社区
- recommendation
- batch processing
- P08 pilot

---

# 24. P08 Handoff

P08 收到的不是“系统已经完成”的抽象说法。

它必须收到：

- Golden Case source identity
- final successful run identity
- P07 blocker history
- current pipeline version
- current profile policy
- current compute cost/time
- current playback delivery
- listening verdict
- regression baseline
- open non-blocking issues

P08 再回答：

> **同一套系统从 1 首扩到 3 首，再扩到 10 首时，是否仍然成立？**

---

# 25. 最终执行口令

> 执行 W01-P07 Golden Song 001。  
> 不再扩展系统。首先等待/核验人类明确指定的一首真实、熟悉、授权音频；没有明确歌曲就 STOP — GOLDEN_SONG_NOT_SELECTED。  
> 冻结 source identity 与 SHA-256，然后从 Source → Data Plane → Job → Worker → Compute → Verify → READY → Delivery → Android → PLAY 完整运行。  
> 所有失败进入 Blocker Register，只修复真正阻塞 Golden Song 的最小问题，并添加对应回归测试；不做任何顺手重构或功能扩张。  
> 完成人类 Source/Render A-B 听觉评审，并将 Engineering Verdict 与 Listening Verdict 分开。  
> 冻结完整 Golden Case Evidence Pack、资源/成本、恢复演练、端到端 traceability 与 regression baseline。  
> 只有 P08 Gate 全部通过，才允许进入 3 → 10 Song Pilot；否则停止并等待人类审核。
