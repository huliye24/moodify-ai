# Moodify v2 — WorkspaceStore 实现验证

**版本：Store Verification 1.0**
**日期：2026-07-25**
**对应执行步骤：P0 / Step 11**
**实现文件：`storage/workspace_store.py` (385 行)**

## 验收清单

| # | 验收项 | 状态 | 证据 |
|---|---|---|---|
| 1 | Project CRUD (create/get/update) | ✅ | `create_project` + `get_project` + `update_project` |
| 2 | Thread CRUD (create/get/update/list) | ✅ | `create_thread` + `get_thread` + `update_thread` + `list_threads` (按 workflow 顺序排序) |
| 3 | Plan CRUD (create/get/list) | ✅ | `create_plan` + `get_plan` + `list_ids` |
| 4 | Version CRUD+检查 (create/get/update/list/create_checked) | ✅ | `create_version` + `get_version` + `update_version`(不可变字段保护) + `list_versions`(环检测) + `create_version_checked` |
| 5 | Approval 追加式写入 (append/list) | ✅ | `append_approval`(去重+JSONL追加) + `list_approvals` |
| 6 | Workflow CRUD | ✅ | `create_workflow` + `get_workflow` + `update_workflow` |
| 7 | 源音频解析 | ✅ | `resolve_source_audio`(精确+模糊+歧义检测) |
| 8 | 输出目录管理 | ✅ | `diagnostic_output_dir` + `processing_output_dir` |
| 9 | 版本音频暂存(原子+哈希) | ✅ | `stage_version_audio`(tmpfile→os.replace+SHA-256) |
| 10 | 原子写入 | ✅ | `_atomic_write_json` + `_atomic_write_jsonl` + `_atomic_replace`(mkstemp+fsync+os.replace) |
| 11 | 崩溃安全 | ✅ | 所有写入通过 tmpfile→fsync→rename 路径 |
| 12 | ID 安全校验 | ✅ | `_SAFE_ID` 正则防路径遍历 |
| 13 | 项目隔离 | ✅ | `{root}/projects/{project_id}/` 独立目录 |
| 14 | JSONL 读写 | ✅ | `_read_jsonl` + `_atomic_write_jsonl` |
| 15 | 版本树环检测 | ✅ | `_validate_version_parent_chain` (parent 链遍历+seen set) |
| 16 | 版本不可变字段保护 | ✅ | `update_version` 中 14 个字段一一校验 |
| 17 | Workflow 身份不可变 | ✅ | `update_workflow` 校验 `created_at` 不变 |
| 18 | 异常语义化 | ✅ | `StorageNotFound` / `StorageConflict` / `StorageCorruption` 三类异常 |

## 存储布局

```
{root}/projects/{project_id}/
├── project.json
├── workflow.json
├── sources/
├── diagnostics/{thread_id}/
├── processing/{thread_id}/
├── threads/{thread_id}.json
├── plans/{plan_id}.json
├── versions/
│   ├── {version_id}.json
│   └── {version_id}.wav
└── approvals.jsonl
```

## 结论

385 行代码覆盖全部 18 项验收要求，CRUD + 异常恢复全部通过。
