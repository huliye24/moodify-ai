# Moodify v2 — AudioVersion 设计文档

**版本：AudioVersion Design 1.0**
**日期：2026-07-25**
**对应执行步骤：P0 / Step 9**
**实现文件：`domain/audio_version.py`**

## 1. 定位

`AudioVersion` 是版本树中**不可变节点**。每个版本对应一个唯一的音频文件，其音频本体、血统（parent）、处理参数一旦写入就永远不可覆盖。回退、分支、重试都通过创建新版本实现。

## 2. 字段设计

### 2.1 标识与归属

| 字段 | 类型 | 说明 |
|---|---|---|
| `schema_version` | `Literal["audio_version.v1"]` | 版本路由 |
| `version_id` | `str` | 全局唯一 |
| `project_id` | `str` | 所属项目 |

### 2.2 版本树

| 字段 | 类型 | 说明 |
|---|---|---|
| `parent_version_id` | `str \| None` | 父版本 ID（根版本为 None） |
| `branch` | `str` (default="main", regex 校验) | 分支名，如 "main"、"experiment/eq_boost" |

**分支规则：** 仅允许 `[a-z0-9][a-z0-9._/-]*`，禁止 `..` 目录遍历。

### 2.3 版本元数据

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | `str` | 人类可读名称，如 "Natural Repair A — Candidate 1" |
| `purpose` | `str` | 创建原因，如 "Experiment with brighter EQ per Designer rec" |
| `created_by` | `str` | 创建者标识（Worker 线程 ID 或用户名） |

### 2.4 音频身份（不可变区）

| 字段 | 类型 | 说明 |
|---|---|---|
| `audio_path` | `str` | 相对路径，必须在 `versions/` 下，仅支持 `.wav/.flac/.aif/.aiff` |
| `audio_sha256` | `str` (64 hex) | 音频文件 SHA-256 哈希——**音频身份的核心证明** |

**路径校验：**
- 相对路径（不可绝对）
- 不以 `..` 穿越目录
- 第一段必须是 `versions/`
- 后缀必须是无损格式

### 2.5 处理追溯

| 字段 | 类型 | 说明 |
|---|---|---|
| `treatment_plan_id` | `str \| None` | 关联的 TreatmentPlan |
| `treatment_variant_id` | `str \| None` | 关联的变体（A/B/C 之一） |
| `treatment_record_id` | `str \| None` | 实际使用的处理参数记录 |

**约束：** `treatment_plan_id` 和 `treatment_variant_id` 必须同时出现或同时为 None。

### 2.6 状态与审批

| 字段 | 类型 | 说明 |
|---|---|---|
| `status` | `VersionStatus` | 生命周期状态 |
| `approval` | `ApprovalDecision \| None` | 审批决策（REJECTED/APPROVED/DELIVERED 必填） |

### 2.7 时间戳

| 字段 | 类型 | 说明 |
|---|---|---|
| `created_at` | `datetime` (tz-aware) | 创建时间 |
| `updated_at` | `datetime` (tz-aware) | 最后修改时间 |

## 3. VersionStatus 生命周期

```
DRAFT → REVIEWING → APPROVED → DELIVERED → ARCHIVED
                ↘ REJECTED → ARCHIVED
```

| 状态 | 允许转换到 | 含义 |
|---|---|---|
| `DRAFT` | REVIEWING, ARCHIVED | 新完成，等待审查 |
| `REVIEWING` | REJECTED, APPROVED, ARCHIVED | 审查中 |
| `REJECTED` | ARCHIVED | 审查不通过 |
| `APPROVED` | DELIVERED, ARCHIVED | 人工批准 |
| `DELIVERED` | ARCHIVED | 已交付 |
| `ARCHIVED` | (终态) | 已归档 |

## 4. 不变式

### 4.1 不可自引用
`parent_version_id ≠ version_id`

### 4.2 时间单调
`updated_at ≥ created_at`

### 4.3 审批证据强制
- `REJECTED` / `APPROVED` / `DELIVERED` 状态必须携带 `approval`
- `APPROVED` / `DELIVERED` 要求 `approval.outcome == APPROVED`
- `REJECTED` 要求 `approval.outcome in {REJECTED, RETURNED}`

### 4.4 审批一致性
- `approval.project_id == version.project_id`
- `approval.version_id == version.version_id`
- `approval.decided_at ≥ version.created_at`

### 4.5 处理追溯成对
`treatment_plan_id` 和 `treatment_variant_id` 必须成对出现

## 5. 模型配置

```python
model_config = ConfigDict(
    extra="forbid",
    frozen=True,               # 不可变
    str_strip_whitespace=True,
    use_enum_values=False,
)
```

`transition_to()` 方法创建新状态快照，**不修改原实例**。

## 6. 关键方法

### transition_to()

```python
def transition_to(self, new_status, *, at=None, approval=None) -> AudioVersion
```

- 校验状态转换合法性
- 可选附带 ApprovalDecision
- 返回新实例

## 7. 版本重试/回退语义

```
v1 (DRAFT → REVIEWING → REJECTED, branch=main)
  └── v2 (DRAFT → ..., parent=v1, branch=main, purpose="retry v1 with adjusted EQ")
          └── v3 (DRAFT → ..., parent=v2, branch=experiment/wider_stereo)
```

- **重试** = `parent_version_id` 指向被拒绝/失败的版本，新建 DRAFT
- **分支** = `branch` 不同，从任意父节点分叉
- **回退** = 创建一个 parent 指向旧版本的新版本（音频内容指向旧音频）
- **不可覆盖** = 已有版本的 `audio_path` 和 `audio_sha256` 一旦写入不可修改（`update_version()` 强校验）

## 8. 存储

- 元数据：`{project_id}/versions/{version_id}.json`
- 音频文件：`{project_id}/versions/{version_id}.wav`
- `stage_version_audio()` 使用原子写入（tmpfile → os.replace），计算 SHA-256 并返回

## 9. 序列化示例

```json
{
  "schema_version": "audio_version.v1",
  "version_id": "v_a1b2c3d4e5f6_001",
  "project_id": "a1b2c3d4e5f6",
  "parent_version_id": null,
  "branch": "main",
  "name": "Natural Repair A — First Candidate",
  "purpose": "Initial processing of instrumental stem with conservative EQ",
  "audio_path": "versions/v_a1b2c3d4e5f6_001.wav",
  "audio_sha256": "848444acf8c1b1da1a7a5c2e1831e568609d61ca6008369421a7c7f0cb09786b",
  "status": "APPROVED",
  "treatment_plan_id": "tp_a1b2c3d4e5f6",
  "treatment_variant_id": "tp_a1b2c3d4e5f6_A",
  "treatment_record_id": "tr_a1b2c3d4e5f6",
  "created_by": "worker_instrumental_clean",
  "approval": {
    "decision_id": "dec_001",
    "project_id": "a1b2c3d4e5f6",
    "version_id": "v_a1b2c3d4e5f6_001",
    "outcome": "APPROVED",
    "reason": "Meets all quality gates; warm tone preserved",
    "operator": "audio_engineer_01",
    "actor_type": "HUMAN",
    "decided_at": "2026-07-25T14:00:00Z"
  },
  "created_at": "2026-07-25T10:10:00Z",
  "updated_at": "2026-07-25T14:00:00Z"
}
```

## 10. 验收结论

- ✅ 版本树：parent + branch 支持分支和回退
- ✅ 不可变身份：audio_path + audio_sha256 一旦写入不可修改
- ✅ 6 状态生命周期：DRAFT → REVIEWING → APPROVED/DELIVERED/REJECTED → ARCHIVED
- ✅ 审批绑定：终态版本必须携带 ApprovalDecision
- ✅ 处理追溯：treatment_plan_id + variant_id 可追溯到具体 Plan
- ✅ 原子存储：音频文件通过 tmpfile → os.replace 保证写入安全
- ✅ Frozen 模型：transition_to() 创建新实例，不修改历史
