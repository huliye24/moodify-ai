# AEP-ACU-004｜验收报告

> 日期：2026-07-03
> 任务：7-Band Perceptual Frequency Map
> 优先级：P1（v0.4 必须完成）
> 状态：**实现完成，验证通过**

---

## 修改文件清单

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `src/moodify/bands.py` | **修改** | DEFAULT 切换为 BAND_7；新增 `risk_hint` 字段；新增 `get_risk_hints()`；`get_band_edges()` 默认改为 "7" |
| `src/moodify/v01_types.py` | **修改** | `AudioMetrics` 新增 `rms_brilliance` 和 `band_spec` 字段；`to_dict()` 新增 brilliance |
| `src/moodify/v01_analyzer.py` | **修改** | 导入 `DEFAULT_EDGES`；`analyze()` 新增 `band_spec` 参数；频谱图支持 7 频段 |
| `src/moodify/reality_metrics.py` | **修改** | 导入 `DEFAULT_EDGES` 替代 `BAND_6_EDGES` |

## BAND_7 默认启用点

```python
# bands.py:62-66
DEFAULT_BANDS: ClassVar[dict] = BAND_7      # ← 这里
DEFAULT_EDGES: ClassVar[list] = BAND_7_EDGES
DEFAULT_NAMES: ClassVar[list] = BAND_7_NAMES
DEFAULT_DISPLAYS: ClassVar[list] = BAND_7_DISPLAYS
DEFAULT_COLORS: ClassVar[list] = BAND_7_COLORS
```

## BAND_6 保留方式

```python
# bands.py:31-38 — 完整保留，未修改
BAND_6: ClassVar[dict[str, FrequencyBand]] = { ... }

# 兼容入口：
get_band_edges("6")  # 返回 6 频段
get_band("presence", "6")  # 用 6 频段查找
```

## 5-8 kHz 报告字段

```python
# AudioMetrics 新增字段
rms_brilliance: float = 0.0   # 5-8 kHz 频段能量 (dB)
band_spec: str = "7"          # 标记频段版本

# to_dict() 输出
"band_spec": "7",
"spectrum": {
    ...
    "brilliance": -2.0,  # NEW FIELD
    ...
}
```

## 验收检查

- [x] 默认诊断使用 BAND_7
- [x] BAND_6 保留为 legacy 模式（`get_band_edges("6")`）
- [x] 5-8 kHz 有独立名称（Brilliance）、数值（rms_brilliance）与解释（risk_hint）
- [x] 5 类样本完成 old/new 对比（E1-E5 全部通过）
- [x] 新增字段不破坏既有 MRS/LUFS/M/S/HPSS 逻辑
- [x] BAND_6 兼容入口保留（`get_band_edges("6")`）
- [x] risk_hint 提供诊断可解释性

## 关键发现

**BAND_6 对 5-8 kHz 信号检测率为 0%。** 一个 6.5 kHz 纯音（模拟齿音频率）在 BAND_6 下完全不被任何频段捕获。BAND_7 通过 brilliance 频段正确捕获。

## 风险与回滚

- **风险：** 历史诊断报告缺少 `rms_brilliance` 字段 → 与新版报告不可直接对比 → `band_spec` 字段标记版本
- **回滚：** 将 `DEFAULT_BANDS` 改回 `BAND_6` + 恢复 v01_analyzer 导入 → 1 行改动

## 后续 EXP-MFY 入口

- EXP-MFY-004: 在 50 首 AI 音频上统计 brilliance 频段能量分布，与真实录音对比
- EXP-MFY-006: 基于 brilliance 异常值设计 sibilance_detector 阈值
