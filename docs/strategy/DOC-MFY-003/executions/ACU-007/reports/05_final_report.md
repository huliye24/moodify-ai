# AEP-ACU-007｜Psychoacoustic Masking Prototype — 最终报告

> 日期：2026-07-03
> 优先级：P2（条件合入）
> 状态：**Prototype 完成，验收标准达成**

---

## 1. 代码修改清单

| 文件 | 变更 | 说明 |
|------|------|------|
| `perception/__init__.py` | **新建** | 感知层模块入口 |
| `perception/masking.py` | **新建** | `MaskingModel` + `PsychoacousticFeatures` + 全部计算逻辑 |

**未修改任何现有文件。**

## 2. 输入/输出 Schema

### 输入（来自 AEP-ACU-006）

```json
{
  "bark": {
    "band_centers_hz": [100.0, 201.0, ...],
    "band_energies_db": [-45.2, -38.1, ...]
  }
}
```

### 输出（本任务新增）

```json
{
  "feature_version": "psychoacoustic_v0.1",
  "masking": {
    "threshold_db": [-60.0, -55.3, -48.1, ...],
    "audible_residual_db": [0.0, 0.0, 0.0, ...],
    "residual_above_threshold_bands": 3
  },
  "risk_proxies": {
    "sharpness_proxy": 0.125,
    "sharpness_note": "risk proxy / hypothesis",
    "fatigue_index": 0.270,
    "fatigue_note": "risk proxy / hypothesis",
    "sibilance_risk": 0.600,
    "sibilance_note": "risk proxy / hypothesis — 5-8 kHz",
    "sibilance_band_energy_db": 0.0,
    "sibilance_audible_residual_db": 2.5
  }
}
```

## 3. 计算逻辑

### 3.1 掩蔽阈值

```
For each Bark band m (as masker):
  For each Bark band b (as target):
    delta = b - m
    if delta >= 0:  spread[m→b] = masker_level - 27.0 * delta  (upward)
    else:           spread[m→b] = masker_level + 10.0 * delta  (downward)
  threshold[b] = max(threshold[b], spread[m→b])

Floor: max(threshold, absolute_threshold_db)
```

### 3.2 可听残差

```
residual[b] = band_energy[b] - threshold[b]
```

### 3.3 齿音风险

```
sibilance_risk = f(energy in Bark 15-20, residual in Bark 15-20)
              = min(1.0, energy_excess/15 * 0.6 + residual/10 * 0.4)
```

### 3.4 疲劳指数

```
fatigue = 0.25 * presence_score + 0.45 * sibilance_score + 0.30 * air_score
```

### 3.5 尖锐度代理

```
sharpness = weighted_mean(residual_pos, weights increasing with Bark number)
```

## 4. 6 样本实验结果

| 样本 | Sharpness | Fatigue | Sibilance | 解释 |
|------|----------|---------|----------|------|
| E1: Clean vocal (1k+2k) | 0.000 | 0.000 | 0.000 | 无高频内容 → 无风险 |
| E2: Harsh 2-5k | 0.000 | 0.083 | 0.000 | Presence 区轻度疲劳 |
| E3: Sibilance (6.5k) | 0.000 | 0.270 | **0.600** | 齿音风险最高 |
| E4: Vocal full | 0.000 | 0.186 | 0.154 | 含轻度齿音 |
| E5: Dense mix | 0.000 | 0.163 | 0.463 | 多频段含齿音分量 |
| E6: Bass heavy | 0.000 | 0.000 | 0.000 | 无高频 → 零风险 |

**验证：** E3（齿音样本）sibilance_risk > E6（低音样本）sibilance_risk ✓

## 5. 可配置阈值

所有阈值通过 `MaskingConfig` dataclass 暴露：

| 参数 | 默认值 | 含义 |
|------|--------|------|
| `spreading_slope_low` | 27.0 dB/Bark | 低频→高频掩蔽效率 |
| `spreading_slope_high` | -10.0 dB/Bark | 高频→低频掩蔽效率（更弱） |
| `absolute_threshold_db` | -60.0 dB | 相对听阈 |
| `sibilance_risk_threshold_db` | -15.0 dB | 齿音风险触发线 |
| `sharpness_high_weight_start_bark` | 14 | ~3 kHz 以上加权 |
| `temporal_window_ms` | 5.0 ms | 时间掩蔽窗口 |

## 6. 验收检查

- [x] `psychoacoustic_features` schema 稳定输出 (feature_version: "psychoacoustic_v0.1")
- [x] Bark/ERB band mapping 可复现（来自 ACU-006）
- [x] masking threshold、audible residual 非空且数值合理
- [x] 5-8 kHz sibilance 风险单独报告
- [x] 6 样本实验完成
- [x] 原有 FFT/mel/bark/ERB 未破坏（独立模块）
- [x] 所有听感判断标记为 "risk proxy / hypothesis"

## 7. MRS v0.4 输入

以下字段建议作为 MRS 可选输入（不改总分权重）：

| 字段 | MRS 候选池 |
|------|-----------|
| `risk_proxies.sibilance_risk` | MRS-P06 |
| `risk_proxies.fatigue_index` | MRS-P07 |
| `risk_proxies.sharpness_proxy` | MRS-P08 |
| `masking.residual_above_threshold_bands` | MRS-P09 |

## 8. 回滚方案

删除 `perception/` 目录。无其他文件修改。

## 9. 不实装项

| 条目 | 原因 | 替代方案 |
|------|------|---------|
| 完整 PEAQ (BS.1387) | v0.4 只做原型 | 本模块的 spreading function 为基础 |
| 时间掩蔽完整模型 | 需要逐帧分析 | 简化为 post-masking flags |
| 绝对 SPL 校准 | 需要硬件校准 | 使用相对归一化 |
