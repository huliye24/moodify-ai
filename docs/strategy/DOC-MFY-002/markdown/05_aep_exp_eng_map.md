# T5｜AEP / EXP / ENG 任务入口映射

> 编号体系说明：
> - **AEP-MFY-XXX** = Atomic Experiment Package — 可独立执行的原子实验包
> - **EXP-MFY-XXX** = Experiment — 需要实验验证的研究任务（假设→实验→数据→结论）
> - **ENG-MFY-XXX** = Engineering — 确定性工程实现任务（已知怎么做，需要写代码）
> - 继承 DOC-MFY-001 的 PHYS/ENG 编号序列，新编号从 MFY-001 开始

---

## 任务包清单

### 包 1：EQ 滤波器标准化

| 属性 | 内容 |
|------|------|
| 来源缺陷 | DEF-001 |
| 层级 | L1 声学合规层 |
| 优先级 | P0 |

**AEP-MFY-001: EQ 滤波器扫频对比实验**

- 类型：验证性实验
- 输入：operators.py FFT EQ + pedalboard RBJ EQ + 理论 RBJ biquad 参考实现
- 方法：对数扫频信号 (20 Hz – 20 kHz) → 三组 EQ 处理 → 幅频响应提取 → RMSE 对比
- 输出：频率响应误差报告 (FFT vs RBJ)、各滤波器类型 (low shelf / high shelf / peaking) 的偏差曲线
- 预计耗时：2 小时（含代码编写和运行）

**EXP-MFY-001: EQ 替换对处理质量的影响评估**

- 类型：对比实验
- 假设：RBJ EQ 处理后的 MRS 与 FFT EQ 无显著差异（p > 0.05），但频率响应可预测性显著提升
- 方法：20 首测试音频 × 2 种 EQ × 3 组参数 (flat / moderate / extreme) → MRS 对比 + 频谱质心对比
- 输出：MRS 等效性检验报告 + 频谱质心分布对比
- 预计耗时：4 小时

**ENG-MFY-001: RBJ biquad EQ 模块实现**

- 类型：工程实现
- 内容：从 `craft_processes.py` 提取 RBJ biquad 实现 → 独立模块 → 替换 `operators.py` 的 FFT EQ
- 验收：扫频测试 RMSE < 0.1 dB；零增益测试 RMSE < -96 dBFS；MRS 回归测试差值 < 2.0 分
- 预计耗时：8 小时

---

### 包 2：Schroeder 混响完善

| 属性 | 内容 |
|------|------|
| 来源缺陷 | DEF-002, DEF-008 |
| 层级 | L1 声学合规层 |
| 优先级 | P0 (DEF-002) / P2 (DEF-008) |

**AEP-MFY-002: 全通滤波器脉冲响应测量**

- 类型：验证性实验
- 输入：当前梳状-only 混响 + 添加全通级后的混响
- 方法：单位脉冲 → 两种混响处理 → 脉冲响应提取 → 回声密度分析
- 输出：脉冲响应对比图、回声密度增长曲线、频谱着色检查 (白噪声通过全通级)
- 预计耗时：1.5 小时

**EXP-MFY-002: 全通级对混响感知质量的影响**

- 类型：对比实验
- 假设：添加全通滤波器级后，MRS texture/space 组件提升 3-8 分
- 方法：20 首测试音频 × 2 种混响 (with/without all-pass) → MRS 对比 + 非正式听感对比
- 输出：MRS texture/space 组件的配对 t 检验报告
- 预计耗时：3 小时

**ENG-MFY-002: Schroeder 全通滤波器实现**

- 类型：工程实现
- 内容：在 `_schroeder_reverb()` 中添加 2 个全通滤波器级 (delay 5 ms / 1.7 ms, gain 0.7)
- 验收：全通级幅频响应平坦 (< 0.1 dB)；脉冲响应无离散回声；MRS space/texture 不降低
- 预计耗时：4 小时

**EXP-MFY-008: 立体声混响改善实验**

- 类型：对比实验
- 假设：双声道独立混响的 MRS space 组件比单声道混响高 3-5 分
- 方法：20 首立体声测试音频 × 2 种混响模式 → MRS space 对比 + IACC 频率曲线
- 预计耗时：3 小时

**ENG-MFY-008: 双声道混响实现**

- 类型：工程实现
- 内容：修改 `apply_reverb()` — 左右声道独立运行，不同延迟 (±5%)
- 验收：单声道输入保持 IACC ≈ 1.0；立体声输入 space 组件改善；无相位问题
- 预计耗时：4 小时

---

### 包 3：感知质量评估 (PEAQ)

| 属性 | 内容 |
|------|------|
| 来源缺陷 | DEF-003, DEF-004 |
| 层级 | L2 感知声学层 |
| 优先级 | P1 |

**EXP-MFY-003: PEAQ Basic 模型在 AI 音频上的适用性验证**

- 类型：验证性实验
- 假设：PEAQ Basic ODG 与人类听感评分的相关性 (r > 0.75) 在 AI 音频上不低于其在传统编码损伤上的表现
- 方法：实现 PEAQ Basic → 20 首 AI 音频处理前后对 → ODG 评分 → 与 MRS 和人类评分对比
- 输出：PEAQ vs MRS vs Human 的三方相关性矩阵
- 预计耗时：16 小时（含 PEAQ 实现和研究）

**ENG-MFY-003: PEAQ Basic 模块实现**

- 类型：工程实现
- 内容：`moodify/perception/peaq.py` — FFT-based ear model + NMR + ODG
- 验收：标准测试向量验证；ODG 输出范围 [-4, 0]；与 MRS 管线集成
- 预计耗时：24 小时

**EXP-MFY-004: 频率掩蔽模型对 MRS 的影响**

- 类型：验证性实验
- 假设：掩蔽感知加权的 MRS 对 AI 频谱空洞的敏感度低于传统 MRS
- 方法：实现 Bark 扩展函数 → 掩蔽阈值计算 → 感知加权 MRS → 对比加权/未加权在 AI 伪影上的评分
- 输出：感知加权 MRS vs 传统 MRS 的差异分析报告
- 预计耗时：12 小时

**ENG-MFY-004: 频率掩蔽感知加权模块**

- 类型：工程实现
- 内容：`moodify/perception/masking.py` — Bark 映射 + 扩展函数 + 掩蔽阈值计算
- 验收：掩蔽曲线与 Zwicker & Fastl (2007) 定性一致；加权后 MRS 人类一致性不低于未加权
- 预计耗时：16 小时

---

### 包 4：心理声学特征扩展

| 属性 | 内容 |
|------|------|
| 来源缺陷 | DEF-005, DEF-007 |
| 层级 | L2 感知声学层 |
| 优先级 | P1 (DEF-005) / P2 (DEF-007) |

**EXP-MFY-005: 标准 MIR 特征对 AI 音频的判别力**

- 类型：探索性实验
- 假设：mel/Bark 频谱、MFCC、chroma、F0 特征在 AI vs 真实音频二分任务上 AUC > 0.65
- 方法：50 AI + 50 真实音频 → librosa 特征提取 → 特征分布对比 → 二分分类 AUC
- 输出：特征判别力排名表 + 推荐纳入 MRS 的特征子集
- 预计耗时：8 小时

**ENG-MFY-005: 心理声学特征提取模块**

- 类型：工程实现
- 内容：`moodify/features/psychoacoustic.py` — mel 频谱、MFCC(13)、chroma(12)、F0(YIN)、chroma_stability、F0_std
- 验收：与 librosa 参考实现输出一致 (tol=1e-6)；处理 3 分钟音频 < 5 秒
- 预计耗时：12 小时

**EXP-MFY-007: Vassilakis 粗糙度 vs 当前代理**

- 类型：对比实验
- 假设：Vassilakis 粗糙度与人类粗糙度评分的 r > 0.70，高于当前卷积方差代理
- 方法：20 首音频 × 2 种粗糙度 + 3 人粗糙度评分 → 相关性对比
- 预计耗时：6 小时

**ENG-MFY-007: 标准粗糙度模型实现**

- 类型：工程实现
- 内容：`diagnosis/metrics.py:compute_roughness()` — Vassilakis (2007) 粗糙度模型
- 验收：合成测试信号 (双纯音 0-200 Hz 频差) 产生合理粗糙度曲线；r > 0.65 vs 人类评分
- 预计耗时：8 小时

---

### 包 5：工程加固

| 属性 | 内容 |
|------|------|
| 来源缺陷 | DEF-006, DEF-009, DEF-011, DEF-012 |
| 层级 | L1/L2/L3 |
| 优先级 | P1 (DEF-006) / P2 (DEF-009/011/012) |

**ENG-MFY-006: 频段定义统一**

- 类型：工程修复
- 内容：统一 `diagnosis/metrics.py` 使用 `bands.py` 的频段定义；添加跨模块频段一致性单元测试
- 验收：ICC > 0.95；`bands.py` 为唯一频段定义来源
- 预计耗时：4 小时

**EXP-MFY-009: stereo-link 参数对动态处理的影响**

- 类型：参数扫描实验
- 假设：50% stereo-link 在 AI 音频上产生优于 100% linked 的 MRS dynamic 评分
- 方法：10 首宽立体声音频 × 3 种 link 模式 (dual-mono / 50% / 100%) → MRS dynamic 对比
- 预计耗时：4 小时

**ENG-MFY-009: 可配置 stereo-link 压缩器**

- 类型：工程实现
- 内容：`apply_compressor()` 添加 `stereo_link` 参数 [0.0, 1.0]
- 验收：link=1.0 行为回归测试；dual-mono 左右独立；增益差异 > 3 dB 触发警告
- 预计耗时：6 小时

**EXP-MFY-011: HPSS margin 自适应**

- 类型：参数优化实验
- 假设：spectral_flux → adaptive_margin 映射使 hpss_leakage 跨音源标准差减小 50%
- 方法：20 首 × 5 margin 值 → optimal margin 标定 → spectral_flux vs optimal_margin 拟合
- 预计耗时：5 小时

**ENG-MFY-011: HPSS 自适应 margin**

- 类型：工程实现
- 内容：`spectral_chain.py` — 处理前计算 spectral_flux → 查找表/回归选择 margin
- 验收：自适应 margin 的盲听测试不劣于固定 margin；hpss_leakage 标准差 < 0.05
- 预计耗时：4 小时

**EXP-MFY-012: Kalman filter vs 岭回归校准**

- 类型：对比实验
- 假设：Kalman filter 在 10 次校准时的预测误差 < 岭回归在 10 次时的预测误差
- 方法：历史校准数据 → 两种方法对比 → 收敛曲线 + B_uncertainty 与真实误差的相关性
- 预计耗时：12 小时

**ENG-MFY-012: Kalman filter 在线校准**

- 类型：工程实现
- 内容：`calibration/kalman.py` — 75 维状态空间 + 增量更新 + 不确定性估计
- 验收：收敛速度 ≥ 岭回归；B_uncertainty 与真实误差 Spearman r > 0.5；MRS 改善不降低
- 预计耗时：16 小时

---

### 包 6：方法论建设

| 属性 | 内容 |
|------|------|
| 来源缺陷 | DEF-010, DEF-013 |
| 层级 | L3 音乐智能层 |
| 优先级 | P2 |

**EXP-MFY-010: AI 评委与人类评委校准实验**

- 类型：校准实验
- 假设：AI 评委对"过度处理"的敏感度低于人类评委
- 方法：10 首音频 × 3 处理强度 × 5 人听感测试 (BS.1116 简化协议) + AI 评委评分 → 偏差量化
- 输出：AI-human 偏差校准曲线 + 95% 置信区间
- 预计耗时：24 小时（含人员协调）

**EXP-MFY-013: Valence-Arousal 情绪维度标定**

- 类型：标定实验
- 假设：8 情绪在 VA 空间的定位具有跨标注者一致性 (ICC > 0.7)
- 方法：3 人标注 8 情绪的 (V, A) 坐标 → ICC 计算 → VA 空间定位
- 输出：8 情绪的 VA 坐标表 + 参数插值算法
- 预计耗时：8 小时

**ENG-MFY-013: VA 情绪插值模块**

- 类型：工程实现
- 内容：`knowledge/emotion_interpolation.py` — VA 坐标 → 工艺参数加权插值
- 验收：相邻情绪参数过渡平滑 (< 10% per VA unit)；中间情绪不违反禁忌症
- 预计耗时：8 小时

---

## 任务依赖图

```text
ENG-MFY-006 (频段统一) ── 无依赖，可立即执行
  │
  ├─→ ENG-MFY-001 (RBJ EQ) ── 依赖 AEP-MFY-001 扫频验证
  │
  ├─→ ENG-MFY-005 (心理声学特征) ── 依赖 EXP-MFY-005 特征验证
  │     │
  │     ├─→ ENG-MFY-004 (掩蔽模型) ── 依赖 EXP-MFY-004
  │     │     │
  │     │     └─→ ENG-MFY-003 (PEAQ) ── 依赖 EXP-MFY-003
  │     │
  │     └─→ ENG-MFY-007 (粗糙度) ── 依赖 EXP-MFY-007
  │
  ├─→ ENG-MFY-002 (全通滤波器) ── 依赖 AEP-MFY-002 脉冲测量
  │     │
  │     └─→ ENG-MFY-008 (立体声混响) ── 依赖 EXP-MFY-008
  │
  ├─→ ENG-MFY-009 (stereo-link) ── 无硬依赖
  ├─→ ENG-MFY-011 (HPSS 自适应) ── 依赖 EXP-MFY-011
  ├─→ ENG-MFY-012 (Kalman 校准) ── 依赖 EXP-MFY-012
  └─→ ENG-MFY-013 (VA 情绪) ── 依赖 EXP-MFY-013
```

---

## 资源估算

| 类别 | 任务数 | 总预计时间 | 关键资源 |
|------|--------|-----------|----------|
| AEP (原子验证) | 2 | 3.5 h | 扫频信号 + 脉冲信号 |
| EXP (研究实验) | 11 | 100 h | 测试音频集 + 计算资源 + 人类标注者 |
| ENG (工程实现) | 11 | 110 h | 开发环境 + 代码审查 |
| **总计** | **24** | **~213 h** | **约 5-6 周 (1 人全职)** |

---

## 验收检查

- [x] 每个缺陷映射到至少 1 个 AEP/EXP/ENG 任务
- [x] 每个实验有类型、假设、方法、输出、预计耗时
- [x] 每个工程任务有内容、验收标准、预计耗时
- [x] 任务依赖图完整
- [x] 编号体系连贯 (AEP-MFY-001~002 / EXP-MFY-001~013 / ENG-MFY-001~013)
- [x] 资源估算合理 (总计 ~213 小时)
