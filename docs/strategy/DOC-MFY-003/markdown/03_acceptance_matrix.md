# DOC-MFY-003｜验收矩阵

> 每个 AEP 的验收标准在此汇总为单一可核查矩阵。
> 验收等级：MUST = 不通过则 v0.4 不发布 | SHOULD = 需要合理理由才能跳过 | MAY = 条件允许则合入

---

## 验收矩阵

| AEP | 验收项 | 量化标准 | 验证方法 | 等级 |
|-----|--------|----------|----------|------|
| ACU-001 | 全通级频谱平坦性 | 幅频响应变化 < 0.1 dB | 白噪声通过全通级 → 频谱对比 | MUST |
| ACU-001 | 脉冲响应无离散回声 | t > 50 ms 峰值比 < 3:1 | 单位脉冲 → 脉冲响应 → 峰值检测 | MUST |
| ACU-001 | MRS texture 提升 | 中位数提升 ≥ 3 分 | 20 首测试音频配对 t 检验 | MUST |
| ACU-001 | MRS space 不降低 | 配对 t 检验 p > 0.05 | 同上 | MUST |
| ACU-002 | 频率响应精度 | 20 Hz-20 kHz RMSE < 0.1 dB vs 理论 | 对数扫频 → FFT → 与理论曲线对比 | MUST |
| ACU-002 | 零增益透明性 | RMSE < -96 dBFS | 所有 EQ 参数=0 → 输出 vs 输入 | MUST |
| ACU-002 | MRS 回归 | 前后差值变化 < 2.0 分 | 20 首测试音频 × 3 参数组 | MUST |
| ACU-002 | 处理延迟 | 增加 < 10% | 计时对比 (新 EQ vs 旧 EQ) | SHOULD |
| ACU-003 | 能量守恒审计 | \|ΔL_residual\| ≤ 3σ (safe 级别) | conservation.py:audit_conservation() | MUST |
| ACU-003 | MRS 不低于当前 | 配对 t 检验 p > 0.05 (不劣于) | 20 首测试音频 | MUST |
| ACU-003 | 无新增可听伪影 | 非正式听感检查 + MRS artifact 组件不降低 | 20 首测试音频 | SHOULD |
| ACU-004 | 单一定义来源 | bands.py 是唯一频段定义 | 代码审查: grep 所有频段边界 → 确认来源 | MUST |
| ACU-004 | 能量守恒 | 7 频段能量总和 = 全频段能量, 误差 < 0.01% | 50 首音频频段能量求和 vs 全频段能量 | MUST |
| ACU-004 | 5-8 kHz 区分度 | Brilliance 区间 AI vs 真实 d > 0.3 | 50 AI + 50 真实 → Cohen's d | SHOULD |
| ACU-005 | 真峰值限幅 | 15 kHz @ -1 dBFS → 真峰值 ≤ ceiling | 4x 过采样真峰值测量 | MUST |
| ACU-005 | 全频段安全 | 真峰值 ≤ ceiling + 0.1 dB (全频段) | 扫频信号 (20 Hz-20 kHz) | MUST |
| ACU-005 | 低频 THD | < 100 Hz 限幅后 THD < 0.5% | 正弦波测试 + THD 测量 | SHOULD |
| ACU-005 | MRS 回归 | 前后差值变化 < 2.0 分 | 20 首测试音频 | MUST |
| ACU-006 | 感知频谱 shape | Mel(n_mels), Bark(n_barks), ERB(n_erbs) 正确 | 维度检查 + 与 librosa 参考对比 | MUST |
| ACU-006 | 低频降维 | 60-250 Hz 在 Bark 上 ≤ 4 个 band | 验证 bark_spectrogram 的低频分辨率 | SHOULD |
| ACU-006 | 计算性能 | < 2x 线性 FFT 时间 | 计时对比 | SHOULD |
| ACU-007 | 掩蔽阈值定性 | 1 kHz 纯音掩蔽阈值峰值在 1 Bark 附近 | 可视化验证 | MUST |
| ACU-007 | 扩展函数不对称 | 低频→高频扩展 > 高频→低频扩展 | 纯音测试 | SHOULD |
| ACU-007 | 计算性能 | 3 分钟音频 < 10 秒 | 计时 | SHOULD |
| ACU-008 | YIN 精度 | 与 librosa.yin RMSE < 1 Hz (f0 < 1000 Hz) | 50 首音频对比 | MUST |
| ACU-008 | AI vs 真实区分度 | F0 稳定性 Cohen's d > 0.5 | 50 AI + 50 真实 | SHOULD |
| ACU-008 | 计算性能 | 3 分钟音频 < 5 秒 | 计时 | SHOULD |
| ACU-009 | Chroma 归一化 | 每帧 chroma 向量和 = 1.0 (tol 1e-6) | 单元测试 | MUST |
| ACU-009 | 调性检测准确率 | 已知调性音频 > 80% | 标注测试集 | SHOULD |
| ACU-009 | AI vs 真实区分度 | 和声稳定性 Cohen's d > 0.3 | 50 AI + 50 真实 | SHOULD |
| ACU-010 | CI 宽度改善 | 分风格 95% CI 比混合窄 ≥ 20% | Bootstrap 1000 次 | MUST |
| ACU-010 | 鲁棒性验证 | MAD 评分在 contaminated sample 上偏差 < SD 评分 | 注入 5% 异常值 → 对比 | SHOULD |
| ACU-010 | CI 覆盖率 | Bootstrap CI 覆盖真实值 ≥ 93% | Monte Carlo 模拟 | SHOULD |

---

## 全局验收门 (v0.4 GA Gate)

以下条件**全部满足**，v0.4 才能标记为"完成"：

| 门编号 | 条件 | 验证方法 |
|--------|------|----------|
| GATE-01 | 所有 MUST 验收项通过 | 验收矩阵 MUST 行逐一核查 |
| GATE-02 | 所有 SHOULD 验收项有明确状态（通过/跳过+理由/失败） | 验收矩阵 SHOULD 行逐一核查 |
| GATE-03 | ruff lint 零错误 | `ruff check .` |
| GATE-04 | pytest -m v01 全通过 | `pytest -m v01` |
| GATE-05 | pytest 全量通过 | `pytest` |
| GATE-06 | MRS 回归: 20 首基线音频处理前后 MRS 差值变化 < 2.0 分 | MRS 回归测试脚本 |
| GATE-07 | A_compliance ≥ 85 (vs 当前 65) | 08_formula_metrics.md 公式计算 |
| GATE-08 | DOC-MFY-003 全部 Markdown 文件无 TODO/占位符 | grep TODO / grep PLACEHOLDER |
| GATE-09 | Founder/CTO 签核 | 人工签核 |

---

## 测试音频基线集

| 要求 | 规格 |
|------|------|
| 数量 | 20 首（固定，不可替换） |
| 来源 | AI 生成 (Suno v3/v4, Udio v1) 至少 12 首 + 真实录音至少 8 首 |
| 风格覆盖 | Classical / Jazz / Rock / Pop / Electronic / Acoustic — 每种 ≥ 2 首 |
| 长度 | 每首 30-180 秒 |
| 格式 | WAV 44.1 kHz 16-bit stereo |
| 存储路径 | `tests/data/baseline/v04/` |
| 冻结时间 | M2 里程碑前冻结（基线集一旦冻结，不可替换或添加） |

---

## 验收检查

- [x] 10 个 AEP 各有 3-5 项验收标准
- [x] MUST/SHOULD/MAY 三级清晰
- [x] 每项有量化标准和验证方法
- [x] 全局验收门 9 项
- [x] 测试基线集规格完整
- [x] GATE-09 预留人工签核
