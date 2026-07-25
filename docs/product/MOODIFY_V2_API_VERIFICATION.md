# Moodify v2 — Workspace API 实现验证

**版本：API Verification 1.0**
**日期：2026-07-25**
**对应执行步骤：P0 / Step 12-16**
**实现文件：`api/routes/workspace_projects.py` (455 行)**

## Step 12 — 项目 CRUD API

| 端点 | 方法 | 行号 | 状态 |
|---|---|---|---|
| `/workspace/projects` | POST | 165-177 | ✅ 创建项目（201 Created） |
| `/workspace/projects/{id}` | GET | 180-185 | ✅ 读取项目 |
| `/workspace/projects/{id}` | PATCH | 188-202 | ✅ 部分更新项目（含 updated_at 自动刷新） |

**Pydantic 模型：** `WorkspaceProjectCreate`（6 字段）, `WorkspaceProjectPatch`（8 可选字段，含 patch_must_change_something validator）

## Step 13 — Brief API

| 端点 | 方法 | 行号 | 状态 |
|---|---|---|---|
| `/workspace/projects/{id}/brief` | POST | 205-222 | ✅ 首次创建 Brief（201，防重复） |
| `/workspace/projects/{id}/brief` | PATCH | 225-245 | ✅ 部分更新 Brief（防 null 字段） |

**Pydantic 模型：** `CreativeBriefPatch`（全部可选，含非空校验）

## Step 14 — 线程查询 API

| 端点 | 方法 | 行号 | 状态 |
|---|---|---|---|
| `/workspace/projects/{id}/threads` | GET | 248-253 | ✅ 按 workflow 顺序返回所有线程 |

## Step 15 — 版本 API

| 端点 | 方法 | 行号 | 状态 |
|---|---|---|---|
| `/workspace/projects/{id}/versions` | POST | 263-281 | ✅ 创建版本（含 cycle check + active 激活） |
| `/workspace/projects/{id}/versions` | GET | 284-289 | ✅ 列出版本（含环检测） |
| `/workspace/projects/{id}/versions/{vid}` | GET | 292-299 | ✅ 读取单个版本 |
| `/workspace/projects/{id}/versions/{vid}/branch` | POST | 302-329 | ✅ 分支新版本 |
| `/workspace/projects/{id}/versions/{vid}/rollback` | POST | 332-370 | ✅ 回退（复用目标版本的 audio_path + sha256） |

**Pydantic 模型：** `AudioVersionCreate`, `AudioVersionBranch`, `AudioVersionRollback`

## Step 16 — 审批 API

| 端点 | 方法 | 行号 | 状态 |
|---|---|---|---|
| `/workspace/projects/{id}/approve` | POST | 384-454 | ✅ 人工审批（Judge 前置检查 + 状态转换 + 追加 JSONL） |

**Pydantic 模型：** `ApprovalRequest`（9 字段）

**审批门禁逻辑（行 417-422）：**
- `outcome=APPROVED` 强制要求 Judge 线程 PASSED
- 若无 PASSED Judge 线程，拒绝批准（409 Conflict）

**事务性操作（行 429-451）：**
1. DRAFT → REVIEWING（如有需要）
2. REVIEWING → APPROVED / REJECTED
3. 追加 `approvals.jsonl`
4. 更新 `version.json`
5. 更新 `project.json`（active + approved + status）

## 错误处理体系

统一的 `_storage_error()` 映射（行 144-162）：

| 异常 | HTTP 状态码 |
|---|---|
| `StorageNotFound` | 404 |
| `StorageConflict` | 409 |
| `StorageCorruption` | 500 |
| `ValidationError` | 422 |
| `ValueError` | 400 |
| other | 500 |

## 结论

5 个 API 组（Project / Brief / Thread / Version / Approval），共 11 个端点，全部已实现。Pydantic 模型覆盖了所有请求/响应 schema，错误映射完整。
