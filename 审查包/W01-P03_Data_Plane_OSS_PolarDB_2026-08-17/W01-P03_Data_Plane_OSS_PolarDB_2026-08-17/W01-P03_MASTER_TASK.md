# W01-P03 — Data Plane: OSS + PolarDB

**Wave:** Moodify Cognitive Wave 01  
**Package:** W01-P03  
**性质:** 数据平面建设 / OSS + PolarDB / Identity + Provenance  
**日期:** 2026-08-17  
**执行对象:** Codex  
**前置依赖:** W01-P00、W01-P01、W01-P02 已完成并通过人类审核  
**后继任务:** W01-P04 Control Plane & Job State Authority  
**原子任务数:** 3  
**核心目标:** 建立唯一、可追溯、可恢复的数据平面，让每一首歌、每一个任务、每一个对象、每一次版本变化都有稳定身份。

---

# 0. 本包解决什么问题

P02 已经决定：

- 哪个节点负责什么；
- metadata 应该进入哪一个数据库；
- binary/object artifact 应该进入哪一个对象存储；
- 哪些服务之间允许通信。

P03 不再讨论拓扑。

P03 只回答：

> **Moodify 中的一首歌，在进入云端以后，怎样拥有一个永不混淆的身份？**

以及：

> **Track、Job、Object、Hash、Pipeline Version、Preset Version、Evidence 之间怎样建立唯一关系？**

如果这一步不稳定，后面的状态机、worker、播放、实验、蒸馏都会产生高认知摩擦。

因此 P03 的真正目标不是“建几个表”，而是建立 Moodify 的：

# Data Identity Backbone

---

# 1. 执行前置 Gate

## GATE P03-0 — P00 Reality

必须读取：

- 当前真实数据库状态；
- 当前 OSS 状态；
- 当前真实音频资产；
- 当前已有数据表；
- 当前是否存在重复 Track / Job / Evidence authority；
- 当前已有 source/stem/render 产物。

若数据库真实状态不清：

> `STOP — DATABASE_REALITY_INCOMPLETE`

若 OSS 是否已开通不清：

> `STOP — OBJECT_STORAGE_REALITY_INCOMPLETE`

---

## GATE P03-1 — P01 Canon

必须读取：

- Current Canon
- Product Boundary
- Internal Systems
- Authority Order

P03 不能重新定义产品身份。

---

## GATE P03-2 — P02 Topology

必须读取：

- Node Role Assignment
- Network Matrix
- Secret Ownership Matrix
- Deployment Boundary
- Target One Song Topology
- Architecture Decision Register
- P03 Handoff

若 P02 仍未决定 metadata DB 或 object storage role：

> `STOP — TOPOLOGY_INCOMPLETE`

---

# 2. 本包的三个原子任务

# T03-1 — OSS Object Space & Object Identity

目标：

建立 Moodify 对象存储的统一 object namespace。

---

## 2.1 对象存储原则

OSS 保存：

- source audio
- stems
- analysis artifacts
- intermediate artifacts
- final renders
- evidence artifacts
- optional reports

OSS 不保存：

- authoritative job state
- relational authority
- primary task queue
- user permissions authority
- database migration state

---

## 2.2 Track 与 Object 必须分离

### Track

代表：

> 一首被 Moodify 识别和处理的逻辑音频作品/输入实体。

### Object

代表：

> 一份具体不可变或版本化的二进制产物。

一个 Track 可以拥有多个 Object：

```text
Track
├── source
├── stem:vocal
├── stem:drums
├── stem:bass
├── analysis:json
├── intermediate:v1
├── render:v1
├── render:v2
└── evidence:v2
```

---

## 2.3 Source Object 不可覆盖原则

原始输入一旦进入 canonical object storage：

> **禁止原位覆盖。**

如果用户重新上传同一个文件：

- 通过内容哈希识别；
- 是否去重由当前 data policy 决定；
- 不允许覆盖既有 source bytes。

---

## 2.4 Object Key 设计要求

Object Key 必须同时满足：

- 可读但不过度依赖文件名；
- 不依赖用户原始文件名作为唯一身份；
- 不使用数据库自增 ID 作为唯一可追溯依据；
- 支持 Track / Job / Artifact Type / Version；
- 支持清晰 lifecycle；
- 不包含 Secret；
- 不包含不必要的个人信息；
- Windows/Linux/cloud 均安全；
- 不依赖中文文件名才能工作。

建议逻辑形式：

```text
moodify/
  tracks/{track_id}/
    source/{source_object_id}.{ext}
    jobs/{job_id}/
      stems/{artifact_id}/{role}.{ext}
      analysis/{artifact_id}.{ext}
      intermediate/{artifact_id}.{ext}
      renders/{artifact_id}.{ext}
      evidence/{artifact_id}.{ext}
```

最终格式必须由执行者结合 P02/P00 现实确定，并写入：

`OBJECT_KEY_CONVENTION.md`

---

## 2.5 Object Manifest

每一个重要 object 至少记录：

- object_id
- track_id
- job_id（如适用）
- artifact_type
- artifact_role
- bucket
- object_key
- content_hash
- hash_algorithm
- byte_size
- mime_type
- created_at
- producer
- producer_version
- pipeline_version
- source_object_id / parent_object_id
- immutable
- retention_class
- evidence_class

---

# T03-2 — PolarDB Metadata Model

目标：

建立数据关系权威。

数据库引擎必须使用 P02 决定的 metadata DB。

P03 不允许为了“更喜欢 PostgreSQL/MySQL”推翻 P02。

---

## 2.6 最小实体

第一阶段至少需要：

### `tracks`

一首逻辑 Track 的身份。

核心字段建议：

- track_id
- owner_scope / user_id（如当前产品已有用户体系）
- source_object_id
- source_hash
- source_format
- source_duration_ms
- source_sample_rate
- source_channels
- created_at
- status_class
- canonical_source_version

---

### `jobs`

一次处理任务。

核心字段建议：

- job_id
- track_id
- job_type
- requested_at
- created_by
- pipeline_version
- processing_profile_version
- current_state
- current_attempt
- failure_code
- failure_summary
- started_at
- finished_at
- ready_object_id

注意：

P03 只建立字段承载能力。

**P04 才定义最终 authoritative state machine。**

不要在 P03 先造第二套状态机。

---

### `objects`

所有持久化对象的索引。

核心字段：

- object_id
- track_id
- job_id
- artifact_type
- artifact_role
- bucket
- object_key
- content_hash
- hash_algorithm
- byte_size
- mime_type
- producer
- producer_version
- created_at
- parent_object_id
- immutable
- retention_class

---

### `evidence`

用于追溯判断与验收。

核心字段：

- evidence_id
- track_id
- job_id
- object_id
- evidence_type
- claim
- method
- evaluator
- evaluator_version
- created_at
- verdict / value
- uncertainty
- evidence_object_id

---

### `versions`

记录系统生产版本，不等于 Git commit 的简单拷贝。

可记录：

- pipeline_version
- preset_version
- model_version
- toolchain_version
- app_contract_version
- created_at
- status

如果现有项目已有更成熟版本模型，可复用，禁止重复造表。

---

## 2.7 ID 原则

所有核心 ID 必须：

- 全局唯一；
- 不依赖单个数据库实例才能解释；
- 不暴露业务敏感信息；
- 可在异步 worker / API / object store 间传递；
- 适合日志；
- 适合未来跨区域迁移。

优先选择：

- UUIDv7 / UUID
- ULID

具体方案必须写 ADR。

---

## 2.8 Hash 原则

source identity 必须至少使用一种内容哈希。

推荐：

`SHA-256`

禁止使用：

- 文件名
- 上传时间
- DB 行号

作为 source identity 的替代。

哈希的作用：

- dedup hint
- provenance
- integrity verification
- replay identity

注意：

> 相同 hash ≠ 相同版权/用户 ownership。

数据模型不能把内容去重与权限归属混为一谈。

---

# T03-3 — Track / Job / Object / Hash / Version / Evidence Contract

这是 P03 最重要的收敛任务。

最终必须形成：

`DATA_IDENTITY_CONTRACT.md`

---

## 2.9 必须满足的关系

### Track → Source

每个 canonical Track 必须有且只有一个 canonical source reference。

### Job → Track

每个 Job 必须属于一个 Track。

### Object → Track

每个 canonical object 必须能追溯到 Track。

### Produced Object → Job

由 pipeline 产生的对象必须能追溯到 producer Job。

### Evidence → Claim

Evidence 必须说明它证明什么，不允许只存“report.json”。

### Version → Production

每一个 final render 必须能回答：

- 哪个 pipeline version
- 哪个 processing profile / preset version
- 哪个 producer/tool version
- 哪些 source/stem inputs
- 哪个 job

---

## 2.10 Provenance Chain

最终必须能从 PLAY 的一个 READY object 反向追溯：

```text
READY Render
    ↓
Object Record
    ↓
Producer Job
    ↓
Pipeline / Preset / Tool Version
    ↓
Input Objects
    ↓
Canonical Source
    ↓
Source Hash
    ↓
Track
```

Evidence 也必须能挂在这条链上。

---

# 3. Data Plane Invariants

必须写入：

`DATA_PLANE_INVARIANTS.md`

至少包括：

## INV-01
Source object 不可原位覆盖。

## INV-02
Object key 不作为数据库唯一业务身份的替代。

## INV-03
数据库不保存大音频二进制。

## INV-04
OSS 不保存 authoritative current job state。

## INV-05
READY object 必须能追溯到 source。

## INV-06
任何 final render 必须有 pipeline version。

## INV-07
任何 evidence 必须有 subject/claim。

## INV-08
任何 orphan object 都必须可检测。

## INV-09
数据库删除不能静默造成对象失去 provenance。

## INV-10
对象删除不能让数据库保留“假存在”引用。

## INV-11
写入必须设计为幂等。

## INV-12
权限归属与内容哈希不得混为一体。

---

# 4. Migration Strategy

P03 不是“空仓库设计”。

必须尊重 P00 已存在的数据。

因此必须先输出：

`CURRENT_TO_TARGET_DATA_MAPPING.md`

把已有：

- local files
- old outputs
- existing DB records
- PR branch artifacts
- current worker paths
- existing evidence

映射到新 data plane。

状态：

- KEEP_AS_IS
- REGISTER
- MIGRATE_LATER
- LEGACY
- ORPHAN_REVIEW
- DELETE_LATER
- HUMAN_DECISION_REQUIRED

禁止本包一开始批量删除旧产物。

---

# 5. Schema Migration Gate

数据库写操作只有满足以下条件才允许：

- P02 已明确 metadata DB；
- 已确认目标是 dev/staging 或人类明确授权的 production；
- migration 文件已生成；
- migration review 完成；
- backup / rollback 路径明确；
- no destructive default；
- dry-run / transaction strategy 可用；
- existing tables 已对照；
- migration 不创建第二套 authority。

如果任何条件不满足：

> `SCHEMA_WRITE_BLOCKED`

可以完成设计与 migration files，但不得执行。

---

# 6. OSS Provisioning Gate

只有满足：

- P02 确定 object storage；
- bucket 已由人类开通或明确授权 Codex 创建；
- region/endpoint 已确认；
- credential source 已确认；
- lifecycle/versioning decision 已确认；
- public access policy 已确认；
- test prefix 已定义；

才能写 OSS。

否则：

> `OSS_WRITE_BLOCKED`

此时 P03 可以：

- 完成 key convention
- 完成 code adapter
- 完成 tests
- 完成 dry-run

但不上传真实对象。

---

# 7. 最小代码实现

如果 Gate 允许，本包可以实现：

- object storage adapter
- metadata repository / DAO
- ID generator
- hashing utility
- object manifest model
- data plane config
- schema migration
- data plane contract tests
- idempotency tests
- provenance tests

禁止同时实现：

- final Job state machine
- queue scheduler
- worker retry engine
- audio processing pipeline
- playback API

这些属于后续包。

---

# 8. 必须通过的测试

至少：

## Test A — Same source hash

同一个源文件重复进入：

- 不产生不可解释的多个 canonical source identity；
- ownership 不被错误合并。

## Test B — Immutable source

同一 source object key 不能被不同 bytes 覆盖。

## Test C — Object provenance

任意 render object 可以追溯到：

- track
- job
- source
- pipeline version

## Test D — Evidence provenance

Evidence 能回答：

> 对什么对象、什么任务、什么 claim 产生。

## Test E — Idempotent register

同一个 object manifest 重复提交，不产生重复逻辑记录。

## Test F — Missing object detection

数据库引用 OSS 不存在对象时，可以被发现。

## Test G — Orphan object detection

OSS 有对象但 DB 无引用时，可以被发现。

## Test H — No large blobs in DB

数据库 schema 不含 source audio/render blob。

---

# 9. 数据权限与隐私

P03 必须记录：

- Track ownership scope
- Source access class
- Render access class
- Evidence access class
- signed URL / service access boundary

禁止：

- public-read bucket 作为默认；
- Android 内置 OSS 长期密钥；
- 通过 hash 推断用户 ownership；
- 把私人音频写进 Git；
- 把真实音频加入测试 fixture，除非已有授权和明确测试 policy。

---

# 10. Retention / Lifecycle

至少定义：

| Artifact | Retention |
|---|---|
| source | long-lived / user policy |
| stems | configurable |
| intermediate | short / cleanup candidate |
| render | versioned / user-facing |
| evidence | long-lived |
| logs | operational retention |
| temp scratch | ephemeral |

P03 不一定立刻启用 OSS lifecycle rule。

但必须决定每类对象的意图。

---

# 11. 必须输出的文件

至少：

1. `00_P03_EXECUTIVE_SUMMARY.md`
2. `01_OBJECT_KEY_CONVENTION.md`
3. `02_METADATA_DATA_MODEL.md`
4. `03_DATA_IDENTITY_CONTRACT.md`
5. `04_DATA_PLANE_INVARIANTS.md`
6. `05_CURRENT_TO_TARGET_DATA_MAPPING.md`
7. `06_MIGRATION_PLAN.md`
8. `07_OSS_PROVISIONING_AND_POLICY.md`
9. `08_SCHEMA_MIGRATION_REPORT.md`
10. `09_DATA_PLANE_TEST_REPORT.md`
11. `10_P04_HANDOFF.md`
12. `11_P03_ACCEPTANCE_REPORT.md`

若实现代码：

- migration files
- data models
- object adapter
- repository layer
- tests

---

# 12. P04 Handoff

P03 完成以后，P04 不再重新定义 Track/Object identity。

P04 只回答：

> **一条已经拥有稳定数据身份的 Job，如何在唯一 authoritative state machine 中被调度、租约、重试、恢复和观测？**

P04 输入：

- Track identity
- Job identity
- objects schema
- evidence schema
- data plane invariants
- metadata DB adapter
- object storage adapter
- migration state
- tested provenance contract

---

# 13. 验收标准

- [ ] P00/P01/P02 Gate 全部通过
- [ ] Object Store 与 Metadata DB 职责严格分离
- [ ] Track / Job / Object / Evidence ID 稳定
- [ ] Source 使用内容哈希
- [ ] Source object 不可覆盖
- [ ] READY render 可反向追溯到 source
- [ ] final render 记录 pipeline version
- [ ] evidence 有 claim/subject
- [ ] 幂等写入已测试
- [ ] orphan / missing object 可检测
- [ ] ownership 与 hash 去重分离
- [ ] 不存在第二套 Job state authority
- [ ] schema migration 非破坏性
- [ ] production 写入若未授权则保持 BLOCKED
- [ ] OSS 写入若未授权则保持 BLOCKED
- [ ] 大音频不进入数据库
- [ ] Android 不持有长期 OSS credential
- [ ] Data Plane Invariants 完成
- [ ] P04 Handoff 完成
- [ ] 完成后停止，不进入 P04

---

# 14. 最终执行口令

> 执行 W01-P03 Data Plane — OSS + PolarDB。  
> 首先通过 P00 Reality、P01 Canon、P02 Topology 三个 Gate。  
> 完成三个原子任务：OSS Object Space、PolarDB Metadata Model、Data Identity Contract。  
> 建立 Track / Job / Object / Hash / Version / Evidence 的唯一关系，确保 source 不可覆盖、render 可追溯、Evidence 可解释、写入可幂等。  
> 不在 P03 创建第二套 Job state machine，不实现 queue/worker orchestration，不开发 playback。  
> 数据库与 OSS 的真实写入必须通过各自 Write Gate；若缺少授权，保留 SCHEMA_WRITE_BLOCKED / OSS_WRITE_BLOCKED，完成设计、migration、adapter 与 tests 即停止。  
> 完成 P04 Handoff 后等待人类审核。
