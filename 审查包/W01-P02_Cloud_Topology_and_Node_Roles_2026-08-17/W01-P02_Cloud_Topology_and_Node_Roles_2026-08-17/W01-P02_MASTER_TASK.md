# W01-P02 — Cloud Topology & Node Responsibility Convergence

**Wave:** Moodify Cognitive Wave 01  
**Package:** W01-P02  
**性质:** 云端架构收敛 / Cloud Topology / Node Responsibility  
**日期:** 2026-08-17  
**执行对象:** Codex  
**前置依赖:** W01-P00 已完成；W01-P01 已完成并通过人类审核  
**后继任务:** W01-P03 Data Plane — OSS + PolarDB  
**原子任务数:** 2  
**核心目标:** 在不部署、不迁移、不修改生产环境的前提下，基于真实基础设施，固定 One Song Infrastructure 的云端职责与边界。

---

# 0. 本包解决什么问题

P00 解决“现实是什么”。

P01 解决“权威是什么”。

P02 只解决：

> **已经存在的服务器、数据库、对象存储与外部服务，应该怎样分工，才能以最低认知摩擦承载 Moodify 的 One Song Infrastructure？**

本包不追求“大而全”的云架构。

不设计未来十万用户规模。

不为尚不存在的需求预留复杂系统。

只为下一阶段真正要跑通的主链服务：

```text
Source Audio
    ↓
Upload / Intake
    ↓
Job
    ↓
Object Storage
    ↓
Worker / Compute
    ↓
Render / Verify
    ↓
READY
    ↓
Playback Delivery
```

---

# 1. 执行前置门

## GATE P02-0 — Reality Gate

必须读取 P00：

- Executive Reality Summary
- Cloud Infrastructure Reality
- Truth Table
- Current System Map
- Evidence Index
- Conflicts / Unknowns / Blockers

如果基础设施事实不完整到无法安全分配职责：

> `STOP — INFRA_REALITY_INCOMPLETE`

---

## GATE P02-1 — Canon Gate

必须读取 P01：

- Current Canon
- Product Boundary
- Internal Systems
- Authority Order
- Canon Changelog
- Acceptance Report

如果产品边界仍未收敛：

> `STOP — CANON_INCOMPLETE`

---

# 2. 本包的两个原子任务

# T02-1 — Node Role Assignment

目标：对每个真实存在的基础设施组件，指定**唯一主职责**与允许的辅助职责。

## 2.1 必须覆盖的对象

以 P00 扫描结果为准，最低包括：

- 杭州 ECS
- 洛杉矶服务器
- PolarDB MySQL
- PolarDB PostgreSQL
- OSS（若已开通）
- 当前真实运行的 worker / API
- 当前真实 Android delivery entry
- 已接入的外部音频 API
- 任何 P00 发现的其他节点

---

## 2.2 每个节点必须回答

| Field | Requirement |
|---|---|
| `node_id` | 唯一编号 |
| `observed_identity` | P00 事实身份 |
| `primary_role` | 唯一主职责 |
| `secondary_roles` | 0~N 个辅助职责 |
| `forbidden_roles` | 明确不能承担什么 |
| `capacity_limit` | 当前阶段容量边界 |
| `concurrency_limit` | 当前阶段并发边界 |
| `data_locality` | 数据从哪里来，到哪里去 |
| `failure_domain` | 该节点失败影响什么 |
| `recovery_owner` | 谁负责恢复 |
| `evidence_ref` | P00 证据 |
| `decision_reason` | 为什么这样分配 |

---

## 2.3 角色词表

优先从以下角色中选择，避免自造近义词：

- `CONTROL_API`
- `JOB_ORCHESTRATION`
- `CPU_WORKER`
- `GPU_WORKER`
- `EXTERNAL_AUDIO_SERVICE`
- `METADATA_DB`
- `OBJECT_STORAGE`
- `PLAYBACK_DELIVERY`
- `OBSERVABILITY`
- `DEV_TEST_ONLY`
- `RESERVE_UNUSED`

若确需新增角色，必须写入 Decision Register 并说明为什么现有词表不足。

---

## 2.4 一节点一主责原则

每个节点必须有一个 `primary_role`。

允许小规模阶段一个节点承担多个辅助角色，但必须显式说明：

- 为什么当前阶段可以共置；
- 资源边界；
- 什么条件下必须拆分；
- 共置失败会造成什么影响。

禁止使用：

> “这台机器什么都可以跑。”

---

## 2.5 One Song 优先

所有角色分配必须先满足：

```text
1 song
→ complete pipeline
→ recoverable
→ evidence-preserving
→ playable
```

而不是：

```text
future scale
→ microservices
→ complex cluster
→ no song actually works
```

---

# T02-2 — Network, Security, Deployment & Service Boundary

目标：固定节点之间**允许怎样通信**，以及每个服务的部署边界。

## 2.6 必须形成 Network Matrix

每一条通信边都必须列出：

- source
- destination
- protocol
- port
- direction
- purpose
- public/private
- authentication
- data class
- allowed / forbidden
- current / target
- evidence

---

## 2.7 网络设计原则

优先级：

1. 同地域私网
2. 受控公网 HTTPS
3. 外部 API 的官方 HTTPS endpoint
4. 禁止将数据库直接暴露为不受控公网服务

如果 P00 现实已经存在公网连接：

- 记录现实；
- P02 可以提出目标边界；
- 不在本包直接修改。

---

## 2.8 Secret Boundary

P02 只定义 Secret 应该在哪里，不写入真实 Secret。

必须形成：

`SECRET_OWNERSHIP_MATRIX.md`

至少覆盖：

- DB credentials
- OSS AccessKey / STS
- external audio API keys
- app/API signing secrets
- service-to-service credentials
- SSH keys

每个 Secret 必须回答：

- owner
- consumer
- storage location class
- rotation owner
- exposure boundary
- forbidden locations

禁止：

- Secret 写进 Git
- Secret 写进 Android 包
- Secret 写进任务包
- 把完整 DSN 写进报告

---

## 2.9 Deployment Boundary

每个服务必须回答：

- source repository/path
- deploy node
- runtime
- process manager
- config source
- log path class
- restart policy
- health check
- expected port
- artifact identity
- rollback unit

P02 只设计并记录，不实际部署。

---

# 3. 必须做出的核心架构决策

## 3.1 Control Plane

P02 必须明确：

- 哪个节点承担 API / Job authority
- 哪个组件是唯一 Job authority
- queue 在当前阶段是：
  - DB-backed
  - Redis
  - local queue
  - other
- 当前阶段是否真的需要 Redis

原则：

> **没有现实必要性，不新增常驻基础设施。**

---

## 3.2 Compute Plane

必须明确：

- CPU worker 在哪里
- 是否存在 GPU worker
- 外部 stem / audio API 在 pipeline 中属于什么角色
- 并发=1 还是更高
- 什么资源指标触发扩容

---

## 3.3 Data Plane 只定边界，不定 Schema

P02 只固定：

- metadata → database
- audio/object artifacts → object storage
- runtime temp → worker local scratch
- logs/evidence → 哪类持久化系统

P03 才设计 OSS prefix 与 PolarDB schema。

---

## 3.4 Delivery Plane

必须明确：

- READY 产物从哪里读取
- Android 从哪里获得 playback URL / metadata
- 是否通过 API 签发访问
- 是否允许客户端直接持有 OSS 长期凭证

默认原则：

> 客户端不得持有长期 OSS Secret。

---

# 4. 禁止过度设计

P02 当前阶段默认禁止引入：

- Kubernetes
- service mesh
- Kafka
- distributed tracing platform
- multi-region active-active
- complex CDN orchestration
- multi-master database
- custom distributed scheduler
- second job state authority

除非 P00/P01 真实证据证明已经存在或当前 One Song 必须依赖。

任何新增基础设施都必须回答：

> **它永久消灭了哪一种当前已发生的摩擦？**

若回答不了，不新增。

---

# 5. 容量边界

必须为每个 compute node 写出当前阶段的容量契约。

至少包括：

- max concurrent jobs
- expected full-song duration range
- RAM safe floor
- disk scratch budget
- swap warning threshold
- CPU saturation warning
- temp asset cleanup ownership
- external API rate assumptions
- what condition blocks expansion to 3-song pilot

不要虚构 benchmark。

如果 P00 没有测量数据：

> `CAPACITY_UNKNOWN — MEASURE_IN_P07/P08`

---

# 6. 失败域设计

必须输出：

`FAILURE_DOMAIN_MATRIX.md`

至少分析：

- Control/API node down
- worker down
- DB unavailable
- OSS unavailable
- external stem API unavailable
- external processing API unavailable
- network partition
- disk full
- job process crash
- app cannot fetch READY track

每种失败必须回答：

- current behavior
- desired behavior
- data loss risk
- job state risk
- recovery authority
- manual action required
- whether P04/P05 must implement support

---

# 7. 目标拓扑文件

必须输出：

`TARGET_ONE_SONG_TOPOLOGY.mmd`

规则：

- 实线：P02 目标主链
- 标注真实节点 alias
- 不画不存在的服务为“已部署”
- planned component 必须标 `PLANNED`
- 数据流与控制流分开标注
- 数据库与 OSS 不得混为一类

建议逻辑：

```text
Client / Operator
      │
      ▼
Control/API
      │
      ├── metadata/job ──> PolarDB
      │
      ├── object refs ──> OSS
      │
      ▼
Worker
      │
      ├── source <────── OSS
      ├── external audio service
      ├── local scratch
      └── render/evidence ──> OSS
                              │
                              ▼
                         READY metadata
                              │
                              ▼
                            PLAY
```

节点具体分配必须由 P00 事实决定。

---

# 8. 必须输出的文件

至少：

1. `00_P02_EXECUTIVE_SUMMARY.md`
2. `01_NODE_ROLE_ASSIGNMENT.md`
3. `01_NODE_ROLE_ASSIGNMENT.csv`
4. `02_NETWORK_MATRIX.md`
5. `03_SECRET_OWNERSHIP_MATRIX.md`
6. `04_DEPLOYMENT_BOUNDARY.md`
7. `05_FAILURE_DOMAIN_MATRIX.md`
8. `06_CAPACITY_AND_SCALING_CONTRACT.md`
9. `07_TARGET_ONE_SONG_TOPOLOGY.mmd`
10. `08_ARCHITECTURE_DECISION_REGISTER.md`
11. `09_P03_HANDOFF.md`
12. `10_P02_ACCEPTANCE_REPORT.md`

---

# 9. Decision Register

每一个重要架构选择都要写：

- decision id
- problem
- observed reality
- options
- selected option
- why
- rejected options
- evidence
- reversibility
- trigger to revisit

特别要求记录：

- control node selection
- worker node selection
- metadata DB selection
- object storage role
- queue choice
- public/private network choices
- external API position
- Android delivery boundary

---

# 10. 本包允许与禁止的动作

## 允许

- 阅读 P00/P01
- 阅读仓库部署脚本
- 读取现有服务配置（Secret 必须遮蔽）
- 做架构决策文档
- 做 Mermaid 图
- 做 matrix / register
- 如需要，新增纯文档 architecture decision records

## 禁止

- 部署
- SSH 上服务器修改文件
- systemctl restart
- docker restart
- 新开端口
- 修改安全组
- 修改数据库
- 建表
- 建 OSS bucket
- 上传对象
- 改 Android
- 改 worker
- 改 API
- 改状态机
- 安装 Redis
- 安装 Docker
- 安装任何依赖

---

# 11. 验收标准

- [ ] P00 Reality 已读取
- [ ] P01 Canon 已读取
- [ ] 所有真实节点都有唯一主职责
- [ ] 每个节点有 forbidden roles
- [ ] network matrix 完成
- [ ] public/private 边界清楚
- [ ] Secret ownership 完成
- [ ] deployment boundary 完成
- [ ] failure domain matrix 完成
- [ ] capacity contract 完成
- [ ] Control / Compute / Data / Delivery 四平面分开
- [ ] 未把 PolarDB 当对象存储
- [ ] 未把 OSS 当任务状态数据库
- [ ] 未创建第二套 Job authority
- [ ] 未为了“未来规模”引入重型基础设施
- [ ] 未执行任何部署或生产修改
- [ ] 所有 UNKNOWN 明确保留
- [ ] target topology 与 P00 reality map 明确区分
- [ ] P03 handoff 完成
- [ ] 完成后停止，不进入 P03

---

# 12. 向 P03 的交接

P03 不再讨论节点职责。

P03 只回答：

> **在 P02 已固定的云端职责下，OSS 与 PolarDB 如何形成唯一、可追溯、可恢复的数据平面？**

P03 输入：

- P00 Reality
- P01 Canon
- P02 Node Role Assignment
- P02 Network Matrix
- P02 Deployment Boundary
- P02 Target One Song Topology
- P02 Architecture Decision Register

---

# 13. 最终执行口令

> 执行 W01-P02 Cloud Topology & Node Responsibility Convergence。  
> 必须先读取并通过 P00 Reality Gate 与 P01 Canon Gate。  
> 只做架构收敛，不做部署。  
> 根据真实服务器能力，为每个节点指定唯一主职责、辅助职责、禁止职责、容量边界和失败域；形成 Network Matrix、Secret Ownership、Deployment Boundary、Capacity Contract 与 Target One Song Topology。  
> 不新增没有现实必要性的重型基础设施，不创建第二套 Job authority，不修改服务器、数据库、OSS、Android、API 或 worker。  
> 所有无法由 P00 证据支持的容量结论写 UNKNOWN。  
> 完成 P03 Handoff 后停止，等待人类审核。
