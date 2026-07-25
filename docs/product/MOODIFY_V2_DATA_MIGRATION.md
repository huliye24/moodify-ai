# Moodify v2 — 数据迁移策略

**版本：Data Migration 1.0**
**日期：2026-07-25**
**对应执行步骤：P0 / Step 4**

## 1. 迁移目标

将现有 v0.1 处理产物（`pre-music/` 下的 JSON 报告）映射为 v2 Workspace 存储格式，实现"旧数据可读、新字段可扩展"。

## 2. 源数据盘点

### 2.1 目录结构

```
pre-music/
├── outputs/                          # 旧全轨处理报告（约 17 首）
│   └── {song_name}_{preset}_report.json
├── 2026-07-24_1441_split_by_lalalai/ # 首个验收样本（分轨处理）
│   ├── {song}_no_vocals_split_by_lalalai.wav
│   ├── {song}_vocals_split_by_lalalai.wav
│   └── moodify_post_v1/
│       ├── instrumental/
│       │   └── {song}_clean_master_report.json
│       ├── vocals_corrected/
│       │   └── {song}_warm_vocal_report.json
│       └── Japprends_...delivery_-14LUFS_v1.wav
└── 2026-07-24_1441_split_by_lalalai/ # 另一次运行...
```

### 2.2 旧 JSON 报告结构（v0.1）

每个旧 JSON 报告包含以下顶级键：

| 键 | 类型 | 可迁移到 |
|---|---|---|
| `scan` | `ScanResult` dict | `ProjectThread`(DIAGNOSIS).outputs |
| `feature_analysis` | `AudioMetrics` dict | `ProjectThread`(DIAGNOSIS).outputs |
| `diagnosis` | `DiagnosisReport` dict | `ProjectThread`(DIAGNOSIS).outputs |
| `quality_gate` | `QualityGate` dict | `ProjectThread`(JUDGE).outputs |
| `delivery` | `DeliveryBundle` dict | `AudioVersion` + Archive 线程输出 |
| `preset` / `requested_preset` | string | `TreatmentPlan.variants[].actions[]` |
| `stage_timings` | dict | `ProjectThread` metadata |
| `workflow` | list[string] | 结构信息，仅日志 |
| `elapsed_s` | float | `ProjectThread` metadata |

### 2.3 验收样本注册表

`data/workspace_v2/acceptance_samples/registry.jsonl` — 1 条记录，JSONL 格式。

## 3. 映射规则

### 3.1 旧报告 → AudioProject

```python
AudioProject(
    project_id=derive_project_id(old_report),      # SHA-256 前 12 位 或 人工指定
    title=extract_title_from_path(old_report),
    status=ProjectStatus.ARCHIVED,                  # 旧数据一律标记为 ARCHIVED
    source_audio_ids=[derive_audio_id(path)],
    creative_brief=None,                            # 旧报告无 Brief，事后补
    legacy_refs=[
        LegacyReference(
            source_type="v01_report",
            legacy_id=old_report_path.stem,
            source_path=str(old_report_path),
            source_hash=sha256(old_report_path),
        )
    ],
)
```

### 3.2 旧报告 → ProjectThread

每份旧报告生成 3 个线程：

| 线程 | ThreadType | 来源 |
|---|---|---|
| Diagnosis 线程 | `DIAGNOSIS` | `scan` + `feature_analysis` + `diagnosis` |
| Process 线程 | `SPECTRUM` (或按 preset 推断) | `preset` + `stage_timings` |
| Judge 线程 | `JUDGE` | `quality_gate` |

所有旧线程状态设为 `PASSED`（终态），`retry_count=0`。

### 3.3 旧报告 → AudioVersion

```python
AudioVersion(
    version_id=derive_version_id(old_report, "v1"),
    project_id=project.project_id,
    parent_version_id=None,                         # 旧报告无版本血缘
    branch="main",
    name=f"{preset}_baseline",
    purpose="migrated from v0.1 report",
    audio_path=f"versions/{version_id}.wav",
    audio_sha256=delivery["sha256"] if present else placeholder,
    status=VersionStatus.ARCHIVED,
    treatment_plan_id=None,                         # 旧报告无 TreatmentPlan
    created_by="migration/v01",
)
```

### 3.4 旧报告 → TreatmentPlan

旧报告没有 TreatmentPlan 概念。迁移时可选生成一个占位 Plan：

```python
TreatmentPlan(
    plan_id=f"migration_{project_id}_v1",
    project_id=project.project_id,
    brief_revision=0,                               # 标记"无 Brief"
    diagnosis_id=diagnosis_thread.thread_id,
    variants=[TreatmentVariant(
        variant_id=f"migration_{project_id}_A",
        label="A",
        name=f"Legacy {preset}",
        objective="Migrated from v0.1 processing",
        problems=diagnosis["issues"],
        actions=[...],                               # 从 preset 反推
        risks=quality_gate["risk_flags"],
    )],
)
```

### 3.5 旧报告 → ApprovalDecision（不生成）

旧报告没有人工审批记录。迁移后 `AudioVersion.approval = None`。

## 4. 迁移流程

### 第一阶段：扫描注册

1. 遍历 `pre-music/`，收集所有 `*_report.json`
2. 对每个报告计算 SHA-256 哈希
3. 生成 `migration_manifest.jsonl`（一个报告一行）

### 第二阶段：逐条迁移

对 manifest 中的每条记录：

1. **去重检查** — 按 `LegacyReference.migration_key` 检查是否已迁移
2. **创建 AudioProject** — 原子写入 `project.json`
3. **导入源音频** — 从旧路径复制/软链接到 `sources/`
4. **创建线程** — 写入 `threads/{id}.json` × 3
5. **创建 TreatmentPlan** — 可选，写入 `plans/{id}.json`
6. **导入音频产物** — 从旧路径复制到 `versions/{id}.wav`
7. **创建 AudioVersion** — 写入 `versions/{id}.json`
8. **创建 ProjectWorkflow** — 写入 `workflow.json`（状态 FINAL）
9. **追加 ApprovalDecision** — 仅当旧报告含人工确认记录时

### 迁移脚本接口

```python
class V01Migration:
    """Read v0.1 reports and write v2 workspace records."""

    def __init__(self, store: WorkspaceStore, dry_run: bool = True): ...

    def scan_reports(self, root: Path) -> list[dict]:
        """Return migration manifest entries."""

    def migrate_one(self, report_path: Path) -> list[str]:
        """Migrate one report; return list of created entity IDs."""

    def migrate_all(self, root: Path) -> dict:
        """Migrate all v0.1 reports; return summary counts."""

    def verify(self, project_id: str) -> bool:
        """Check a migrated project's integrity."""
```

## 5. 目标存储布局

迁移后，每个旧报告生成一个项目目录：

```
{workspace_root}/
└── projects/
    └── {project_id}/
        ├── project.json          # AudioProject
        ├── workflow.json         # ProjectWorkflow (stage=FINAL)
        ├── sources/
        │   └── {audio_id}.wav   # 从旧路径复制/链接
        ├── diagnostics/
        │   └── {thread_id}/
        ├── processing/
        │   └── {thread_id}/
        ├── threads/
        │   ├── {diagnosis_thread_id}.json
        │   ├── {process_thread_id}.json
        │   └── {judge_thread_id}.json
        ├── plans/
        │   └── {plan_id}.json
        ├── versions/
        │   ├── {version_id}.json
        │   └── {version_id}.wav
        └── approvals.jsonl       # 空，或含人工记录
```

## 6. 边界与约束

### 不迁移的内容
- 旧 PDF 报告、频谱 PNG（路径登记入 LegacyReference，文件保留原位）
- 失败的旧运行（`success=false` 的报告跳过）
- 旧 calibration/experiment 数据（属于科学实验路径，不进入 Workspace）

### 兼容性保证
- 旧 `pre-music/` 目录不做任何修改——迁移是纯读取+写入新位置
- 旧 `/operator/*` 和 `/studio/*` API 继续使用原有数据路径
- 新旧数据共存，通过 `LegacyReference` 互相引用

### 幂等性
- `migration_key = f"{source_type}:{legacy_id}:{source_hash}"` 保证同一条旧报告只迁移一次
- 重复运行 `migrate_all()` 安全——已存在的 `project_id` 跳过

### 数据完整性验证

迁移后对每个项目执行：

1. `project.json` 可反序列化为 `AudioProject`
2. `workflow.json` 可反序列化为 `ProjectWorkflow`，stage 为 FINAL 或 FAILED
3. 所有 `threads/*.json` 可反序列化，`project_id` 匹配
4. 所有 `versions/*.json` 可反序列化，`audio_sha256` 匹配实际文件哈希
5. `versions/{id}.wav` 文件存在且可读
6. `LegacyReference.source_path` 指向的文件存在
7. 版本树无环

## 7. ID 派生规则

```python
def derive_project_id(report_path: Path) -> str:
    """SHA-256 前 12 位 hex，保证唯一和可排序."""
    return hashlib.sha256(str(report_path).encode()).hexdigest()[:12]

def derive_thread_id(project_id: str, role: str) -> str:
    return f"{project_id}_{role.lower()}_migration"

def derive_version_id(project_id: str, variant: str) -> str:
    return f"{project_id}_{variant}"
```

## 8. 迁移脚本位置

- 迁移逻辑：`moodify-core-package/src/moodify/storage/migration.py`
- Manifest 输出：`data/workspace_v2/migrations/migration_manifest.jsonl`
- 迁移日志：`data/workspace_v2/migrations/migration.log`

## 9. 验收标准

- [ ] 可扫描 `pre-music/` 下所有有效 v0.1 报告，生成完整 manifest
- [ ] 单条迁移可通过所有 7 项完整性检查
- [ ] 批量迁移全部报告，无报错
- [ ] 重复迁移幂等，不产生重复项目
- [ ] 迁移后所有旧报告对应的源文件路径可访问
- [ ] `WorkspaceStore.list_ids()` 返回预期数量的项目
- [ ] 旧 `pre-music/` 目录未被修改
