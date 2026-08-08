# AEP-ACU-002｜Biquad 复用决策

> 日期：2026-07-03
> 审计文件：`moodify_runtime/craft_processes.py:518-644`

---

## 1. craft_processes.py 现有 biquad 审计

| 函数 | 行号 | 滤波器类型 | 系数公式 |
|------|------|-----------|----------|
| `_biquad_low_shelf()` | 520-551 | Low Shelf | RBJ Audio EQ Cookbook ✓ |
| `_biquad_high_shelf()` | 554-583 | High Shelf | RBJ Audio EQ Cookbook ✓ |
| `_biquad_peaking()` | 586-615 | Peaking | RBJ Audio EQ Cookbook ✓ |
| `_biquad_highpass()` | 618-644 | High Pass | RBJ Audio EQ Cookbook ✓ |

**系数验证：**
- Low shelf: 使用正确的 A = 10^(gain/40), alpha = sin(w0)/(2*Q), 标准 RBJ shelf 系数 — **正确**
- High shelf: 同上，符号变化符合 standard cookbook — **正确**
- Peaking: b0=1+alpha*A, b1=-2*cos(w0), b2=1-alpha*A, a0=1+alpha/A, a1=-2*cos(w0), a2=1-alpha/A — **正确**
- HPF: 标准 RBJ HPF coefficients — **正确**

---

## 2. 问题与局限

### 2.1 性能：Python for-loop

```python
for i in range(len(result)):
    x0 = float(result[i])
    y0 = b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
    result[i] = y0
```

- 每样本 Python 循环 → 3 分钟音频 (44.1kHz) 约 8M 次迭代 → **极慢**（估算 > 10 秒/滤波器级）
- 标准做法：`scipy.signal.lfilter([b0,b1,b2], [1,a1,a2], x)` 或 `scipy.signal.sosfilt()`

### 2.2 缺失滤波器类型

- **缺少 LPF (low-pass filter)** — RBJ cookbook 中的 LPF 未实现
- 缺少 notch/bandpass/allpass — 但 v0.4 不需要这些

### 2.3 API 耦合

- 函数直接操作 numpy 数组，但设计为 craft_processes 的私有函数
- 没有采样率/参数验证
- 没有系数缓存（重复调用相同参数需重新计算）

---

## 3. 复用决策

**结论：部分复用——系数公式复用，实现重写。**

| 方面 | 决策 | 理由 |
|------|------|------|
| 系数公式 | **复用** | craft_processes.py 的 RBJ 系数公式经过验证，正确 |
| 处理函数 | **重写** | 用 `scipy.signal.lfilter` 替代 Python for-loop，性能提升 100x+ |
| API | **重设计** | 设计 `FilterSpec` / `apply_rbj_eq()` 作为公共 API |
| 缺失类型 | **补充** | 添加 LPF（AEP-ACU-002 要求支持 HPF+LPF） |

---

## 4. 实现计划

### 新模块：`moodify/processing/rbj_eq.py`

```python
# 系数函数（从 craft_processes.py 复用公式，用 scipy.lfilter 实现）
def rbj_low_shelf_coeffs(freq_hz, q, gain_db, sr) -> tuple
def rbj_high_shelf_coeffs(freq_hz, q, gain_db, sr) -> tuple
def rbj_peaking_coeffs(freq_hz, q, gain_db, sr) -> tuple
def rbj_highpass_coeffs(freq_hz, q, sr) -> tuple
def rbj_lowpass_coeffs(freq_hz, q, sr) -> tuple

# 处理函数（向量化 scipy.lfilter）
def apply_rbj_eq(audio, sr, filters: list[dict]) -> np.ndarray

# EQ 模式切换
def apply_eq(audio, sr, *, mode="rbj", ...)
```

### 修改：`operators.py`

- `apply_eq()` 新增 `mode` 参数：`"rbj"` (default) / `"legacy_fft"`
- 旧 shelf/peak 函数保留并改名（加 `_legacy` 后缀）
- `OPERATOR_REGISTRY` 新增 `"eq_legacy_fft"` 用于 A/B 测试
