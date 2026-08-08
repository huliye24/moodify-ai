# DSK-MFY-CAPABILITY-ACCRETION-018 Progress

**Status:** READY_FOR_CODEX_REVIEW  
**Dependency:** DSK-MFY-CAPABILITY-ACCRETION-017 ACCEPTED（本机执行完成后由 Codex 验收；017 注册表与探测器可用）

| Stage | Status | Gate | Evidence |
|---|---|---|---|
| Stage A｜Adapter Protocol 与基类 | PASS | PASS (2026-08-02) | base.py：Protocol/结果/错误分类/受控执行 |
| Stage B｜六个适配器 | PASS | PASS (2026-08-02) | 7 适配器 + 5 真实工具 E2E |
| Stage C｜CLI 与文档 | PASS | PASS (2026-08-02) | 36/36 测试 + ruff + 文档 + HANDOFF |

## 阶段记录（2026-08-02 UTC）

- Stage A：ProviderAdapter Protocol、AdapterResult、六类错误分类
  （invalid_input/provider_defect/environment_failure/timeout/partial_output/
  policy_rejection）、受控进程基类（argv 数组、超时、evidence、路径防护、
  输出目录全新/为空）。
- Stage B：7 适配器（musescore/ffmpeg/ffprobe/sox/rubberband/audacity/
  basic_pitch）；009 知识组合而非修改；audacity 诚实 human_handoff 降级；
  basic_pitch 唯一允许 import 008 的内部适配器。
- Stage C：CLI `capability adapters/invoke`；36/36 测试 + 55/55 009 回归 +
  ruff clean；5 真实工具端到端成功（musescore PDF/ffmpeg FLAC/ffprobe JSON/
  sox stats/rubberband WAV）。
- 深度维持验收：每个适配器新增 provider 边界知识（sox --norm 参数形式、
  stat 输出流、ffmpeg/rubberband 版本在 stderr）已入 FAILURE_LEDGER；
  009/008 边界未松动；evidence 结构化持久化不依赖工人记忆。
