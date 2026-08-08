# DSK-MFY-CAPABILITY-ACCRETION-020 Progress

**Status:** READY_FOR_CODEX_REVIEW  
**Dependency:** DSK-MFY-CAPABILITY-ACCRETION-019 ACCEPTED（本机执行完成后由 Codex 验收；017-019 注册表/适配器/网关可用）

| Stage | Status | Gate | Evidence |
|---|---|---|---|
| Stage A｜CapabilityValidator 规则库 | PASS | PASS (2026-08-02) | rules.py：6 规则全带 historical_source |
| Stage B｜候选生成与选择 | PASS | PASS (2026-08-02) | candidates.py：生成/排序/拒绝理由 |
| Stage C｜CLI 与文档 | PASS | PASS (2026-08-02) | 61/61 测试 + ruff + 台账 + HANDOFF |

## 阶段记录（2026-08-02 UTC）

- Stage A：ValidationRule（rule_id/description/level/historical_source/check）、
  RuleResult、ValidationReport（error 级失败即 rejected）；6 条通用规则全部
  携带真实地质来源（009 台账 #4/#10、厚度标准 §4.4、round-trip 合同、EX-005）；
  规则集来自 registry quality_policy 声明 + 能力绑定，provider 不可关闭。
- Stage B：CandidateSpec/Candidate（绑定独立 envelope）/CandidateRanker
  （accepted 优先）/RejectionReason（rule_id+measured+expected）；失败候选
  与理由全量保留（负面知识）；回退仅走声明路径（机制就位）。
- Stage C：CLI `capability validate`（从 ExecutionRecord 重放）与
  `capability candidates`（参数变体生成）；61/61 + 55/55 + ruff clean；
  validate 显示逻辑修正（PASS 不打印失败文案）。
- 深度维持验收：规则库 6 条全部有历史来源（无凑数）；验证失败候选与理由
  完整保留；规则对缺失产物健壮（EX-009 模式第三次验证）。