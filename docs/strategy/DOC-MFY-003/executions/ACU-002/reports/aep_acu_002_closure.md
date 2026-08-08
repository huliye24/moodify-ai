# AEP-ACU-002｜封口报告

> 日期：2026-07-03
> 任务：RBJ Biquad Equalizer Replacement
> 优先级：P0（阻塞 v0.4 发布）
> 执行角色：Audio DSP Engineer
> 状态：**代码实现完成，曲线验证通过，测试通过，AB 听感待填充**

---

## 1. 完成项

### 1.1 代码变更

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `moodify/processing/rbj_eq.py` | **新建** | RBJ biquad EQ 完整实现（5 种滤波器类型 + 频响计算 + 向量化处理） |
| `moodify/processing/operators.py` | **修改** | `apply_eq` 新增 `mode` 参数；`mode="rbj"` (default) 使用新 EQ；`mode="legacy_fft"` 保留旧 EQ |
| `moodify/processing/operators.py` | **修改** | 旧 FFT EQ 函数重命名为 `_apply_shelf_freq_legacy` / `_apply_peak_freq_legacy` |
| `moodify/processing/operators.py` | **修改** | `OPERATOR_REGISTRY` 新增 `"eq_legacy_fft"` 键用于 A/B 测试 |
| `moodify/processing/__init__.py` | **修改** | 导出 rbj_eq 模块的公共 API（10 个符号） |

### 1.2 滤波器支持

| 类型 | 状态 | 系数验证 |
|------|------|---------|
| `low_shelf` | ✅ 已实现 | RBJ Audio EQ Cookbook 公式 |
| `high_shelf` | ✅ 已实现 | RBJ Audio EQ Cookbook 公式 |
| `peaking` | ✅ 已实现 | RBJ Audio EQ Cookbook 公式 |
| `high_pass` | ✅ 已实现 | RBJ Audio EQ Cookbook 公式 |
| `low_pass` | ✅ 已实现 | RBJ Audio EQ Cookbook 公式 |

### 1.3 测试

| 测试类别 | 数量 | 状态 |
|---------|------|------|
| 系数无 NaN（正常参数） | 5 | ✅ |
| 系数无 NaN（极端参数） | 5 × 8 = 40 组合 | ✅ |
| 0 dB 恒等（系数 b==a） | 3 | ✅ |
| 0 dB 恒等（信号通过） | 3 | ✅ |
| Mono/Stereo 形状保持 | 2 | ✅ |
| 空滤波器链恒等 | 1 | ✅ |
| 输出无 NaN/Clip | 10 | ✅ |
| 无效滤波器类型异常 | 1 | ✅ |
| 频响验证（DC/Nyquist/中心频率） | 7 | ✅ |
| HPF/LPF 衰减验证 | 2 | ✅ |
| 级联滤波 | 2 | ✅ |
| Legacy EQ 可访问性 | 3 | ✅ |
| 长度保持 | 4 | ✅ |
| **总计** | **45** | **✅ 45/45 PASSED** |

### 1.4 频响曲线

| 曲线图 | 文件 | 状态 |
|--------|------|------|
| Low Shelf RBJ vs Legacy | `aep_acu_002_low_shelf_comparison.png` | ✅ |
| High Shelf RBJ vs Legacy | `aep_acu_002_high_shelf_comparison.png` | ✅ |
| Peaking RBJ vs Legacy | `aep_acu_002_peaking_comparison.png` | ✅ |
| 五种滤波器类型全览 | `aep_acu_002_all_filter_types.png` | ✅ |
| Q 值行为对比 | `aep_acu_002_q_comparison.png` | ✅ |

### 1.5 文档

| 文档 | 文件 | 状态 |
|------|------|------|
| 旧 EQ 审计 | `notes/old_eq_audit.md` | ✅ |
| Biquad 复用决策 | `notes/biquad_reuse_decision.md` | ✅ |
| 频响曲线报告 | `reports/aep_acu_002_eq_curves.md` | ✅ |
| AB 听感记录 | `reports/aep_acu_002_ab_listening.md` | ✅ 模板就绪，待填充 |
| 封口报告 | `reports/aep_acu_002_closure.md` | ✅ 本文件 |

---

## 2. 未完成项 / 待办

| 编号 | 条目 | 优先级 | 说明 |
|------|------|--------|------|
| TODO-01 | AB 听感填充 | P1 | 需要准备 3-5 首 AI 音频 + 2 首真实录音样本，执行盲听对比 |
| TODO-02 | 端到端 MRS 回归测试 | P1 | 需要 20 首基线音频处理前后 MRS 差值 < 2.0 分的系统性验证 |
| TODO-03 | preset 迁移 | P2 | 历史 preset 需要重新调参——因为 RBJ Q 值与旧 Q 值含义不同 |
| TODO-04 | 处理延迟对比 | P2 | 需要测量 RBJ vs Legacy FFT 的实际处理时间（预期 RBJ 更快——lfilter 向量化 vs FFT 块处理） |

---

## 3. 风险与迁移注意事项

### 3.1 Q 值含义变更

**这是最大的迁移风险。**

| 参数 | Legacy FFT 含义 | RBJ 含义 |
|------|---------------|----------|
| `peak_q` | Gaussian sigma = freq/q | RBJ peaking Q = fc/bw |
| Q=1.0 的带宽 | ~1.0 oct (Gaussian) | ~1.4 oct (RBJ standard) |

**影响：** 历史 preset 的 Q 值不能直接用于 RBJ EQ。需要逐 preset 重新调试，或提供 Q 值映射函数。

### 3.2 Shelf 过渡带宽变更

| 参数 | Legacy FFT | RBJ (Q=0.707) |
|------|-----------|---------------|
| 过渡宽度 | ~0.3 oct (硬编码) | ~1.0 oct |

**影响：** RBJ shelf 的过渡更陡（更窄的过渡带 = 更干净的分频），但这也意味着在截止频率附近 RBJ 的增益变化更"果断"——对音频的影响更集中。

### 3.3 Legacy FFT EQ 的维护状态

`mode="legacy_fft"` 已标记为 deprecated，调用时发出 `DeprecationWarning`。建议：
- v0.4: legacy mode 保留但不推荐
- v0.5: legacy mode 移至单独的 `moodify/processing/legacy_eq.py`
- v0.6: 移除 legacy mode（届时新 preset 已充分积累）

---

## 4. 验收矩阵判定

对照 DOC-MFY-003 验收矩阵中的 ACU-002 MUST/SHOULD 项：

| 验收项 | 标准 | 实测 | 判定 |
|--------|------|------|------|
| MUST: 频率响应精度 | RMSE < 0.1 dB vs 理论 | < 0.05 dB | **PASS** |
| MUST: 零增益透明性 | RMSE < -96 dBFS | < -180 dB (b==a) | **PASS** |
| MUST: MRS 回归 | 差值 < 2.0 分 | 待测 (TODO-02) | **PENDING** |
| SHOULD: 处理延迟 | 增加 < 10% | 待测 (TODO-04) | **PENDING** |
| MUST: ruff lint | 零错误 | 待 CI 运行 | **PENDING** |
| MUST: pytest -m v01 + pytest 全量 | 全部通过 | 45/45 新测试通过; v01/全量待 CI | **PENDING** |

---

## 5. 结论

**RBJ biquad EQ 的核心实现已经完成。** 五种滤波器类型的系数生成、向量化处理、频响验证和单元测试均已完成并通过。

MUST 验收项中的 2 项（频率响应精度、零增益透明性）已通过。剩余的 MUST 项（MRS 回归、ruff lint、pytest 全量）和 SHOULD 项（处理延迟）需要在 CI 环境和基线音频上运行。

**下一步：**
1. 运行 `ruff check .` + `pytest -m v01` + `pytest`
2. 准备 20 首基线音频，运行 MRS 回归
3. 填充 AB 听感记录
4. 如果所有 MUST 项通过 → ACU-002 封口
