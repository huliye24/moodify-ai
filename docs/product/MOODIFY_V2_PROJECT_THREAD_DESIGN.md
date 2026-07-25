# Moodify v2 — ProjectThread 设计文档

**版本：ProjectThread Design 1.0**
**日期：2026-07-25**
**对应执行步骤：P0 / Step 7**
**实现文件：`domain/thread.py`**

## 1. 定位

`ProjectThread` 是 Moodify v2 工作流的**最小持久执行单元**。它不是操作系统线程，不是聊天对话线程，而是一个记录角色、状态、输入输出的有生命周期的工作流节点。

每个线程在项目上下文中执行一个明确的任务类型（诊断、设计、DSP 处理、审查等），并将结果持久化为结构化数据。

## 2. 核心分类

### 2.1 逻辑角色（ThreadRole — 6 类）

| 角色 | 枚举值 | 职责 |
|---|---|---|
| Producer | `PRODUCER` | 管理 Brief 和项目配置 |
| Analyst | `ANALYST` | 音频扫描 + 指标提取 + 诊断报告 |
| Designer | `DESIGNER` | 基于 Brief + Diagnosis 生成 TreatmentPlan |
| Worker | `WORKER` | 执行 DSP 处理，产生候选音频版本 |
| Judge | `JUDGE` | 技术质量审查（clipping、响度、动态、MRS） |
| Archive | `ARCHIVE` | 打包交付物和元数据 |

### 2.2 线程类型（ThreadType — 11 类）

| 类型 | 枚举值 | 归属角色 | 说明 |
|---|---|---|---|
| Brief 编辑 | `BRIEF` | Producer | 创建/编辑 CreativeBrief |
| 音频诊断 | `DIAGNOSIS` | Analyst | 运行 scan→analyze→diagnose |
| 方案设计 | `DESIGN` | Designer | 生成 TreatmentPlan |
| 人声处理 | `VOCAL` | Worker | DSP 人声链 |
| 频谱处理 | `SPECTRUM` | Worker | DSP 频谱链 |
| 动态处理 | `DYNAMICS` | Worker | DSP 动态链 |
| 空间处理 | `SPACE` | Worker | DSP 空间链 |
| 响度处理 | `LOUDNESS` | Worker | DSP 响度链 |
| 导出 | `EXPORT` | Worker | 平台格式导出 |
| 审查 | `JUDGE` | Judge | 质量门检查 |
| 归档 | `ARCHIVE` | Archive | 打包交付记录 |

### 2.3 Role-Type 强制绑定

```python
ROLE_BY_THREAD_TYPE = {
    BRIEF: PRODUCER,
    DIAGNOSIS: ANALYST,
    DESIGN: DESIGNER,
    VOCAL / SPECTRUM / DYNAMICS / SPACE / LOUDNESS / EXPORT: WORKER,
    JUDGE: JUDGE,
    ARCHIVE: ARCHIVE,
}
```

`ProjectThread` 的 model_validator 在构造时强制校验 `thread_type` 和 `role` 的一致性。

## 3. 字段设计

### 3.1 标识

| 字段 | 类型 | 说明 |
|---|---|---|
| `schema_version` | `Literal["project_thread.v1"]` | 版本路由 |
| `thread_id` | `str` (min_length=1) | 全局唯一 |
| `project_id` | `str` (min_length=1) | 所属项目 |

### 3.2 类型与状态

| 字段 | 类型 | 说明 |
|---|---|---|
| `thread_type` | `ThreadType` | 线程类型 |
| `role` | `ThreadRole` | 执行角色（由 thread_type 决定） |
| `status` | `ThreadStatus` | 当前状态 |

**ThreadStatus（8 种状态）：**

```
PLANNED → QUEUED → RUNNING → PASSED / REJECTED
                                    ↓
                              AWAITING_USER
                                    ↓
                              FAILED / CANCELED
```

| 状态 | 含义 |
|---|---|
| `PLANNED` | 已排入计划，等待执行 |
| `QUEUED` | 已入队，等待 CPU/Worker |
| `RUNNING` | 正在执行 |
| `AWAITING_USER` | 暂停等待人工输入 |
| `PASSED` | 执行成功，终态 |
| `REJECTED` | 审查不通过，终态（可重试） |
| `FAILED` | 执行失败，终态（可重试） |
| `CANCELED` | 被取消，终态（不可重试） |

### 3.3 输入输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `inputs` | `dict[str, Any]` | 执行输入参数 |
| `outputs` | `dict[str, Any]` | 执行产出数据（诊断结果、方案、指标等） |
| `current_task_id` | `str \| None` | 当前关联的任务标识 |

### 3.4 重试与错误

| 字段 | 类型 | 说明 |
|---|---|---|
| `retry_count` | `int` (ge=0) | 已重试次数 |
| `max_retries` | `int` (ge=0, default=2) | 最大重试次数 |
| `error` | `str \| None` | 错误信息（FAILED 状态必填） |

### 3.5 时间戳

| 字段 | 类型 | 说明 |
|---|---|---|
| `created_at` | `datetime` (tz-aware) | 创建时间 |
| `updated_at` | `datetime` (tz-aware) | 最后修改时间 |
| `started_at` | `datetime \| None` | 开始执行时间 |
| `finished_at` | `datetime \| None` | 结束时间 |

## 4. 状态转换规则

```python
ALLOWED_TRANSITIONS = {
    PLANNED:       → {QUEUED, CANCELED}
    QUEUED:        → {RUNNING, FAILED, CANCELED}
    RUNNING:       → {AWAITING_USER, PASSED, REJECTED, FAILED, CANCELED}
    AWAITING_USER: → {QUEUED, RUNNING, PASSED, REJECTED, CANCELED}
    PASSED:        → {}     # 终态
    REJECTED:      → {}     # 终态（通过 queue_retry 可回到 QUEUED）
    FAILED:        → {}     # 终态（通过 queue_retry 可回到 QUEUED）
    CANCELED:      → {}     # 终态，不可重试
}
```

**重试路径：** `REJECTED` / `FAILED` → `queue_retry()` → `QUEUED`（前提：`retry_count < max_retries`）

重试不修改原线程的历史，而是创建一个新的状态快照。

## 5. 不变式

### 5.1 角色一致
`role` 必须等于 `ROLE_BY_THREAD_TYPE[thread_type]`。

### 5.2 时间戳单调
`updated_at ≥ created_at`，`started_at ≥ created_at`，`finished_at ≥ started_at`。

### 5.3 时区强制
所有 datetime 字段必须 timezone-aware。

### 5.4 状态与时间戳联动
- `RUNNING` 必须有 `started_at`
- `PASSED` / `REJECTED` / `FAILED` / `CANCELED` 必须有 `finished_at`
- `FAILED` 必须有 `error`

### 5.5 重试上限
`retry_count ≤ max_retries`

## 6. 模型配置

```python
model_config = ConfigDict(
    extra="forbid",
    frozen=True,               # 不可变——状态变化通过 transition_to() 创建新实例
    str_strip_whitespace=True,
    use_enum_values=False,
)
```

`frozen=True` 使得线程是事实上的 append-only 日志。`transition_to()` 返回一个新 `ProjectThread` 实例（拷贝不修改），存储层负责原子替换旧文件。

## 7. 关键方法

### transition_to()

```python
def transition_to(self, new_status, *, at=None, error=None, outputs=None) -> ProjectThread
```

- 校验状态转换合法性
- 自动设置 started_at / finished_at
- 返回新实例

### queue_retry()

```python
def queue_retry(self, *, at=None, task_id=None) -> ProjectThread
```

- 仅 REJECTED / FAILED 可调用
- 递增 retry_count
- 清空 error、started_at、finished_at
- 返回 QUEUED 状态的新实例

## 8. 在流水线中的实例

```
Analyst 线程:  DIAGNOSIS → PLANNED → QUEUED → RUNNING → PASSED
               outputs = {scan, metrics, diagnosis}

Designer 线程: DESIGN → PLANNED → QUEUED → RUNNING → PASSED
               outputs = {treatment_plan_id, variant_count}

Worker 线程:   SPECTRUM → PLANNED → QUEUED → RUNNING → PASSED
               outputs = {version_id, output_audio, quality_gate_report}

Judge 线程:    JUDGE → PLANNED → QUEUED → RUNNING → PASSED/REJECTED
               outputs = {gate_results, recommendation, risk_flags}
```

## 9. 存储

线程以 `{project_id}/threads/{thread_id}.json` 存储。每次 `transition_to()` 调用后，由服务层调用 `store.update_thread(new_thread)` 原子替换文件。

## 10. 序列化示例

```json
{
  "schema_version": "project_thread.v1",
  "thread_id": "dx_a1b2c3d4e5f6",
  "project_id": "a1b2c3d4e5f6",
  "thread_type": "DIAGNOSIS",
  "role": "ANALYST",
  "status": "PASSED",
  "current_task_id": null,
  "inputs": {"source_path": "sources/instrumental_01.wav"},
  "outputs": {
    "scan": {"exists": true, "loudness_lufs": -21.0, ...},
    "metrics": {"duration_s": 131.5, ...},
    "diagnosis": {"overall_health": "fair", "issues": [...], ...}
  },
  "error": null,
  "retry_count": 0,
  "max_retries": 2,
  "created_at": "2026-07-25T10:00:00Z",
  "updated_at": "2026-07-25T10:01:30Z",
  "started_at": "2026-07-25T10:00:05Z",
  "finished_at": "2026-07-25T10:01:30Z"
}
```

## 11. 验收结论

- ✅ 6 角色 × 11 类型，分类覆盖 MVP 完整工作流
- ✅ 8 状态状态机 + 合法转换矩阵
- ✅ Frozen 模型 + transition_to() 保证 append-only 语义
- ✅ 内置重试机制（REJECTED/FAILED → queue_retry → QUEUED）
- ✅ 时间戳与状态一致性自动校验
- ✅ 通过 `ROLE_BY_THREAD_TYPE` 强制角色-类型绑定
