# DSK-MFY-SCORE-ENGINE-009｜验证报告（Stage 3）

**日期：** 2026-08-02 UTC  
**验证方式：** 程序生成的合成 MIDI + 明确测试 fixture；不处理真实歌曲。

## 1. 测试结果

| 套件 | 结果 |
|---|---|
| `tests/score_engine/`（新增，55 个） | **55/55 PASS** |
| 008 回归 `test_transcription_stems.py` + `test_transcription.py`（24 个） | **24/24 PASS**（venv site-packages 环境下） |
| Ruff（src + cli + tests） | clean |
| CLI help/smoke（score import-midi / export / backends / transcribe / presets / daw engines） | 全部正常，旧 CLI 无回归 |

## 2. 合成端到端 + 双运行（`outputs/deepseek_validation/DSK-MFY-SCORE-ENGINE-009/runs/`）

4 个合成 MIDI 夹具，每个跑完整链路（MIDI → canonical JSON → MusicXML → MuseScore → PDF/SVG → roundtrip report），两次全新目录：

| fixture | run1 | run2 |
|---|---|---|
| mono_melody | success / PASS | success / PASS |
| duo_tracks | success / PASS | success / PASS |
| chord_with_gap | success / PASS | success / PASS |
| tempo_change | success / PASS | success / PASS |

规范化语义（status/roundtrip/score_id/parts/notes）双运行一致；PDF 含非确定性
元数据（MuseScore 生成时间戳），不在 canonical 比较范围内（已注明）。

## 3. 失败矩阵

| 场景 | 期望 | 实测 |
|---|---|---|
| 非法 MIDI header | MidiParseError | ✅ |
| SMPTE division | MidiParseError（不支持） | ✅ |
| 不支持的 MIDI format | MidiParseError | ✅ |
| 截断 MIDI | MidiParseError | ✅ |
| 文件不存在 | FileNotFoundError | ✅ |
| 伪 MuseScore 路径 | UNAVAILABLE，稳定降级 | ✅ |
| 超时 | failure + timed_out evidence | ✅ |
| 非零退出码 | failure，无伪成功 | ✅ |
| 输出目录非空 | 拒绝（不覆盖） | ✅ |
| MusicXML 目标已存在 | FileExistsError（不覆盖） | ✅ |
| 未知 schema 字段 | ValueError（严格拒绝） | ✅ |
| 源 MIDI 被修改 | 禁止；哈希不变已验证 | ✅ |

## 4. 未运行项（明确记录）

- 完整 Core 回归套件（179 个 Workspace v2 测试）未全量重跑——本任务只新增
  `score_engine/` 目录与 `cli.py` 追加子命令，未触碰 Core DSP/Runtime/Bridge/MRS/008 实现；
  Codex 可在验收时全量运行。
- 真实歌曲端到端：禁止（任务规则）。
- 多页 SVG 的 PNG 转换：未实现（能力位冻结，本任务不承诺 PNG）。
