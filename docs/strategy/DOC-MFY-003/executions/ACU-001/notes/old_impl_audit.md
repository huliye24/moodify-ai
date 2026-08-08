# AEP-ACU-001｜旧实现审计报告

> 审计对象: `moodify-core-package/src/moodify/processing/operators.py:_schroeder_reverb()`
> 审计日期: 2026-07-02
> 对照标准: Schroeder (1962) "Natural Sounding Artificial Reverberation"

---

## 1. 当前代码 (operators.py:262-275)

```python
def _schroeder_reverb(signal: np.ndarray, sr: int, rt60: float) -> np.ndarray:
    """简化 Schroeder 混响器。"""
    comb_delays = [int(sr * d) for d in [0.0297, 0.0371, 0.0411, 0.0437]]
    comb_gains  = [10.0 ** (-3.0 * d / rt60) for d in [0.0297, 0.0371, 0.0411, 0.0437]]

    output = np.zeros(len(signal) + max(comb_delays) + 2000)
    for delay, gain in zip(comb_delays, comb_gains):
        for n in range(len(signal)):
            output[n + delay] += signal[n] * gain
            if n + delay < len(output) - delay:
                output[n + delay] += output[n] * gain * 0.5

    return output[:len(signal) + 2000]
```

---

## 2. 缺陷分析

### DEF-ACU-001-A: 非标准反馈注入 (严重)

**问题**: 第 273 行 `output[n + delay] += output[n] * gain * 0.5`

- `output[n]` 是**所有 4 个梳状滤波器输出的累加和**，不是当前梳状滤波器自己的输出。
- 这导致交叉耦合 (cross-coupling)：梳状滤波器 A 的输出被注入到梳状滤波器 B 的反馈路径中。
- 标准反馈梳状滤波器应为：`y[n] = x[n] + g * y[n-D]`，其中 `y[n-D]` 是当前滤波器自己的历史输出。
- 交叉耦合使混响响应不可预测——4 个延迟线之间的相互作用产生非预期的共振峰和抵消谷。

**根因**: 代码用单一 `output` 数组累加所有梳状滤波器输出，然后从这个累加数组中取反馈值。

**修复方向**: 每个梳状滤波器维护自己的延迟线 (delay buffer)，反馈只来自自己的历史输出。

### DEF-ACU-001-B: 缺少全通滤波器级 (严重)

**问题**: 函数的 docstring 写"简化 Schroeder 混响器"，注释写"4 个梳状滤波器 + 2 个全通"，但代码中**完全没有全通滤波器实现**。

Schroeder (1962) 的原始设计明确要求：
1. 多个并联梳状滤波器（提供频率相关的混响时间）
2. **两个串联全通滤波器**（增加回声密度而不引入频率着色）

全通滤波器的作用：
- 增加时域扩散 (temporal diffusion)
- 将离散回声转化为统计上不可区分的扩散混响
- 不改变幅频响应（全通 = 常数幅频，仅改变相位）

缺少全通级的后果：
- 回声密度增长仅为线性（仅来自梳状反馈），非指数
- 混响尾音可感知为离散回声（flutter echo 效应），尤其在 50 ms 后
- 冲击音 (percussive) 材料上的混响不自然

**根因**: 代码注释提到了全通但从未实现。

**修复方向**: 在梳状滤波器组之后串联 2 个全通滤波器。

### DEF-ACU-001-C: 反馈增益衰减因子硬编码 0.5 (中等)

**问题**: 反馈路径的 `* 0.5` 乘数是硬编码的，无理论依据。

标准反馈梳状滤波器的增益应与 RT60 相关：
```text
g = 10^(-3 * delay / rt60)
```
这确保在 rt60 秒后，信号衰减 60 dB。

当前的 `gain * 0.5` 组合（其中 gain = 10^(-3*d/rt60)）意味着实际反馈增益是理论值的一半，导致混响时间短于指定的 RT60。

**根因**: `0.5` 可能是调试参数，被意外保留。

**修复方向**: 移除硬编码的 0.5，使用标准增益公式。

---

## 3. 与 Schroeder (1962) 的对齐差距

| 组件 | Schroeder 1962 要求 | 当前实现 | 对齐 |
|------|---------------------|----------|------|
| 梳状滤波器数量 | 4 (推荐) | 4 | ✅ |
| 梳状延迟长度 | 互质 (mutually prime) | ~29.7/37.1/41.1/43.7 ms — 基于质数 | ✅ |
| 梳状反馈结构 | `y[n] = x[n] + g*y[n-D]` (自反馈) | 交叉耦合反馈 | ❌ |
| 梳状增益 | `g = 10^(-3*D/RT60)` | 增益公式正确但被 0.5 衰减 | ❌ |
| 全通滤波器数量 | 2 (推荐) | 0 | ❌ |
| 全通延迟长度 | ~5 ms, ~1.7 ms (推荐) | 无 | ❌ |
| 全通增益 | ~0.7 (推荐) | 无 | ❌ |

---

## 4. 调用者影响分析

`_schroeder_reverb()` 被 `apply_reverb()` (operators.py:238, 247) 调用。

`apply_reverb()` 也有自身问题 (DEF-008: 单声道求和丢失立体声信息)，但不在 AEP-ACU-001 范围内。修复 `_schroeder_reverb()` 的函数签名 `(signal, sr, rt60)` 应保持不变以保持向后兼容。

---

## 5. 废弃策略

旧实现的处理：
- 保留为 `_schroeder_reverb_legacy()` — 添加 `@deprecated` 标记
- 新实现命名为 `_schroeder_reverb()` — 替换原函数
- `apply_reverb()` 无需修改（调用接口不变）
- 添加模块级 `__all__` 或文档说明废弃状态

---

## 6. 风险评估

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| 新实现音色与旧实现差异过大 | 中 | 中 | 提供 IR/频谱对比 + AB 听感记录 |
| 新实现计算量高于旧实现 (每个 comb 独立 buffer) | 高 | 低 | 新实现仍然 O(N)，增加常数因子 < 2x |
| 全通级增益不当导致不稳定 | 低 | 高 | 单元测试覆盖 g=0~0.9 的稳定性 |
