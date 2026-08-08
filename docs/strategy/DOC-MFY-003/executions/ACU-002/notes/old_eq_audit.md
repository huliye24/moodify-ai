# AEP-ACU-002｜旧 EQ 实现审计

> 日期：2026-07-03
> 审计范围：`operators.py` 中所有 EQ 相关函数

---

## 1. 旧 EQ 实现位置

| 函数 | 行号 | 类型 | 职责 |
|------|------|------|------|
| `apply_eq()` | 40-113 | 入口 | 频域 EQ 主函数，block-wise overlap-add FFT |
| `_resolve_eq_params()` | 19-37 | 参数解析 | 将 band 名称 (Sub/Bass/Mid/...) 映射为 EQ 参数 |
| `_apply_shelf_freq()` | 116-127 | 频域曲线 | sigmoid 过渡的 shelf 曲线 |
| `_apply_peak_freq()` | 130-138 | 频域曲线 | Gaussian 形状的 peak 曲线 |

---

## 2. 算法分析

### 2.1 Shelf 实现 (`_apply_shelf_freq`)

```python
# Low shelf: sigmoid from 1.0 → gain_lin around freq
curve = 1.0 + (gain_lin - 1.0) * (1.0 / (1.0 + np.exp((freqs - freq) / (freq * 0.3))))

# High shelf: sigmoid from gain_lin → 1.0 around freq
curve = 1.0 + (gain_lin - 1.0) * (1.0 / (1.0 + np.exp(-(freqs - freq) / (freq * 0.3))))
```

**问题：**
- 过渡宽度硬编码为 `freq * 0.3`（约 0.3 倍频程），不可调节
- 没有 Q/bandwidth 参数——用户无法控制 shelf 斜率
- sigmoid 过渡形状与标准 2 阶 shelf 的 dB/octave 斜率不匹配
- 在 freq 处增益为 `1.0 + (gain_lin - 1.0) * 0.5`（中点），而标准 shelf 的 3dB 点在 cutoff_frequency_hz 处

### 2.2 Peak 实现 (`_apply_peak_freq`)

```python
bw = freq / max(q, 0.1)
curve = 1.0 + (gain_lin - 1.0) * np.exp(-((freqs - freq) / bw) ** 2)
```

**问题：**
- 带宽定义 `bw = freq / q` 与标准 peaking 滤波器的带宽定义不一致
  - 标准 RBJ peaking: 带宽 = `freq / q`（在 gain_db/2 点测量）或 `bw_oct = sinh(1/(2*q)) * 2 / ln(2)`
  - 当前的 Gaussian sigma = `freq / q`，但 Gaussian 的 -3dB 点不等于 peaking 滤波器的 half-gain 点
- Gaussian 形状是对称的（在线性频率轴上），而标准 peaking 在 log 频率轴上对称
- Q=1.0 时的实际效果与 DAW 中 Q=1.0 的 peaking 滤波器完全不同

### 2.3 FFT Block Processing (`apply_eq`)

- 4 秒块 + 25% overlap-add
- 每块做 FFT → 乘频域响应 → IFFT
- 问题：FFT 长度 = `block_len * 2`（零填充），但频域响应基于 `rfftfreq(block_len * 2)` —— 正确，但产生了不必要的计算开销
- block-wise 处理会导致低频段时间分辨率不足（4s 块 = 0.25 Hz 分辨率，远超需要）

---

## 3. 调用链

```
OPERATOR_REGISTRY["eq"] → apply_eq()
                         ├── _resolve_eq_params()  [band name → params]
                         ├── _apply_shelf_freq()   [low shelf, sigmoid]
                         ├── _apply_shelf_freq()   [high shelf, sigmoid]
                         └── _apply_peak_freq()    [peaking, Gaussian]

apply_chain(audio, sr, [{"op": "eq", "params": {...}}])
  → apply_eq(audio, sr, **params)
```

**唯一的公共入口**：`apply_eq()` 通过 `OPERATOR_REGISTRY` 和 `apply_chain()` 被调用。无直接调用者。

---

## 4. 参数接口（需保持不变）

```python
def apply_eq(audio, sr,
             bands=None,
             low_shelf_gain_db=0.0, low_shelf_freq=200.0,
             high_shelf_gain_db=0.0, high_shelf_freq=6000.0,
             peak_freq=1000.0, peak_gain_db=0.0, peak_q=1.0)
```

**参数含义在当前实现中的实际行为：**
| 参数 | 含义 | 实际行为 |
|------|------|----------|
| `low_shelf_gain_db` | Low shelf 增益 | sigmoid 过渡，中点 200 Hz |
| `low_shelf_freq` | Low shelf 频率 | sigmoid 中点频率 |
| `high_shelf_gain_db` | High shelf 增益 | sigmoid 过渡，中点 6000 Hz |
| `high_shelf_freq` | High shelf 频率 | sigmoid 中点频率 |
| `peak_freq` | Peak 频率 | Gaussian 中心频率 |
| `peak_gain_db` | Peak 增益 | Gaussian 峰值增益 |
| `peak_q` | Peak Q 值 | 带宽 = peak_freq / q（非标准 Q） |

---

## 5. 声学合规缺陷

对照 DOC-MFY-002 的 DEF-001：

| 缺陷 | 严重度 | 说明 |
|------|--------|------|
| 滤波器形状不可预测 | P0 | sigmoid/Gaussian 与标准 EQ 无对应关系 |
| Q 值定义非标准 | P0 | `peak_q` 含义与行业惯例不同 |
| 无带宽控制 | P0 | shelf 过渡宽度固定，无法调节 |
| 参数不可跨版本复现 | P0 | 任何 FFT 参数变更都会改变频率响应 |
| 音频工程师不可理解 | P0 | "3 dB at 2.5 kHz" 的实际效果未知 |

---

## 6. 保留策略

旧 FFT EQ 不应直接删除。原因：
1. 历史 preset 可能依赖 sigmoid/Gaussian 曲线的特定行为
2. 作为实验对比的基线
3. A/B 测试需要旧实现作为对照组

**保留方式**：
- `apply_eq` → 改为 `mode="rbj"` (默认) + `mode="legacy_fft"`
- 旧函数重命名为 `_apply_shelf_freq_legacy()` / `_apply_peak_freq_legacy()`
- `OPERATOR_REGISTRY` 增加 `"eq_legacy_fft"` 键
