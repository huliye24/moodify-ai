# DSK-MFY-SCORE-ENGINE-009｜实施审计（Stage 0）

**日期：** 2026-08-02 UTC  
**HEAD：** `df3a8a3`（`codex/mainline-cloud-dev-20260603`）  
**本审计为只读事实记录；所有既有文件属于用户，本任务不修改。**

## 1. 依赖状态

| 依赖 | 状态 |
|---|---|
| DSK-MFY-STEM-MIDI-008 HANDOFF | 存在且可读；状态 ACCEPTED_AFTER_CODEX_FINISH_WITH_BENCHMARK_LIMITS（Codex 2026-08-01 验收） |
| Python | 3.11.9（`C:\Program Files\Python311\python.exe`） |
| venv-basic-pitch | 存在（`.venv-basic-pitch\Scripts\python.exe`），含 008 依赖 |
| MuseScore | `C:\Program Files\MuseScore 4\bin\MuseScore4.exe`，版本 `MuseScore4 4.5.1` |
| AGENTS.md | 仓库根目录不存在 |

## 2. 现有曲谱链事实

- `tools/score_asset_pipeline.py`：Basic Pitch MIDI 清洗脚本（量化 68/120 BPM、chordal/mono/drum 简化），输出干净 MIDI；不产生 MusicXML/PDF/SVG。
- 现有 MIDI/MusicXML 产物（用户资产，只读，不在本任务处理范围）：
  - `pre-music/`：真实歌曲转录 MIDI（多曲目，含分轨、合并、frozen、歌词对齐版本）
  - `pre-music/**/musescore_analysis_v0_1/`：含 MusicXML 与 MIDI 分析产物
  - `output/pdf/Nous_pouvons_score_assets/`：final_assets / final_assets_v2 / bass_trial 下含干净 MIDI 与 `.musicxml`
  - `outputs/midi-smoke/a4.mid`：测试产物
- 现有 `moodify.cli` 无 score 命令；`transcribe` / `transcribe-stems` 只到 MIDI。
- 008 交付了 `moodify/transcription_pipeline/`（stems/profiles/runner/midi_cleanup），是本任务的 MIDI 上游来源之一。

## 3. Git/dirty 边界

- 工作树大量既有修改与未跟踪文件（`moodify-core-package/src/moodify/cli.py`、`pyproject.toml`、`docs/tasks/deepseek/*`、`pre-music/`、`output/`、`tools/` 等）均属用户，**不整理、不覆盖、不暂存、不提交**。
- 本任务只写允许范围内的新文件：
  - `moodify-core-package/src/moodify/score_engine/`（新目录）
  - `moodify-core-package/src/moodify/cli.py`（追加 score 子命令）
  - `moodify-core-package/tests/score_engine/`（新目录）
  - `moodify-core-package/pyproject.toml`（仅必要时加可选依赖/入口）
  - `docs/architecture/MSE_ARCHITECTURE.md`、`docs/architecture/SCORE_ENGINE_ARCHITECTURE.md`
  - `docs/tasks/deepseek/DSK-MFY-SCORE-ENGINE-009/`
  - `outputs/deepseek_validation/DSK-MFY-SCORE-ENGINE-009/`
- 禁止 Git 分支/暂存/提交/推送/reset/clean/stash/checkout。

## 4. 许可证边界

- Moodify 包声明 `Apache-2.0`（`moodify-core-package/pyproject.toml`）。
- MuseScore 4.5.1 为 GPLv3 独立外部程序；本任务**只通过参数数组独立进程调用**，不复制源码、不修改其安装目录、不修改 site-packages。
- 不引入新第三方 Python 依赖；如需依赖 → `SCOPE_CHANGE_REQUEST.md` + HOLD。
- 本任务产生的任何产物（canonical JSON、MusicXML、PDF、SVG、manifest）的许可证归属与生成工具版本记入 `LICENSE_INTEGRATION_NOTE.md`（Stage 3）。

## 5. 只读事实源 SHA-256 基线

以下为本任务读取的编排/合同/架构文件，作为事实基线；Stage 3 双运行验证时源文件哈希必须不变：

| 文件 | 说明 |
|---|---|
| `docs/tasks/deepseek/DSK-MFY-SCORE-ENGINE-009/00_TASK_ORCHESTRATION.md` | 本任务编排 |
| `docs/tasks/deepseek/DSK-MFY-SCORE-ENGINE-009/02_CODEX_ACCEPTANCE_MATRIX.md` | Codex 验收矩阵 |
| `docs/tasks/deepseek/DSK-MFY-SCORE-ENGINE-009/03_PRINCIPLE_SEED.md` | 原则种子 |
| `docs/tasks/deepseek/DSK-MFY-STEM-MIDI-008/HANDOFF.md` | 008 交接（依赖） |
| `docs/tasks/deepseek/DSK-MFY-STEM-MIDI-008/00_TASK_ORCHESTRATION.md` | 008 编排 |
| `docs/architecture/MSE_ARCHITECTURE.md` | MSE 架构 |
| `docs/architecture/AUDIO_TO_MIDI.md` | 转录架构 |
| `tools/score_asset_pipeline.py` | 现有清洗脚本 |
| `moodify-core-package/pyproject.toml` | 包元数据 |
| `moodify-core-package/src/moodify/cli.py` | CLI 入口 |

（具体 SHA-256 在 Stage 3 生成 `manifest` 时统一记录到验证输出。）

## 6. 环境约束

- 本机 8 GB RAM / 低功耗双核（LSM 模式）：音频/谱面处理串行执行，禁止并行进程。
- MuseScore 缺失或调用失败时必须稳定 `UNAVAILABLE`，不得伪装成功。
- 本任务只处理程序生成的合成 MIDI 与测试 fixture；不处理真实歌曲。
