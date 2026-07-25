# Moodify v2 — AudioProject 设计文档

**版本：AudioProject Design 1.0**
**日期：2026-07-25**
**对应执行步骤：P0 / Step 5**
**实现文件：`domain/project.py`**

## 1. 定位

`AudioProject` 是 Moodify Workspace v2 的**核心聚合根**。一切操作——诊断、设计、处理、审查、审批、归档——都以它作为入口和上下文边界。

一个 `AudioProject` 代表一首歌的完整工艺历史。

## 2. 字段设计

### 2.1 标识与元数据

| 字段 | 类型 | 说明 |
|---|---|---|
| `schema_version` | `Literal["audio_project.v1"]` | 用于跨版本反序列化路由 |
| `project_id` | `str` (min_length=1) | 全局唯一标识，推荐 `SHA-256[:12]` 或结构化 ID |
| `title` | `str` (min_length=1) | 人类可读项目名 |
| `created_at` | `datetime` (tz-aware) | 创建时间 |
| `updated_at` | `datetime` (tz-aware) | 最后修改时间 |

### 2.2 状态

| 字段 | 类型 | 说明 |
|---|---|---|
| `status` | `ProjectStatus` | 生命周期状态，见下方状态机 |

**ProjectStatus 枚举（10 个状态）：**

```
CREATED → BRIEFING → ANALYZING → DESIGNING → PROCESSING → REVIEWING → AWAITING_USER → APPROVED → DELIVERED → ARCHIVED
                                                                                          ↓
                                                                                       FAILED
```

| 状态 | 含义 | 触发条件 |
|---|---|---|
| `CREATED` | 项目已创建，等待 Brief | 初始状态 |
| `BRIEFING` | 正在填写/编辑 Brief | 开始编辑 Brief |
| `ANALYZING` | 正在执行音频诊断 | Analyst 线程启动 |
| `DESIGNING` | 正在生成 Treatment Plan | Designer 线程启动 |
| `PROCESSING` | 正在执行 DSP 处理 | Worker 线程启动 |
| `REVIEWING` | Judge 正在进行质量审查 | Judge 线程启动 |
| `AWAITING_USER` | 等待人工审批 | Judge 通过，等待人操作 |
| `APPROVED` | 人工已批准 | ApprovalDecision.outcome=APPROVED |
| `DELIVERED` | 已生成交付物 | Archive 线程完成 |
| `ARCHIVED` | 项目归档，只读 | 显式归档操作 |
| `FAILED` | 工作流失败 | 不可恢复的错误 |

### 2.3 源音频

| 字段 | 类型 | 说明 |
|---|---|---|
| `source_audio_ids` | `list[str]` (min_length=1) | 源音频文件 ID 列表，对应 `sources/` 目录下的文件名 |

**约束：** 元素必须非空、无重复。

### 2.4 Creative Brief

| 字段 | 类型 | 说明 |
|---|---|---|
| `creative_brief` | `CreativeBrief \| None` | 可选的创意简报。项目创建时可为 None，BRIEFING 阶段填写 |

### 2.5 版本追踪

| 字段 | 类型 | 说明 |
|---|---|---|
| `active_version_id` | `str \| None` | 当前活跃版本的 ID（用于 UI 和 API 的默认版本上下文） |
| `approved_version_id` | `str \| None` | 已获人工批准的版本 ID |
| `delivered_version_id` | `str \| None` | 已完成交付的版本 ID |

### 2.6 旧系统追溯

| 字段 | 类型 | 说明 |
|---|---|---|
| `legacy_refs` | `list[LegacyReference]` | 可选的旧系统引用，支持从 v0.1 迁移时保留来源追溯 |

**LegacyReference 结构：**

| 字段 | 类型 | 说明 |
|---|---|---|
| `source_type` | `str` | 旧系统类型，如 `"v01_report"` |
| `legacy_id` | `str` | 旧系统中的唯一 ID |
| `source_path` | `str \| None` | 旧文件路径 |
| `source_hash` | `str \| None` | 旧文件 SHA-256 |
| `migration_key` | property | `"source_type:legacy_id:source_hash"` — 幂等迁移键 |

### 2.7 扩展预留

| 字段 | 类型 | 说明 |
|---|---|---|
| `commercial_project_id` | `str \| None` | 未来对接商业化系统的项目 ID |
| `privacy_policy` | `dict[str, Any]` | 未来权限/隐私策略配置 |

## 3. 不变式（Pydantic Validators）

### 3.1 source_audio_ids 唯一
所有 ID 去空白后必须非空且无重复。

### 3.2 时间戳必须带时区
`created_at` 和 `updated_at` 必须为 timezone-aware datetime，防止跨时区排序错误。

### 3.3 updated_at ≥ created_at
防止时钟回拨导致的非法状态。

### 3.4 终态必须已审批
`APPROVED`、`DELIVERED`、`ARCHIVED` 状态必须设置 `approved_version_id`。

### 3.5 DELIVERED 一致性
`DELIVERED` 状态要求 `delivered_version_id == approved_version_id`。

## 4. 模型配置

```python
model_config = ConfigDict(
    extra="forbid",              # 拒绝未定义字段
    str_strip_whitespace=True,   # 自动去除字符串空白
    validate_assignment=True,    # 属性赋值时也触发验证
    use_enum_values=False,       # 序列化使用枚举成员名
)
```

`validate_assignment=True` 确保即便是局部更新（PATCH API）也不会绕过验证。

## 5. 生命周期与状态转换

```
               ┌─────────────────────────────────────────┐
               │                                         │
  CREATED → BRIEFING → ANALYZING → DESIGNING → PROCESSING
                                                  │
                                                  ▼
              ARCHIVED ← DELIVERED ← APPROVED ← REVIEWING
                  ▲                       │
                  │         AWAITING_USER │
                  │              ▲        │
                  │              │        │
                  └──── FAILED ──┴────────┘
```

状态转换由 `ProjectWorkflow`（`domain/workflow.py`）管理，不直接在 `AudioProject` 上实现。`AudioProject.status` 是 `ProjectWorkflow.stage` 的快照投影，由服务层保持同步。

## 6. 与相关模型的关系

```
AudioProject ──1:1── CreativeBrief
             ──1:N── ProjectThread[]
             ──1:N── AudioVersion[]
             ──1:1── ProjectWorkflow
             ──1:N── LegacyReference[]
```

- **CreativeBrief** — 内嵌值对象（可空），随 Project 的 PATCH 一起更新
- **ProjectThread** — 独立实体，通过 `project_id` 外键关联
- **AudioVersion** — 独立实体，通过 `project_id` 外键关联，`active/approved/delivered_version_id` 指向具体版本
- **ProjectWorkflow** — 独立状态机，通过 `project_id` 关联
- **LegacyReference** — 内嵌值对象列表，用于迁移追溯

## 7. 序列化示例

```json
{
  "schema_version": "audio_project.v1",
  "project_id": "a1b2c3d4e5f6",
  "title": "J'apprends à te recevoir maladroitement",
  "status": "BRIEFING",
  "source_audio_ids": ["instrumental_01", "vocals_01"],
  "creative_brief": {
    "schema_version": "creative_brief.v1",
    "goal": "Warm intimate mix for streaming",
    "preserve": ["emotional phrasing", "natural dynamics"],
    "avoid": ["harsh highs", "clipping"],
    "platform": "streaming",
    "reference": []
  },
  "active_version_id": null,
  "approved_version_id": null,
  "delivered_version_id": null,
  "commercial_project_id": null,
  "legacy_refs": [],
  "privacy_policy": {},
  "created_at": "2026-07-25T10:00:00Z",
  "updated_at": "2026-07-25T10:00:00Z"
}
```

## 8. 验收结论

- ✅ 模型定义完整：16 个字段 + 2 个内嵌类型（ProjectStatus, LegacyReference）
- ✅ 不通过验证：5 组 Pydantic validators 覆盖 ID、时间戳、状态一致性
- ✅ 可序列化：`model_dump(mode="json")` 输出标准 JSON，可直接写入 WorkspaceStore
- ✅ 向后兼容：`legacy_refs` 支持 v0.1 迁移追溯
- ✅ 向前扩展：`commercial_project_id` 和 `privacy_policy` 预留 Phase 2/3
