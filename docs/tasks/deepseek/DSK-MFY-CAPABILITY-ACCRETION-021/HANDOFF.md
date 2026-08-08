# DSK-MFY-CAPABILITY-ACCRETION-021 HANDOFF

**Status:** READY_FOR_CODEX_REVIEW  
**Worker:** DeepSeek | **Date:** 2026-08-02 UTC  
**Branch:** `codex/mainline-cloud-dev-20260603` | **HEAD:** `df3a8a3c`（未提交新 commit）

## 三阶段状态

| Stage | 状态 |
|---|---|
| Stage A（记录模型） | PASS |
| Stage B（提案机制与政策） | PASS |
| Stage C（CLI、验证与文档） | PASS |

最终判定：**READY_FOR_CODEX_REVIEW**（本 Worker 不得宣布 ACCEPT）。

## CLI

```powershell
py -3.11 -m moodify.cli capability history [--case-id <id>] [--store-dir knowledge]   # 三类记录
py -3.11 -m moodify.cli capability propose --store-dir knowledge --case-id <id> \
    --capability-id <cap> --out proposal.json                                            # 提案（不自动生效）
py -3.11 -m moodify.cli capability policy [--store-dir knowledge]                        # 版本化政策
```

## 交付物

| 位置 | 内容 |
|---|---|
| `moodify-core-package/src/moodify/capability_registry/knowledge/` | records（Measurement/Judgment/NegativeKnowledge + KnowledgeStore）、policy（RuleChangeProposal/PolicyLedger）、cli |
| `moodify-core-package/src/moodify/cli.py` | `capability history/propose/policy` 挂载 |
| `moodify-core-package/tests/capability_registry/test_knowledge.py` | 8 个测试 |
| `docs/architecture/CAPABILITY_ACCRETION_ARCHITECTURE.md` | 知识层状态更新 |
| `docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-021/` | PROGRESS/VALIDATION/FAILURE_LEDGER/HANDOFF |

## 关键设计

- **NegativeKnowledgeRecord 一等公民**：被拒绝候选/回退/验证失败/规则来源
  全部持久化（POSC-003 负面知识）；禁止清理为"临时事故"。
- **提案不自动生效**：未确认 apply 被拒绝（实测）；人工确认后 policy_version
  递增（policy/1 → policy/2 实测）。
- **政策 ledger 是地质记录**：每次变更引用被替代规则 + 其历史来源
  （"规则可改变，不可遗忘"，PR-007）。
- **防污染**：最小样本门槛默认 N≥3，单例/异常案例不触发提案（实测拒绝）。
- **失忆防护**：记录只追加；修正 append superseded 标记，原文永不改写
  （实测：supersede 后原记录与标记都保留）。
- **不重复存储**：记录按 execution_record_id/record_id 与 019/020 关联。

## 验证摘要

- 69/69 capability_registry + 55/55 score_engine；Ruff clean。
- 知识循环端到端实测：3 case 记录 → 单 case 提案被门槛拒绝 → 3 case 聚合
  提案 → 未确认被拒 → 确认后 policy/1 生效（带地质引用）→ policy/2。

## 限制（事实边界）

- 记录关联按 record_id 链接；跨包自动编译（执行→测量→判断）留给集成任务。
- 未触碰 moodify_runtime（接口对接需 SCOPE_CHANGE_REQUEST 由 Codex 决定）。
- 179 个 Workspace v2 全量回归未跑（未触碰 Core 实现）。

## Codex 验收命令

```powershell
py -3.11 -m pytest tests/capability_registry/test_knowledge.py -v
py -3.11 -m moodify.cli capability history --store-dir <021 输出>
py -3.11 -m moodify.cli capability policy --store-dir <021 输出>
py -3.11 -m moodify.cli capability propose --store-dir <021 输出> --case-id case-loop-0 \
    --capability-id media.transcode --out t.json   # 应被样本门槛拒绝
py -3.11 -m moodify.cli score backends   # 旧 CLI 回归
```

DeepSeek Worker 停止于此。最终判定属于 Codex。
