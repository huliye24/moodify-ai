# ThinkPad Test Baseline — Core

**Task:** MOODIFY_THINKPAD_HEAVY_LANE_001 (Phase C)
**Date:** 2026-10-05
**Branch:** `feat/thinkpad-heavy-lane-001` @ `f887ab33`（测试期间该分支只含 docs/scripts 新增，无 Core 代码改动）
**Runtime:** `moodify-core-package/.venv`（Python 3.10.10, pytest 9.1.1, ruff 0.15.15）

---

## 命令（仓库 canonical，CONTRIBUTING.md / README 原文）

```bash
cd moodify-core-package
python -m ruff check src tests ../tests
python -m pytest -q tests ../tests
```

## 结果

```text
ruff:    All checks passed!
pytest:  1403 passed, 6 skipped, 14 warnings in 519.84s (0:08:39)
         exit code 0
```

| 项 | 值 |
|---|---|
| collected（passed+skipped） | 1409 |
| passed | **1403** |
| failed | **0** |
| errors | 0 |
| skipped | 6 |
| duration | 519.84 s（8:39） |
| warnings | 14（librosa audioread 弃用 / PySoundFile 回退，出现在特定测试） |

## 失败分类（§9）

**零失败 → 无需 PRE_EXISTING_FAILURE / REGRESSION 拆分，也没有任何「为了绿灯而静默修复」的动作。**

1. 本分支在测试时未改动任何 Core 代码（只有 docs/ + scripts/ 新增），因此不存在由本分支引入回归的可能；结果为 main 基线的本机复现。
2. 6 个 skipped 的跳过原因在 `-q` 模式下未捕获（无失败，未追查）；如需完整 skip 清单可另跑 `-rs`。
3. 14 个 warnings 为既有库弃用提示，未处置——不属本任务的修复范围，不静默修改。

## 与仓库记录的差异（如实记录）

`docs/REPOSITORY_STATUS.md` 记录 2026-10-03 基线为 **1197 passed / 5 skipped**；
本机实测为 **1403 passed / 6 skipped**。差异来自该日期之后合入的
Project Model 0.1、Capability Registry、Provider Router 等测试
（本分支 HEAD 含 PR #42/#43/#44）。**本文件记录实测值，不修改旧记录。**

## 环境条件（诚实声明）

测试期间本机同时发生了少量短时 CLI 作业（PROCESS/分析验证，见
`THINKPAD_PROCESS_PIPELINE.md`）——即便如此 0 失败。全套测试为本机
**单线程串行**运行，非 xdist 并行；总时长含全部音频处理测试。

## 优化 001 后的回归复跑（同日同会话）

改动：`auditory/decode.py` + `auditory/spectrogram.py`（ffmpeg 发现/版本探测
memoize，见 `THINKPAD_PROCESS_PERFORMANCE.md` §3）。

```text
命令同 canonical；结果: 1403 passed, 6 skipped, 14 warnings in 256.04s (0:04:16)
exit 0 —— passed/skipped 与基线完全一致，零回归。
```

256s vs 基线 519s 的差异来自热缓存（与优化无关，冷热差效应见性能文档 §1.2）。
