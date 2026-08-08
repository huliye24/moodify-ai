# DSK-MFY-ORDER-BEAUTY-022 Progress

**Status:** READY_FOR_CODEX_REVIEW  
**前置依据：** `project_analytics/runs/2026-08-02T094746+0800/overall-project-analysis/`  
**任务状态：** 执行完成

| Stage | Status | Gate | Evidence |
|---|---|---|---|
| Stage A｜建立错误族谱 | PASS | PASS (2026-08-02) | 19 错误 → 2 族（见 FAILURE_LEDGER） |
| Stage B｜恢复领域契约 | PASS | PASS (2026-08-02) | AudioProject 等 21 符号恢复，CanonicalProject 迁移独立文件 |
| Stage C｜明确依赖契约 | PASS | PASS (2026-08-02) | pretty_midi 显式 skip（importorskip） |
| Stage D｜建立分层门禁 | PASS | PASS (2026-08-02) | collect 647 ✅ fast 435 ✅ core 179 ✅ integration 3+1 ✅ |

## 执行记录（2026-08-02 UTC）

- **基线**：469 tests / 19 collection errors（任务编写时复核 450/19）。
- **根因分析**：19 个收集错误全部源于 `moodify.domain` 公共导出契约漂移——
  工作树中 `domain/__init__.py` 被清空、`domain/project.py` 被替换为
  CanonicalProject 实验 dataclass（无消费者），导致 v2 的 AudioProject
  pydantic 聚合（被 22 个 v2 测试 + services/archive.py 引用）无法导入。
- **Stage B 修复**：从 git HEAD 恢复 `project.py`（AudioProject 完整模型）与
  `__init__.py`（21 符号 re-export）；CanonicalProject 实验模型**迁移到
  独立文件 `canonical_project.py`**（不删除用户工作，不遮挡 v2 契约）。
- **Stage C 修复**：`test_transcription_stems.py` 顶层 `import pretty_midi`
  改为 `pytest.importorskip("pretty_midi")`——pretty_midi 是 transcription
  extra 测试依赖（装于 .venv-basic-pitch），缺失时显式 skip 而非收集崩溃。
- **结果**：19 收集错误 → **0**；`pytest --collect-only -q` 退出码 0，
  647 tests collected。
- **全量运行**：**647 passed, 1 skipped**（908s，退出码 0）。
- **分层门禁**：collect 647 ✅ / fast 435 ✅ / core 179 ✅ / integration 3+1 ✅
  （`tools/test_gates.py`，evidence 存 `docs/testing/gates/`）。
- **公共 API 合约测试**：`tests/v2/test_domain_public_contract.py`（5 tests）。
- **Ruff**：domain + v2 tests clean（修复 2 个未用 import）。
