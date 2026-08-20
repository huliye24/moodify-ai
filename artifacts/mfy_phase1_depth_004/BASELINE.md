# MFY-PHASE1-DEPTH-004 Baseline

- Recorded: 2026-08-09
- Base: `codex/moodify-1.0-release-convergence`（Phase I-C `8618cb4` 之上）
- 初始测试：237 passed, 5 skipped（含 ffmpeg PATH）

## 现状审计

- Phase I-A（测量权威）、I-B（时间事件）、I-C（多尺度表示）已交付
- 现有 `judgment.py`：technical_assessment/workflow_decision/reasons/risk_flags——**无证据状态、无不确定性分类、无覆盖声明**
- 现有 events：有 rule 推导 confidence（阈值余量+窗数，basis 可文档化）
- 无证据图/完整性/冲突/bundle

## 设计决策

- 新 `auditory/evidence/` 包（5 模块）+ `auditory/uncertainty.py`（U1-U7 有界枚举）
- 证据图：JUDGMENT→EVENT/WINDOW→MEASUREMENT→PROFILE→SOURCE→RULE（轻量结构，非图数据库）
- 判断三态分离：classification（技术分类）/ evidence_state（SUPPORTED/PARTIAL/INSUFFICIENT/CONFLICTING/NOT_APPLICABLE/INVALID）/ workflow_decision（PASS_TO_LISTENING/REJECT_TECHNICAL/INCONCLUSIVE/REVIEW_REQUIRED）
- Fail-closed：critical 缺失/无效证据 → 强制 INCONCLUSIVE + EVIDENCE_INCOMPLETE（resolver 组装后应用）
- 覆盖率：NO_MEASURED_RISK 必须伴随 evaluated_domains 声明
- bundle 确定性：logical hash 排除 uuid 身份（node_id/ref 中 EVENT/PROFILE 的 uuid），仅语义内容
- 全局/局部差异（全局正常 + 局部事件）非冲突（E406）
