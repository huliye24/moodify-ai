# DSK-MFY-CAPABILITY-ACCRETION-021 Progress

**Status:** READY_FOR_CODEX_REVIEW  
**Dependency:** DSK-MFY-CAPABILITY-ACCRETION-020 ACCEPTED（本机执行完成后由 Codex 验收；017-020 全链可用）

| Stage | Status | Gate | Evidence |
|---|---|---|---|
| Stage A｜记录模型 | PASS | PASS (2026-08-02) | records.py：三类记录 + 追加式 store |
| Stage B｜提案机制与政策 | PASS | PASS (2026-08-02) | policy.py：提案不自动生效 + 地质引用 + 门槛 |
| Stage C｜CLI 与文档 | PASS | PASS (2026-08-02) | 69/69 测试 + ruff + 知识循环实测 + HANDOFF |

## 阶段记录（2026-08-02 UTC）

- Stage A：MeasurementRecord（输入特征/参数/测量/耗时）、JudgmentRecord
  （批准/拒绝/修订+结构化理由）、NegativeKnowledgeRecord（被拒绝候选/回退/
  验证失败/规则来源）——全部追加式存储，修正 append superseded（失忆防护实测）。
- Stage B：RuleChangeProposal（四种变更类型、evidence 关联、含负面知识关联、
  不自动生效）、PolicyLedger（版本递增、地质引用：被替代规则+来源）、
  meets_sample_threshold（N≥3 防污染）。
- Stage C：CLI history/propose/policy；69/69 + 55/55 + ruff clean；知识循环
  端到端实测（3 case → 提案 → 确认 → policy/1 生效 → policy/2）。
- 深度维持验收：负面知识一等公民（POSC-003 落地）；政策 ledger 携带
  地质引用（规则可改变不可遗忘）；单 case 提案被门槛拒绝（防污染实测）；
  记录只追加不删除（失忆防护实测）。