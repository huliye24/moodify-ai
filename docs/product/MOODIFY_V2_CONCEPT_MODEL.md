# Moodify Studio Workspace v2 — 概念模型盘点

**版本：Concept Model 1.0**
**日期：2026-07-25**
**对应执行步骤：P0 / Step 3**

## 1. 概念全景

Moodify v2 的概念模型围绕"以项目为中心的音乐工艺工作流"组织，涵盖 8 个核心域模型、6 个逻辑角色、3 个服务适配器和 1 个存储层。

```
AudioProject ──┬── CreativeBrief        (创意意图)
               ├── ProjectThread[]       (工作线程)
               ├── AudioVersion[]        (版本树)
               │     └── ApprovalDecision (审批证据)
               ├── TreatmentPlan[]       (处理方案)
               │     └── TreatmentVariant[] (A/B/C 候选)
               │           └── TreatmentAction[] (工程步骤)
               └── ProjectWorkflow       (阶段状态机)
```

## 2. 核心域模型职责清单

### 2.1 AudioProject（项目聚合根）

| 项 | 内容 |
|---|---|
| **职责** | 代表一首歌的完整工艺历史，是所有操作的人口 |
| **关键字段** | project_id, title, status, source_audio_ids, creative_brief, active_version_id, approved_version_id |
| **生命周期** | CREATED → BRIEFING → ANALYZING → DESIGNING → PROCESSING → REVIEWING → AWAITING_USER → APPROVED → DELIVERED → ARCHIVED |
| **不变式** | APPROVED/DELIVERED/ARCHIVED 必须有 approved_version_id；updated_at ≥ created_at |
| **文件** | `domain/project.py` — `AudioProject`, `ProjectStatus`, `LegacyReference` |

### 2.2 CreativeBrief（创意简报）

| 项 | 内容 |
|---|---|
| **职责** | 承载用户的结构化创作意图，是诊断、设计、处理、审查的共同输入 |
| **关键字段** | goal, preserve[], avoid[], platform, reference[] |
| **不变式** | preserve 和 avoid 不可有交集；列表项不可为空或重复 |
| **修改规则** | 可编辑，但修改需在版本日志中记录时间和内容 |
| **文件** | `domain/creative_brief.py` — `CreativeBrief` |

### 2.3 ProjectThread（工作线程）

| 项 | 内容 |
|---|---|
| **职责** | 持久化工作流节点，记录角色、状态、输入、输出和重试信息。不是 OS 线程也不是聊天线程 |
| **关键字段** | thread_id, project_id, thread_type, role, status, inputs, outputs, error, retry_count, max_retries |
| **角色枚举** | PRODUCER, ANALYST, DESIGNER, WORKER, JUDGE, ARCHIVE |
| **线程类型** | BRIEF, DIAGNOSIS, DESIGN, VOCAL, SPECTRUM, DYNAMICS, SPACE, LOUDNESS, EXPORT, JUDGE, ARCHIVE |
| **状态转换** | PLANNED → QUEUED → RUNNING → PASSED/REJECTED/FAILED / AWAITING_USER；REJECTED/FAILED 可 QUEUED 重试 |
| **不变式** | thread_type 与 role 强绑定（ROLE_BY_THREAD_TYPE）；retry_count ≤ max_retries；RUNNING 必须有 started_at；终态必须有 finished_at |
| **文件** | `domain/thread.py` — `ProjectThread`, `ThreadRole`, `ThreadType`, `ThreadStatus` |

### 2.4 TreatmentPlan / TreatmentVariant / TreatmentAction（处理方案族）

| 项 | 内容 |
|---|---|
| **职责** | Designer 线程输出，包含 1-3 个候选 A/B/C 变体，每个变体包含有序工程步骤 |
| **TreatmentPlan** | plan_id, project_id, brief_revision, diagnosis_id, variants[], recommended_variant_id |
| **TreatmentVariant** | variant_id, label(A/B/C), objective, problems[], preserve[], actions[], risks[], target_metrics |
| **TreatmentAction** | action_id, order(从1连续), step_type, public_summary, reason, target_metrics, parameter_bounds |
| **步骤类型** | IMPORT, STEM_SEPARATION, VOCAL_CORRECTION, NOISE_REDUCTION, SPECTRAL_BALANCE, DYNAMIC_SHAPING, TRANSIENT_REPAIR, SPACE_DESIGN, STEREO_CONTROL, STEM_MIX, LOUDNESS_NORMALIZATION, TRUE_PEAK_LIMITING, PLATFORM_EXPORT, QUALITY_REVIEW, MANUAL_ADJUSTMENT, APPROVAL, DELIVERY |
| **不变式** | action_id 在 variant 内唯一；order 从 1 连续；variant labels 从 A 开始 |
| **文件** | `domain/treatment_plan.py` — `TreatmentPlan`, `TreatmentVariant`, `TreatmentAction`, `TreatmentStepType` |

### 2.5 AudioVersion（音频版本节点）

| 项 | 内容 |
|---|---|
| **职责** | 版本树中的不可变节点，音频本体永远不可覆盖 |
| **关键字段** | version_id, project_id, parent_version_id, branch, audio_path, audio_sha256, status, treatment_plan_id, treatment_variant_id, approval |
| **生命周期** | DRAFT → REVIEWING → REJECTED/APPROVED → DELIVERED → ARCHIVED |
| **不变式** | audio_path 必须在 versions/ 下；audio_sha256 必须 64 位 hex；不可自引用为 parent；REJECTED/APPROVED/DELIVERED 必须有 approval；回退通过新建版本实现 |
| **文件** | `domain/audio_version.py` — `AudioVersion`, `VersionStatus` |

### 2.6 ApprovalDecision（审批决策）

| 项 | 内容 |
|---|---|
| **职责** | 追加式的不可变人工审批证据，绑定到确切版本 |
| **关键字段** | decision_id, project_id, version_id, outcome, reason, operator, actor_type, return_to_thread |
| **结果枚举** | APPROVED, REJECTED, RETURNED |
| **强制规则** | APPROVED 必须由 HUMAN 做出；RETURNED 必须指定 return_to_thread；无人工批准的版本不得进入 Final |
| **文件** | `domain/approval.py` — `ApprovalDecision`, `ApprovalOutcome`, `ApprovalActorType` |

### 2.7 ProjectWorkflow（项目工作流状态机）

| 项 | 内容 |
|---|---|
| **职责** | 追踪项目在 8 阶段流水线中的位置，支持暂停/恢复/失败 |
| **阶段序列** | INTAKE → BRIEF → DIAGNOSIS → DESIGN → PROCESS → JUDGE → APPROVAL → FINAL |
| **动作** | ADVANCE, PAUSE, RESUME, FAIL |
| **附加状态** | PAUSED（记录 paused_from）、FAILED（记录 failure_reason） |
| **不变式** | 事件历史末尾必须匹配当前 stage；非 INTAKE 状态必须有历史 |
| **文件** | `domain/workflow.py` — `ProjectWorkflow`, `WorkflowStage`, `WorkflowAction`, `WorkflowEvent` |

### 2.8 LegacyReference（旧系统引用）

| 项 | 内容 |
|---|---|
| **职责** | 指向旧系统记录的只读追溯指针，支持幂等迁移 |
| **关键字段** | source_type, legacy_id, source_path, source_hash |
| **工具方法** | migration_key — 用于幂等迁移键 |
| **文件** | `domain/project.py` — `LegacyReference` |

## 3. 服务层适配器

| 服务 | 文件 | 职责 |
|---|---|---|
| **Analyst** | `services/analyst.py` | 封装 v0.1 的 scan_audio + analyze + diagnose，产出诊断线程输出 |
| **Designer** | `services/designer.py` | 基于 Brief + Diagnosis 产出 TreatmentPlan（首版支持规则模板，LLM 可插拔） |
| **DspWorker** | `services/dsp_worker.py` | 封装 v0.1 的 process_audio，将 TreatmentPlan 映射为 preset/craft chain 执行 |

三个服务均通过 `WorkspaceStore` 读写，不直接操作文件系统。

## 4. 存储层

| 组件 | 文件 | 职责 |
|---|---|---|
| **WorkspaceStore** | `storage/workspace_store.py` | 项目隔离的 JSON/JSONL 本地存储，支持原子快照写入、追加式审批记录和崩溃安全 |

以 `{root}/{project_id}/` 为隔离单元，每个项目目录包含 `project.json`、`threads/`、`versions/`、`plans/`、`approvals/` 子目录。

## 5. 新旧概念映射

v2 设计明确复用了 v0.1/v0.2 的下层能力，但重新组织了上层模型：

| v0.1/v0.2 概念 | v2 对应 | 映射关系 |
|---|---|---|
| `OperatorJob`（API `OperatorJobCreateRequest`） | `ProjectThread` + `DspWorkerService` | 旧 OperatorJob 是"一次处理请求"，v2 拆分为持久线程 + 可重试 Worker 执行 |
| `CandidateVersion`（MVP 文档概念） | `AudioVersion` | 旧概念是"处理的候选输出"，v2 扩展为完整版本树，支持分支、血缘和不可变音频 |
| `QualityGate` / `GateResult`（diagnosis/quality_gate.py） | `GateResult` + Judge 线程 + `ApprovalDecision` | 旧 Gate 是三段式技术检查，v2 接手 GateResult 的做法并将其嵌入 Judge → Approval 人工门禁 |
| `DeliveryBundle`（v01_types.py / v01_delivery.py） | `AudioVersion.status=DELIVERED` + Archive 线程 | 旧 Delivery 是文件打包，v2 将 DELIVERED 作为版本状态，归档由 Archive 线程统一执行 |
| `StudioProject`（MVP 文档概念） | `AudioProject` | 旧概念是"一个工作室项目"，v2 实现为具体聚合根 |
| `ProcessResult`（v01_types.py） | `DspWorker` 输出 + `AudioVersion` | 旧结构是一次 pipeline 运行结果，v2 将其拆分为线程输出和不可变版本记录 |
| `ScanResult` / `DiagnosisReport`（v01_types.py） | Analyst 线程输出 | 旧结构是单一诊断报告，v2 将其作为 Analyst 线程的持久化输出 |

## 6. 复用边界原则

1. **下层能力复用，上层模型重建** — v0.1 的 `scan_audio`、`analyze`、`diagnose`、`process_audio` 函数不变，但它们的调用入口从 `cli.py` / `main.py` 迁移到 `services/` 下的适配器。
2. **旧 API 不破坏** — `/studio/*` 和 `/operator/*` 接口继续工作，v2 新增 `/workspace/*` 路径前缀。
3. **存储格式兼容** — v0.1 的 JSON 报告格式保持可读，v2 的 JSONL/JSON 存储使用新 schema_version 区分。
4. **Gate 逻辑继承** — `QualityGate` 的三段式检查逻辑保留，v2 的 Judge 线程调用同一套门控规则。
5. **禁止重复建模** — 已由 v2 域模型覆盖的概念（项目、版本、线程、审批），不再在旧 dataclass 中重复定义。旧 `v01_types.py` 中的 dataclass 仅在 v0.1 适配器内部使用。

## 7. 概念依赖拓扑

```
CreativeBrief ─────────────────────────────────────────┐
                                                       │
AudioProject ──┬── ProjectWorkflow (阶段状态机)         │
               │                                       │
               ├── ProjectThread[] (6 角色)             │
               │     ├── ANALYST ── 读取 Brief          │
               │     ├── DESIGNER ── 读取 Brief + Dx   │
               │     ├── WORKER ─── 执行 TreatmentPlan  │
               │     └── JUDGE ─── 检查 AudioVersion    │
               │                                       │
               ├── TreatmentPlan[]                      │
               │     └── TreatmentVariant[]             │
               │           └── TreatmentAction[]         │
               │                                       │
               ├── AudioVersion[]                       │
               │     └── ApprovalDecision               │
               │                                       │
               └── LegacyReference[] (追溯旧系统)        │
```

## 8. 盘点结论

v2 概念模型已涵盖 MVP 所需的全部核心抽象：

- ✅ 项目系统（AudioProject + ProjectWorkflow）
- ✅ Creative Brief（CreativeBrief）
- ✅ 工作线程状态（ProjectThread + 6 角色 + 11 类型）
- ✅ Treatment Plan（TreatmentPlan → TreatmentVariant → TreatmentAction）
- ✅ 音频版本树（AudioVersion + 分支/血缘/不可变音频）
- ✅ Judge 与人工审批（GateResult 复用 + ApprovalDecision）
- ✅ 比较与归档（Version Compare API + Archive 线程）
- ✅ 存储层（WorkspaceStore）

不存在重复建模；旧 v0.1 dataclass 均通过适配器封装，避免与 v2 域模型形成平行体系。
