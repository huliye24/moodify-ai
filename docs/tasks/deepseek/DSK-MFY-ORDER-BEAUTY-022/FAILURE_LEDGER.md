# DSK-MFY-ORDER-BEAUTY-022｜失败族谱与失败台账

**日期：** 2026-08-02 UTC  
**规则：** 历史失败不得删除或改写为成功（PR-007）。

## 1. 失败族谱（按根因聚合，而非 19 个表面报错）

### 族 1｜moodify.domain 公共导出契约漂移（19/19 错误）

- **唯一根因**：工作树中 `domain/__init__.py` 被清空（50 行 re-export 删除），
  `domain/project.py` 被替换为 CanonicalProject 实验 dataclass。
- **缺失符号**：AudioProject、ProjectThread、TreatmentAction、ApprovalActorType
  （从 `moodify.domain`）；AudioProject（从 `moodify.domain.project`）。
- **受影响**：tests/v2/ 下 19 个文件（647 收集中的 19 个模块级 ImportError）。
- **调用方**：22 个 v2 测试 + 生产代码 `services/archive.py:188`。
- **最小修复面**：恢复 `project.py` + `__init__.py`（git HEAD 版本）；
  CanonicalProject 迁移到 `canonical_project.py`（保留实验，不删除）。

### 族 2｜pretty_midi 测试依赖契约不清（1/1 错误）

- **唯一根因**：`test_transcription_stems.py` 顶层 `import pretty_midi`，
  而系统 Python 3.11 未安装（仅 .venv-basic-pitch 有）。
- **依赖层级**：pretty_midi 属于 `transcription` extra 测试依赖
  （pyproject.toml `[project.optional-dependencies].transcription`），
  不是核心必需依赖。
- **最小修复面**：`pytest.importorskip("pretty_midi")`——可选能力边界
  显式降级，缺失时跳过相关测试（auditable skip），不在收集阶段崩溃。

## 2. 修复结果

| 指标 | 修复前 | 修复后 |
|---|---|---|
| 收集错误 | 19 | **0** |
| 收集测试数 | 469 | **647** |
| 全量运行 | — | **647 passed, 1 skipped** |
| `--collect-only` 退出码 | 非 0 | **0** |

## 3. 处置记录

- 未通过减少测试文件、静默吞 import 错误、无条件 skip 或删除测试达成——
  恢复的是真实契约（git HEAD 的 v2 实现仍存在），pretty_midi skip 是
  带 importorskip 语义的可审计降级。
- CanonicalProject 实验模型被保留（独立文件），未丢失用户工作；
  其去留需 Codex/用户决策（实验 vs v2 双模型并存是显式临时状态）。
