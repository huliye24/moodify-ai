# DSK-MFY-CAPABILITY-ACCRETION-018｜验证报告

**日期：** 2026-08-02 UTC

## 1. 测试结果

| 套件 | 结果 |
|---|---|
| `tests/capability_registry/`（017 21 + 018 新增 15 = 36） | **36/36 PASS** |
| 009 回归 `tests/score_engine/`（55） | **55/55 PASS** |
| Ruff（src + cli + tests） | clean |
| CLI smoke：`capability adapters`、`capability invoke` | 正常 |
| 旧 CLI 回归：`score backends`、`transcribe --help` | 无回归 |

## 2. 真实工具端到端（合成 fixture，`outputs/deepseek_validation/DSK-MFY-CAPABILITY-ACCRETION-018/`）

| adapter | capability | 输入 | 结果 | 产物 |
|---|---|---|---|---|
| musescore.cli | notation.render | 合成 MusicXML | ✅ success | tone.pdf |
| ffmpeg.cli | media.transcode | 合成 WAV | ✅ success | tone.flac |
| ffprobe.cli | media.probe | 合成 WAV | ✅ success | tone.json |
| sox.cli | audio.measure_loudness | 合成 WAV | ✅ success | tone_stats.txt |
| rubberband.cli | audio.time_stretch | 合成 WAV (tempo=0.9) | ✅ success | tone_stretched.wav |
| audacity.cli | waveform.region_edit | — | UNAVAILABLE（human_handoff） | 如实降级 |

## 3. 失败矩阵

| 场景 | 期望 | 实测 |
|---|---|---|
| 超时 | failure + error_class=timeout | ✅ 测试 |
| 非零退出码 | failure + provider_defect + stderr | ✅ 测试 |
| 输入缺失 | failure + invalid_input | ✅ 测试 |
| 输出目录非空 | failure + invalid_input | ✅ 测试 |
| Audacity headless 未实现 | unavailable + human_handoff + policy_rejection | ✅ 测试+实测 |
| Basic Pitch venv 缺失 | unavailable + environment_failure | ✅ 测试 |
| argv 数组（无 shell 拼接） | 命令为 list | ✅ 测试 |
| MuseScore 单 -o / 无 -I（009 知识） | 命令含且仅含一个 -o | ✅ 测试 |

## 4. 未运行项（如实记录）

- BasicPitchAdapter 真实转录调用未执行（需要真实音频 + Basic Pitch 推理，
  耗时长且属 008 已验证范围；Adapter 仅包一层接口）。Codex 可自行执行。
- 179 个 Workspace v2 全量回归未跑（未触碰 Core 实现）。
- Audacity headless 自动化明确不实现（human_handoff 语义，非缺漏）。

## 5. 过程中失败与修正（记入 FAILURE_LEDGER）

- sox `--norm -1` 被 getopt 当选项 → 改 `--norm=-1`
- sox stat 输出在 stderr → 基类 stdout_target 时 stderr 合并进文件
- ffmpeg/rubberband 版本输出在 stderr → 版本探测合并 stdout+stderr
- audacity errors 字符串拼接误成 str → 加尾逗号成元组
- 测试 mock 捕获到版本探测调用 → 用 call_args_list 筛选 invoke 命令
