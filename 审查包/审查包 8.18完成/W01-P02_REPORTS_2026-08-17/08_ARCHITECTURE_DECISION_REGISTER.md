# 08 — Architecture Decision Register

**P02 · 2026-08-17 · base: P00 Reality + P01 Canon**

---

## ADR-001 — Control Node Selection

- Problem: 哪个节点承担 API / Job authority（任务书 §3.1）
- Observed reality: LA 已承载对外 BFF/API/Ear API/worker；杭州承载数据 API + worker（E13/E14）
- Options: (a) LA 为控制面 (b) 杭州为控制面 (c) 双控制面
- **Selected: (a) LA 为控制面**（primary=CONTROL_API）
- Why: 对外产品面（PLAY）在 LA；BFF/API/隧道均已在 LA；控制面应靠近对外交付
- Rejected: (b) 杭州 1.6GB 内存不足且远离对外面；(c) 双控制面违反"无第二套 authority"（R3）
- Evidence: E13/E15/E16
- Reversibility: 高（文档级分配）
- Revisit trigger: 控制面迁移/拆分部署单元时

## ADR-002 — Worker Node Selection

- Problem: CPU worker 在哪里
- Observed reality: LA moodify-worker（队列近空）+ 杭州 moodify-data-worker（pilot 实证）
- **Selected: 双 worker，但职责分离**——杭州 = 数据工厂 CPU_WORKER（主责）；LA = Ear worker（辅助，控制面同机）
- Why: 杭州的 10-song pilot 是唯一实证批处理能力；LA worker 保留承载 Ear API 相关任务
- Rejected: 仅 LA（丢实证能力）/ 仅杭州（Ear API 在 LA 需本地 worker）
- Evidence: E13/E14/E18 §12
- Revisit: 3-song pilot 后按实测重分配

## ADR-003 — Metadata DB Selection

- Problem: 元数据权威库
- Observed reality: PolarDB moodify_dev（19 表 ≈0 数据，schema-only）；SQLite 实跑队列
- **Selected: PolarDB moodify_dev（172.27.118.104）= 目标 METADATA_DB**
- Why: 唯一业务 schema 容器；任务书禁止把 DB 当对象存储、OSS 当状态库（R4）
- Rejected: SQLite 升级为业务库（不可审计/不可并发）；上海 PG（未用）；空壳实例（无 schema）
- Evidence: E17（BLOCKED）/E18
- Reversibility: 中（schema 未冻结前可换）
- Revisit: P03 schema 设计后

## ADR-004 — Object Storage Role

- Problem: 对象存储角色
- Observed reality: **NOT_PROVISIONED**（无 OSS/S3/R2）
- **Selected: OSS = OBJECT_STORAGE（PLANNED，P03 设计 prefix/凭据/生命周期）**
- Why: 音频对象必须离开服务器磁盘（R5：本地盘=scratch）；P00 技术债 #P0
- Rejected: 继续本地磁盘（不可扩展）；自建 MinIO（新增常驻基础设施，R6 禁止）
- Evidence: TT-036/E18 §11
- Revisit: P03 开通后

## ADR-005 — Queue Choice

- Problem: 队列后端
- Observed reality: SQLite（LA node.sqlite3 16KB 近空；杭州 data_node 历史）
- **Selected: 保持 SQLite local queue；不引 Redis**
- Why: R6——当前无现实必要性（队列近空，并发=1）；Redis 是新增常驻基础设施
- Rejected: Redis（无负载证据）；PolarDB-backed queue（P04 评估，现阶段 schema 未冻结）
- Evidence: E13/E14/TT-037
- Reversibility: 高（队列后端替换不改变接口）
- Revisit: P04 控制面任务（任务量增长 / 需要多 worker 时）

## ADR-006 — Public/Private Network Choices

- Problem: 公网/私网边界
- Observed reality: 杭州 :8000 公网可达（service-key）；DB 端口关闭；PolarDB 私网
- **Selected: 目标——杭州 :8000 收紧为仅 LA 白名单；DB 保持私网；LA→PolarDB 不经跨地域直连**
- Why: 最小攻击面（任务书 §2.7 优先级）；跨地域 DB 直连延迟/成本无必要
- Rejected: DB 公网（禁止）；保留杭州 API 全公网（现状风险，记录不改）
- Evidence: E16/E17
- Revisit: P03 实施时

## ADR-007 — External Audio API Position

- Problem: lalal 分离在 pipeline 中的位置
- Observed reality: audiolla 容器（LA，健康，无自动调用）
- **Selected: audiolla 保持为 LA 本地代理（EXTERNAL_AUDIO_SERVICE）；LALAL.AI 为云端后端**
- Why: 已有部署 + 健康；代理隔离计费/限流细节
- Rejected: 直连 LALAL API（重复）；杭州侧部署（内存不足）
- Evidence: E13/E15/E18 §27
- Revisit: P05 接入自动 pipeline 后评估

## ADR-008 — Android Delivery Boundary

- Problem: Android 如何获得 READY 曲目
- Observed reality: 直接静态 URL（resolveUrl，无鉴权）
- **Selected: 目标——经 BFF 签发限时 URL；客户端不持长期云凭据（R7）**
- Why: 防越权访问；OSS 开通后不能把 AccessKey 给客户端
- Rejected: 客户端直连 OSS（R7 禁止）
- Evidence: E18 §24/E26
- Revisit: P06 交付面实施时

## ADR-009 — 共置决策（LA 多角色）

- Problem: LA 一机 5 类职责
- **Selected: 允许共置（小规模豁免），primary=CONTROL_API**
- Why: 服务量小；资源余量充足；拆分=新增部署单元（R6）
- 拆分条件: audiolla >1.5GB 驻留 / 队列持续任务 / 对外流量竞争
- Evidence: E13/E15
- Revisit: 上述条件触发时

## ADR-010 — 腾讯云/空实例处置

- Problem: 已删除腾讯云 + 2 个空 PolarDB
- **Selected: 腾讯云 OBSOLETE 不纳入；PolarDB 空壳（NODE-004/005）= RESERVE_UNUSED**
- Why: 不承担职责；保留不删除（资源堆积记录）
- Evidence: 用户确认 2026-08-12；E18
- Revisit: P03/P04 决定释放或迁移

## 禁止引入清单落实（§4）

- Kubernetes / service mesh / Kafka / tracing / multi-region / CDN orchestration / multi-master DB / custom scheduler / second job authority：**全部未引入**（无证据需要）。
- 新增基础设施唯一候选 = OSS（P03，有明确必要性：对象存储缺失是 P0 瓶颈）。
