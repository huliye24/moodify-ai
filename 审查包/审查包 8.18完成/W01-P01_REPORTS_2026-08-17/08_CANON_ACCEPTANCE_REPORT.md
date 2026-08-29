# 08 — Canon Acceptance Report

**W01-P01 · 2026-08-17 · base 98f7b96e**

## Changeset

| Path | Change |
|---|---|
| README.md | 对外身份收敛为 Moodify Music / Player + PLAY；Ear 内部化；Canon 引用；诚实现状 |
| AGENTS.md | Product Identity + Canon Reference + 8 级 Authority Order + Agent Rules + Canon Change Rule |
| docs/canon/CURRENT_CANON.md | 新增：Canon v1.0（身份/不变量/变更规则） |
| docs/canon/PRODUCT_BOUNDARY.md | 新增：对外产品与边界、非目标、证据边界 |
| docs/canon/INTERNAL_SYSTEMS.md | 新增：内部系统分类（Ear/云端/状态机/外部能力） |
| docs/canon/AUTHORITY_ORDER.md | 新增：8 级权威顺序 |
| docs/canon/CURRENT_ARCHITECTURE.md | 新增：云端现状（P00 事实，非理想图） |
| docs/canon/CANON_CHANGELOG.md | 新增：R7 变更记录 |
| docs/REPOSITORY_STATUS.md | 重写：历史快照 → Canon 入口 + 事实状态 |
| docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md | 顶部 INTERNAL 标记（内容保留） |
| docs/ASSET_MODEL.md | 顶部 INTERNAL 标记（内容保留） |
| scripts/canon_guard.py | 新增：Canon drift guard（只读） |
| moodify-core-package/tests/test_canon_guard.py | 新增：3 个 guard 测试 |

## Verification

| 项 | 结果 |
|---|---|
| git diff --check | PASS（仅 LF/CRLF 警告） |
| scripts/canon_guard.py | PASS（当前仓库） |
| pytest tests/test_canon_guard.py | 3/3 PASS |
| ruff（canon_guard.py + test） | PASS |
| README/AGENTS 身份一致 | PASS（guard 校验） |
| 无第二套 Canon | PASS（无 AGENTS_NEW/README_V2） |
| 无 runtime/DB/OSS/服务器改动 | PASS（本包只动文档 + 新增 guard 脚本/测试） |
| PR #21 未动 | PASS |
| 历史资产未删除 | PASS（仅加标记） |

## 未决（HUMAN_DECISION_REQUIRED）

1. CD-011 对外命名细节（Music vs Player、域名品牌）
2. CD-014 宪法 v1.0 正文是否更新
3. CD-015 单一 state machine 统一方案
4. GitHub main 合并策略（154 commits）

## 结论

**P01 验收通过（机器门）。** 等待人类审核；不进入 W01-P02。
