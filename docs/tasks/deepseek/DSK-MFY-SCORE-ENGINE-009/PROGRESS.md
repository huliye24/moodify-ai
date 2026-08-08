# DSK-MFY-SCORE-ENGINE-009 Progress

**Status:** READY_FOR_CODEX_REVIEW  
**Dependency 008:** ACCEPTED_AFTER_CODEX_FINISH_WITH_BENCHMARK_LIMITS（HANDOFF 可读，Codex 2026-08-01 验收）

| Stage | Status | Gate | Evidence |
|---|---|---|---|
| Stage 0｜合同与损失边界 | PASS | PASS (2026-08-02) | 00_IMPLEMENTATION_AUDIT.md, MOODIFYSCORE_CONTRACT.md, SCORE_BACKEND_CONTRACT.md, ROUNDTRIP_LOSS_CONTRACT.md, STAGE_0_GATE.md |
| Stage 1｜内部模型与 MusicXML | PASS | PASS (2026-08-02) | tests/score_engine/ 40/40 + ruff clean |
| Stage 2｜MuseScoreBackend | PASS | PASS (2026-08-02) | tests 55/55 + ruff clean + CLI smoke |
| Stage 3｜验证与继承 | PASS | PASS (2026-08-02) | 合成 E2E 双运行 + 55/55 + 008 回归 24/24 + 文档 + HANDOFF |

逐阶段记录 UTC、文件、命令、退出码、测试、round-trip、失败、只读哈希、
许可证和范围检查。历史失败不得删除或改写为成功。

## Stage 0 记录（2026-08-02 UTC）

- 交付 5 个合同/审计文件，STAGE_0_GATE 判定 PASS。
- 环境：Python 3.11.9、MuseScore 4.5.1（`C:\Program Files\MuseScore 4\bin\MuseScore4.exe`）、venv-basic-pitch 存在、无 AGENTS.md。
- HEAD `df3a8a3`；工作树既有修改/未跟踪文件属用户，只写允许范围新文件。

## Stage 1 记录（2026-08-02 UTC）

- 实现：`score_engine/model.py`（严格类型 v0.1 模型）、`midi_ingest.py`（SMF0/1 解析、raw tick/tempo/拍号/调号保真、measure 推断）、`serialization.py`（canonical JSON、稳定 ID、未知键拒绝）、`musicxml_exporter.py`（MusicXML 4.0 partwise、tie、tempo、time/key）。
- 测试 `tests/score_engine/`：40/40 PASS，ruff clean。
- 修复记录：fixture builder 重复 header bug；NoteOn tick 字段名；MIDI tempo 整数 micros 精度（rel=1e-4 容差）。
- 测试覆盖：单轨/多轨/tempo change/拍号变化/休止间隙/和弦/跨小节/Unicode/空轨/非法 MIDI/未知字段/稳定序列化/源哈希不变/双运行一致。

## Stage 2 记录（2026-08-02 UTC）

- 实现：`score_engine/backend.py`（Protocol/能力位/注册表）、`musescore_backend.py`（探测/argv 数组进程/超时/evidence/PDF+SVG）、`roundtrip.py`（重解析对比 roundtrip_report.json）、`score_engine/cli.py`（import-midi/export/backends），cli.py 挂载 score 子命令。
- 关键修正：MuseScore 4.5.1 一次只接受一个 `-o`（分两次调用）；不支持 `-I` 参数（去掉）；多页 SVG 自动加 `-1` 后缀（glob 收集）。
- CLI smoke：`score backends`（musescore v4.5.1 available，Verovio/LilyPond/OSMD capability-bit only）、`score import-midi`、`score export`（PDF+SVG 生成，round-trip PASS）。
- 测试 55/55 PASS，ruff clean。
- 失败注入：伪路径→UNAVAILABLE、非空输出目录→拒绝、超时→failure、exit!=0→failure 均有测试。

## Stage 3 记录（2026-08-02 UTC）

- 合成 E2E 双运行（`outputs/deepseek_validation/DSK-MFY-SCORE-ENGINE-009/runs/run_1|run_2`）：
  4 夹具全部 success + round-trip PASS，规范化语义一致。
- 008 回归 24/24 PASS（venv-basic-pitch site-packages）；旧 CLI smoke 无回归。
- 交付：SCORE_ENGINE_ARCHITECTURE.md（新）、MSE_ARCHITECTURE.md（更新）、
  VALIDATION_REPORT.md、FAILURE_LEDGER.md、LICENSE_INTEGRATION_NOTE.md、
  BACKEND_CAPABILITY_MATRIX.md、HANDOFF.md。
- 未运行项（如实记录）：179 个 Workspace v2 全量回归未跑；真实歌曲端到端禁止。
- 最终状态：READY_FOR_CODEX_REVIEW。

