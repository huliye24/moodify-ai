# DSK-MFY-ORDER-BEAUTY-022 HANDOFF

**Status:** READY_FOR_CODEX_REVIEW  
**Worker:** DeepSeek | **Date:** 2026-08-02 UTC  
**Branch:** `codex/mainline-cloud-dev-20260603` | **HEAD:** `df3a8a3c`（未提交新 commit）

## 四阶段状态

| Stage | 状态 |
|---|---|
| Stage A（建立错误族谱） | PASS |
| Stage B（恢复领域契约） | PASS |
| Stage C（明确依赖契约） | PASS |
| Stage D（建立分层门禁） | PASS |

最终判定：**READY_FOR_CODEX_REVIEW**（本 Worker 不得宣布 ACCEPT）。

## 结果对比

| 指标 | 修复前 | 修复后 |
|---|---|---|
| 收集错误 | 19 | **0** |
| 收集测试数 | 469 | **647** |
| 全量运行 | — | **647 passed, 1 skipped**（exit 0） |

## 根因与修复（失败族谱）

**族 1｜domain 公共导出契约漂移（19/19）**
- 工作树中 `domain/__init__.py` 被清空、`domain/project.py` 被替换为
  CanonicalProject 实验 dataclass（无消费者），v2 的 AudioProject pydantic
  聚合（22 测试 + services/archive.py 引用）无法导入。
- 修复：从 git HEAD 恢复 `project.py` + `__init__.py`；CanonicalProject
  **迁移到独立文件 `domain/canonical_project.py`**（不删除用户工作）。

**族 2｜pretty_midi 测试依赖契约不清（1/1）**
- `test_transcription_stems.py` 顶层 `import pretty_midi`，系统 Python 未装
  （仅 .venv-basic-pitch）。改为 `pytest.importorskip`——可选能力边界
  显式降级，缺失时 auditable skip。

## 交付物

| 文件 | 内容 |
|---|---|
| `src/moodify/domain/project.py` | 恢复 v2 AudioProject 聚合（git HEAD） |
| `src/moodify/domain/__init__.py` | 恢复 21 符号 re-export |
| `src/moodify/domain/canonical_project.py` | CanonicalProject 实验模型（独立保留） |
| `tests/v2/test_domain_public_contract.py` | 公共 API 合约回归（5 tests） |
| `tests/test_transcription_stems.py` | pretty_midi importorskip |
| `tools/test_gates.py` | 四层门禁（collect/fast/core/integration） |
| `docs/testing/gates/gates_*.json` | 门禁证据快照 |
| `docs/tasks/deepseek/DSK-MFY-ORDER-BEAUTY-022/` | PROGRESS/VALIDATION/FAILURE_LEDGER/HANDOFF |

## 分层门禁

```
collect      ✅ 647 collected, 0 errors
fast         ✅ 435 passed
core         ✅ 179 passed (Workspace v2)
integration  ✅ 3 passed, 1 skipped
```

## 关键决策

- **恢复真实契约而非掩盖**：AudioProject 是 v2 事实源（22 测试 + 生产代码
  引用），CanonicalProject 无消费者——按 022 Stage B"迁移到唯一当前模型"，
  当前模型是 AudioProject。
- **实验保留不删除**：CanonicalProject 移到独立模块，双模型并存是**显式
  临时状态**，去留待 Codex/用户决策（024 边界任务可处理）。
- **依赖契约明确**：pretty_midi 属 transcription extra，缺失时 importorskip
  而非收集崩溃。

## 限制（事实边界）

- 未修改 pyproject.toml（依赖分组已正确，问题在测试 import 方式）。
- 未触碰 audio/DSP 算法；未新增功能。
- fast 层双运行一致已测；core/integration 未双跑（时间约束）。
- 647 全量运行约 15 分钟（LSM 机器），门禁脚本已固化分层以缩短迭代。

## Codex 验收命令

```powershell
py -3.11 -m pytest --collect-only -q
py -3.11 -m pytest tests/v2/test_domain_public_contract.py -v
py -3.11 -m pytest tests/v2 -q
py -3.11 -m moodify.cli --help   # 回归
python tools/test_gates.py collect core integration
```

DeepSeek Worker 停止于此。最终判定属于 Codex。
