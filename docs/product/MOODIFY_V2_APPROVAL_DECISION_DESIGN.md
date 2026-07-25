# Moodify v2 — ApprovalDecision 设计文档

**版本：ApprovalDecision Design 1.0**
**日期：2026-07-25**
**对应执行步骤：P0 / Step 10**
**实现文件：`domain/approval.py`**

## 1. 定位

`ApprovalDecision` 是追加式的不可变人工审批证据。它绑定到一个确切的 `AudioVersion`，记录谁、何时、基于什么理由做出了什么决定。它是 Final 归档前的最后一道**人控门禁**。

核心原则：**没有人工 ApprovalDecision 的版本不得标记为 Final。**

## 2. 字段设计

| 字段 | 类型 | 说明 |
|---|---|---|
| `schema_version` | `Literal["approval_decision.v1"]` | 版本路由 |
| `decision_id` | `str` | 决策唯一 ID |
| `project_id` | `str` | 所属项目 |
| `version_id` | `str` | 被审批的版本 |
| `outcome` | `ApprovalOutcome` | 审批结果 |
| `reason` | `str` (min_length=1) | 审批理由 |
| `operator` | `str` (min_length=1) | 操作者标识 |
| `actor_type` | `ApprovalActorType` | 操作者类型 |
| `return_to_thread` | `ThreadType \| None` | 退回目标（仅 RETURNED） |
| `supersedes_decision_id` | `str \| None` | 替代的旧决策 ID |
| `decided_at` | `datetime` (tz-aware) | 决策时间 |

## 3. 枚举定义

### ApprovalOutcome

| 值 | 含义 | 对版本的影响 |
|---|---|---|
| `APPROVED` | 批准 | 版本可进入 DELIVERED |
| `REJECTED` | 拒绝 | 版本标记为 REJECTED，不可进入 Final |
| `RETURNED` | 退回修改 | 版本标记为 REJECTED，指定退回线程 |

### ApprovalActorType

| 值 | 含义 |
|---|---|
| `HUMAN` | 人工决策（APPROVED 必须由 HUMAN 做出） |
| `SYSTEM` | 系统自动决策（如超时自动退回） |

## 4. 不变式

### 4.1 人工批准
`outcome == APPROVED` 时，`actor_type` 必须是 `HUMAN`。系统不能代行最终批准。

### 4.2 退回必须指定线程
`outcome == RETURNED` 时，`return_to_thread` 必填（指明退回到哪个处理线程重做）。

### 4.3 非退回不设 return_to_thread
`outcome != RETURNED` 时，`return_to_thread` 必须为 None。

### 4.4 不可自我替代
`supersedes_decision_id ≠ decision_id`

### 4.5 时间戳时区
`decided_at` 必须 timezone-aware。

## 5. 模型配置

```python
model_config = ConfigDict(
    extra="forbid",
    frozen=True,               # 不可变——审批一旦做出不可修改
    str_strip_whitespace=True,
    use_enum_values=False,
)
```

**frozen=True 的设计意图：** 审批决策是法律/审计级别的记录。即便管理员也不能修改已做出的决定。撤回或变更通过创建新决策并设置 `supersedes_decision_id` 指向旧决策来实现。

## 6. 存储

审批以 **JSONL（JSON Lines）追加式**存储：

```
{project_id}/approvals.jsonl
```

每行一个 ApprovalDecision。`WorkspaceStore.append_approval()` 保证：
- 原子追加（不会写坏已有行）
- 拒绝重复 decision_id
- 读取时逐行验证

## 7. 与流水线的交互

```
Worker → AudioVersion(DRAFT)
  → Judge 线程 → RUNNING → PASSED/REJECTED
    → (PASSED) AudioVersion(REVIEWING)
      → 人工审查 → ApprovalDecision
        ├── APPROVED → AudioVersion(APPROVED) → DELIVERED → Final
        ├── REJECTED → AudioVersion(REJECTED) → 终止
        └── RETURNED → AudioVersion(REJECTED) + return_to_thread=
              ThreadType.SPECTRUM → Worker 重新处理 → 新 AudioVersion
```

## 8. 序列化示例

```json
// APPROVED
{
  "schema_version": "approval_decision.v1",
  "decision_id": "dec_20260725_001",
  "project_id": "a1b2c3d4e5f6",
  "version_id": "v_a1b2c3d4e5f6_001",
  "outcome": "APPROVED",
  "reason": "Warm tone preserved; all quality gates green; stereo image intact",
  "operator": "audio_engineer_01",
  "actor_type": "HUMAN",
  "return_to_thread": null,
  "supersedes_decision_id": null,
  "decided_at": "2026-07-25T14:00:00Z"
}

// RETURNED
{
  "schema_version": "approval_decision.v1",
  "decision_id": "dec_20260725_002",
  "project_id": "a1b2c3d4e5f6",
  "version_id": "v_a1b2c3d4e5f6_002",
  "outcome": "RETURNED",
  "reason": "Vocal too compressed; dynamic range below threshold",
  "operator": "audio_engineer_01",
  "actor_type": "HUMAN",
  "return_to_thread": "SPECTRUM",
  "supersedes_decision_id": null,
  "decided_at": "2026-07-25T14:30:00Z"
}

// Supersedes (覆盖旧决定)
{
  ...
  "outcome": "APPROVED",
  "supersedes_decision_id": "dec_20260725_002",
  ...
}
```

## 9. 验收结论

- ✅ 3 种审批结果：APPROVED / REJECTED / RETURNED
- ✅ HUMAN 强制：最终批准必须由人做出
- ✅ RETURNED 带退回线程类型，支持自动化重试
- ✅ supersedes 支持决策变更的完整审计链
- ✅ Frozen 不可变 + 追加式 JSONL 存储
- ✅ 与 AudioVersion 的状态联动（APPROVED/REJECTED 必须带审批证据）
- ✅ 与 Judge 线程串联形成完整质量门禁链
