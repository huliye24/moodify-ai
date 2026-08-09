# MFY-PHASE1-DEPTH-001 Baseline

- Recorded: 2026-08-09
- Base: 当前工作分支 `codex/auditory-intelligence-unification` @ `6446f75`（含 Moodify 1.0 RC 4 commits e81108d..fdac22d）
- main: `0b355e7`（未推进；任务包"从最新 main"在现实中=当前分支，差异已记录于 mfy_1_0_rc_001/baseline.md）
- 实现目标：`moodify/auditory/metrics.py`、`stereo.py`、`models.py`
- 初始测试：184 passed（1.0 收敛分支基线；含 ffmpeg PATH 时全量 207 passed, 5 skipped）

## 审计发现（P0）

| 问题 | 位置 | 修复 |
|---|---|---|
| 非 48k/44.1k 采样率 K 加权未重采样（直接套 48k 系数） | metrics.py `_k_weighted` | 新 loudness.py：其他采样率先 resample_poly 到 48k |
| true_peak 为 Hann 卷积粗糙近似 | metrics.py `true_peak_db` | 新 true_peak.py：4x polyphase 过采样 |
| 立体声响度为 mono-mean 近似（非通道独立加权） | metrics.py `integrated_lufs` | 新 loudness.py：每通道 K 加权 + 加权能量合并 |
| LRA 短内容返回 0.0（误导） | metrics.py `loudness_range_lu` | 返回 None → MetricValue UNAVAILABLE |
| plr_db method 标签 "derived" 语义不清 | metrics.py | 改 "peak-to-rms"；注册表定义明确（非 EBU PLR） |
| 28 指标无权威注册表 | — | 新增 measurement_registry_v1.yaml + 加载器 |
