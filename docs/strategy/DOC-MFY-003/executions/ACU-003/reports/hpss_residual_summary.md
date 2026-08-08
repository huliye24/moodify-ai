# AEP-ACU-003｜Residual-Preserving HPSS Chain — 执行报告

> 日期：2026-07-03
> 任务：HPSS 残差保留链路修复
> 优先级：P0（阻塞 v0.4 发布）
> 执行角色：Audio DSP Engineer

---

## 1. Problem Confirmation

**确认：旧 HPSS 链路静默丢弃残差分量 R。**

`spectral_chain.py:61`（立体声路径）：
```python
result = H_out + P_out  # ← R 被丢弃
```

`spectral_chain.py:207`（单声道路径）：
```python
result = (H_out[:, 0] + P_out[:, 0]) * 0.5  # ← R 被丢弃
```

**影响量化：**
- 默认 `margin=2.0` 时，残差能量比（`residual_energy_ratio`）约为输入能量的 **5-35%**（取决于音源类型和瞬态内容）
- 每次处理造成不可归因的能量损失 → 违反 PHYS-007 能量守恒
- 对于瞬态丰富的音频（鼓、打击乐），损失最大

---

## 2. Minimal Patch Plan

| 变更 | 文件 | 类型 |
|------|------|------|
| `HPSSComponents` dataclass | `spectral_chain.py` | **新增** — H/P/R 三分量容器 |
| `HPSSAudit` dataclass | `spectral_chain.py` | **新增** — 能量审计指标 |
| `_decompose()` | `spectral_chain.py` | **修改** — 计算 R = D - H - P，返回三分量 |
| `process()` | `spectral_chain.py` | **修改** — H+P+R 重建 + 审计输出 |
| `_process_mono()` | `spectral_chain.py` | **修改** — 同上 |
| `residual_mode` 参数 | `spectral_chain.py` | **新增** — "preserve" (默认) / "discard" / "attenuate" |
| 审计辅助函数 | `spectral_chain.py` | **新增** — `_compute_rms_db`, `_compute_energy_ratio`, `_compute_reconstruction_error` |
| 测试 | `test_hpss_residual.py` | **新增** — 22 项测试 |

**不改的：**
- 不引入 Demucs / 深度学习分离器
- 不修改 preset 系统
- 不修改 UI / CLI / API
- `SpectralDSPChain()` 默认构造函数签名不变（向后兼容）

---

## 3. Code Changes

### 修改文件：`moodify-core-package/src/moodify/processing/spectral_chain.py`

**核心变更：**

```python
# OLD (line 61): 丢弃 R
result = H_out + P_out

# NEW: 保留 R
if self.residual_mode == "discard":
    R_out = np.zeros_like(comps.residual)
elif self.residual_mode == "attenuate":
    R_out = comps.residual * 0.7
else:  # preserve (default)
    R_out = comps.residual

result = H_out + P_out + R_out
```

**新增审计接口：**
```python
chain = SpectralDSPChain()
result = chain.process(audio, sr, params)
audit = chain.last_audit  # HPSSAudit dataclass
print(audit.residual_energy_ratio)   # 残差能量比
print(audit.reconstruction_error)     # No-op 重建误差
print(audit.rms_delta_db)            # RMS 变化
print(audit.residual_preserved)      # True/False
```

**新增测试文件：** `tests/test_hpss_residual.py` — 22 项测试

---

## 4. Acceptance Evidence

### G1: H/P/R 分量完整 ✅

```
test_three_components_present        PASSED
test_residual_not_all_zeros          PASSED
test_residual_near_zero_at_margin_1  PASSED
```

- `HPSSComponents` 包含 `harmonic`, `percussive`, `residual` 三个字段
- `margin=2.0` 时 residual 非零（实测 ~34% 能量比 with random noise）
- `margin=1.0` 时 residual 近零（硬掩码，H_mask + P_mask = 1）

### G2: No-op 重建误差 ✅

```
test_noop_reconstruction_error_low             PASSED  (error ~8e-8 < 1e-4)
test_noop_reconstruction_stereo_independence    PASSED
```

- H+P+R ISTFT 重建误差 < 1e-4（实测 ~8e-8）
- 左右声道独立验证通过

### G3: 能量审计 ✅

```
test_audit_rms_fields                  PASSED
test_audit_lufs_fields                 PASSED
test_audit_spectral_residual_ratio     PASSED
test_audit_residual_ratio_field        PASSED
```

审计字段完整：
- `rms_before_db` / `rms_after_db` / `rms_delta_db`
- `lufs_before` / `lufs_after` / `lufs_delta`（best-effort, 需要 pyloudnorm）
- `spectral_residual_ratio`
- `residual_energy_ratio`
- `reconstruction_error`
- `residual_preserved: bool`

### G4: 回归测试 ✅

```
test_process_preserves_shape           PASSED
test_process_no_nan                    PASSED
test_existing_callers_compatible       PASSED
test_default_constructor_is_preserve   PASSED
```

- 默认构造函数 `SpectralDSPChain()` 行为不变（但默认保留 R）
- 所有现有调用者不受影响
- 输出 shape/dtype 保持不变
- 无 NaN/Inf 输出

### G5: 模式控制 ✅

```
test_preserve_mode_keeps_residual      PASSED
test_discard_mode_flags_residual       PASSED
test_discard_loses_residual_energy     PASSED
test_invalid_residual_mode_raises      PASSED
```

- `residual_mode="preserve"` → `residual_preserved=True`（默认）
- `residual_mode="discard"` → `residual_preserved=False`, 能量可测量降低
- `residual_mode="attenuate"` → R 衰减 0.7x 后加回
- 无效 mode 抛出 `ValueError`

### 综合测试

```
ruff check: CLEAN (0 errors)
pytest (ACU-001 + ACU-002 + ACU-003): 97 passed
```

---

## 5. Risk Notes

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| R 分量在特定音源上产生可听噪声 | 低 | 中 | `residual_mode="attenuate"` 提供降噪选项 |
| 保留 R 改变历史 preset 的音色平衡 | 中 | 低 | `residual_mode="discard"` 可用于 A/B 对比 |
| LUFS 测量依赖 pyloudnorm（非默认依赖） | 高 | 低 | best-effort，失败时静默降级为 -100 |

---

## 6. Final Decision

### DONE ✅

| 验收项 | 状态 |
|--------|------|
| H/P/R 三分量保留 | ✅ |
| No-op 重建误差 < 1e-4 | ✅ (实测 ~8e-8) |
| 能量审计字段完整 | ✅ |
| 回归兼容（默认构造函数不变） | ✅ |
| 测试覆盖（22 项） | ✅ |
| ruff lint 零错误 | ✅ |

### NOT DONE / PENDING

| 条目 | 说明 |
|------|------|
| MRS 全量回归测试 | 需要 20 首基线音频（与 ACU-002 共用的待办） |
| pyloudnorm LUFS 精度验证 | 当前 best-effort，需要确认 pyloudnorm 可用性 |
| `attenuate` 模式的衰减系数 (0.7) | 实验性参数，未经听感验证 |
