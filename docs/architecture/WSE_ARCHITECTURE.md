# WSE Architecture

WSE 回答“声音发生了什么”，不回答“是否更好”。所有记录必须带 adapter version、单位、时间范围、backend、warnings 和 confidence；不可计算时写 `null`。

| 子模块 | 输入 | 输出/指标 | 当前状态 | 后续实验 | 验收 |
|---|---|---|---|---|---|
| Loudness and dynamics | PCM, sample rate | peak, RMS, crest, LUFS, LRA, true peak, clipping | Partial；bridge 有 peak/RMS/crest/LUFS，LRA/TP null | 与 BS.1770/R128 工具交叉验证 | 固定音频与参考工具误差在预注册阈值内 |
| Spectrum and tonal balance | PCM | centroid, entropy, flux, band fractions/tilt | Partial | 窗长/曲风稳定性、校准噪声 | 固定参数重放一致，单位完整 |
| Transient analysis | PCM | onset/transient density, crest evolution | Experimental/partial proxy | 与人工标注鼓点对照 | 报告 precision/recall 与失败段落 |
| Stereo and channel | stereo PCM | L/R correlation, width, balance | Partial | mono/反相/多声道边界 | 合成夹具精确通过 |
| Phase and correlation | channels/stems | correlation, phase rotation warnings | Partial | 频带相位与 mono fold-down | 已知相位夹具检测稳定 |
| Masking analysis | mix/stems | band/time masking candidates | Experimental | 与 stem mute/专家标注对照 | 不把能量重叠直接称可听掩蔽 |
| Residual analysis | aligned A/B | gain, residual, relative residual, diff SNR | Partial | 对齐、延迟和非线性残差 | 已知 gain/delay 夹具 |
| Section-level evolution | sections + PCM | per-section trajectories | Planned | 窗口与 MSE section 联合 | 相同 section IDs 可重放 |
| Before/after comparison | aligned assets | waveform/spectrum/dynamic deltas | Partial | loudness-matched comparison | 身份、对齐与参数齐全 |
| Measurement confidence | metric provenance | confidence/status/reason | Planned | backend disagreement model | 每值都有 available/null 原因 |

当前实现映射：`moodify-core-package/src/moodify/v01_analyzer.py`、`reality_metrics.py`、`features/`、`perception/`、`moodify-bridge/src/moodify_bridge/metrics.py`。任何 RMS→LUFS 近似只能标为 proxy，不得写 standard loudness。

