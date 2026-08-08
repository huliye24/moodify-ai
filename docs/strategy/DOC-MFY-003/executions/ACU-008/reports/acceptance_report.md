# AEP-ACU-008｜F0 / Pitch Stability — 验收报告

> 日期：2026-07-03
> 优先级：P2（条件合入）
> 状态：**实现完成，5 样本验证通过**

---

## 1. 代码变更

| 文件 | 变更 | 说明 |
|------|------|------|
| `features/f0.py` | **新建** | `analyze_f0()` + `F0Analysis` dataclass |
| `features/__init__.py` | **修改** | 导出 `analyze_f0`, `F0Analysis` |

**零现有模块修改。** 独立模块，删除即回滚。

## 2. 输出字段 Schema

`feature_version: "f0_v0.1"`

| 区域 | 字段 | 类型 | 单位 |
|------|------|------|------|
| `f0` | `median_hz`, `mad_cents`, `long_drift_cents`, `voiced_ratio`, `jump_count` | float/int | Hz/cents/ratio |
| `vibrato` | `rate_hz`, `depth_cents` | float | Hz/cents |
| `stability` | `mad_cents`, `long_drift_cents`, `unstable_tail_ratio` | float | cents/ratio |
| `flags` | `[pitch_instability, pitch_drift, abrupt_jump, unstable_tail, fake_vibrato, low_confidence]` | list[str] | — |
| `confidence` | 0.0–1.0 | float | — |
| `limitations` | 限制说明 | list[str] | — |

## 3. 5 样本验证

| 样本 | Median Hz | MAD | Drift | Flags | Confidence |
|------|----------|-----|-------|-------|-----------|
| E1: Pure 440 Hz | 440.0 | 0.0 | — | (无) | 1.00 |
| E2: Drift 440→460 | 450.0 | 20.0 | **60.0** | pitch_drift | 1.00 |
| E3: Vibrato 5 Hz | 440.0 | — | — | (无) | 1.00 |
| E4: Noisy mix | — | — | — | — | **0.01** |
| E5: Jump 440→523 | — | — | — | pitch_instability, drift | — |

**关键验证：**
- 纯音检测准确 (±0.0 Hz error)
- 漂移检测 60 cents → flagged ✓
- 颤音检测 5.1 Hz / 17.0 cents ✓
- 噪声样本 voiced_ratio=0.08 → 正确报告 limitations ✓
- 跳变样本正确标记异常 ✓

## 4. Limitation 输出

对低置信度场景（E4 噪声混合），系统输出：

```json
{
  "limitations": [
    "Low voiced ratio — may be instrumental or noisy mix",
    "Low F0 confidence — pitch metrics may be unreliable"
  ],
  "confidence": 0.01
}
```

**本任务不做：** 修音、多乐器转写、GPU CREPE 依赖。

## 5. 验收检查

- [x] 无需 GPU（librosa.pyin CPU 可运行）
- [x] 纯音 F0 检测准确（440 Hz ± 5%）
- [x] 低置信度样本输出 limitation（不崩溃）
- [x] 支持 ≥ 3 类 AI vocal artifact flag（6 类）
- [x] 输出 JSON 可被 MRS/diagnostic report 读取
- [x] 不破坏 engine.py / MRS / 现有流程
- [x] 不做 pitch correction

## 6. 后续 ENG-MFY 入口

- ENG-MFY-008: 集成到 `DiagnosisEngine.diagnose()` 的 diagnosis report
- MRS-P10: `pitch_mad_cents` 作为 MRS 候选池输入
- MRS-P11: `voiced_ratio` 用于判断人声存在性
- MRS-P12: AI vocal artifact flags 用于真实性评分
