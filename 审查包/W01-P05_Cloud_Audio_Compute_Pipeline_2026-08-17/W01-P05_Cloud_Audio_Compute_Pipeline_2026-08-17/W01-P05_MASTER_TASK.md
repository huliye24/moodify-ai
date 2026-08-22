# W01-P05 — Cloud Audio Compute Pipeline

**Wave:** Moodify Cognitive Wave 01  
**Package:** W01-P05  
**性质:** 音频计算主链建设 / Worker Pipeline / Render & Verification  
**日期:** 2026-08-17  
**执行对象:** Codex  
**前置依赖:** W01-P00 ~ W01-P04 已完成并通过人类审核  
**后继任务:** W01-P06 Delivery + PLAY  
**原子任务数:** 2  
**核心目标:** 让一个已经被 P04 合法 claim 的 RUNNING Job，在不改变控制平面权威的前提下，完成一次可追溯、可恢复、可验证的音频计算，并产出 READY candidate。

---

# 0. P05 的唯一问题

P04 已经解决：

- Job 是谁；
- Track 是谁；
- 谁拥有当前 lease；
- retry 怎么发生；
- failure 怎么记录；
- 状态怎么变化；
- READY 的控制权属于谁。

P05 不再讨论这些。

P05 只回答：

> **拿到一个合法 RUNNING Job 以后，Worker 具体怎么算？**

并且必须满足：

> **算出来的不只是一个音频文件，而是一条可以解释、复现、验证、失败可恢复的生产链。**

---

# 1. 两个原子任务

## T05-1 — Unified Audio Compute Pipeline

把当前已经存在、且被 P00/P01 判定为可保留的能力收敛到一条 pipeline：

```text
Acquire Source
   ↓
Validate Input
   ↓
Stem / Separate      (if required)
   ↓
Analyze
   ↓
Judge / Ear
   ↓
Intervene            (or BYPASS)
   ↓
Preset / Profile Decision
   ↓
Render
   ↓
Verify
   ↓
Register Artifacts
   ↓
Return Completion Candidate
```

注意：

- 这是一条内部生产线；
- 不是用户 UI；
- 不要求所有歌曲都走全部步骤；
- 每一步都必须有明确输入、输出和证据；
- 不允许 pipeline 自己把 Job 直接改成 READY；
- READY 仍由 P04 控制平面根据 completion contract 决定。

---

## T05-2 — Pipeline Version / Failure / BYPASS / Recovery / Output Contract

固定：

- pipeline version
- stage vocabulary
- stage input/output contract
- stage failure semantics
- BYPASS semantics
- verification gate
- local scratch lifecycle
- external-service adapter contract
- output object registration
- replay/recovery boundary
- deterministic production fingerprint

---

# 2. 前置 Gate

## GATE P05-0 — Control Plane Gate

必须读取 P04：

- Authoritative State Machine
- State Transition Matrix
- Lease Contract
- Retry Policy
- Failure Taxonomy
- Event & Attempt Model
- Idempotency Contract
- Control API / Command Contract
- P05 Handoff
- P04 Acceptance Report

若以下任一项仍不明确：

- attempt identity
- lease/fencing
- failure report path
- completion command
- output object registration path

则：

> `STOP — CONTROL_PLANE_CONTRACT_INCOMPLETE`

---

## GATE P05-1 — Data Plane Gate

必须读取 P03：

- Data Identity Contract
- Object Key Convention
- Object Manifest
- Metadata Data Model
- Data Plane Invariants
- Object Storage Adapter status
- Provenance tests

若 P05 不能安全注册 output object：

> `STOP — OUTPUT_REGISTRATION_INCOMPLETE`

---

## GATE P05-2 — Capability Reality Gate

必须基于 P00/P01/P02 重新核验当前真实可用能力：

- FFmpeg
- stem/separation tool
- analysis code
- Ear/judgment code
- DSP/intervention chain
- preset/profile logic
- render path
- verification path
- external APIs
- worker runtime dependencies

每个能力只能归类为：

- `CANONICAL_AVAILABLE`
- `INTERNAL_AVAILABLE`
- `EXPERIMENTAL_AVAILABLE`
- `EXTERNAL_AVAILABLE`
- `UNAVAILABLE`
- `UNKNOWN`

禁止把“讨论过”当“已接入”。

---

# 3. 先做 Capability Map，再改 Pipeline

必须先输出：

`CURRENT_AUDIO_CAPABILITY_MAP.md`

至少包含：

| Capability | Current implementation | Runtime verified | Canon class | Input | Output | Failure behavior | Decision |
|---|---|---:|---|---|---|---|---|

需要检查：

- current core pipeline
- Auditory Intelligence / Ear
- existing v0.1 process path
- PR #21 worker/data-factory code
- any Demucs/LALAL/Audiolla integration
- FFmpeg usage
- treatment/preset systems
- verification/evidence systems

### 硬规则

> **P05 不允许为了“统一”而把所有历史处理代码都塞进主线。**

只允许保留：

- 当前 Canon 需要；
- 已有现实能力；
- 对 One Song 主链有直接价值；
- 能被验证和追溯。

---

# 4. Pipeline Stage Vocabulary

P04 已经规定：

> State != Stage

P05 负责 stage vocabulary。

建议最小候选：

```text
ACQUIRE
VALIDATE
STEM
ANALYZE
JUDGE
INTERVENE
PROFILE
RENDER
VERIFY
REGISTER
```

最终可根据真实实现收敛。

每个 stage 必须有：

- stage_id
- stage_name
- required / optional
- preconditions
- input object types
- output object types
- executor
- tool/model version
- timeout
- failure mappings
- retry safety
- evidence produced
- cleanup responsibility
- bypass eligibility

---

# 5. Stage Contract

必须形成 `PIPELINE_STAGE_CONTRACT.md`。

## 5.1 Stage 输入

任何 stage 不得依赖“上一步留下的神秘本地文件”。

输入必须来自：

- P03 object reference
- explicit config
- pipeline context
- previous stage result manifest

---

## 5.2 Stage 输出

输出必须明确属于：

- durable object
- temporary scratch
- metadata
- evidence
- decision

并说明：

- 是否持久化
- 是否进入 OSS
- 是否进入 DB
- 谁清理

---

## 5.3 Stage Result

建议统一结构：

```json
{
  "stage": "ANALYZE",
  "status": "SUCCEEDED",
  "attempt_id": "...",
  "input_objects": ["..."],
  "output_objects": ["..."],
  "evidence_refs": ["..."],
  "metrics": {},
  "decision": null,
  "failure": null,
  "producer_version": "...",
  "started_at": "...",
  "finished_at": "..."
}
```

状态建议只用于 stage result：

- `SUCCEEDED`
- `BYPASSED`
- `FAILED`

不要创造另一套 job lifecycle。

---

# 6. ACQUIRE / VALIDATE

## ACQUIRE

Worker 根据 P03 object ref 下载 canonical source 到 local scratch。

必须验证：

- object exists
- content hash
- expected byte size
- accessible mime/type
- lease/fencing still valid before expensive work

---

## VALIDATE

最低验证：

- readable audio
- duration
- sample rate
- channels
- codec/container
- decode succeeds
- not empty
- not obviously truncated（如果可检测）
- size/duration within current capacity contract

失败映射：

- unsupported input → `INPUT_INVALID`
- corrupt source → `INPUT_INVALID`
- storage fetch transient → `STORAGE_TRANSIENT`

---

# 7. STEM / Separation

STEM 是 optional stage。

是否执行必须由：

- pipeline version/profile
- track requirements
- canonical decision

决定。

禁止：

> 每首歌都无条件分轨，只因为系统“能分轨”。

---

## 7.1 Adapter Contract

无论使用：

- local Demucs
- LALAL.AI
- other external API
- future internal separator

都必须通过统一 adapter：

```text
separate(input_object, requested_roles, context)
→ StemResult
```

StemResult 至少：

- provider
- provider_version/model
- requested roles
- produced stems
- content hashes
- duration alignment
- sample rate
- channel count
- evidence
- provider job reference（如外部）

---

## 7.2 External API Rule

外部服务必须：

- timeout
- rate-limit mapping
- retryable/permanent classification
- no secret logging
- provider job id recorded
- input/output provenance preserved
- provider version/model if available
- cost/usage metadata if available

P05 不把外部 API 当成不可解释黑洞。

---

# 8. ANALYZE

ANALYZE 输出结构化听觉/工程特征。

优先复用当前已经存在的 Moodify 分析能力。

可包括：

- waveform metrics
- loudness
- peak
- dynamics
- spectrum
- phase/channel relationship
- clipping
- transient/density features
- structural features（如果已有）
- stem statistics（如果 stem exists）

禁止：

> 为了 P05 新建一个完整研究体系。

P05 只把已验证能力接入生产 contract。

---

# 9. JUDGE / Internal Ear

这是内部能力，不是公开产品面。

JUDGE 必须输出：

- judgment_id
- subject
- observations
- detected conditions
- confidence / uncertainty
- evidence refs
- recommended action
- `INTERVENE / BYPASS / HUMAN_REVIEW`

不得只输出一个“质量分”。

---

## 9.1 Human Authority

如果当前判断仍需要人耳权威：

必须允许：

`HUMAN_REVIEW_REQUIRED`

P05 不允许因为自动化方便就删除人类判断边界。

但 W01 的 One Song 主链若要自动完成，也必须明确：

- 什么条件可以自动继续
- 什么条件必须停住
- P07 Golden Song 如何提供人工确认

---

# 10. INTERVENE

INTERVENE 只在有理由时运行。

输入：

- source/stems
- judgment
- profile
- approved processing chain

输出：

- transformed object(s)
- processing manifest
- parameter manifest
- tool version
- evidence refs

---

## 10.1 BYPASS

BYPASS 是一级合法决策，不是失败。

满足以下情况可以 BYPASS：

- 未发现足够证据支持干预；
- 干预收益不确定；
- 当前 profile 明确保留原信号；
- verification 发现处理版本不优于 source；
- 人类 authority 要求保留。

BYPASS 必须记录：

- reason
- evidence
- decision owner
- affected stages
- source/final relationship

原则：

> **不确定时保留原始信号，比强行“处理”更符合 Moodify。**

---

# 11. PROFILE / Preset Decision

用户不应该被要求理解内部技术 preset。

P05 中的 profile/preset 是：

> **生产系统内部的处理决策对象。**

必须版本化。

至少记录：

- profile_id
- profile_version
- reason
- source judgment
- parameters / chain reference
- compatibility requirements

禁止：

- 只记录 `clean_master` 这类字符串却无法知道其真实参数版本；
- 修改 preset 内容后仍复用同一个 version identity。

---

# 12. RENDER

RENDER 产生最终播放候选。

必须明确：

- container
- codec
- sample rate
- bit depth / bitrate
- channels
- loudness policy
- dither/resample policy
- source lineage
- profile/pipeline version

首阶段应优先稳定、可验证格式。

不要在 P05 同时设计复杂自有加密音频格式。

---

# 13. VERIFY

VERIFY 是进入 completion candidate 前的硬门。

至少分：

## Technical Verification

- file exists
- hash
- decode succeeds
- duration sane
- sample rate/channels expected
- no NaN/invalid data
- no catastrophic clipping/overflow
- no obvious truncation
- artifact registered

## Comparative Verification

如果进行了 INTERVENE：

- before/after metrics
- no unsupported degradation
- judgment target 是否改善/保持
- Evidence 完整

## Human Verification

如果当前 policy 要求人耳：

- human verdict
- reviewer
- date
- comparison ref

---

## 13.1 Verify Result

结果只能：

- `PASS`
- `FAIL`
- `HUMAN_REVIEW_REQUIRED`

只有 PASS 才能提交 completion candidate。

---

# 14. Pipeline Version

必须输出 `PIPELINE_VERSION_CONTRACT.md`。

Pipeline Version 不是随便的 Git commit。

它应该代表：

> 一套会影响最终音频产物的生产语义集合。

至少绑定：

- stage order
- enabled/disabled stages
- adapter versions
- tool/model versions
- analysis schema
- judgment policy
- intervention/profile version
- render policy
- verify policy

---

## 14.1 Production Fingerprint

建议计算：

`production_fingerprint`

由稳定序列化后的以下内容构成：

- pipeline version
- input object hash
- stage config
- profile version
- tool/model versions
- render policy version

使用 SHA-256。

目的：

- 判断两次处理是否“语义上同一次生产配置”
- replay
- audit
- cache/idempotency hint

不能用 fingerprint 代替 Job ID。

---

# 15. Local Scratch Contract

Worker 本地磁盘只用于：

- downloaded source
- temporary stems
- intermediate files
- local render temp
- transient logs

默认不是长期资产权威。

必须规定：

- scratch root
- per-job directory
- naming
- max disk budget
- cleanup on success
- cleanup on failure
- cleanup after crash
- preserve-on-debug policy
- path traversal guard

例如：

```text
scratch/{job_id}/{attempt_id}/
```

---

# 16. Recovery Boundary

P05 不管理 lease，但必须尊重 P04。

在这些时间点检查 lease/fencing：

- before expensive stage
- before external API submit（如果成本高）
- before durable object upload
- before completion submit

如果 lease 已失效：

> `STALE_ATTEMPT_ABORT`

不得继续注册 authoritative output。

---

# 17. Failure Mapping

P05 必须把底层异常映射到 P04 failure taxonomy。

示例：

| Pipeline Failure | P04 Failure Class |
|---|---|
| decode failed | INPUT_INVALID |
| OSS timeout | STORAGE_TRANSIENT |
| separator API 429 | EXTERNAL_API_RATE_LIMIT |
| separator permanent reject | EXTERNAL_API_PERMANENT |
| OOM | WORKER_RESOURCE_EXHAUSTED |
| FFmpeg timeout | PROCESS_TIMEOUT |
| tool crash | PROCESS_CRASH |
| verify target not met | VERIFICATION_FAILED |
| unexpected invariant | INTERNAL_BUG |

禁止 worker 自己发明另一套顶层 failure taxonomy。

---

# 18. Output Contract

P05 最终不返回“一个路径”。

它返回 `CompletionCandidate`。

至少：

- job_id
- track_id
- attempt_id
- lease/fencing identity
- pipeline_version
- production_fingerprint
- source_object_id
- ready_candidate_object_id
- supporting_object_ids
- evidence_refs
- verification_result
- resource_summary
- stage_results
- completed_at

P04 控制平面验证后决定是否：

`VERIFYING -> READY`

---

# 19. Artifact Types

建议第一阶段统一：

- `source`
- `stem`
- `analysis`
- `intermediate`
- `render_candidate`
- `render_final`
- `evidence`
- `report`

P05 产生的最终对象在控制平面确认前：

> 默认是 `render_candidate`

P04/P06 的发布流程再决定如何成为用户可播放 `render_final`。

---

# 20. Minimal Pipeline Runner

建议形成一个清晰入口：

```text
run_pipeline(job_context) -> CompletionCandidate | FailureReport
```

`job_context` 必须显式包含：

- identifiers
- lease/fencing
- input object refs
- pipeline version
- config refs
- adapter registry
- stage reporter

禁止通过全局变量/隐式目录寻找关键运行输入。

---

# 21. Tests

至少：

## TST-01 — Source Integrity
下载后 hash 与 P03 record 一致。

## TST-02 — Invalid Audio
损坏/不支持输入 → INPUT_INVALID。

## TST-03 — Optional Stem Bypass
不需要 STEM 的 profile 不调用 separator。

## TST-04 — External API Transient
模拟 rate limit/timeout → 正确 failure class。

## TST-05 — Judgment BYPASS
无干预证据时 pipeline 可合法 BYPASS 并继续。

## TST-06 — Profile Version Binding
改变处理参数必须改变 profile/production fingerprint。

## TST-07 — Render Provenance
render candidate 可追溯 source/job/pipeline/profile/tools。

## TST-08 — Verification Failure
技术验证失败不能提交 PASS candidate。

## TST-09 — Stale Lease Before Upload
lease 失效 → 不注册 authoritative output。

## TST-10 — Duplicate Pipeline Replay
相同 input + same production semantics 有一致 fingerprint。

## TST-11 — Scratch Cleanup
success/failure 后符合 cleanup policy。

## TST-12 — No Secret Logging
外部 API key 不进入日志/manifest。

## TST-13 — Stage Result Completeness
每个执行 stage 都有 StageResult。

## TST-14 — Object Registration
durable outputs 全部通过 P03 adapter 注册。

## TST-15 — No Direct READY Mutation
worker 无权直接写 READY。

---

# 22. Integration Test

P05 至少要完成一条**测试环境/授权样本**的端到端 compute run：

```text
claimed RUNNING test job
→ acquire
→ validate
→ optional stem
→ analyze
→ judge
→ intervene/bypass
→ profile
→ render
→ verify
→ register
→ completion candidate
```

注意：

这不是 P07 Golden Song。

P05 只证明：

> **计算链作为工程系统可以工作。**

P07 才用真实熟悉歌曲验证产品听感与完整云链。

---

# 23. 允许修改

如果 P00-P04 Gate 允许：

- worker pipeline code
- internal adapters
- pipeline manifest
- profile versioning
- stage reporting
- scratch handling
- render/verify code
- integration tests
- deployment config for compute worker

---

# 24. 禁止修改

- P04 state machine semantics
- P04 lease/retry authority
- P03 identity semantics
- product Canon
- Android UI
- playback API
- public product surface
- database authority
- OSS bucket policy（除非 P03 已授权且只是适配）
- automatic scaling
- multi-worker orchestration

---

# 25. 必须输出的文件

至少：

1. `00_P05_EXECUTIVE_SUMMARY.md`
2. `01_CURRENT_AUDIO_CAPABILITY_MAP.md`
3. `02_UNIFIED_PIPELINE_ARCHITECTURE.md`
4. `03_PIPELINE_STAGE_CONTRACT.md`
5. `04_PIPELINE_VERSION_CONTRACT.md`
6. `05_EXTERNAL_SERVICE_ADAPTERS.md`
7. `06_JUDGMENT_AND_BYPASS_POLICY.md`
8. `07_PROFILE_AND_INTERVENTION_CONTRACT.md`
9. `08_RENDER_CONTRACT.md`
10. `09_VERIFICATION_CONTRACT.md`
11. `10_LOCAL_SCRATCH_CONTRACT.md`
12. `11_FAILURE_MAPPING.md`
13. `12_COMPLETION_CANDIDATE_CONTRACT.md`
14. `13_PIPELINE_TEST_REPORT.md`
15. `14_P06_HANDOFF.md`
16. `15_P05_ACCEPTANCE_REPORT.md`

以及代码/测试（若 Gate 允许）。

---

# 26. P06 Handoff

P06 不再重新处理音频。

P06 从 P05 接收：

- READY candidate / final render identity
- object ref
- duration / format / playback metadata
- verification evidence
- access classification
- track metadata
- version identity

P06 只回答：

> **一个已经被系统确认 READY 的音频对象，怎样安全、稳定、低摩擦地送到 Android 并完成 PLAY？**

---

# 27. 验收标准

- [ ] P03/P04 Gate 通过
- [ ] Current Audio Capability Map 完成
- [ ] 只有一条 canonical compute pipeline
- [ ] stage vocabulary 固定
- [ ] stage input/output 显式
- [ ] 无关键“神秘本地文件”依赖
- [ ] external API 通过 adapter
- [ ] JUDGE 输出 evidence + uncertainty
- [ ] BYPASS 是合法一等决策
- [ ] profile/preset 版本化
- [ ] render contract 固定
- [ ] VERIFY 是 completion 前硬门
- [ ] pipeline version 固定
- [ ] production fingerprint 可生成
- [ ] scratch 生命周期明确
- [ ] stale attempt 不能提交结果
- [ ] failure 映射到 P04 taxonomy
- [ ] durable output 通过 P03 注册
- [ ] worker 不直接写 READY
- [ ] integration compute test 通过
- [ ] P06 Handoff 完成
- [ ] 完成后停止，不进入 P06

---

# 28. 最终执行口令

> 执行 W01-P05 Cloud Audio Compute Pipeline。  
> 必须先通过 P03 Data Plane 与 P04 Control Plane Gate，并先生成 Current Audio Capability Map。  
> 只收敛已有且对 One Song 主链有直接价值的音频能力，不把全部历史实验代码塞进生产主线。  
> 建立统一 stage contract：Acquire / Validate / optional Stem / Analyze / Judge / Intervene-or-BYPASS / Profile / Render / Verify / Register。  
> Worker 必须尊重 attempt/lease/fencing，不得直接修改 Job READY；所有持久对象通过 P03 注册，所有失败映射到 P04 taxonomy。  
> 固定 pipeline version、production fingerprint、profile version、scratch lifecycle、external-service adapters、verification gate 与 CompletionCandidate。  
> 完成一条测试环境或授权样本的端到端 compute run 后停止，等待人类审核，不进入 P06。
