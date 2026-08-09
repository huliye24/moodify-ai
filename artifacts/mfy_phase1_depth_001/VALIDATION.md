# Reference Validation — MFY-PHASE1-DEPTH-001

日期：2026-08-09
参考实现：FFmpeg ebur128（版本记录于测试运行环境；winget ffmpeg）

## P0 验证结果

| 指标 | 参考 | 实测 | 容差 | 结果 |
|---|---|---|---|---|
| integrated_lufs（sine 0.5 gain 440Hz 48k 4s） | ffmpeg ebur128: -9.7 LUFS | 本实现: -10.40 LUFS | ±1.0 LU | PASS（差 0.7） |
| integrated_lufs 立体声身份 | 单声道能量语义 | L=R 加权合并 ≈ mono | ±0.05 | PASS |
| integrated_lufs 短内容 | 门限底线 | -70.0（<1 gating block） | — | PASS（语义正确） |
| loudness_range_lu 短内容 | EBU 3342 不足时长 | None → UNAVAILABLE | — | PASS（不再假 0） |
| loudness_range_lu 动态家族 | 响/静 8s | > 3.0 LU | > 3.0 | PASS |
| true_peak 插值峰值 | 交错满幅样本 | 重建峰值 > 离散峰值 | tp > sp | PASS |
| sample_peak/rms 解析真值 | 数学精确 | -3/-6/-12 dBFS sine | ±0.01/0.02 | PASS（44.1/48/96k 全矩阵） |
| stereo_correlation | 解析 | L=R → 1.0; L=-R → -1.0 | ±1e-3 | PASS |
| dc_offset / clipping / silence | 解析 | 精确 | exact | PASS |
| 截止估计器 | 低通阶梯 8-14k | 单调跟踪 | ±3k 带内 | PASS（ESTIMATOR 语义） |

## 未验证/诚实标注

- true_peak 未与认证响度表（TC Electronics 等）对比——polyphase 为近似，注册表 known_limitations 已记录
- 44.1k 使用 48k K 加权系数（文献接受，<0.1 LU）——注册表记录
- 5.1 环绕通道加权未实现（当前 mono/stereo）——注册表 channel_policy 明确
