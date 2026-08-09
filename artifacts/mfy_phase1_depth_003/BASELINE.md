# MFY-PHASE1-DEPTH-003 Baseline

- Recorded: 2026-08-09
- Base: `codex/moodify-1.0-release-convergence`（Phase I-B `8767246` 之上）
- 初始测试：222 passed, 5 skipped（含 ffmpeg PATH）

## 现状审计

- Phase I-A（测量权威：metrics/loudness/true_peak/registry）、Phase I-B（时间听觉：events 包）已交付
- 无统一跨尺度表示：timeline.py（固定 1s 窗）与 events 窗口无共同时钟契约
- metrics.py 的 bands 定义与 temporal events 的 spectrum 域各自为政（G10 需集中）

## 设计决策

- 新 `auditory/representation/` 包（7 模块）+ 4 尺度注册（S0 MICRO 40/20、S1 SHORT 400/100、S2 MEDIUM 2000/500、S3 TRACK）
- 样本时钟优先（sample-index-first）：窗口 (start_sample, end_sample) → ms 派生；跨尺度映射 = 区间算术（无昂贵图）
- 特征平面 → Phase I-A 权威（feature_registry 解析 measurement_registry；BANDS 集中定义）
- S1 的 STFT 每窗计算，S2 独立 FFT（不同窗长无法复用——文档记录；S1 内 band 特征共享一次 FFT）
- 缺失值 NaN（JSON null / NPZ NaN），不静默 0 填充
- S3 = compute_metrics 全局（与 Phase I-A 完全一致）
- 事件叠加：I-B 事件 → S1 重叠窗索引
