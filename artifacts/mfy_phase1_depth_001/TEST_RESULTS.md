# Test Results — MFY-PHASE1-DEPTH-001

日期：2026-08-09

| 套件 | 结果 |
|---|---|
| tests/auditory/test_measurement_correctness.py | 23 passed（含 ffmpeg oracle，PATH 注入） |
| 全量回归 | 207 passed, 5 skipped（1.0 收敛分支基线 184 + 新增 23） |
| Ruff（auditory + tests） | All checks passed |

## 覆盖（08 验收 H 项）

- 解析真值：sample_peak/rms（-3/-6/-12 dBFS × 44.1/48/96k 矩阵）、DC、clipping、silence
- 采样率矩阵：44.1/48/96k
- mono/stereo：响度身份、correlation 身份/反相
- FFmpeg 对比：ebur128 integrated loudness
- 容差边界：oracle 差 0.7 LU
- 短/静音/不可用：LRA UNAVAILABLE、短内容 -70 门限
- 序列化/版本：注册表 schema_version + algorithm_version
