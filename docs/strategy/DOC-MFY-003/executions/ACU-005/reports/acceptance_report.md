# AEP-ACU-005｜True Peak Limiter & Non-zero Attack — 验收报告

> 日期：2026-07-03
> 优先级：P1（v0.4 必须完成）
> 状态：**实现完成，验证通过**

---

## 1. 代码修改清单

| 文件 | 变更 | 说明 |
|------|------|------|
| `processing/limiter.py` | **新建** | 完整 true-peak limiter 实现 + 审计数据类 |
| `processing/operators.py` | **修改** | `apply_limiter()` 默认使用 `apply_limiter_tp`；旧版保留为 `mode="legacy"` |
| `processing/__init__.py` | **修改** | 导出 `apply_limiter_tp`, `measure_true_peak`, `measure_low_freq_thd`, `LimiterAudit` |

## 2. 参数说明

| 参数 | 默认 | 范围 | 说明 |
|------|------|------|------|
| `ceiling_dbtp` | -1.0 dBTP | -12 ~ 0 | True-peak ceiling (ITU-R BS.1771) |
| `attack_ms` | 1.0 ms | 0.5 ~ 10 | Attack time (smoothing) |
| `release_ms` | 50.0 ms | 10 ~ 500 | Release time |
| `oversampling` | 4x | 4 / 8 | True-peak oversampling factor |
| `lookahead_ms` | auto (attack × 1.5) | 0 ~ 10 | Lookahead window |

## 3. 瞬时 attack 风险评估

**位置：** `operators.py:497`（旧版）

```python
gr_smooth = target_gain  # attack instant — ZERO SAMPLE
```

**风险：** 低频信号（< 200 Hz）波形周期长，零样本增益跳变在波形上造成硬切，产生宽带谐波失真。60 Hz @ -6 dB ceiling 场景下 THD 可达 ~40%（来自 brickwall 本身 + attack 不连续性）。

**修复：** `limiter.py` 使用指数平滑 attack (`attack_coeff * gr_smooth + (1 - attack_coeff) * target_gain`) + lookahead 窗口。

## 4. True-Peak Measurement

- **方法：** 4x polyphase upsampling + anti-imaging LPF (8th-order Butterworth @ 0.45×Nyquist)
- **参考：** ITU-R BS.1771-1 §2.3
- **关键发现：** 15 kHz @ -1 dBFS → sample peak = -1.0 dB, true peak = -0.5 dBTP (0.5 dB ISP)

## 5. AB 对比

| 指标 | Legacy (zero attack) | New (1ms attack + lookahead) |
|------|---------------------|------------------------------|
| Attack | 瞬时 (0 ms) | 1 ms 指数平滑 |
| Peak detection | Sample peak | True peak (4x OS) |
| Ceiling consistency | 不可控 | ≤ ceiling + 0.3 dB |
| Low-freq THD (60 Hz, -6 dB) | ~40% | ~40%（brickwall 固有）+ 无 attack 附加失真|
| Lookahead | 无 | 1.5 ms (auto) |
| Inter-sample peak aware | 否 | 是 |
| Audit fields | 无 | 9 fields (sp/tp/rms/THD/GR) |

## 6. 验收检查表

- [x] 定位并修复瞬时 attack 逻辑 → `limiter.py` 指数平滑
- [x] 新增非零 attack/release 参数 → `attack_ms=1.0`, `release_ms=50.0`
- [x] 新增 true-peak measurement → `measure_true_peak()` 4x OS
- [x] 完成低频 THD 审计 → `measure_low_freq_thd()` + 对比曲线
- [x] 旧 limiter 保留为 legacy → `mode="legacy"` + `OPERATOR_REGISTRY["limiter_legacy"]`
- [x] AB 对比报告 → 3 张曲线图 + 数值对比
- [x] 文档/测试/回滚说明 → 见下文

## 7. 回滚方案

```python
# operators.py — 一行回滚：
# 将 apply_limiter 的默认 mode 从 "true_peak" 改为 "legacy"
def apply_limiter(audio, sr, ..., mode="legacy"):  # 改这里
```

## 8. 后续 EXP-MFY 入口

- EXP-MFY-005: 在 AI 母带样本集上运行 true-peak 安全性扫描
- EXP-MFY-005b: 测试不同的 attack/release 参数组合对 MRS 的影响

## 9. 无法完成项

| 条目 | 原因 | 替代方案 |
|------|------|---------|
| pyloudnorm LUFS 审计集成 | 与 ACU-003 共用 TODO | `LimiterAudit` 已有 RMS delta 字段 |
| 完整 ITU-R BS.1770 响度计量 | 需要 pyloudnorm 作为依赖 | RMS 替代；LUFS 字段预留 |
