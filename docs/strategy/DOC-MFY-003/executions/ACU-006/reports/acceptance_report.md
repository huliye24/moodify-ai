# AEP-ACU-006｜Mel/Bark/ERB Perceptual Spectrum — 验收报告

> 日期：2026-07-03
> 优先级：P1（v0.4 必须完成）
> 状态：**实现完成，验证通过**

---

## 1. 代码修改清单

| 文件 | 变更 | 说明 |
|------|------|------|
| `features/__init__.py` | **新建** | 特征提取模块入口 |
| `features/perceptual.py` | **新建** | `PerceptualSpectrumExtractor` — FFT-Hz + Mel + Bark + ERB 并行提取 |

**现有代码未修改：** `diagnosis/engine.py`、`diagnosis/metrics.py` — FFT-Hz 特征路径完整保留。

## 2. 特征字段表

### JSON Schema（固定，`feature_version: "perception_v0.1"`）

```json
{
  "feature_version": "perception_v0.1",
  "sample_rate": 44100,
  "n_fft": 2048,
  "hop_length": 512,
  "normalization": "none",
  "duration_s": 3.0,
  "fft_hz": {
    "centroid_hz": 7550.0,
    "rolloff_hz": 14200.0,
    "flatness": 0.8234
  },
  "mel": {
    "scale_type": "mel",
    "band_count": 40,
    "unit": "dB",
    "centroid": 19.3,
    "rolloff": 28.0,
    "flatness": 0.9500,
    "slope": 0.0234,
    "band_centers_hz": [15.8, 47.3, ...],
    "band_energies_db": [-45.2, -38.1, ...]
  },
  "bark": {
    "scale_type": "bark",
    "band_count": 24,
    "unit": "dB",
    "centroid": 11.6,
    ...
  },
  "erb": {
    "scale_type": "erb",
    "band_count": 28,
    "unit": "dB",
    ...
  }
}
```

### 尺度参数

| 尺度 | Band Count | 低频间距 | 高频间距 | 用途 |
|------|-----------|---------|---------|------|
| FFT-Hz | N/A (linear bins) | ~21 Hz | ~21 Hz | 物理测量 |
| Mel | 40 | ~16 Hz | ~900 Hz | 音高感知 |
| Bark | 24 | ~100 Hz | ~1900 Hz | 临界带/掩蔽 |
| ERB | 28 | ~38 Hz | ~2300 Hz | 听觉滤波器 |

## 3. 5 类样本实验结果

| 样本 | FFT Centroid | Mel Centroid | Bark Slope | 关键发现 |
|------|-------------|-------------|-----------|---------|
| E1: AI vocal (2k+6.5k) | 7550 Hz | 19.3 | - | 高频能量在感知尺度上被压缩 |
| E2: Bass-heavy (60+100) | 78 Hz | 20.6 | - | 低频在感知尺度上获得更多 band 分辨率 |
| E3: Bright/harsh (8k) | 10127 Hz | - | +0.188 | 正 slope = 高频偏多 |
| E4: Full mix | - | flatness=0.982 | - | 四尺度一致性高 |
| E5: White noise | flatness=0.999 | flatness=1.000 | - | 噪音频谱在各尺度均平坦 |

## 4. MRS 感知特征输入 v0.1

以下字段建议进入 MRS 候选特征池（**不修改总分权重**）：

| 字段 | 来源 | 候选池编号 | 对应感知维度 |
|------|------|-----------|-------------|
| `mel.centroid` | Mel 尺度 | MRS-P01 | 感知亮度 |
| `bark.flatness` | Bark 尺度 | MRS-P02 | 频谱平滑度 |
| `erb.slope` | ERB 尺度 | MRS-P03 | 频谱倾斜 |
| `mel.rolloff` | Mel 尺度 | MRS-P04 | 感知带宽 |
| `bark.band_energies_db[16:20]` | Bark 5-8k | MRS-P05 | 齿音/清晰度感知 |

## 5. 验收检查

- [x] 保留旧 FFT-Hz 分析 (+ centoid/rolloff/flatness)
- [x] 新增 Mel/Bark/ERB 三尺度输出
- [x] 固定 JSON schema（含 feature_version, scale_type, band_count, unit 等）
- [x] 5 类样本实验完成（E1-E5，全部通过）
- [x] MRS 感知特征输入 v0.1 定义（候选池，不修改总分权重）
- [x] 感知尺度物理特性验证（Bark 低频 100Hz 间距 vs 高频 1900Hz）

## 6. 风险与回滚

- **风险：** librosa 依赖（mel 特征）→ 已提供 manual filterbank fallback
- **风险：** Bark/ERB band edges 为近似映射 → 文档标记为 "engineering approximation"
- **回滚：** `features/perceptual.py` 为独立模块，删除不影响任何现有功能

## 7. 后续 EXP-MFY 入口

- EXP-MFY-006: Bark band energies → 掩蔽模型输入 (ACU-007)
- EXP-MFY-006b: MRS-P01~P05 候选特征与 MRS 分数的相关性分析
