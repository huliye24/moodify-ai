# DSK-MFY-CAPABILITY-ACCRETION-017 Progress

**Status:** READY_FOR_CODEX_REVIEW  
**Dependency:** DSK-MFY-SCORE-ENGINE-009 ACCEPTED（HANDOFF 可读，Codex 2026-08-01 验收）

| Stage | Status | Gate | Evidence |
|---|---|---|---|
| Stage A｜Registry 模型与 schema | PASS | PASS (2026-08-02) | model.py + 序列化测试 |
| Stage B｜环境探测器 | PASS | PASS (2026-08-02) | detect.py ×8 实测 + 负面知识 |
| Stage C｜首批能力注册 | PASS | PASS (2026-08-02) | bootstrap.py + capability_registry.json（7/7） |
| Stage D｜验证与文档 | PASS | PASS (2026-08-02) | 21/21 测试 + ruff + 架构文档 + HANDOFF |

## 阶段记录（2026-08-02 UTC）

- Stage A：CapabilityContract/ProviderRecord/CapabilityRegistry 严格模型；
  canonical JSON（未知键拒绝、schema 校验、双运行一致）。
- Stage B：8 个只读探测器（musescore/ffmpeg/ffprobe/sox/rubberband/audacity/
  basic_pitch/moodify_self），known_failure_modes 携带负面知识。
- Stage C：7 能力/7 provider 注册，全部 active，版本/许可/路径实测；
  `capability probe/regenerate/list` CLI 挂载。
- Stage D：21/21 测试 PASS，Ruff clean，旧 CLI 无回归；
  CAPABILITY_ACCRETION_ARCHITECTURE.md + VALIDATION + FAILURE_LEDGER + HANDOFF。
- 深度维持验收：探测结果可复现保存（regenerate 机制）；009/008 边界
  以负面知识形式入册未松动；本次新增 6 条失败记录已入 FAILURE_LEDGER。
