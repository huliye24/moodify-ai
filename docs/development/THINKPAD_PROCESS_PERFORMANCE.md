# ThinkPad PROCESS Performance — Baseline, Bottleneck, Optimization 001

**Task:** MOODIFY_THINKPAD_HEAVY_LANE_001 (Phase F/G, Optimization 18/19)
**Date:** 2026-10-05
**Branch:** `feat/thinkpad-heavy-lane-001`
**Tool:** `scripts/benchmark_process.py`（官方 CLI 入口计时 + 进程树内存采样）
**被测材料:** `local_audio_assets/inputs/test_{A_10s,B_60s,C_180s}.wav`（ignored，不入 Git）

---

## 1. 基线（三档输入，官方 PROCESS 路径）

### 1.1 冷启动（本会话首次运行；Windows 冷文件缓存 + Defender 首扫状态）

| 输入 | validate | analyze | process | verify | **total** |
|---|---:|---:|---:|---:|---:|
| A 10s | 0.92 | 6.02 | 2.12 | 2.82 | **11.99** |
| A 10s（重跑） | 0.82 | 5.88 | 2.13 | 2.66 | **11.61** |
| B 60s | 0.87 | 8.87 | 2.63 | 3.20 | **15.70** |
| C 180s | 0.84* | 15.82 | 4.23 | 4.51 | **25.52** |

### 1.2 热态稳态（同会话重复运行，n≥2，取中位数；**含优化 001 后**）

| 输入 | validate | analyze | process | verify | **total** |
|---|---:|---:|---:|---:|---:|
| A 10s | 0.59 | 3.54 | 1.42 | 1.72 | **7.1–7.6** |
| B 60s | 0.56 | 5.36 | 1.86 | 2.18 | **9.3–10.2** |
| C 180s | 0.55 | 10.09 | 2.96 | 3.06 | **16.4–17.1** |

（优化前的热态 analyze 数值保留在 §3 前后对照表中。）

**冷热差 ≈ 35–40%**（C: 25.5s 冷 → ~16.7s 热）——首次运行的开销主要是系统级
文件缓存/Defender 首扫，不是应用逻辑。**报告性能数字必须标注冷/热状态**；
§3 的前后对照全部在热态下测量。

### 1.3 内存（进程树峰值，warm/cold 差异不显著）

| 输入 | analyze peak | process peak | verify peak |
|---|---:|---:|---:|
| A 10s | 126 MB | 91 MB | 115 MB |
| B 60s | 281 MB | 175 MB | 206 MB |
| C 180s | 655 MB | 377 MB | 428 MB |
| （validate：36 MB，与输入无关） | | | |

内存随时长线性增长（analyze ~3.6 MB/音频秒），180s 输入已达 655MB —— 在
本机 ~15.5GB / 当时可用 ~1GB 的 RAM 条件下，长输入 + 并发作业会触到内存边界。

### 1.4 阶段成本结构（固定 vs 随音频时长）

由 A/B/C 三点线性拟合（热态，含优化 001 后）：

```text
validate:  0.55–0.59s  纯固定（进程启动 + import moodify.release_cli ≈ 0.6s）
analyze:   ≈3.2s 固定 + ≈0.038 s/音频秒   （固定 = CLI 导入 0.6s + scipy.signal 懒导入 1.8s + 解码/两次频谱图/报告装配的固定部分）
process:   ≈1.3s 固定 + ≈0.009 s/音频秒
verify:    ≈1.7s 固定 + ≈0.008 s/音频秒
```

180s 输入时 analyze 约 2/3 随时长（固定占 ~31%）；60s 输入约 40% 固定；
10s 输入的 process 约 93% 固定。**「固定开销主导」还是「DSP 主导」取决于输入长度，
两句话各自都有数字支撑。**

## 2. 瓶颈定位（cProfile，analyze/B 档 8.89s 冷态）

```text
compute_metrics                 3.13s   ← 其中 scipy.signal 首次导入 1.80s（懒导入，auditory/loudness.py）
  subprocess 合计               2.77s
    ├─ generate_spectrogram ×2  1.75s   ← 2 次独立 ffmpeg showspectrumpic（各自解码输入）
    ├─ _ffmpeg_version ×2       0.30s   ← 【冗余】metadata 探针，每次渲染后再 spawn 一次 ffmpeg -version
    ├─ decode（ffmpeg 解码）    0.24s
    ├─ ffprobe probe            0.22s
    ├─ decode.ffmpeg_version×1  0.15s   ← 【冗余】同一条命令第 3 次 spawn
    └─ check_output ×2          0.13s
compute_stereo_metrics          0.55s
_stft_views + npz_compressed    0.50s
CLI 启动导入                    0.69s（numpy 0.20 + pydantic 0.06 + moodify.contracts 链 0.30+）
```

**结论（有数字支撑）：**
1. **短输入被固定开销主导**（10s 输入的 process 93% 是固定成本）；长输入的 analyze 由
   逐秒 DSP 主导（180s 时约 2/3 随时长）。两句话都是事实，取决于输入长度。
2. **三个独立可攻击的固定成本**：CLI 导入 0.6s/阶段 ×4 阶段；analyze 的 scipy.signal
   懒导入 1.8s；**冗余的 ffmpeg -version spawn ×3（热态 0.167s/次，实测 3 次循环 = 0.500s）**。
3. 频谱图渲染两次各自解码输入（下一步候选：单 ffmpeg 双子图输出；涉及 evidence 记录格式，本轮不做）。

## 3. Optimization 001（本轮实施）——ffmpeg 发现与版本探测去重

**改动（仅 Core，2 文件）：**
- `auditory/decode.py`：`_which_ffmpeg` / `_which_ffprobe` / `ffmpeg_version` 加
  `lru_cache(maxsize=1)`（进程内单次发现/单次版本探测；异常不被 lru_cache 缓存，
  缺 binary 仍在每次调用时如实抛出）。
- `auditory/spectrogram.py`：删除本模块私有的重复实现（`_ffmpeg` / `_ffmpeg_version`
  各自独立探测 PATH 并 spawn `ffmpeg -version`），委托给 decode 的已缓存实现。
  探测顺序、异常类型（FfmpegNotFound）、返回值完全一致。

**机制性预测：** analyze 每次消除 2 次 `ffmpeg -version` spawn；单次热态成本实测
0.167s（`for i in 1 2 3; ffmpeg -version` = 0.500s）→ 预测节省 ≈0.33s/analyze。

**实测（热态稳态前后中位数，同机同会话）：**

| 输入 | analyze 前 | analyze 后 | Δ |
|---|---:|---:|---:|
| A 10s | 3.736s | 3.539s | **−0.197s（−5.3%）** |
| B 60s | 5.825s | 5.364s | **−0.461s（−7.9%）** |

同批数据中 process/verify 阶段前后无变化（与改动只影响 analyze 路径一致）。
B 档 −0.46s 高于机制预测 0.33s —— 后半段采样仍在持续受机器预热漂移影响
（after 组最后两次最快），故 Δ 的有效区间应视为 **−0.2 ～ −0.46s**；
两种输入的改善方向与机制一致，但幅度带有运行间漂移，不做精确归因。

**零行为变化验证：**
- 优化前后对同输入生成的 `spectrum_linear.png` / `spectrum_log.png` **sha256 逐位一致**。
- 针对性测试 199 passed（tests/auditory + msp02 + mamse001）。
- 全量回归套件：见 `THINKPAD_TEST_BASELINE.md` 更新节。

## 4. 已识别但未实施（留给后续任务，避免一次改动过大）

| 候选 | 预估收益 | 为什么本轮不做 |
|---|---|---|
| CLI 导入瘦身（release_cli → release → contracts/fingerprint 链 0.30s+，numpy/pydantic 0.26s） | ~0.2–0.3s × 4 阶段 | 触及所有命令的入口导入结构，需单独任务 + 全量回归 |
| 两次频谱图合并为单 ffmpeg（一次解码两路输出） | ~0.2–0.5s/analyze（长输入更大） | 改变 evidence 记录的 command 结构 + 旧版 ffmpeg 回退分支，非低风险 |
| scipy.signal 导入 1.8s | 结构性 | 被 loudness 真实使用，无替代余地（无低风险选项） |
| 并行化（xdist 不属于产品路径，不改产品） | — | 进程模型是产品设计（CLI per job），不改架构 |
