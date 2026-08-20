# MFY-PHASE1-DEPTH-005 Baseline

- Recorded: 2026-08-09
- Base: `codex/moodify-1.0-release-convergence`（Phase I-D `ada3532` 之上）
- 初始测试：251 passed, 5 skipped（含 ffmpeg PATH）

## 现状审计

- Phase I-A..D 已交付（测量/事件/表示/证据权威）
- 无受控实验基础设施；检测器阈值从未被已知扰动验证

## 设计决策

- 新 `auditory/lab/` 包（8 模块）+ 9 个强制算子（versioned 确定性）+ C1-C6 合成源
- Ground truth 从构造与算子参数导出（绝不从检测输出）
- 实验设计中发现并修正的**梯级问题**（真实实验室价值）：
  - HARD_CLIP/NEAR_CLIP 需 pre_gain 12dB（数字满幅削波定义 vs 源峰值 0.3）
  - NEAR_CLIP 必须钳制（clamp）而非归一化（归一化导致近削波样本占比 0.2% < 检测阈值）
  - GAIN_STEP 段长须 ≥ 400ms 窗（短段被窗平滑）；12dB 留阈值余量
  - LOWPASS 实验须用宽带源（C3）——纯音源上低通无效
  - 修复 Phase I-B 遗留 bug：stereo 事件 domain 硬编码 "integrity"（导致 stereo 检测用错窗口时钟）
