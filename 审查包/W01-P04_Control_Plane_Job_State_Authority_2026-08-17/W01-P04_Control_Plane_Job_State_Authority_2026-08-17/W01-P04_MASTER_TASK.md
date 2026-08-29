# W01-P04 — Control Plane & Authoritative Job State Machine

**Wave:** Moodify Cognitive Wave 01  
**Package:** W01-P04  
**性质:** 控制平面建设 / Job Authority / Queue / Lease / Retry / Recovery / Observability  
**日期:** 2026-08-17  
**执行对象:** Codex  
**前置依赖:** W01-P00、W01-P01、W01-P02、W01-P03 已完成并通过人类审核  
**后继任务:** W01-P05 Cloud Audio Compute Pipeline  
**原子任务数:** 3  
**核心目标:** 建立 Moodify 唯一的 Job 控制权威，让“一首歌现在在哪一步、谁在处理、失败后怎么办、是否可重试、是否已经 READY”永远只有一个可追溯答案。

---

# 0. 本包解决什么问题

P03 已建立：

- Track identity
- Job identity
- Object identity
- Hash
- Version
- Evidence provenance
- Metadata DB 与 OSS 的职责边界

但“有一个 `jobs.current_state` 字段”并不等于拥有可靠控制平面。

P04 要解决的是：

> **Job 的状态如何被唯一地改变？**

以及：

> **Worker 崩溃、网络断开、进程重启、重复请求、超时、外部 API 失败时，系统怎样恢复而不制造双重执行、状态漂移或无法解释的结果？**

P04 是 One Song Infrastructure 真正的“交通规则”。

---

# 1. 三个原子任务

## T04-1 — 收敛唯一 Authoritative Job State Machine

目标：

- 找出当前所有状态机、queue、orchestration、worker lease 机制；
- 选择/收敛为一个 Job Authority；
- 建立状态迁移表；
- 将 pipeline stage 与 job lifecycle 分离；
- 建立 transition precondition；
- 建立 terminal state。

---

## T04-2 — Queue / Lease / Retry / Recovery / Idempotency

目标：

- 每个 Job 同一时刻最多一个有效 owner；
- worker 通过 lease 领取任务；
- heartbeat 可续租；
- lease 过期后任务可恢复；
- retry 有明确预算；
- duplicate request 不产生不可解释的双重任务；
- restart 后不需要人工猜测 Job 状态。

---

## T04-3 — Failure / Event / Evidence / Observability

目标：

- 每个失败有结构化 failure code；
- 每个状态变化产生 append-only event；
- event 不是第二个 state authority；
- logs 能按 track_id / job_id / attempt_id 查询；
- 控制平面提供最小 health / queue / job observability；
- READY / FAILED 的结论有证据。

---

# 2. 前置 Gate

## GATE P04-0 — P03 Data Identity Gate

必须读取：

- Data Identity Contract
- Metadata Data Model
- Data Plane Invariants
- Object Key Convention
- Migration State
- P04 Handoff
- Data Plane Test Report

若 Track / Job / Object identity 仍不稳定：

> `STOP — DATA_IDENTITY_INCOMPLETE`

---

## GATE P04-1 — Existing Authority Discovery

在任何代码变更前，必须扫描当前仓库真实存在的：

- state machine
- workflow engine
- queue
- worker claim
- lease
- retry
- recovery
- API job handlers
- cron/timer worker
- restart recovery
- SQLite / Redis / DB-backed queue
- PR / branch 中尚未合并但可能已实现的 control plane

输出：

`CURRENT_CONTROL_AUTHORITY_MAP.md`

每个候选系统标记：

- `CANONICAL_CANDIDATE`
- `LEGACY`
- `EXPERIMENTAL`
- `DUPLICATE`
- `UNKNOWN`

### 硬规则

> **不得在没有完成现有 authority discovery 的情况下创建新状态机。**

若现有系统可收敛，应优先迁移/扩展。

---

# 3. Job State 与 Pipeline Stage 必须分离

这是 P04 的核心设计规则。

## 3.1 Job Lifecycle State

Job State 只表达控制生命周期。

建议的最小候选状态：

```text
CREATED
QUEUED
RUNNING
RETRY_WAIT
VERIFYING
READY
FAILED
CANCELED
```

这只是候选，最终必须结合现有实现与 P00-P03 决定。

---

## 3.2 Pipeline Stage

`stage` 表达正在做什么，例如未来 P05 可能定义：

- intake
- stem
- analyze
- judge
- intervene
- render
- verify
- publish

但 P04 不提前决定 P05 的最终 stage vocabulary。

因此：

> **State 是控制权威；Stage 是进度描述。**

禁止把每个 DSP 步骤都升级成状态机一级状态，造成状态爆炸。

---

# 4. Authoritative State Machine Invariants

必须建立 `CONTROL_PLANE_INVARIANTS.md`，至少包含：

## CP-INV-01 — One State Authority
一个 Job 只有一个 authoritative current state。

## CP-INV-02 — State Change Is Transactional
状态改变与必要的 attempt/lease/event 写入必须在一致性边界内完成。

## CP-INV-03 — No Silent Transition
任何状态变化必须记录 transition event。

## CP-INV-04 — Event Log Is Audit, Not Authority
append-only event history 不替代 `jobs.current_state` 的当前权威。

## CP-INV-05 — One Valid Lease
同一 Job 同一时刻最多一个有效 lease owner。

## CP-INV-06 — Lease Has Expiry
所有 worker ownership 都有明确过期时间。

## CP-INV-07 — Heartbeat Does Not Change Business Result
heartbeat 只维护 lease，不可把 FAILED/READY 重新变 RUNNING。

## CP-INV-08 — Terminal Is Protected
READY / FAILED / CANCELED 的回退必须经过显式 reset/replay policy，不允许普通 worker 修改。

## CP-INV-09 — Retry Is Budgeted
retry 次数、原因、backoff、终止条件必须明确。

## CP-INV-10 — Idempotent Command
同一 idempotency key 的相同命令不得创建不同逻辑结果。

## CP-INV-11 — Recovery Is Deterministic
worker/node 重启后，系统通过数据库事实恢复，不靠人工记忆。

## CP-INV-12 — Failure Is Structured
失败必须至少有 failure_class / failure_code / retryable。

## CP-INV-13 — READY Requires Artifact
Job 进入 READY 前必须存在可验证 ready_object_id。

## CP-INV-14 — READY Requires Verification
如果当前 Canon 要求 verify，则 READY 前必须有 verification evidence。

## CP-INV-15 — Worker Cannot Invent State
worker 只能调用控制平面允许的 transition/command。

---

# 5. 最小状态迁移候选

最终状态必须由 ADR 决定，但建议从以下最小图开始验证：

```text
CREATED
   ↓
QUEUED
   ↓
RUNNING ───────────────┐
   │                   │
   ├──> VERIFYING      │ transient/retryable failure
   │        ↓          │
   │      READY        ↓
   │              RETRY_WAIT
   │                   ↓
   └───────────────> QUEUED

CREATED / QUEUED / RETRY_WAIT
   └──────────────> CANCELED

RUNNING / VERIFYING
   └──────────────> FAILED  (terminal after retry budget/policy)
```

注意：

- `LEASED` 默认建议作为 lease metadata，而不是一级业务状态；
- `attempt` 不是 state；
- `stage` 不是 state；
- `failure` 不一定立即 terminal。

如果现有系统有更成熟且已验证结构，优先复用。

---

# 6. Transition Contract

每一条 transition 必须定义：

- from_state
- command
- to_state
- actor
- preconditions
- transactional writes
- event_type
- idempotency behavior
- side effects allowed
- side effects forbidden
- retry semantics
- terminal protection

示例：

```text
QUEUED
  + claim(worker_id)
  -> RUNNING
```

事务内至少完成：

- 验证当前 state=QUEUED
- 验证没有有效 lease
- 创建 attempt_id
- 创建 lease_id
- 设置 lease_owner
- 设置 lease_expires_at
- current_state=RUNNING
- append JOB_CLAIMED event

如果并发两个 worker claim：

> 只能一个成功。

---

# 7. Lease Contract

必须输出 `LEASE_CONTRACT.md`。

至少定义：

- lease_id
- job_id
- attempt_id
- owner
- acquired_at
- expires_at
- heartbeat_at
- lease_version / fencing token（若需要）
- release reason

---

## 7.1 Lease 原则

- lease 必须有 TTL；
- heartbeat 只延长当前有效 lease；
- 过期 lease 不可继续 commit result；
- 旧 worker 恢复后不得覆盖新 worker 结果；
- lease expiry 后 recovery runner 可以重新 queue；
- 完成/失败时释放 lease。

---

## 7.2 Fencing

如果存在以下风险：

- worker A lease 过期；
- worker B 已重新取得任务；
- worker A 又恢复并上传最终结果；

则必须设计一种 fencing/version 检查。

可以是：

- lease_version
- attempt_number
- optimistic version
- compare-and-set

最终方案写 ADR。

---

# 8. Retry Contract

必须输出 `RETRY_POLICY.md`。

每个 failure class 必须明确：

- retryable
- max attempts
- backoff
- jitter（如需要）
- retry requires cleanup?
- retry requires new attempt?
- terminal failure mapping

推荐 failure classes：

- `INPUT_INVALID`
- `STORAGE_TRANSIENT`
- `STORAGE_PERMANENT`
- `DB_TRANSIENT`
- `EXTERNAL_API_RATE_LIMIT`
- `EXTERNAL_API_TRANSIENT`
- `EXTERNAL_API_PERMANENT`
- `WORKER_RESOURCE_EXHAUSTED`
- `PROCESS_TIMEOUT`
- `PROCESS_CRASH`
- `VERIFICATION_FAILED`
- `INTERNAL_BUG`
- `CANCELED_BY_USER`
- `UNKNOWN_FAILURE`

不要为每个 traceback 创造独立顶层 failure class。

---

# 9. Recovery Contract

必须覆盖：

## Case A — Worker crash
- lease eventually expires
- job does not remain RUNNING forever
- incomplete attempt preserved
- new attempt can start

## Case B — Control node restart
- state is recovered from DB
- no in-memory-only authority

## Case C — Network partition
- stale worker cannot commit after lease/fencing loss

## Case D — DB temporary unavailable
- worker must not silently assume success

## Case E — OSS upload succeeds but DB commit fails
- detect orphan object
- no false READY
- reconciliation path exists

## Case F — DB says object exists but OSS missing
- no READY delivery
- reconciliation/error path exists

---

# 10. Idempotency Contract

必须区分：

## Create Job Idempotency
同一个用户/系统请求重复提交。

## Transition Idempotency
同一个 command 重复发送。

## Artifact Registration Idempotency
P03 已定义。

## Completion Idempotency
worker 因网络超时重复 complete。

---

## 10.1 Idempotency Key

至少包含：

- scope
- key
- request fingerprint
- created_at
- result reference
- expiry/retention policy

同一个 key + 不同 request fingerprint：

> 必须冲突，不可静默复用。

---

# 11. Queue Strategy

P02 已经决定 queue 方向，P04 实现/收敛它。

如果当前阶段使用 DB-backed queue：

必须证明：

- atomic claim
- lease
- retry
- ordering requirement
- polling interval
- no duplicate owner
- crash recovery

如果使用 Redis/Celery：

必须证明：

- 它是 P02 已批准的 authority 辅助层；
- authoritative current state 仍归数据库或明确权威；
- broker message 不成为唯一事实来源。

禁止：

> queue 自己成为不可追溯的“隐藏状态机”。

---

# 12. Event Log

建议追加 `job_events`（若现有系统已有等价结构则复用）。

Event 至少包含：

- event_id
- job_id
- track_id
- attempt_id
- event_type
- actor_type
- actor_id
- from_state
- to_state
- stage
- occurred_at
- correlation_id
- payload_ref / safe payload
- failure_code（如适用）

Event 必须 append-only。

但：

> **jobs.current_state 仍是当前状态权威。**

---

# 13. Attempt Model

建议有显式 attempt。

每次真正执行：

```text
job
  ├── attempt 1
  ├── attempt 2
  └── attempt 3
```

Attempt 至少记录：

- attempt_id
- job_id
- attempt_number
- worker_id
- lease_id
- started_at
- ended_at
- outcome
- failure_code
- resource summary
- output object refs
- log/evidence refs

这会让 retry 不再覆盖历史失败。

---

# 14. Observability

P04 不建设大型监控平台。

只建立最小可用观测面。

必须能回答：

### Job
- current state
- current stage
- current attempt
- current lease owner
- lease expiry
- retry count
- last failure
- ready object
- updated_at

### Queue
- queued count
- retry_wait count
- running count
- stale lease count
- failed count
- ready count

### Worker
- worker_id
- last heartbeat
- current job
- version
- capacity
- health

### Control
- DB reachable
- object store reachable（轻量）
- queue authority healthy
- build/commit/version

---

# 15. Evidence & Logs

所有日志必须至少携带：

- track_id
- job_id
- attempt_id
- correlation_id
- stage
- worker_id（若有）

禁止：

- log 中输出 Secret；
- log 中输出签名 URL 完整 query；
- 只留下无结构 traceback 而没有 failure record。

---

# 16. 最小 Control API / Command Surface

如果现有 API 可复用，优先扩展。

建议逻辑命令：

- create job
- enqueue job
- claim job
- heartbeat lease
- report progress/stage
- complete job
- fail attempt
- cancel job
- get job
- list queue summary
- get worker health

不要求全部暴露为公网 REST。

内部 worker command 应使用内部 auth / private boundary。

---

# 17. Mutation / Migration Gate

P04 可以实现代码和数据库 migration，但必须满足：

- P03 metadata DB write 已授权；
- 当前 control authority 已发现；
- migration 不创建第二套 authority；
- transition matrix 已 review；
- rollback plan 已明确；
- dev/test 先通过；
- production deploy 仍需单独授权。

若生产变更未授权：

> `CONTROL_PLANE_DEPLOY_BLOCKED`

可以完成：

- code
- migrations
- tests
- local/integration simulation
- deployment plan

但不能改真实 production。

---

# 18. 必须通过的测试

## TST-01 — Concurrent Claim
两个 worker 同时 claim 一个 QUEUED job。

Expected:
- 只有一个 owner

## TST-02 — Lease Expiry Recovery
RUNNING worker 消失。

Expected:
- lease expires
- job recoverable
- stale worker cannot later overwrite result

## TST-03 — Duplicate Complete
worker 重复发送 complete。

Expected:
- idempotent
- no duplicate READY event/object relation

## TST-04 — Retry Budget
连续 transient failures。

Expected:
- attempts increase
- backoff applied
- max attempts respected
- eventually terminal FAILED if budget exhausted

## TST-05 — Permanent Failure
INPUT_INVALID。

Expected:
- no pointless retry

## TST-06 — Control Restart
restart control process in test env.

Expected:
- state survives
- queue recoverable
- no in-memory-only authority

## TST-07 — OSS/DB Split Brain Simulation
object write success, DB commit fail.

Expected:
- no READY
- orphan detectable

## TST-08 — READY Guard
try READY without ready_object_id / required verification.

Expected:
- reject

## TST-09 — Terminal Protection
ordinary worker tries READY -> RUNNING.

Expected:
- reject

## TST-10 — Idempotent Create
same idempotency key repeated.

Expected:
- same logical job result

## TST-11 — Idempotency Conflict
same key, different request fingerprint.

Expected:
- conflict

## TST-12 — Event Completeness
every transition creates one append-only event.

---

# 19. 必须输出的文件

至少：

1. `00_P04_EXECUTIVE_SUMMARY.md`
2. `01_CURRENT_CONTROL_AUTHORITY_MAP.md`
3. `02_AUTHORITATIVE_STATE_MACHINE.md`
4. `02_STATE_TRANSITION_MATRIX.csv`
5. `03_CONTROL_PLANE_INVARIANTS.md`
6. `04_LEASE_CONTRACT.md`
7. `05_RETRY_POLICY.md`
8. `06_RECOVERY_CONTRACT.md`
9. `07_IDEMPOTENCY_CONTRACT.md`
10. `08_FAILURE_TAXONOMY.md`
11. `09_EVENT_AND_ATTEMPT_MODEL.md`
12. `10_OBSERVABILITY_CONTRACT.md`
13. `11_CONTROL_API_COMMAND_CONTRACT.md`
14. `12_MIGRATION_AND_DEPLOYMENT_PLAN.md`
15. `13_CONTROL_PLANE_TEST_REPORT.md`
16. `14_P05_HANDOFF.md`
17. `15_P04_ACCEPTANCE_REPORT.md`

如实现代码，还应包含：

- migrations
- state transition module
- repository/service changes
- lease/retry implementation
- tests
- health/queue summary

---

# 20. P05 Handoff

P05 不再重新设计 Job 状态机。

P05 只回答：

> **一个被控制平面合法 claim 的 RUNNING Job，怎样执行完整音频计算 pipeline，并以可验证方式产出 READY candidate？**

P05 从 P04 接收：

- job_id
- track_id
- attempt_id
- lease/fencing token
- stage reporting contract
- input object refs
- pipeline version
- output registration contract
- failure taxonomy
- completion/failure command
- Evidence contract

---

# 21. 验收标准

- [ ] P03 Data Identity Gate 通过
- [ ] Existing Authority Discovery 完成
- [ ] 只有一个 authoritative state machine
- [ ] State 与 Stage 分离
- [ ] transition matrix 完成
- [ ] 所有 state change 可追溯
- [ ] event log 不成为第二状态权威
- [ ] 一个 Job 同时最多一个有效 lease
- [ ] lease 有 expiry
- [ ] stale worker 无法覆盖新 attempt
- [ ] retry 有预算
- [ ] permanent failure 不盲目 retry
- [ ] restart/recovery 不依赖进程内存
- [ ] create/transition/complete 有 idempotency
- [ ] READY 有 artifact guard
- [ ] READY 有 verification guard（如 Canon 要求）
- [ ] terminal state 受保护
- [ ] failure taxonomy 结构化
- [ ] queue summary / stale lease 可观测
- [ ] logs 可按 job/attempt/correlation 查询
- [ ] 不引入第二套 queue/state authority
- [ ] 未授权时 production deploy 保持 BLOCKED
- [ ] P05 Handoff 完成
- [ ] 完成后停止，不进入 P05

---

# 22. 最终执行口令

> 执行 W01-P04 Control Plane & Authoritative Job State Machine。  
> 必须先读取 P03 Data Identity，并完成 Existing Authority Discovery。  
> 优先收敛现有 state/queue/orchestration，不得直接新造第二套控制系统。  
> 完成三个原子任务：唯一 Job State Machine、Queue/Lease/Retry/Recovery/Idempotency、Failure/Event/Evidence/Observability。  
> 将 Job State 与 Pipeline Stage 分离；保证同一 Job 同时最多一个有效 lease；保证 stale worker 无法覆盖新 attempt；保证 restart 后可以从数据库事实恢复；保证 READY 有 artifact/evidence gate；保证所有 transition append event 但 event 不成为第二 authority。  
> 生产部署未授权时保持 CONTROL_PLANE_DEPLOY_BLOCKED，只完成代码、migration、测试和部署计划。  
> 完成 P05 Handoff 后停止，等待人类审核。
