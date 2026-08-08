# DOC-MFY-003｜AEP-ACU-001~010 任务卡清单

> 每张任务卡是可独立执行的原子研发包。
> 格式：任务定义 → 研发意义 → 输入/输出 → 实验入口 → 工程入口 → 冻结标准
> 优先级：P0 = 阻塞发布 | P1 = 高优先级 | P2 = 条件性合入

---

## AEP-ACU-001: Schroeder Reverb 合规修复 [P0]

### 任务定义

将 `processing/operators.py` 的 `_schroeder_reverb()` 从"仅梳状滤波器"升级为 Schroeder (1962) 原始设计的"梳状 + 全通"完整架构。

### 研发意义

当前混响尾音稀疏——在 50 ms 后可感知离散回声（flutter echo 效应），因为缺少全通滤波器级的回声密度倍增效应。Schroeder (1962) 的原始设计包含 4 个并联梳状滤波器 + 2 个串联全通滤波器——缺一不可。

### 输入

- `processing/operators.py:262-275` — 当前 `_schroeder_reverb()` 实现
- Schroeder (1962) 论文或等效技术描述 (R09)
- 单元脉冲信号 (dirac delta) — 用于脉冲响应测量
- 白噪声 (20 Hz – 20 kHz) — 用于全通级频谱着色验证

### 输出

- 修改后的 `_schroeder_reverb()` — 添加 2 个全通滤波器级
- 脉冲响应对比图 (修复前 vs 修复后)
- 回声密度增长曲线 (echo density vs time)
- 白噪声频谱通过测试结果 (全通级幅频响应平坦性 < 0.1 dB)
- 20 首测试音频的 MRS texture/space 组件对比

### 实验入口

```text
1. 生成单位脉冲 → 分别通过旧/新混响 → 提取脉冲响应
2. 脉冲响应上检测离散回声峰值 (t > 50 ms)
3. 生成白噪声 → 通过全通级 → 验证频谱变化 < 0.1 dB
4. 20 首测试音频 → MRS texture/space 组件配对 t 检验
```

### 工程入口

- `processing/operators.py:_schroeder_reverb()` — 在梳状滤波器循环后添加 2 个全通级
- 全通公式: `y[n] = -g * x[n] + x[n-K] + g * y[n-K]`
- 参考参数: K1 = int(sr * 0.005), g1 = 0.7; K2 = int(sr * 0.0017), g2 = 0.7

### 冻结标准

- [ ] 全通级幅频响应平坦度误差 < 0.1 dB (白噪声测试)
- [ ] 脉冲响应 t > 50 ms 内无可辨识离散回声 (峰值比 < 3:1)
- [ ] MRS texture 组件提升 ≥ 3 分 (20 首测试音频中位数)
- [ ] MRS space 组件不降低 (配对 t 检验 p > 0.05)
- [ ] ruff lint 通过
- [ ] pytest -m v01 通过

---

## AEP-ACU-002: RBJ Biquad EQ 替换 [P0]

### 任务定义

将 `processing/operators.py` 的 FFT sigmoid/Gaussian EQ（`_apply_shelf_freq()` / `_apply_peak_freq()`）替换为 RBJ biquad 标准滤波器。

### 研发意义

当前的 sigmoid 过渡和 Gaussian 峰值的滤波器形状不可预测——过渡宽度约为 0.3 倍频程，Q 值与标准 peaking 滤波器的 Q 值不对应。这导致：(a) 滤波器级联时相互作用不可控，(b) 诊断参数跨版本不可复现，(c) 音频工程师无法理解"3 dB at 2.5 kHz"的实际效果。

### 输入

- `processing/operators.py:116-138` — 当前 FFT EQ 实现
- RBJ Audio EQ Cookbook (R10) — 双二阶滤波器设计公式
- `craft_processes.py` — 已有的 RBJ biquad 参考实现
- 对数扫频信号 (20 Hz – 20 kHz, 10 秒) — 用于频率响应验证

### 输出

- 新的 `_apply_rbj_shelf()` 和 `_apply_rbj_peak()` 函数（时域 biquad 实现）
- 或：废弃 operators.py 的 EQ，全线使用 pedalboard EQ
- 频率响应对比报告 (FFT EQ vs RBJ EQ vs 理论曲线)
- 20 首测试音频的 A/B MRS 对比

### 实验入口

```text
1. 实现 RBJ biquad: low_shelf / high_shelf / peaking 三种滤波器类型
2. 对数扫频 → 三组 EQ (FFT / RBJ / 理论) → 提取幅频响应
3. 计算 FFT vs RBJ、RBJ vs 理论的 RMSE
4. 20 首测试音频 × 3 组参数 (flat/moderate/extreme) → MRS 对比
```

### 工程入口

**方案 A (推荐):** 废弃 operators.py 的 FFT EQ，使用 pedalboard 的 PeakFilter / LowShelfFilter / HighShelfFilter（pedalboard 内部使用 JUCE RBJ biquad）。

**方案 B:** 从 `craft_processes.py` 提取 RBJ biquad 实现为独立模块 `processing/rbj_eq.py`，替换 operators.py 的 EQ。

### 冻结标准

- [ ] 扫频测试：20 Hz – 20 kHz 范围内 RBJ vs 理论 RMSE < 0.1 dB
- [ ] 零增益测试：所有 EQ 参数 = 0 时，输出 vs 输入 RMSE < -96 dBFS
- [ ] MRS 回归：20 首测试音频处理前后 MRS 差值变化 < 2.0 分
- [ ] 处理延迟不增加 > 10%
- [ ] ruff lint 通过
- [ ] pytest -m v01 通过 + pytest 全量通过

---

## AEP-ACU-003: HPSS 残差守恒 [P0]

### 任务定义

HPSS 分解 (librosa.decompose.hpss) 产生三个分量：Harmonic (H)、Percussive (P) 和 Residual (R = input - H - P)。当前 `processing/spectral_chain.py` 丢弃 R。改为保留 R 并审计其能量。

### 研发意义

丢弃残差分量的能量占输入能量的 5-15%（取决于音源和 margin 参数）。这直接违反 PHYS-007 能量守恒——处理链的能量损失不可归因。HPSS 残差守恒修复后，A_compliance 的 H_HPSS 因子从 0.85 升至 0.90。

### 输入

- `processing/spectral_chain.py` — 当前 HPSS 分解与处理流程
- DOC-MFY-001 PHYS-007 守恒公式
- 20 首测试音频（覆盖钢琴、人声、EDM、管弦乐 4 种音源类型）

### 输出

- 修改后的 `spectral_chain.py` — 保留 R 分量
- 残差能量分析报告（R_energy / total_energy，按音源类型分组）
- R 分量频谱分析（判断 R 主要是噪声还是有结构的信号残余）
- 三种处理策略的 A/B 测试：丢弃 R / 保留 R 不加处理 / R 单独处理

### 实验入口

```text
1. 20 首音频 → HPSS (margin=2.0) → 测量 R_energy / total_energy
2. 分析 R 的频谱特性: 白噪声-like (平坦频谱) vs 结构化 (有谱峰)
3. 三种 R 处理策略的 MRS 对比:
   a) R_discard (当前)
   b) R_add_back (直接加回输出)
   c) R_process (R 经低强度处理后加回)
4. 选择最优策略 → 实现
```

### 工程入口

- `processing/spectral_chain.py` — 在 HPSS 分解后保留 R，在重合成时将 R 加回
- 或：R 经低强度压缩（ratio ≤ 1.5）+ 低架滤波（gain ≤ 3 dB）后加回

### 冻结标准

- [ ] 处理后的能量审计: |ΔL_residual| ≤ 3σ (safe) — 当前丢弃 R 时 > 3σ
- [ ] MRS 不低于当前（丢弃 R 的版本）
- [ ] 无新增可听伪影（R 分量加回不应引入噪声感）
- [ ] ruff lint 通过
- [ ] pytest -m v01 通过

---

## AEP-ACU-004: 7 频段默认启用 [P1]

### 任务定义

将当前 6 频段（Sub/Bass/Low-Mid/Mid/Presence/Air）扩展为 7 频段，增加 5-8 kHz 的 Brilliance/Clarity 区间，解决当前 5 kHz (Presence 上界) 到 8 kHz (Air 下界) 的分析盲区。

### 研发意义

5-8 kHz 范围是人耳对齿音 (sibilance, ~5-7 kHz)、清晰度 (clarity, ~6-8 kHz) 和"空气感"的起始区间最敏感的区域。对于 AI 音频，此频段常出现过度的噪声状能量（模型"填充高频"的伪影）。当前 6 频段将此区域拆分到 Presence 的尾部和 Air 的首部——两者都不对 5-8 kHz 做针对性诊断。

### 输入

- `bands.py` — 当前 6 频段定义
- `diagnosis/metrics.py` — 频段能量分析器（需同步更新）

### 输出

- 新的 7 频段定义文件（或更新 `bands.py`）
- 7 频段能量分析器
- 50 首音频的 6 频段 vs 7 频段诊断对比
- 各频段与心理声学 Bark 尺度的对应表

### 实验入口

```text
1. 定义 7 频段边界:
   Sub: 20-60 Hz
   Bass: 60-250 Hz
   Low-Mid: 250-500 Hz
   Mid: 500-2000 Hz
   Presence: 2000-5000 Hz
   Brilliance: 5000-8000 Hz   ← NEW
   Air: 8000-16000 Hz

2. 50 首 AI 音频的 7 频段能量分布分析
3. 重点分析 5-8 kHz 区间的诊断价值:
   - AI 音频在此区间的能量是否与真实录音有显著差异？
   - 是否有可检测的伪影特征（如过度的白噪声能量）？
4. 更新 acoustic_ct.py 的 PDF 报告中的频段显示
```

### 工程入口

- `bands.py` — 从 `SEVEN_BAND_STANDARD` 或直接替换 `SIX_BAND_STANDARD`
- `diagnosis/metrics.py` — 更新 `SpectrumAnalyzer` 的频段定义
- 统一所有模块的频段引用（使用 `bands.py` 作为 single source of truth — DEF-006 修复）

### 冻结标准

- [ ] `bands.py` 是唯一的频段定义来源（消除 DEF-006 不一致）
- [ ] 7 频段能量总和 = 全频段能量（能量守恒验证，误差 < 0.01%）
- [ ] 5-8 kHz Brilliance 区间能量与真实录音参考分布有区分度 (d > 0.3)
- [ ] 诊断参数数量不变（18 参数），仅频段分辨率提升
- [ ] ruff lint + pytest 通过

---

## AEP-ACU-005: True Peak Limiter [P1]

### 任务定义

将 `processing/operators.py:apply_limiter()` 从"采样峰值砖墙限幅器"升级为"真峰值 (True Peak) 砖墙限幅器"，参照 ITU-R BS.1771-1。

### 研发意义

采样峰值 (sample peak) 和真峰值 (true peak) 之间的差异可达 0-3 dB——取决于信号的频率内容和 DAC 的重建滤波器。这意味着当前限幅器声称 -1.0 dBFS 的天花板，实际 DAC 输出可能达到 +2.0 dBFS，导致削波。真峰值限幅器通过 4x 过采样检测片间峰值 (inter-sample peaks)，消除此类隐性削波。

### 输入

- `processing/operators.py:309-343` — 当前 `apply_limiter()` 实现
- ITU-R BS.1771-1 — 真峰值测量标准
- 测试信号：高频纯音 (15 kHz @ -1 dBFS) — 采样峰值与真峰值差异最大的场景

### 输出

- 修改后的 `apply_limiter()` — 4x 过采样真峰值检测 + 非零 attack (1 ms)
- 真峰值 vs 采样峰值对比报告（多频率、多电平）
- 20 首音频的限幅器安全性对比

### 实验入口

```text
1. 15 kHz 纯音 @ -1 dBFS → 当前限幅器 → 测量真峰值（使用 4x 过采样）
2. 同上 → 新限幅器 → 验证真峰值 ≤ ceiling
3. 扫频信号 (20 Hz – 20 kHz) → 测量真峰值余量随频率的变化
4. 20 首音频 A/B: 当前限幅器 vs 真峰值限幅器 → MRS 对比 + 削波计数
```

### 工程入口

- `processing/operators.py:apply_limiter()` — 添加 4x 过采样阶段:
  1. 4x 上采样 (零填充 + 低通滤波)
  2. 真峰值检测
  3. 增益衰减计算
  4. 4x 下采样
- 添加非零 attack (1 ms) — 降低低频失真

### 冻结标准

- [ ] 15 kHz @ -1 dBFS 输入 → 真峰值输出 ≤ ceiling (无片间峰值削波)
- [ ] 全频段扫频：真峰值始终 ≤ ceiling + 0.1 dB
- [ ] 低频 (< 100 Hz) 限幅后的 THD < 0.5% (非零 attack 的效果)
- [ ] 处理延迟增加 < 10 ms
- [ ] MRS 回归通过 (20 首音频差值 < 2.0 分)
- [ ] ruff lint + pytest 通过

---

## AEP-ACU-006: Mel / Bark / ERB 感知频率尺度 [P1]

### 任务定义

在 `diagnosis/metrics.py` 或新建 `moodify/features/psychoacoustic.py` 中加入 Mel 尺度、Bark 尺度和 ERB 尺度三种感知频率映射，并提供对应的频谱表示。

### 研发意义

人耳频率分辨率非线性：低频 ~3 Hz，高频 ~500 Hz。线性 FFT 对 100 Hz 和 10 kHz 应用相同的频率分辨率，导致：(a) 低频分析过度（频率仓比人耳分辨能力更细），(b) 高频分析不足（频率仓比人耳分辨能力更粗）。Mel/Bark/ERB 三种尺度各自从不同角度建模这种非线性——Mel 基于音高感知实验，Bark 基于临界频带和掩蔽，ERB 基于听觉滤波器带宽。

### 输入

- `diagnosis/metrics.py` — 当前频谱分析器（线性 FFT）
- librosa — mel 频谱 (`librosa.feature.melspectrogram`)
- Zwicker (1961) Bark 尺度公式: `Bark(f) = 13 * arctan(0.00076 * f) + 3.5 * arctan((f/7500)^2)`
- Glasberg & Moore (1990) ERB 尺度公式: `ERB(f) = 24.7 * (4.37 * f/1000 + 1)`

### 输出

- `moodify/features/psychoacoustic.py` — 三个感知频谱提取函数
- 感知频谱 vs 线性频谱的对比分析（在 10 首音频上）
- 频段能量在感知尺度和线性尺度下的差异报告

### 实验入口

```text
1. 实现 bark_spectrogram(), mel_spectrogram(), erb_spectrogram()
2. 10 首音频 → 线性频谱 + 三种感知频谱
3. 对比分析:
   - 低频 (< 250 Hz): 感知尺度用更少的参数表示→降维效果
   - 高频 (> 5 kHz): 感知尺度用更多的参数表示→增维效果
4. 确定哪些 MRS 特征组应切换到感知尺度
```

### 工程入口

- 新建 `moodify/features/psychoacoustic.py`
- 三个公共函数：`bark_spectrogram(y, sr)`, `mel_spectrogram(y, sr)`, `erb_spectrogram(y, sr)`
- `diagnosis/metrics.py` 的 `SpectrumAnalyzer` 增加 `scale` 参数: `"linear"` (default) / `"mel"` / `"bark"` / `"erb"`

### 冻结标准

- [ ] Bark/Mel/ERB 三种频谱输出 shape 正确（Mel: n_mels 维度；Bark: n_barks 维度；ERB: n_erbs 维度）
- [ ] 低频区域 (60-250 Hz) 在 Bark 尺度上由 2-3 个 band 表示（vs 线性 FFT 的数十个 bin）
- [ ] 三种感知频谱的计算时间 < 线性 FFT 的 2x
- [ ] ruff lint + pytest 通过

---

## AEP-ACU-007: 心理声学掩蔽初版 [P2]

### 任务定义

实现频率同时掩蔽 (simultaneous masking) 的最小模型：Bark 尺度映射 + 扩展函数 (spreading function) + 掩蔽阈值计算。不实现时间掩蔽，不实现完整 PEAQ。

### 研发意义

这是 L2 感知声学层的入口。当前 MRS 的所有频谱特征假设各频率通道独立——但人耳不是这样工作的。掩蔽模型使系统能够：(a) 识别"能量存在但人耳听不到"的频率分量（被邻近强分量掩蔽），(b) 量化 AI 音频中可听和不可听伪影的区别。这是 PEAQ (AEP-ACU 后续) 和感知加权 MRS 的前置条件。

### 输入

- Zwicker & Fastl (2007) 第 7-8 章 — 掩蔽模型理论
- AEP-ACU-006 的 Bark 尺度映射
- 测试信号：1 kHz 纯音 + 不同频率/电平的掩蔽探针

### 输出

- `moodify/perception/masking.py` — 最小掩蔽模型
- 掩蔽阈值计算函数：`compute_masking_threshold(spectrum, sr) → threshold_per_bark`
- 典型音频信号的激励模式 (excitation pattern) 和掩蔽阈值图
- 感知可听度图 (perceptual audibility map) — 哪些频谱成分高于掩蔽阈值

### 实验入口

```text
1. 实现简化掩蔽模型:
   a) 线性 FFT → Bark 尺度映射 (每 Bark band 的能量)
   b) 扩展函数卷积 (低频掩蔽高频的效率高于反向)
   c) 掩蔽阈值 = 扩展后的激励 - 可听度偏移
2. 验证: 1 kHz 纯音 → 掩蔽阈值应在 1 Bark 附近达到峰值
3. 在 10 首 AI 音频上计算感知可听度图
```

### 工程入口

- 新建 `moodify/perception/masking.py`
- 公共函数：`compute_masking_threshold(spectrum_db, sr)` → `threshold_db`
- 依赖 AEP-ACU-006 先完成（需要 Bark 尺度映射）

### 冻结标准

- [ ] 1 kHz 纯音的掩蔽阈值峰值在 1 Bark 附近（定性验证）
- [ ] 扩展函数不对称性验证：低频掩蔽高频的扩展 > 高频掩蔽低频的扩展
- [ ] 处理一首 3 分钟音频的掩蔽计算时间 < 10 秒
- [ ] ruff lint + pytest 通过

---

## AEP-ACU-008: F0 / Pitch Stability [P2]

### 任务定义

使用 YIN 算法 (de Cheveigné & Kawahara 2002) 实现基频 (F0) 检测和音高稳定性度量，建立 AI 音频特有缺陷（F0 不稳定、无意识转调）的量化工具。

### 研发意义

AI 生成音乐的一个已知问题是 F0 不稳定——模型不理解"同音高"概念，导致人声或主旋律音高在不需要转调的地方漂移。当前 Moodify 没有任何工具来测量这个问题。F0 稳定性度量为诊断引擎增加一个维度——可以量化"这个音频的音高有多稳定"。

### 输入

- YIN 算法论文 (NEW-02)
- librosa.yin / librosa.pyin — 参考实现
- 50 首 AI 音频 + 50 首真实录音 — 比较 F0 稳定性分布

### 输出

- `moodify/features/f0.py` — YIN F0 检测 + F0 稳定性度量
- 函数：`compute_f0(y, sr) → (f0_hz, voiced_prob, f0_stability)`
- AI vs 真实录音的 F0 稳定性对比报告 (t 检验 + 效应量)
- F0 轨迹可视化示例（AI 音频的不稳定 vs 真实录音的稳定）

### 实验入口

```text
1. 实现 YIN F0 检测 (基于 librosa.yin 或自实现)
2. 定义 F0 稳定性: f0_stability = 1 - std(diff(log(f0))) / mean(f0) [归一化]
3. 50 AI + 50 真实音频 → F0 稳定性分布对比
4. 假设: AI 音频的 F0 稳定性显著低于真实录音 (p < 0.001, d > 0.8)
```

### 工程入口

- 新建 `moodify/features/f0.py`
- 公共函数：`compute_f0(y, sr, frame_length=2048, hop_length=512)` → dict
- 返回：f0_hz (array), voiced_prob (array), f0_stability (float), f0_variability_cents (float)

### 冻结标准

- [ ] YIN 输出与 librosa.yin 一致 (RMSE < 1 Hz for f0 < 1000 Hz)
- [ ] AI 音频 F0 稳定性中位数 vs 真实录音: d > 0.5 (Cohen's d)
- [ ] 处理 3 分钟音频的 F0 计算时间 < 5 秒
- [ ] ruff lint + pytest 通过

---

## AEP-ACU-009: Chroma / Key / Harmony [P2]

### 任务定义

实现 12 维 chroma 特征提取、调性 (key) 检测和和声一致性度量，建立 AI 音频和声缺陷的量化工具。

### 研发意义

AI 音频的一个已知问题是和声不一致——模型可能在两小节之间无意识转调，或产生不属于任何标准调式的半音。当前 MRS 的 artifact 组无法检测这种"理论错误"——因为它在物理上不是"伪影"（没有削波/噪声），但在音乐上是一个缺陷。Chroma + Key 检测提供了评估和声质量的工具。

### 输入

- librosa.feature.chroma_cqt / chroma_stft — 参考实现
- Krumhansl-Schmuckler key-finding 算法 — 调性检测
- 50 首 AI 音频 + 50 首真实录音 — 比较 chroma 分布

### 输出

- `moodify/features/chroma.py` — chroma 提取 + 调性检测 + 和声稳定性
- 函数：`compute_chroma(y, sr) → (chroma, key, key_strength, harmony_stability)`
- AI vs 真实录音的 chroma 稳定性对比报告
- 和声不稳定案例的 chroma 帧间变化图

### 实验入口

```text
1. 12 维 chroma (C, C#, D, ..., B) 逐帧提取
2. 调性检测: 平均 chroma 向量 × Krumhansl-Schmuckler 调性模板 → 最大相关
3. 和声稳定性: chroma_stability = mean(cosine_similarity(chroma_t, chroma_{t+1}))
4. 50 AI + 50 真实 → chroma 稳定性分布对比
```

### 工程入口

- 新建 `moodify/features/chroma.py`
- 公共函数：`compute_chroma(y, sr, hop_length=512)` → dict
- 返回：chroma (12×T), key (str), key_strength (float), harmony_stability (float)

### 冻结标准

- [ ] Chroma 向量和为 1（归一化验证）
- [ ] 调性检测在已知调性的测试音频上准确率 > 80%
- [ ] AI 音频和声稳定性中位数 vs 真实录音: d > 0.3 (Cohen's d)
- [ ] 处理 3 分钟音频的 chroma 计算时间 < 3 秒
- [ ] ruff lint + pytest 通过

---

## AEP-ACU-010: MRS 参考集鲁棒化 [P2]

### 任务定义

将 MRS 的参考分布从"单一通用分布"升级为"分风格参考分布 + 非正态鲁棒评分 + 置信区间"。

### 研发意义

当前 MRS 参考分布是一个"所有真实录音的混合"——这是有问题的：(a) 古典音乐和 EDM 的频谱质心分布差异巨大——混在一起的参考分布会稀释风格特异的正常范围，(b) 非正态特征的 Mahalanobis 距离在尾部不可靠，(c) 没有置信区间，使用者不知道"75 分和 78 分是否有显著差异"。

### 输入

- `reality_metrics.py` — 当前 MRS 参考统计计算
- MRS 参考音频集（真实录音，≥ 100 首）
- 风格标签（至少：Classical / Jazz / Rock / Pop / Electronic / Acoustic）

### 输出

- 分风格参考分布（μ, σ 按风格分组）
- 鲁棒评分：使用 MAD (Median Absolute Deviation) 替代标准差
- 置信区间：bootstrap CI (95%)
- 分风格 MRS 评分 vs 混合 MRS 评分的对比分析

### 实验入口

```text
1. 100+ 首真实录音按风格分组 (≥ 6 组，每组 ≥ 15 首)
2. 每组计算: μ_i, MAD_i (鲁棒), σ_i (用于对比)
3. 20 首测试音频 → 混合参考 MRS vs 分风格参考 MRS
4. Bootstrap (n=1000) → 95% CI for each MRS
5. 分析: 分风格 MRS 是否比混合 MRS 更精确（CI 更窄）
```

### 工程入口

- `reality_metrics.py` — 添加 `reference_by_genre` 参数
- 新建 `moodify/mrs_robust.py` — 鲁棒评分 + Bootstrap CI

### 冻结标准

- [ ] 分风格 MRS 的 95% CI 宽度比混合 MRS 窄 ≥ 20%
- [ ] MAD-based 评分的异常值敏感性 < SD-based 评分（在 contaminated sample 上验证）
- [ ] Bootstrap CI 覆盖真实 MRS 值的比例 ≥ 93%（接近名义 95%）
- [ ] ruff lint + pytest 通过

---

## 任务优先级与依赖汇总

```text
P0 (阻塞 v0.4 发布):
  ACU-001 (Schroeder) ── 独立
  ACU-002 (RBJ EQ)    ── 独立
  ACU-003 (HPSS 残差) ── 独立

P1 (必须完成，可并行):
  ACU-004 (7 频段)    ── 独立（修复 DEF-006 作为前提）
  ACU-005 (True Peak) ── 独立
  ACU-006 (感知尺度)  ── 独立（ACU-007 的前置）

P2 (条件合入):
  ACU-007 (掩蔽)      ── 依赖 ACU-006
  ACU-008 (F0)        ── 独立
  ACU-009 (Chroma)    ── 独立
  ACU-010 (MRS 鲁棒)  ── 独立
```

---

## 验收检查

- [x] 10 张任务卡全部创建 (ACU-001 ~ ACU-010)
- [x] 每张卡有：任务定义、研发意义、输入、输出、实验入口、工程入口、冻结标准
- [x] P0 × 3, P1 × 3, P2 × 4
- [x] 冻结标准每项可量化验证
- [x] 依赖关系明确（ACU-007 依赖 ACU-006）
- [x] 每张卡标注代码文件路径
