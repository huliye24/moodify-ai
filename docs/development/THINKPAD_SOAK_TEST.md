# ThinkPad PROCESS Soak Test (Phase H)

**Task:** MOODIFY_THINKPAD_HEAVY_LANE_001
**Date:** 2026-10-05
**Branch:** `feat/thinkpad-heavy-lane-001`
**Tool:** `scripts/soak_process.py`（15 连发 `moodify protocol process`，每作业独立输出目录）

---

## 命令

```bash
python scripts/soak_process.py --input local_audio_assets/inputs/test_A_10s.wav --jobs 15
```

## 结果（run `soak/test_A_10s_20261005_161230`）

```text
jobs:              15/15 ok（0 失败、0 崩溃）
process 时长:      1.291s – 1.579s（first 1.471 / last 1.486 —— 无逐作业劣化）
峰值内存（进程树）: 91.0 – 91.4 MB，first 91.1 / last 91.1 —— 无增长趋势
output 哈希校验:   0 mismatch（15/15 与 CLI 自报 sha256 一致）
孤儿解码进程:      ffmpeg/ffprobe before=0 after=0 —— 无进程泄漏
工作目录残留:      none（每作业目录只含 job.json + out/）
模型缓存:          N/A —— 0.1 process 路径不加载任何模型
status:            pass
```

**确定性观察（附加证据）：** 15 次输出 WAV 的 sha256 与当日更早的独立运行**逐位相同**
（`07826cc75be7…`），说明同一 Core + 同一输入 + 同一预设的 process 输出可复现。

## 诚实记录

1. **首轮 soak 的 `hash_ok=False` 是工具 bug，不是管道问题。** soak 脚本曾给实际哈希
   加了 `sha256:` 前缀再与 CLI 原始 hex 比较，15/15 误报失败；已修复
   （容忍两种形式），复测 15/15 通过。两次运行都在本目录留痕。
2. **「内存泄漏」在本管道的语义**：每个作业是一个全新 CLI 进程（产品设计如此），
   因此这里测的是逐作业峰值趋势与进程回收，而非常驻进程泄漏。常驻服务端泄漏
   检测属于 Cloud Production / node 队列的范畴，不在本路径。
3. 未测量 GPU（本机无 CUDA，见 baseline §5）；未测并发多作业（V1 产品路径为
   单作业顺序执行；并发压力属未来任务）。
