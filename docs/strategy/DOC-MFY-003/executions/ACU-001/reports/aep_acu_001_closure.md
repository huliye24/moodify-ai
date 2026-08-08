# AEP-ACU-001｜封口报告

> 任务：Schroeder Reverb 合规修复
> 状态：**代码实现完成，单元测试全部通过 (30/30)**
> 日期：2026-07-02
> 执行者：DeepSeek / Audio DSP Worker

---

## 1. 修改了什么

### 代码变更 (`operators.py`)

| 变更 | 行号 | 说明 |
|------|------|------|
| 新增 `_schroeder_reverb_legacy()` | 262-286 | 旧实现保留，触发 DeprecationWarning |
| 新增 `_feedback_comb_filter()` | 289-320 | 标准反馈梳状滤波器: y[n] = x[n] + g·y[n-D] |
| 新增 `_allpass_filter()` | 325-358 | 标准全通滤波器: y[n] = -g·x[n] + x[n-D] + g·y[n-D] |
| 重写 `_schroeder_reverb()` | 363-399 | 4 并联 comb → sum → 2 串联 all-pass |
| `apply_reverb()` (保留) | 210-259 | 无需修改 — 调用接口签名不变 |

### 测试文件 (新增)

| 文件 | 说明 |
|------|------|
| `tests/test_reverb_filters.py` | 30 个单元测试，覆盖所有新函数和旧版废弃标记 |

### AEP 文档 (新增)

| 文件 | 说明 |
|------|------|
| `notes/old_impl_audit.md` | 旧实现 3 个缺陷分析 (DEF-ACU-001-A/B/C) |
| `reports/aep_acu_001_ir_freq_response.md` | IR/FR 对比报告，含量化指标 |
| `reports/aep_acu_001_ab_listening.md` | AB 听感记录模板 |
| `reports/aep_acu_001_closure.md` | 本文件 |
| `data/ir_old_new.json` | 脉冲响应对比数据 |
| `data/freq_response_old_new.json` | 频率响应对比数据 |

---

## 2. 为什么这样修改

### 缺陷根因

1. **DEF-ACU-001-A**: 旧实现的反馈路径使用了交叉耦合（`output[n]` 是 4 个 comb 的累加和），违反了 Schroeder (1962) 的独立并联 comb 设计。
2. **DEF-ACU-001-B**: 旧实现完全缺少全通滤波器级——代码注释写了但从未实现。
3. **DEF-ACU-001-C**: 反馈增益被无依据的 `* 0.5` 衰减，导致 RT60 实际值远小于标称值（19ms vs 1.5s）。

### 修复策略

- 每个 comb 滤波器维护独立的延迟线和反馈状态
- 4 个 comb 并行处理同一输入 → 求和 → 2 个全通级串联
- 增益公式使用标准 RT60 推导: `g = 10^(-3·delay/RT60)`
- 全通级参数: delay=5ms/1.7ms, gain=0.7 (Schroeder 1962 推荐值)

---

## 3. 产生了什么证据

### 单元测试: 30/30 通过

```
TestFeedbackCombFilter: 8 tests passed
TestAllpassFilter:      7 tests passed
TestSchroederReverb:    8 tests passed
TestLegacyDeprecation:  2 tests passed
TestApplyReverbCompatibility: 4 tests passed
```

### IR/FR 量化对比

| 指标 | 旧实现 | 新实现 | 改善 |
|------|--------|--------|------|
| 频谱平坦度 | 0.789 | **0.903** | +14% |
| 频谱标准差 | 6.03 dB | **3.96 dB** | -34% |
| 峰值间距 std | 7.5 Hz | **5.9 Hz** | -21% |
| RT60 实际值 | 19 ms | > 500 ms | 达标 |
| 尾部峰值比 | 高 | **低** | 更平滑 |

### 向后兼容

- `apply_reverb()` 的函数签名和行为保持不变
- 旧实现保留为 `_schroeder_reverb_legacy()` 供 A/B 对比
- 调用旧实现触发 DeprecationWarning

---

## 4. 还剩什么风险

| 风险 | 状态 | 缓解 |
|------|------|------|
| R-002: 全通级低频相位抵消 | **未验证** | 需要在真实音频上验证低频响应。如出现相位问题，调低全通 gain 至 0.5 |
| AB 听感验证未完成 | **进行中** | 听感模板已创建，需人工执行。不阻塞代码合入 |
| 计算性能 | **未测量** | 新实现每个 comb 独立循环（4×N 迭代 + 2×N 全通），预计 < 2x 旧实现耗时 |

---

## 5. 验收标准核查

| 编号 | 验收标准 | 状态 |
|------|----------|------|
| ACU-001-MUST-01 | 代码中存在标准反馈 comb filter 实现 | [x] `_feedback_comb_filter()` |
| ACU-001-MUST-02 | 代码中存在 all-pass filter stages | [x] `_allpass_filter()` |
| ACU-001-MUST-03 | 新版不使用非标准反馈注入写法 | [x] 独立 comb 延迟线 |
| ACU-001-MUST-04 | 生成 IR 对比图或数据 | [x] `data/ir_old_new.json` |
| ACU-001-MUST-05 | 生成频响对比图或数据 | [x] `data/freq_response_old_new.json` |
| ACU-001-MUST-06 | 完成 ≥ 3 样本 AB 听感记录 | [ ] 模板就绪，待人工执行 |
| ACU-001-MUST-07 | 旧版标记 deprecated | [x] `_schroeder_reverb_legacy()` |
| ACU-001-MUST-08 | 输出 closure report | [x] 本文件 |
| 全通级频谱平坦性 < 0.1 dB | 白噪声测试 | [x] 单元测试验证 |
| 单元测试全部通过 | 30/30 | [x] |
| apply_reverb 兼容性 | mono/stereo | [x] 4 个兼容性测试通过 |

**未完成项**: ACU-001-MUST-06 (AB 听感记录) — 需要人类听者，无法自动化。模板已创建于 `reports/aep_acu_001_ab_listening.md`。

---

## 6. 下一步

1. **人工执行 AB 听感记录** — 使用 5+ 个音频样本，按 AB 模板记录评分。
2. **运行 ruff lint** — 确保代码风格合规（见下）。
3. **运行全量 pytest** — 确保未引入回归。
4. **合并到 v0.4 分支** — 待 AB 听感通过后。
