# Moodify Studio Workspace v2 — 运行手册

## 1. 启动

### 环境变量
```bash
export MOODIFY_WORKSPACE_ROOT=data/workspace_v2
```

### 启动 API 服务
```bash
cd moodify-core-package
python -m uvicorn moodify.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 访问 UI
浏览器打开: `http://localhost:8000/workspace/projects/ui`

---

## 2. 创建项目 (黄金路径)

### 2.1 准备源音频
```bash
mkdir -p data/workspace_v2/projects/{PROJECT_ID}/sources
cp your_audio.wav data/workspace_v2/projects/{PROJECT_ID}/sources/{SOURCE_ID}.wav
```

### 2.2 创建项目
```bash
curl -X POST http://localhost:8000/workspace/projects \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "WS_001",
    "title": "My First Project",
    "source_audio_ids": ["source_01"]
  }'
```

### 2.3 创建 Creative Brief
```bash
curl -X POST http://localhost:8000/workspace/projects/WS_001/brief \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Warm acoustic master for streaming",
    "preserve": ["vocal presence", "dynamic range"],
    "avoid": ["harshness", "over-compression"],
    "platform": "streaming",
    "reference": ["ref_warm_master"]
  }'
```

### 2.4 运行处理流水线
通过服务层执行或 API 逐步推进:
1. Analyst 分析 → 产生 DIAGNOSIS 线程
2. Designer 设计 → 产生 TreatmentPlan
3. DSP Worker 处理 → 产生 AudioVersion
4. Judge 评判 → 通过后进入 APPROVAL
5. 人工审批 → 通过 API 提交审批决定
6. 归档 → ArchiveService 生成归档清单

### 2.5 人工审批
```bash
curl -X POST http://localhost:8000/workspace/projects/WS_001/approve \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "DEC_001",
    "version_id": "WS_001_v001",
    "outcome": "APPROVED",
    "reason": "Quality gates passed, ready for delivery",
    "operator": "Producer Name",
    "actor_type": "HUMAN"
  }'
```

---

## 3. 恢复任务

### 3.1 检查项目状态
```bash
curl http://localhost:8000/workspace/projects/WS_001 | jq .status
```

### 3.2 查看工作流阶段
```bash
# 通过线程列表判断当前阶段
curl http://localhost:8000/workspace/projects/WS_001/threads | jq '.[] | {type: .thread_type, status: .status}'
```

### 3.3 重试失败任务
```python
from moodify.services.retry import RetryOrchestrator
from moodify.storage import WorkspaceStore

store = WorkspaceStore("data/workspace_v2")
orch = RetryOrchestrator(store)

# 自动检测并重试
result = orch.handle_workflow_failure("WS_001")
print(result)
```

### 3.4 手动重置线程
```python
from moodify.domain import ProjectThread, ThreadStatus
from moodify.storage import WorkspaceStore

store = WorkspaceStore("data/workspace_v2")
thread = store.get_thread("WS_001", "thread_id")
retried = thread.queue_retry()
store.update_thread(retried)
```

---

## 4. 版本管理

### 4.1 查看版本树
```bash
curl http://localhost:8000/workspace/projects/WS_001/versions | jq '.[] | {id: .version_id, name: .name, status: .status, parent: .parent_version_id}'
```

### 4.2 比较版本
```bash
curl http://localhost:8000/workspace/projects/WS_001/versions/v001/compare/v002
```

### 4.3 创建分支版本
```bash
curl -X POST http://localhost:8000/workspace/projects/WS_001/versions/v001/branch \
  -H "Content-Type: application/json" \
  -d '{
    "version_id": "WS_001_v002",
    "branch": "experiment",
    "name": "Experimental Mix",
    "purpose": "Try different EQ curve",
    "audio_path": "versions/WS_001_v002.wav",
    "audio_sha256": "...",
    "created_by": "engineer"
  }'
```

### 4.4 回退版本
```bash
curl -X POST http://localhost:8000/workspace/projects/WS_001/versions/v001/rollback \
  -H "Content-Type: application/json" \
  -d '{
    "version_id": "WS_001_v003",
    "branch": "main",
    "name": "Rollback to v001",
    "purpose": "Revert experiment",
    "created_by": "engineer"
  }'
```

---

## 5. 归档

```python
from moodify.services.archive import ArchiveService
from moodify.storage import WorkspaceStore

store = WorkspaceStore("data/workspace_v2")
service = ArchiveService(store)

# 归档
result = service.archive_project("WS_001", "WS_001_archive_001")
print(result)

# 验证归档完整性
verification = service.verify_archive("WS_001")
print(verification)
```

---

## 6. 故障排查

### 6.1 源音频找不到
- 检查 `data/workspace_v2/projects/{PROJECT_ID}/sources/` 目录
- 确认源音频 ID 与文件名匹配（支持 .wav/.flac/.aif/.aiff）

### 6.2 DSP 处理失败
- 查看对应 EXPORT 线程的 error 字段
- 检查 `ProcessingOutputDir` 是否有权限写入
- 确认 v0.1 pipeline 依赖完整

### 6.3 Judge reject (MRS 评分低)
- MRS < 60: 自动拒绝，检查处理参数合理性
- MRS 60-75: 边缘通过，记录警告
- MRS 不可用: 降级到结构检查

### 6.4 工作流卡在某个阶段
- 查看线程列表确认哪个线程未完成
- 检查线程是否为 FAILED/REJECTED 状态
- 使用 RetryOrchestrator 重试或手动推进

### 6.5 存储冲突 (409)
- 检查是否有重复的 entity ID
- 检查版本树是否形成环
- 检查审批 decision_id 是否重复

### 6.6 数据损坏 (500)
- 检查对应 JSON 文件格式
- 验证 JSONL 每行是否是合法 JSON
- 从备份恢复（如有）

---

## 7. 数据目录结构

```
data/workspace_v2/
└── projects/
    └── {PROJECT_ID}/
        ├── project.json          # AudioProject
        ├── workflow.json         # ProjectWorkflow
        ├── approvals.jsonl       # 审批记录 (追加)
        ├── sources/              # 源音频
        ├── diagnostics/          # 诊断输出
        ├── processing/           # 处理中间产物
        ├── threads/              # 各线程状态
        ├── plans/                # TreatmentPlan
        ├── versions/             # AudioVersion + 音频文件
        └── archive/              # 归档产出
            └── archive_manifest.json
```
