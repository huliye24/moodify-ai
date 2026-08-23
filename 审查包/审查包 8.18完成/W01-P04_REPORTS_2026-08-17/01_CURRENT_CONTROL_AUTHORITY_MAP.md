# 01 — Current Control Authority Map

**W01-P04 · 2026-08-17 · 扫描完成于任何代码变更之前（硬规则 §2）**

## 发现的候选系统

| 系统 | 路径 | 状态枚举 | 机制 | 分类 |
|---|---|---|---|---|
| **node/**（旧队列） | src/moodify/node/（queue.py/worker.py/db.py/models.py/resources.py） | 4 态：QUEUED/RUNNING/SUCCEEDED/FAILED | SQLite WAL 队列；`lease_next()` BEGIN IMMEDIATE 原子领取 + lease_until(6h)；`retry_or_fail()` 3 次；`recover_expired()`/`recover_interrupted()`；资源守卫；**无 heartbeat、无 cancel** | **LEGACY**（生产实跑：LA/杭州 worker） |
| **reconstruction_job/**（新，未提交） | src/moodify/reconstruction_job/（contract/store/engine/worker/routes/retention） | 11 态：QUEUED/VALIDATING/ANALYZING/PLANNING/RECONSTRUCTING/VERIFYING/HUMAN_REQUIRED/SUCCEEDED/SOURCE_WINS/FAILED/CANCELLED | lease_next/recover_interrupted/retry_or_fail（仅 TRANSIENT）/request_cancel/admin_cancel/幂等唯一键/retention 清扫 | **CANONICAL_CANDIDATE**（未跟踪目录=并行会话未提交工作；设计最完整但 state/stage 未分离） |
| **data_plane/repository.py**（P03，已提交） | src/moodify/data_plane/repository.py | current_state 裸字段（默认 "CREATED"） | 幂等注册；**无迁移定义** | **UNKNOWN → P04 填补**（本包实现基准） |
| data_factory/ | src/moodify/data_factory/runner.py | 无持久状态机（lifecycle=COMPLETED 一次性写） | 同步顺序执行；case_runner 幂等/原子 | LEGACY |
| orchestration/workflow_engine.py | src/moodify/orchestration/ | PhaseStatus 5 态（进程内 DSP 阶段） | 无持久任务状态 | LEGACY |
| contracts/production_case.py | src/moodify/contracts/ | LifecycleState 6 态 + AuthorityState 4 态 | case 生命周期（非 job） | CANONICAL（case 域，独立） |
| stems/store.py | src/moodify/stems/ | StemStatus 4 态 | 外部 LALAL 轮询跟踪 | EXPERIMENTAL |
| authority/escalation.py | src/moodify/authority/ | MACHINE_DECIDED/HUMAN_REQUIRED/INCONCLUSIVE/FAILED | 评审升级 | CANONICAL（评审域） |
| physics/reliable_runner.py | src/moodify/physics/ | Heartbeat 类 | 实验脚本 | EXPERIMENTAL |

## 现状缺口（P04 必须填补）

1. **无 canonical 状态迁移定义/校验**——任何模块都能随意改 current_state。
2. **无 heartbeat 续租**——只有一次性 lease_until(6h)。
3. **auditory jobs 无 cancel**。
4. **node / reconstruction_job / data_plane 三处状态存储无映射关系**。
5. **reconstruction_job 将 stage 混入 state**（VALIDATING/ANALYZING/PLANNING/RECONSTRUCTING 是 stage 不是 lifecycle）——违反 State≠Stage 原则。
6. **无事件日志（append-only）**、无 attempt 模型、无结构化 failure taxonomy 的统一实现。

## P04 收敛决策

- **权威实现基准 = P03 已提交的 `data_plane.repository`**（jobs 表字段承载），在其上实现统一状态机模块（`control.py`），对齐 8 态生命周期。
- **reconstruction_job/ 标记 CANONICAL_CANDIDATE（未提交，并行会话工作）**：其 11 态将映射到 8 态（见 02 报告）；本包不修改该目录。
- **node/ 保持生产运行**（LA/杭州），其 4 态映射到 8 态；P04 不部署改动（CONTROL_PLANE_DEPLOY_BLOCKED）。
- 不创建第二套 queue/state authority：data_plane.control 是唯一权威实现，node/reconstruction_job 是运行时投影/迁移目标。

## 证据

- Explore agent 扫描（2026-08-17）；src 目录文件确认；git ls-files（reconstruction_job 未跟踪）。
