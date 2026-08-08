# AEP-ACU-004｜Old vs New Report Diff

> 日期：2026-07-03
> 对比：BAND_6 (legacy) vs BAND_7 (new default)

---

## 1. 频段定义差异

```
                    BAND_6 (legacy)              BAND_7 (v0.4 default)
                    ==============              ====================
Sub      20-60 Hz   [████████]                  [████████]
Bass     60-250 Hz  [████████████]              [████████████]
Low-Mid  250-500 Hz [█████]                     [█████]
Mid      500-2 kHz  [████████████████]           [████████████████]
Presence 2-5 kHz    [████████████████████]       [████████████████████]
          5-8 kHz   [         GAP          ]     [████████████] ← Brilliance NEW
Air      8-16 kHz   [████████████████████████]   [████████████████████████]
```

## 2. 6.5 kHz 测试音对比

| 测试 | BAND_6 输出 | BAND_7 输出 |
|------|-----------|-----------|
| 6.5 kHz 纯音 | presence: -120 dB, air: -120 dB | brilliance: 0.0 dB |
| 诊断覆盖 | **0%** — 完全漏记 | **100%** — 正确捕获 |
| 风险提示 | 无 | "sibilance / clarity gap" |

## 3. 报告字段变化

### AudioMetrics.to_dict() — 旧版

```json
{
  "spectrum": {
    "sub_bass": -12.0,
    "bass": -8.0,
    "low_mid": -10.0,
    "mid": -6.0,
    "presence": -4.0,
    "air": -15.0
  }
}
```

### AudioMetrics.to_dict() — 新版

```json
{
  "band_spec": "7",
  "spectrum": {
    "sub_bass": -12.0,
    "bass": -8.0,
    "low_mid": -10.0,
    "mid": -6.0,
    "presence": -4.0,
    "brilliance": -2.0,
    "air": -15.0
  }
}
```

新增字段：
- `band_spec`: 标记使用的频段版本
- `brilliance`: 5-8 kHz 独立能量值

## 4. 诊断风险提示差异

| 频段 | BAND_6 风险提示 | BAND_7 风险提示 |
|------|---------------|---------------|
| Sub | 无 | rumble |
| Bass | 无 | mud |
| Low-Mid | 无 | boxiness |
| Mid | 无 | nasal |
| Presence | 无 | harshness |
| Brilliance | **不存在** | **sibilance / clarity gap** ← NEW |
| Air | 无 | hiss |

## 5. 5 类样本验证结果

| 实验 | 样本 | BAND_6 | BAND_7 | 判定 |
|------|------|--------|--------|------|
| E1 | 6.5 kHz sibilance | 漏记 100% | brilliance: -1.4 dB | PASS |
| E2 | 8 kHz harsh | 混淆 Air/Presence | brilliance/air 分离清晰 | PASS |
| E3 | 12 kHz air | 正常 | brilliance: -120, air: 0 | PASS |
| E4 | 平衡频谱 | 正常 | 7 频段全有值 | PASS |
| E5 | AI 高频噪声 | 无法区分 | brilliance: -8.0, air: -3.5 | PASS |

## 6. 回滚方案

```python
# 恢复 BAND_6 为默认：
# bands.py:
DEFAULT_BANDS = BAND_6   # 改回这一行
DEFAULT_EDGES = BAND_6_EDGES
DEFAULT_NAMES = BAND_6_NAMES

# v01_analyzer.py:
from moodify.bands import (
    BAND_6_EDGES as BAND_EDGES,  # 改回
)
```
