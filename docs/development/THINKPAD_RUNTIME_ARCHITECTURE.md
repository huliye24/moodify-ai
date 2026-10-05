# ThinkPad Runtime Architecture — Moodify Heavy Development Lane

**Task:** MOODIFY_THINKPAD_HEAVY_LANE_001 (Phase B)
**Date:** 2026-10-05
**Branch:** `feat/thinkpad-heavy-lane-001`
**Status:** ESTABLISHED — 所有已建运行时均通过真实功能验证；未建项如实记录原因。

---

## 1. Runtime inventory

目标结构（§7 of the task）在本仓库的**实际**对应关系——按仓库代码里真实存在的
运行时契约建立，不是按假设的名字建立：

| Runtime | Path | Purpose | Status |
|---|---|---|---|
| **Core Runtime** | `moodify-core-package/.venv` | PROCESS / 分析 / DSP / 测试 / 基准 | ✅ 已存在（本机创建），已验证 |
| **Score Runtime** | `.venv-score/`（repo root） | MIDI → MusicXML（music21） | ✅ 本次新建，已验证 |
| **Basic-Pitch Runtime** | `.venv-basic-pitch/`（repo root） | 音频 → MIDI（basic-pitch CLI） | ✅ 本次新建，已验证 |
| **Audio Runtime** | *（并入 Core Runtime）* | librosa / soundfile / soxr / sr | 无独立 `.venv-audio` 存在或被引用 |
| **Demucs Runtime** | — | Demucs 源分离 | ❌ **NOT_APPLICABLE** — 见 §5 |
| **Heavy Model Runtime** | — | 未来精分离档 | 未建（无消费者，§5） |

两个专用 venv 的**位置不是自选的**：`moodify-desktop/src/runtime.js` 把它们固定在
repo root（`.venv-basic-pitch` / `.venv-score`），并允许 `MOODIFY_VENV_BASIC_PITCH` /
`MOODIFY_VENV_SCORE` 环境变量显式覆盖。运行时缺失时抛 `RuntimeMissingError`
（code = `DEPENDENCY_MISSING`），**绝不静默回退到系统 python**（HOTFIX 000 / F4）。

## 2. Build commands（可复现）

```bash
# Core（重建时）
cd moodify-core-package
D:\python\python.exe -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"

# Score（repo root）
D:\python\python.exe -m venv .venv-score
.venv-score/Scripts/python.exe -m pip install music21        # 9.9.2

# Basic-Pitch（repo root）
D:\python\python.exe -m venv .venv-basic-pitch
.venv-basic-pitch/Scripts/python.exe -m pip install basic-pitch==0.4.0
```

全部以本机解释器 `D:\python\python.exe`（Python 3.10.10）为基座**本机构建**，
未从其他机器拷贝任何 venv。三个 venv 均被 `.gitignore` 覆盖
（`.venv` / `/.venv-score/` / `.venv-basic-pitch/`），不会进入 Git。

## 3. Verification evidence（2026-10-05 实测）

```text
Core     : .venv/Scripts/moodify.exe doctor
           → {"ready": true, "status": "ok", core_version "1.0.0-rc.1"}
           → ffmpeg found (9.0.2-full_build), 8 packages importable

Basic-Pitch:
           PYTHONUTF8=1 .venv-basic-pitch/Scripts/basic-pitch.exe <out> <piano.wav>
           → piano_basic_pitch.mid (30s 输入 → 1898 B MIDI)  ✅
           backend: onnxruntime 1.23.2（wheel 内置 icassp_2022/nmp.onnx 模型）

Score    : PYTHONUTF8=1 .venv-score/Scripts/python.exe midi_to_musicxml.py
               piano_basic_pitch.mid piano.musicxml
           → MusicXML 4.0, 109991 B, {"ok": true}            ✅
```

### GBK trap（中国区 Windows 必修）

`basic-pitch` CLI 在 cp936 控制台下打印 emoji 即崩溃：

```text
UnicodeEncodeError: 'gbk' codec can't encode character '\u2728'
```

**所有 python 子进程必须带 `PYTHONUTF8=1`**（桌面壳既有做法）。缺失该环境变量时
失败形态是深层 traceback，不是「缺依赖」。此坑归入运行时契约。

## 4. Core Runtime details（已验证）

```text
Python 3.10.10 · pip 26.2.1 · moodify 1.0.0rc1 (editable, D:\moodify-ai\moodify-core-package)
numpy 2.2.6 · scipy 1.15.3 · librosa 0.11.0 · soundfile 0.13.1 · pyloudnorm 0.2.0
pedalboard 0.9.23 · pydantic 2.13.2 · jsonschema 4.26.0 · matplotlib 3.10.8
fastapi 0.136.0 · uvicorn 0.44.0 · pytest 9.1.1 (+xdist 3.8.0) · ruff 0.15.15
```

版本与 `pyproject.toml` 的 python<3.11 分支钉版一致（numpy 2.2.6 / scipy 1.15.3）。

## 5. Demucs — 为什么**不是**一个需要建的运行时

`MOODIFY_THINKPAD_HEAVY_LANE_001` §13/§14 假设存在 Demucs 路径。**审计结论：不存在。**

证据（2026-10-05 全仓检索）：

```text
1. 零执行代码：src/ tools/ scripts/ tests/ ops/ 中没有任何 `import demucs` / `import torch`
   （grep -rn "^\s*(import|from)\s+(torch|demucs)" → 0 hits）
2. 能力注册表自证：capabilities/builtin.py::stem.separate 的 notes 原文——
   "a Demucs extra that is declared in pyproject with no code behind it."
3. 技术路线决策已移除：orchestration/workflow_engine.py 头注与
   processing/spectral_chain.py 头注均写明「使用 HPSS 频谱分解替代 Demucs 深度学习源分离」；
   决策文档 docs/engineer/2026-05-28/2026-05-28_技术路线决策_Demucs移除与HPSS替代.md
4. 唯一「未来」提法：moodify-desktop/src/main.js:501 注释——「模型引擎（Demucs / BS-RoFormer）
   为后续『精分离』档」，即目标态，无实现。
5. pyproject.toml 的 `separation = ["demucs", "torch>=2.0"]` extra：declared-with-no-code，
   仓库无任何安装路径引用它。
```

因此：**不安装 torch/Demucs**。为一个没有消费者的 extra 建 venv 属于「experimental
dumping ground」反模式（§21），还会无谓占用数 GB 磁盘。当前分离路径是
`moodify-desktop/scripts/dsp_separate.py`（DSP 中置估计 + HPSS，预览级，
`grade=PREVIEW_NOT_MASTERING_GRADE`），仅需 numpy + soundfile——Core venv 即可跑。

**NOTE / 跨线提示：** 若未来接入 Demucs/BS-RoFormer 精分离档，它应走
`moodify-desktop/src/main.js` 注释中的 runLong 通道，并需要一个
`.venv-demucs` 类运行时 + `.gitignore` 条目（当前 `.gitignore` **没有**
`.venv-demucs`/`.venv-audio` 模式）。这属于未来功能，不做预告性建设。

## 6. 节点上不存在的工具（诚实记录）

```text
Node.js     NOT INSTALLED → Studio (Electron) JS 测试在本节点无法运行（属 mainline lane）
Java        NOT INSTALLED → Android 构建在本节点无法运行（属 mainline lane）
CUDA/NVIDIA NOT AVAILABLE → 一切模型工作为 CPU 模式（见 THINKPAD_NODE_BASELINE.md §5）
```
