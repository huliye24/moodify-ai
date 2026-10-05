# ThinkPad Separation / Demucs Audit

**Task:** MOODIFY_THINKPAD_HEAVY_LANE_001 (Phase E)
**Date:** 2026-10-05
**Branch:** `feat/thinkpad-heavy-lane-001`

---

## 0. Headline finding

**仓库当前没有任何 Demucs 执行路径。** §13 的十个问题中，与 Demucs 相关的部分是
「不存在」，而**真实存在的分离路径有两条 + 一条 TARGET**。本审计按实测回答十个问题，
并给出真实路径的验证证据。

## 1. §13 十问 —— 逐条回答

| # | 问题 | 回答 |
|---|---|---|
| 1 | 哪个模块拥有 Demucs？ | **没有模块。** 全仓 `import demucs` / `import torch` = 0 hits（src/ tools/ scripts/ tests/ ops/）。`pyproject.toml` 有 `separation = ["demucs", "torch>=2.0"]` extra —— declared-with-no-code（能力注册表 `stem.separate` 的 notes 原文如此）。 |
| 2 | 哪个运行时执行它？ | 不存在。 |
| 3 | subprocess 还是 Python API？ | 不存在。真实分离路径①走 subprocess（见 §2）。 |
| 4 | 模型存哪里？ | Demucs：N/A。Basic-Pitch：**模型随 wheel 内置**，`site-packages/basic_pitch/saved_models/icassp_2022/nmp.onnx`，无下载。 |
| 5 | 首次模型下载多久？ | **不需要下载**（上条）。这也回答了「模型缓存」问题的实际形态。 |
| 6 | 第二次执行复用缓存？ | 无缓存问题：模型在本地 wheel 里，每次进程直接加载（basic-pitch 单次加载约数秒，见 §3）。 |
| 7 | CPU 模式支持？ | Demucs N/A；真实路径全部 CPU（本节点无 CUDA，见 baseline §5）。 |
| 8 | GPU 模式支持？ | N/A —— 本节点 `GPU_ACCELERATION = NOT_AVAILABLE`，无 GPU 路径可测。 |
| 9 | 失败回退是什么？ | 运行时缺失 → `RuntimeMissingError`（code=`DEPENDENCY_MISSING`），**绝不静默回退系统 python**（HOTFIX 000/F4）；脚本内部失败 → 非零退出，错误上抛（不吞）。 |
| 10 | 三个分离路径的整合状态？ | 无统一契约：①lalal 云客户端（CONNECTED_UNTESTED）②桌面 DSP 预览脚本（preview-grade）③Demucs extra（无代码）。能力注册表原文记录此三分裂。 |

## 2. 真实分离路径（本次实测）

### 路径 A：桌面快速分离（DSP 中置估计 + HPSS）— `moodify-desktop/scripts/dsp_separate.py`

调用方式与桌面壳 `main.js::stems:run` 完全一致（`.venv-basic-pitch` 的 python +
`dsp_separate.py <src> --outdir <case>/stems`），本次在 ThinkPad 实测：

```text
input:  local_audio_assets/inputs/test_A_10s.wav (10.0s 44.1k 2ch)
output: 4 stems (vocals / instrumental / harmonic / percussive) + manifest.json
elapsed_s (脚本自报): 13.93   wall: 15.0s
engine_note 随产物携带：「非模型快速分离……不构成母带级分轨」（诚实边界，写进 manifest，UI 直接呈现）
```

**这就是「重分离」位置的现状：不是 Demucs，是预览级 DSP。** 10s 输入 ~14s，
线性外推 180s ≈ 4-5 分钟量级（未实测，不写成事实）。

### 路径 B：lalal.ai 云端分离 — `moodify/api/routes/stems.py`

FastAPI 路由 `/api/v1/stems`（fire-and-check 客户端，需 API key）。**未测试**：
需要云端凭据与网络调用，且属「未验证不写成已运行」的边界。状态维持
仓库既有记录 `CONNECTED_UNTESTED`。

### 路径 C：MIDI 转录（Basic-Pitch ONNX）— 已实测

```text
.venv-basic-pitch/Scripts/basic-pitch.exe --save-midi --model-serialization onnx <outdir> <wav>
（与 main.js::midi:run 的参数一致）
实测: 30s piano.wav → piano_basic_pitch.mid (1898 B) ✅ · onnxruntime 1.23.2 · CPU
```

### TARGET（未实现）

```text
精细分离引擎（Demucs / BS-RoFormer 等成熟公开引擎）— main.js:501 注释标为「后续档」
若接入：应走 runLong 通道 + 新专用 venv + .gitignore 条目（当前无 .venv-demucs 模式）
```

## 3. 与 §14 的关系

§14「若功能已存在则基准 30/60/180s」：**Demucs 功能不存在**，故不执行 Demucs 基准。
存在的是预览级 DSP 分离（路径 A），其 10s 实测已记录；把预览级脚本当「Demucs 基准」
汇报会是伪造。若主线上线精细分离档，基准任务应在新任务包中定义。

## 4. 结论

```text
DEMUCS_PATH        = ABSENT（declared-with-no-code；2026-05-28 技术决策用 HPSS 替代）
REAL_SEPARATION    = 预览级 DSP（本地，已验证）+ lalal 云（未测）+ 精细档（TARGET）
RUNTIME_FOR_STEMS  = .venv-basic-pitch（既有多用途约定，本次沿用默认三 venv 结构）
```
