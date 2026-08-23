# 01 — Node Role Assignment

**Decision Basis:** P00 snapshot（审查包/W01-P00_REPORTS_2026-08-17）；P01 Canon（docs/canon/* + 审查包/W01-P01_REPORTS_2026-08-17）
**Date:** 2026-08-17
**Architect/Agent:** Claude A（huliye24 本地会话）
**原则:** 一节点一主责（R2）；One Song before scale（R1）；无证据不虚构容量（R9）。

---

## NODE-001 — LA（103.144.246.242, moodify-ear-runner）

- Observed identity: 亿速云 Yisu VPS（hostname yisu-6a7bcb73aac20）
- Provider / Region: 亿速云 / 洛杉矶
- CPU/RAM: 4 vCPU AMD EPYC 7H12 / 7.7 GiB（可用 6.1G）/ 98GB disk（76G 可用）
- Current services: nginx:80、cloudflared 隧道、moodify-api:8000（Ear FastAPI）、moodify-music:3100（vinext）、moodify-music-bff:8100、moodify-worker（SQLite）、docker audiolla
- Current deployed commit: UNKNOWN（tar 发布，无 git）
- **Primary role:** CONTROL_API（对外 API/BFF + 内部 Ear API 控制面）
- Secondary roles: PLAYBACK_DELIVERY（nginx/music-platform/music-media）；CPU_WORKER（moodify-worker）；EXTERNAL_AUDIO_SERVICE（audiolla 容器宿主）
- Forbidden roles: METADATA_DB（不跑业务数据库）；OBJECT_STORAGE（不做对象存储）
- Max concurrency: 1 worker + 1 audiolla 容器（现状）；未实测更高并发
- Capacity evidence: raw_scan LA（E13/E15）；audiolla 驻留 ~770MB；node 123MB；uvicorn 68MB
- Local scratch budget: 未专门分配（磁盘 76G 可用，可承载临时产物）
- Data inputs: 外部用户/Android；杭州 API 回传
- Data outputs: audiolla → LALAL.AI；BFF → 杭州 API；静态音频 → 用户
- Failure domain: 官网/平台/API/worker/audiolla 全在同机 → **单点**（P00 黑箱调查 §25 确认）
- Recovery owner: 人工（Codex + 用户）；24x7 recover_interrupted_jobs（worker 级）
- Reason: 现状已承载全部对外面与控制面；一节点一主责取 CONTROL_API，其余显式声明为辅助共置（小规模阶段允许，条件见下）
- Revisit trigger: audiolla 或 worker 迁移出 LA；官网独立成部署单元；对外流量显著增长
- Evidence refs: raw_scan/LA_103_144_246_242_scan.txt；MOODIFY_CLOUD_CURRENT_STATE_2026-08-17.md

## NODE-002 — 杭州（120.55.191.146, Aliyun ECS）

- Observed identity: iZln9jrdhi9iv6Z（Ubuntu 26.04 / kernel 7.0）
- Provider / Region: 阿里云 / cn-hangzhou（VPC vpc-bp1sty2c4ogudtqo68dro）
- CPU/RAM: 2 vCPU / 1.6 GiB / 2GiB swap / 40GB disk（23G 可用）
- Current services: moodify-api:8000（公网 service-key）、moodify-data-worker、4 timers
- **Primary role:** CPU_WORKER（数据工厂批处理）
- Secondary roles: CONTROL_API（内部数据 API）；JOB_ORCHESTRATION（4 timers + SQLite data_node）
- Forbidden roles: PLAYBACK_DELIVERY（不对公网播放）；METADATA_DB；OBJECT_STORAGE
- Max concurrency: 1（LSM 结论：并行=1；10-song pilot 0 OOM）
- Capacity evidence: raw_scan HZ（E14/E16）；pilot 10/10 SUCCEEDED（swap ~1GiB）
- Data inputs: inbox/数据源；LA BFF 的 API 调用
- Data outputs: /var/lib/moodify（本地 scratch）；PolarDB（目标）
- Failure domain: 数据工厂中断；swap 依赖是硬约束
- Recovery owner: 人工（Codex + 用户）；24x7 recover
- Reason: 数据工厂是杭州唯一实证能力；主责=CPU_WORKER
- Revisit trigger: 3-song pilot 前确认内存/swap 边界；P04 控制面任务
- Evidence refs: raw_scan/HZ_120_55_191_146_scan.txt

## NODE-003 — PolarDB MySQL pc-bp19502y46246gv6n（172.27.118.104）

- Observed identity: MySQL 8.0.18 XEngine；moodify_dev 19 表
- **Primary role:** METADATA_DB（目标元数据权威库；现状 schema-only）
- Forbidden roles: OBJECT_STORAGE；PLAYBACK_DELIVERY；CPU_WORKER
- Capacity: ≈0 数据（tracks 32 / track_versions 6 / audit 10 / idempotency 18 / creation_passports 6）
- Data locality: 入 = 杭州 API/worker（目标）；出 = BFF/API 查询（目标）
- Failure domain: 当前无生产流量 → 失败影响小；接入后为元数据单点
- Recovery owner: 人工（PolarDB 控制台 + 备份）
- Evidence: MOODIFY_CLOUD_CURRENT_STATE（E18）；**直接核验 BLOCKED（E17）**
- Revisit trigger: P03 完成 schema 设计并验证连通
- Note: 任务书禁止把 PolarDB 当对象存储（§11 验收）；本分配遵守 R4。

## NODE-004 — PolarDB MySQL pc-bp1112f8t24wdta5t（172.27.118.106）

- **Primary role:** RESERVE_UNUSED（空壳历史实例，不承担职责）
- Evidence: E18；直接核验 BLOCKED（E17）
- Revisit: P03/P04 决定释放或迁移

## NODE-005 — PolarDB PG pc-uf65m4xqwst72vq5a（101.133.107.206）

- **Primary role:** RESERVE_UNUSED（在线未用，内容未确认）
- Evidence: E18
- Revisit: P04 数据权威决策时评估

## NODE-006 — OSS（NOT_PROVISIONED）

- **Primary role:** OBJECT_STORAGE（目标；**PLANNED**）
- 现状: 无 bucket、无凭据、无对象（P00 TT-036）
- Forbidden: METADATA_DB（不得把 OSS 当任务状态库）；JOB_ORCHESTRATION
- Revisit: P03 开通并设计 prefix 后

## NODE-007 — audiolla 容器（LA docker）

- **Primary role:** EXTERNAL_AUDIO_SERVICE（lalal.ai 分离代理）
- Capacity: 1 容器；驻留 ~770MB；127.0.0.1:18080→8000
- 现状: 健康运行，无自动 pipeline 调用（CONNECTED_UNTESTED）
- Failure domain: 与 LA 同机；容器失败影响分离能力（不影响播放）
- Revisit: P05 接入自动 pipeline 后

## NODE-008 — Android Moodify Music 3.1

- **Primary role:** PLAYBACK_DELIVERY（客户端）
- Forbidden: CONTROL_API / METADATA_DB / OBJECT_STORAGE / JOB_ORCHESTRATION
- 现状: APK 3.1.0 发布；本地 + URL 播放（resolveUrl）；无账户体系
- Revisit: P05/P06 接入账户/上传功能

## NODE-009 — Cloudflare（DNS + 隧道）

- **Primary role:** PLAYBACK_DELIVERY（公网边界；HTTPS 终止）
- 现状: LA cloudflared 隧道（rongjingmusic.com 等）
- 注意: 不是独立计算节点；隧道失败 = 官网/平台不可达

## NODE-010 — SQLite 队列（LA node.sqlite3 + 杭州 data_node）

- **Primary role:** JOB_ORCHESTRATION（现状队列实现）
- 决策: 保持 SQLite local queue；**不引 Redis**（R6：无现实必要性）
- 禁止: METADATA_DB / OBJECT_STORAGE
- Failure domain: SQLite 文件损坏 = 队列丢失（当前近空，损失小）
- Revisit: P04 控制面任务评估 DB-backed 迁移

---

## Cross-node Summary

| Node | Primary role | Secondary roles | Forbidden roles | Concurrency | Failure domain |
|---|---|---:|---|---|---|
| NODE-001 LA | CONTROL_API | PLAYBACK_DELIVERY, CPU_WORKER, EXTERNAL_AUDIO_SERVICE | METADATA_DB, OBJECT_STORAGE | 1 worker + 1 容器 | 单点（全服务同机） |
| NODE-002 杭州 | CPU_WORKER | CONTROL_API, JOB_ORCHESTRATION | PLAYBACK_DELIVERY, METADATA_DB, OBJECT_STORAGE | 1 | swap 依赖 |
| NODE-003 PolarDB moodify_dev | METADATA_DB | — | OBJECT_STORAGE, PLAYBACK_DELIVERY, CPU_WORKER | schema-only | 无流量→低影响 |
| NODE-004 PolarDB 空壳 | RESERVE_UNUSED | — | METADATA_DB, OBJECT_STORAGE | — | 无 |
| NODE-005 PolarDB PG | RESERVE_UNUSED | — | METADATA_DB, OBJECT_STORAGE | — | 无 |
| NODE-006 OSS | OBJECT_STORAGE（PLANNED） | — | METADATA_DB, JOB_ORCHESTRATION | 0 | 未开通 |
| NODE-007 audiolla | EXTERNAL_AUDIO_SERVICE | — | OBJECT_STORAGE, METADATA_DB, PLAYBACK_DELIVERY | 1 | 与 LA 同机 |
| NODE-008 Android | PLAYBACK_DELIVERY | — | CONTROL_API, METADATA_DB, OBJECT_STORAGE, JOB_ORCHESTRATION | 1 设备 | 客户端 |
| NODE-009 Cloudflare | PLAYBACK_DELIVERY（边界） | OBSERVABILITY(边界) | CONTROL_API | 1 隧道 | 官网/平台不可达 |
| NODE-010 SQLite 队列 | JOB_ORCHESTRATION | — | METADATA_DB, OBJECT_STORAGE | 1 worker/机 | 文件损坏→队列丢 |

## 共置说明（一节点多角色的小规模豁免）

- **LA（NODE-001）**：现状 5 类职责同机。原因：当前阶段服务量小（1 worker 队列近空、audiolla 单容器、网站静态为主）；资源边界 = 4C/8G 实测余量充足。拆分条件：audiolla 驻留超过 1.5GB、worker 队列有持续任务、或对外流量使 nginx/API 竞争资源。共置失败影响 = 官网+平台+API 同时不可用（单点，已记录）。
- **杭州（NODE-002）**：API + worker 同机。原因：1.6GB 内存下分开会浪费；API 仅内部 service-key 调用。拆分条件：内存消耗使 swap 常驻 >1.5GB。
