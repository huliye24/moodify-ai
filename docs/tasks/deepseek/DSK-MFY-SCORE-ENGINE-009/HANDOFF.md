# DSK-MFY-SCORE-ENGINE-009 HANDOFF

**Status:** READY_FOR_CODEX_REVIEW  
**Worker:** DeepSeek | **Date:** 2026-08-02 UTC  
**Branch:** `codex/mainline-cloud-dev-20260603` | **HEAD:** `df3a8a3c`（未提交新 commit）

## 四阶段状态

| Stage | 状态 |
|---|---|
| Stage 0（事实、合同、损失边界冻结） | PASS |
| Stage 1（内部模型 + MIDI ingest + MusicXML exporter） | PASS |
| Stage 2（MuseScoreBackend 最小闭环） | PASS |
| Stage 3（合成端到端、双运行、文档、继承） | PASS |

最终判定：**READY_FOR_CODEX_REVIEW**（本 Worker 不得宣布 ACCEPT）。

## 三个 CLI

```powershell
py -3.11 -m moodify.cli score import-midi <in.mid> --output <out.json>   # MIDI → canonical MoodifyScore
py -3.11 -m moodify.cli score export <score.json> --output-dir <dir>     # → MusicXML/PDF/SVG + roundtrip_report.json
py -3.11 -m moodify.cli score backends [--json]                          # 能力与可用性
```

实测（本机 MuseScore 4.5.1）：import → export 全链路成功，PDF/SVG 生成，
round-trip verdict=PASS。

## 交付物

| 位置 | 内容 |
|---|---|
| `moodify-core-package/src/moodify/score_engine/` | model / midi_ingest / serialization / musicxml_exporter / backend / musescore_backend / roundtrip / cli |
| `moodify-core-package/src/moodify/cli.py` | 追加 `score` 子命令（import-midi / export / backends） |
| `moodify-core-package/tests/score_engine/` | 55 个测试（含合成 MIDI fixture builder） |
| `docs/architecture/SCORE_ENGINE_ARCHITECTURE.md` | 新架构文档（v0.1） |
| `docs/architecture/MSE_ARCHITECTURE.md` | 更新 Score representation 状态为 v0.1 implemented |
| `docs/tasks/deepseek/DSK-MFY-SCORE-ENGINE-009/` | 5 合同 + PROGRESS/VALIDATION/FAILURE_LEDGER/LICENSE_NOTE/BACKEND_CAPABILITY_MATRIX/HANDOFF |
| `outputs/deepseek_validation/DSK-MFY-SCORE-ENGINE-009/` | 合成 E2E 双运行产物（runs/run_1、run_2）+ manifest |

## 内部模型（MoodifyScore v0.1）

- schema `moodifyscore/0.1`；canonical JSON（键排序、内容派生 score_id、未知键拒绝）。
- 保留：原始 tick、track/channel/program、tempo/拍号/调号（存在时）、源 SHA-256。
- 推断分层：measure 布局（有时间签名时，status=inferred）；key/voice 不可靠时保持 unknown，
  不伪造音乐学结论；无人工输入，因此永不出现 `confirmed`。
- 不依赖 `.mscz`；MusicXML 只承载交换内容，evidence/revision/confidence 只属于 MoodifyScore。

## 验证摘要

- `tests/score_engine/` 55/55 PASS；008 回归 24/24 PASS（venv-basic-pitch site-packages 环境）；Ruff clean。
- 合成 4 夹具双运行：全部 success + round-trip PASS，规范化语义一致。
- 失败矩阵：非法/截断/SMPTE MIDI、伪路径、超时、非零退出码、非空输出目录、覆盖拒绝、
  未知字段、源哈希不变——全部有测试并实测。
- 旧 CLI（transcribe / presets / daw engines）smoke 无回归。
- 未运行项（如实记录）：179 个 Workspace v2 全量回归未跑（未触碰 Core 实现）；真实歌曲端到端禁止。

## 关键决策

- MuseScore 4.5.1 一次只接受一个 `-o`、不支持 `-I` 参数；PDF/SVG 分两次 argv 调用；
  多页 SVG 页码后缀用 glob 收集。
- 未实现后端（Verovio/LilyPond/OSMD）仅能力位，`available=False`，无假实现。
- 进程调用全部 argv 数组；超时/退出码/stdout/stderr/命令/版本/输出哈希入 evidence。
- 输出目录必须全新/为空；拒绝覆盖与路径逃逸；源 MIDI 只读。

## 限制（事实边界）

- 无真实歌曲 ground truth；准确率声明禁止，直到独立 benchmark 任务提供证据。
- 无调号推断、无 voice 划分启发式（每 part 单 voice）、无 `.mscz` 往返、无 PNG、无人工编辑。
- 8 GB 约束：无并行 MuseScore 进程。
- 许可证：Moodify 保持 Apache-2.0；MuseScore GPLv3 仅外部进程调用，未复制/修改其任何文件；
  未引入新 Python 依赖，`pyproject.toml` 未改动。

## Codex 验收命令

```powershell
py -3.11 -m pytest tests/score_engine/ -v
py -3.11 -m moodify.cli score backends
py -3.11 -m moodify.cli score import-midi tests\score_engine\fixtures\mono.mid --output tmp\s.json
py -3.11 -m moodify.cli score export tmp\s.json --output-dir tmp\out
py -3.11 -m moodify.cli transcribe --help   # 旧 CLI 回归
```

DeepSeek Worker 停止于此。最终判定属于 Codex。
