# Moodify 分析报告 — Control Theory.mp3

- 报告契约：`moodify.msp_report/0.2`（协议 `moodify.sound/0.2`）
- case：`case_5fe1d78c2fd54271ab51889b7d30b80f`
- 生成时间：2026-10-02T02:09:10.344953+00:00
- 源音频：`Control Theory.mp3` / `sha256:2512d01011c997aa63591a996b97e5115c1775be430dc213c8b47f641d244896`
- 技术状态：**PARTIAL** · NO_TECHNICAL_BLOCKERS


## 判断边界

| 评估层 | 状态 |
| --- | --- |
| L1 测量（技术状况） | EXECUTED |
| L2 受控比较（感知差异） | NOT_RUN |
| L3 音乐判断（表达/比例/意图） | NOT_PROMISED |
| L4 制作判断（可编辑/可追溯） | NOT_PROMISED |
| L5 文化判断（人类作者身份） | NOT_PROMISED |

## 测量

### 响度与动态

| 指标 | 值 | 单位 | 状态 | 可见性 |
| --- | --- | --- | --- | --- |
| `crest_factor_db` | 14.32 | dB | VALID | 能看到峰均比（动态压缩的代理指标）；看不到压缩是音乐风格还是技术损伤 |
| `integrated_lufs` | -16.33 | LUFS | VALID | 能看到全曲门限后的稳态响度；看不到响度随段落的叙事分布，也不判断该响度是否适合特定平台或审美 |
| `loudness_range_lu` | 5.37 | LU | VALID | 能看到响度分布跨度（LRA）；看不到动态处理是风格还是损伤，短于 6s 的素材不可用 |
| `plr_db` | 14.82 | dB | VALID | 能看到真峰与 RMS 的差值；与 crest_factor_db 一样不判断动态的因果 |
| `rms_dbfs` | -16.11 | dBFS | VALID | 能看到平均信号能量；看不到响度感知（K 计权见 integrated_lufs） |
| `sample_peak_dbfs` | -1.79 | dBFS | VALID | 能看到采样点峰值；看不到采样点之间的真峰（对照 true_peak_dbfs） |
| `true_peak_dbfs` | -1.29 | dBFS | VALID | 能看到 4x 过采样重建峰值裕量；看不到后续有损编码是否引入新的intersample peak |

### 信号完整性

| 指标 | 值 | 单位 | 状态 | 可见性 |
| --- | --- | --- | --- | --- |
| `clipping_sample_count` | 0 | samples | VALID | 能看到 ≥0.999 满幅样本数；看不到软削波、模拟饱和或限幅器先期损伤 |
| `clipping_sample_ratio` | 0 | ratio | VALID | 能看到满幅样本占比；同 clipping_sample_count 的盲区 |
| `dc_offset_left` | 3.47e-05 | linear | VALID | 能看到左声道直流偏置；看不到偏置来自录音链还是下游处理 |
| `dc_offset_right` | -2.79e-05 | linear | VALID | 能看到右声道直流偏置；看不到偏置来自录音链还是下游处理 |
| `finite_sample_ratio` | 1 | ratio | VALID | 能看到有限样本占比（分析置信度代理）；只反映数值完整性 |
| `invalid_sample_count` | 0 | samples | VALID | 能看到非有限（NaN/Inf）样本数；看不到极低电平下的数值异常 |
| `longest_silence_seconds` | 1.3 | s | VALID | 能看到最长连续静音时长；看不到该静音在曲式中的位置与功能 |
| `near_clipping_sample_count` | 0 | samples | VALID | 能看到 0.95–0.999 区间样本数；该数值本身不定罪（可能是正常母带余量策略） |
| `silence_ratio` | 0.006357 | ratio | VALID | 能看到 -60 dBFS 以下窗口占比；看不到留白是音乐意图还是缺陷 |

### 频谱

| 指标 | 值 | 单位 | 状态 | 可见性 |
| --- | --- | --- | --- | --- |
| `estimated_high_frequency_cutoff_hz` | 13130.9 | Hz | VALID | 能看到 99.5% 能量截止频率；看不到截止是母带选择还是低质量编码残留 |
| `estimated_noise_floor_dbfs` | -22.3 | dBFS | VALID | 能看到 p10 帧电平（本底噪声代理）；看不到噪声类型（嘶声/嗡声/量化噪声） |
| `spectral_centroid_hz` | 935.2 | Hz | VALID | 能看到功率加权中心频率（明暗代理）；看不到音色是否正确或讨喜 |
| `spectral_flatness` | 0.00084 | ratio | VALID | 能看到噪声性/纯音性整体倾向；看不到具体哪个频带偏离 |
| `spectral_flux` | 2573.09 | mag/frame | VALID | 能看到平均帧间谱变化（活动度代理）；看不到节奏或瞬态的语义 |
| `spectral_rolloff_85_hz` | 1318.4 | Hz | VALID | 能看到 85% 能量累积边界；不定位具体频段问题（结合频段比读取） |
| `spectral_rolloff_95_hz` | 4289.1 | Hz | VALID | 能看到 95% 能量累积边界；不定位具体频段问题（结合频段比读取） |

### 频段能量占比

| 指标 | 值 | 单位 | 状态 | 可见性 |
| --- | --- | --- | --- | --- |
| `air_10000_16000_hz` | 0.0128723 | ratio | VALID | — |
| `bass_60_120_hz` | 0.129147 | ratio | VALID | — |
| `brilliance_5000_10000_hz` | 0.0264641 | ratio | VALID | — |
| `core_mid_500_2000_hz` | 0.265378 | ratio | VALID | — |
| `low_mid_120_250_hz` | 0.103679 | ratio | VALID | — |
| `mid_250_500_hz` | 0.12163 | ratio | VALID | — |
| `presence_2000_5000_hz` | 0.0693295 | ratio | VALID | — |
| `sub_20_60_hz` | 0.270294 | ratio | VALID | — |
| `ultrasonic_16000_24000_hz` | 0.00120783 | ratio | VALID | — |

### 立体声

| 指标 | 值 | 单位 | 状态 | 可见性 |
| --- | --- | --- | --- | --- |
| `mid_energy_ratio` | 0.912279 | ratio | VALID | 能看到中信号能量占比；看不到单声道兼容性的听感后果 |
| `negative_correlation_ratio` | 0 | ratio | VALID | 能看到负相关帧占比（相位风险代理）；看不到哪个频段/时刻在反相（查 timeline） |
| `phase_risk_ratio` | 0 | ratio | VALID | 能看到低相关帧占比（相位风险代理）；看不到哪个频段/时刻在反相（查 timeline） |
| `side_energy_ratio` | 0.087721 | ratio | VALID | 能看到侧信号能量占比；看不到单声道兼容性的听感后果 |
| `side_to_mid_db` | -10.17 | dB | VALID | 能看到侧/中能量差（宽度代理）；不等于听感宽度 |
| `stereo_correlation` | 0.8252 | ratio | VALID | 能看到声道间线性相关；看不到声像的具体布局与听感宽度 |
| `stereo_width_proxy` | 0.1748 | ratio | VALID | 能看到 1-|相关| 宽度代理；不等于听感宽度 |

### 格式

| 指标 | 值 | 单位 | 状态 | 可见性 |
| --- | --- | --- | --- | --- |
| `channels` | 2 | ch | VALID | 能看到声道数；不判断布局选择的意图 |
| `duration` | 204.56 | s | VALID | 能看到媒体时长；不判断时长变化的原因 |
| `sample_rate` | 48000 | Hz | VALID | 能看到采样率；不判断重采样历史 |

### 其他

| 指标 | 值 | 单位 | 状态 | 可见性 |
| --- | --- | --- | --- | --- |
| `band_energy_air_10000_16000_hz` | 3963.05 | linear-power | VALID | — |
| `band_energy_bass_60_120_hz` | 39761.1 | linear-power | VALID | — |
| `band_energy_brilliance_5000_10000_hz` | 8147.64 | linear-power | VALID | — |
| `band_energy_core_mid_500_2000_hz` | 81703.3 | linear-power | VALID | — |
| `band_energy_low_mid_120_250_hz` | 31920.2 | linear-power | VALID | — |
| `band_energy_mid_250_500_hz` | 37446.8 | linear-power | VALID | — |
| `band_energy_presence_2000_5000_hz` | 21344.9 | linear-power | VALID | — |
| `band_energy_sub_20_60_hz` | 83216.8 | linear-power | VALID | — |
| `band_energy_ultrasonic_16000_24000_hz` | 371.862 | linear-power | VALID | — |

## 发现

无。未发现触发阈值的技术风险。

## 后处理方案

状态：**DRAFT_PLAN_NOT_EXECUTED**（方案不等于执行；执行需显式提交 process 作业）

无自动算子建议（未发现可安全映射到标准算子的发现）。

下一步（可直接复制的命令形式）：

```text
moodify protocol process <job.json>  # {"protocol": "moodify.sound/0.2", "type": "process", "source": "Control Theory.mp3", "preset": "<preset>", "output_dir": "<dir>"}
```

## 证据与溯源

- 扫描 profile：`MFY-WSE-SCAN-PROFILE-001`；频谱图：`scan/spectrum_linear.png`, `scan/spectrum_log.png`
- 时间线窗口：409（`scan/timeline_metrics.jsonl`）
- STFT 阵列：`scan/analysis_data.npz`
- Core 1.0.0-rc.1 · 判断规则 1.0 · ffmpeg ffmpeg version 8.1.1-full_build-www.gyan.dev Copyright (c) 2000-2026 the FFmpeg developers
- profile 参数哈希：`sha256:f0ff177ddc7b05d3a934848b9fd55d79a453b908707231360e772850afde45f1`

> 本报告只覆盖 L1 测量层（以及标注为 EXECUTED 的层）。未标注 EXECUTED 的层不构成任何听感、音乐或商业判断。
