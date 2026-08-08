# T2｜缺陷登记表

> 审计方法：代码→理论→标准 三层对照
> 模板：每缺陷含审计发现、风险等级、声学/音乐理论原因、科学假设、变量定义、实验步骤、工程实现入口、预期结果、验收标准、后续任务编号
> 风险等级定义：P0 = 阻塞发布（声音质量/合规性严重受损）| P1 = 高优先级（显著影响处理质量或理论完整性）| P2 = 常规（边际改善或长期完善）

---

## 严重问题 (P0)

### DEF-001：主 EQ 路径使用非标准 FFT sigmoid/Gaussian 滤波器

- **审计发现**：`processing/operators.py:116-138` 的 `_apply_shelf_freq()` 和 `_apply_peak_freq()` 使用 sigmoid 过渡和 Gaussian 峰值，而非行业标准 RBJ biquad 滤波器 (Audio EQ Cookbook, R10)。`craft_processes.py` 中有正确的 RBJ 实现，但未接入主处理路径。
- **风险等级**：P0
- **声学/音乐理论原因**：RBJ biquad 滤波器的幅频响应经过精确数学定义——低架滤波器的 DC 增益、Nyquist 增益、截止频率处的 -3 dB 点（或 shelf 的中点增益）是可预测的。sigmoid 逼近在高频端的滚降速率不可控（sigmoid 的过渡宽度为 freq × 0.3，约为 0.3 倍频程），且 Gaussian peaking 的 Q 值与标准 peaking 滤波器的 Q 值不对应。这导致：(a) 滤波器形状不可预测，(b) 多个滤波器级联时产生不可控的相互作用，(c) 竞品和音频工程师无法理解"3 dB at 2.5 kHz"的实际效果。
- **科学假设**：使用 RBJ biquad 替换 FFT EQ 后，EQ 频率响应与理论曲线的 RMSE 将从当前估计的 ±1.5 dB 降至 ±0.1 dB 以内。
- **变量定义**：
  - `freq_response_error` = |H_actual(f) - H_theory(f)| 的 RMS 值 (dB)
  - `cascade_interaction` = 两个滤波器级联的实测响应与预期乘积响应的偏差 (dB)
  - `MRS_delta_EQ` = RBJ EQ 处理 vs FFT EQ 处理的 MRS 差值
- **实验步骤**：
  1. 对 operators.py 的 EQ 和 pedalboard (RBJ) 的 EQ 施加相同的参数 (shelf_gain=±6 dB, peak_gain=±6 dB, Q=1.0)
  2. 使用对数扫频信号 (20 Hz – 20 kHz) 测量两者的幅频响应
  3. 计算每个频率点的 |H_FFT(f) - H_RBJ(f)| 误差
  4. 在 20 首测试音频上对比两个 EQ 路径的处理结果，测量 MRS 差异
- **工程实现入口**：将 `craft_processes.py` 中的 RBJ biquad 实现抽取为独立模块，替换 `operators.py` 中的 FFT EQ。或废弃 operators.py 的 EQ，全线使用 pedalboard EQ（pedalboard 内部使用 JUCE 的 RBJ biquad）。
- **预期结果**：RBJ EQ 在全频段的频率响应误差 < 0.1 dB（受浮点精度限制）。MRS 改善不显著（EQ 不是 MRS 的主要驱动因素），但诊断参数的跨版本可重复性显著提升。
- **验收标准**：
  - 扫频测试：20 Hz – 20 kHz 范围内 RMSE < 0.1 dB
  - MRS 回归测试：20 首测试音频的处理前后 MRS 差值变化 < 2.0 分
  - 零增益测试：所有 EQ 参数为 0 时，输出 = 输入 (RMSE < -96 dBFS)
- **后续任务编号**：EXP-MFY-001 / ENG-MFY-001

### DEF-002：Schroeder 混响缺少全通滤波器级

- **审计发现**：`processing/operators.py:262-275` 的 `_schroeder_reverb()` 只实现了 4 个并联梳状滤波器，缺少 Schroeder (1962, R09) 原始设计中的串联全通滤波器级。全通级的作用是增加回声密度（echo density）而不改变频谱——缺少它们会导致混响尾音听起来"稀疏"或有可辨识的离散回声。
- **风险等级**：P0
- **声学/音乐理论原因**：Schroeder (1962) 的完整设计包含：(1) 多个并联梳状滤波器（提供频率相关的混响时间），(2) 两个串联全通滤波器（增加时域扩散而不引入额外的频率着色）。全通滤波器通过引入群延迟色散（group delay dispersion）使回声密度呈指数增长——在 50 ms 内从稀疏的离散回声过渡到统计上不可区分的扩散混响。缺少全通级意味着回声密度增长仅为线性（仅来自梳状滤波器的反馈），导致：(a) 混响尾音可感知为离散回声（flutter echo 效应），(b) 冲击音的混响响应不自然，(c) 混响的空间感（spaciousness）不足。
- **科学假设**：添加 2 个串联全通滤波器后，混响的感知自然度（通过 MRS texture 和 space 组件评估）将提升 5-10%。
- **变量定义**：
  - `echo_density` = 每秒回声数（可通过混响脉冲响应的峰值检测估算）
  - `temporal_spread` = 混响脉冲响应的时域扩散度量
  - `MRS_space_delta` = 添加全通级前后 MRS space 组件的差值
- **实验步骤**：
  1. 实现 Schroeder 全通滤波器（可调延迟长度和增益系数）
  2. 在梳状滤波器后串联 2 个全通滤波器（参考 Schroeder 1962 的推荐参数：延迟 5 ms / 1.7 ms，增益 0.7）
  3. 测量添加全通级前后的脉冲响应
  4. 在 20 首测试音频上对比新旧混响的 MRS texture 和 space 组件
  5. 进行非正式听感对比
- **工程实现入口**：在 `_schroeder_reverb()` 函数末尾添加 2 个全通滤波器级。全通滤波器实现：y[n] = -g × x[n] + x[n-K] + g × y[n-K]，其中 g 为增益系数 (0 < g < 1)，K 为延迟采样数。
- **预期结果**：脉冲响应的时域扩散度量提升 > 50%。MRS space/temporal 组件提升 3-8 分。无新增频率着色（全通滤波器的幅频响应为常数 1）。
- **验收标准**：
  - 全通级的幅频响应验证：白噪声通过全通级后，频谱变化 < 0.1 dB
  - 脉冲响应测试：t > 50 ms 后无可见的离散回声峰值
  - MRS space 组件不降低，texture 组件提升 3+ 分
- **后续任务编号**：EXP-MFY-002 / ENG-MFY-002

---

## 强烈建议修复 (P1)

### DEF-003：无感知音频质量评估模型 (PEAQ)

- **审计发现**：MRS 使用马氏距离 (Mahalanobis distance) 作为质量度量（`reality_metrics.py`），但未实现 ITU-R BS.1387-2 (PEAQ, R08) 或任何基于心理声学模型的感知质量评估。马氏距离假设特征空间是欧几里得的，但听觉感知空间不是——频率掩蔽、时间掩蔽、响度感知都是非线性的。
- **风险等级**：P1
- **声学/音乐理论原因**：PEAQ (Perceptual Evaluation of Audio Quality) 是 ITU-R BS.1387 定义的客观感知音频质量测量标准。它包含：(1) 基于 FFT 的耳模型（外耳/中耳滤波 + 频率到 Bark 尺度映射 + 频域扩展函数），(2) 基于滤波器组的耳模型，(3) 认知模型（将感知特征映射到单一质量评分 ODG — Objective Difference Grade）。MRS 的 7 组马氏距离是感知模型的简化代理——它测量"距离参考分布的统计距离"，而非"人耳感知到的差异"。两者的关键差异：两个在特征空间中距离相同的音频，如果差异落在不同的临界频带，感知差异可能相差数倍。
- **科学假设**：引入 PEAQ Basic 模型（FFT-based ear model）作为 MRS 的补充维度，将提升 MRS 与人类听感评分的一致性（相关系数从当前估计的 r ≈ 0.65 提升至 r ≈ 0.80）。
- **变量定义**：
  - `ODG` = Objective Difference Grade [-4, 0]，PEAQ 输出，0 = 不可感知差异，-4 = 非常恼人
  - `NMR` = Noise-to-Mask Ratio (dB)，PEAQ 中间特征——信号能量与掩蔽阈值的比值
  - `MRS_human_corr` = MRS 评分与人类听感评分的 Pearson 相关系数
- **实验步骤**：
  1. 实现 PEAQ Basic (FFT-based) 模型：外耳/中耳滤波 → 加窗 FFT → Bark 尺度映射 → 频域扩展 → 掩蔽阈值计算 → NMR → ODG
  2. 在 20 首 AI 音频的处理前后对上计算 ODG
  3. 对比 ODG 与 MRS 在相同音频对上的评分
  4. 收集 5 人听感测试数据，计算 MRS 和 ODG 各自与人类评分的一致性
- **工程实现入口**：新建 `moodify/perception/peaq.py`，实现 PEAQ Basic 模型。在 MRS 计算管线中添加可选的 PEAQ 维度。
- **预期结果**：ODG 比 MRS 对编码伪影和频谱空洞更敏感（因为掩蔽模型检测到可听噪声）。MRS + ODG 组合评分的人类一致性 r > 0.80。
- **验收标准**：
  - PEAQ 实现在已知测试信号上产生符合 BS.1387 标准的 ODG 值（使用标准测试向量验证）
  - MRS + ODG 组合评分与人类评分的相关系数 > 0.75
- **后续任务编号**：EXP-MFY-003 / ENG-MFY-003

### DEF-004：无频率掩蔽模型

- **审计发现**：DOC-MFY-001 R05 (Zwicker & Fastl 2007) 明确标注 MRS "未实现频率掩蔽模型"——这是已知的理论缺口，但当前代码中没有任何掩蔽相关计算。所有频谱分析（S1-S5、reality_metrics.py 的 spectrum 组）均假设频率通道独立，忽略人耳的频率掩蔽效应。
- **风险等级**：P1
- **声学/音乐理论原因**：人耳基底膜 (basilar membrane) 的频率分析不是独立的 FFT 频率仓——每个临界频带 (Bark scale) 内，强信号会掩蔽弱信号。具体机制：(1) 同时掩蔽 (simultaneous masking)：一个强的 1 kHz 纯音可以掩蔽其上下各 0.5 Bark 范围内的较弱分量；(2) 前向/后向掩蔽 (temporal masking)：强音结束后约 50-200 ms 内，后续弱音被掩蔽；(3) 掩蔽的非对称性：低频掩蔽高频的效率高于高频掩蔽低频（因为基底膜的激励模式向上扩展）。忽略掩蔽意味着：MRS 对"能量集中在少数临界频带"的 AI 伪影不敏感——这些能量可能在物理上存在，但在感知上被掩蔽了。
- **科学假设**：引入频率掩蔽权重后，MRS 对 AI 生成音频中"多余但不被感知"的频谱成分将降权，从而使 MRS 更贴近真实听觉体验。
- **变量定义**：
  - `masking_threshold(f)` = 频率 f 处的掩蔽阈值 (dB SPL)
  - `excitation_pattern` = 基底膜激励模式——信号能量在 Bark 尺度上的卷积扩展
  - `SMR` = Signal-to-Mask Ratio (dB)
- **实验步骤**：
  1. 实现简化的掩蔽模型：FFT → Bark 尺度映射 → 扩展函数 (spreading function) 卷积 → 掩蔽阈值计算
  2. 在 MRS 特征提取中，使用掩蔽阈值对频谱特征进行感知加权
  3. 对比加权前后的 MRS 在 AI 伪影（频谱空洞、密集尖峰）上的评分差异
- **工程实现入口**：新建 `moodify/perception/masking.py`。在 reality_metrics.py 的 spectrum 和 artifact 组特征提取中加入可选的掩蔽感知加权。
- **预期结果**：对于有明显频谱空洞的 AI 音频（如 Suno v3 高频缺失），掩蔽感知 MRS 的 artifact 组评分与传统 MRS 有显著差异（d > 0.5 标准差）。
- **验收标准**：
  - 掩蔽模型输出与 Zwicker & Fastl (2007) 第 7 章节的图表在定性上一致
  - 掩蔽感知 MRS 与人类评分的一致性不低于传统 MRS
- **后续任务编号**：EXP-MFY-004 / ENG-MFY-004

### DEF-005：MRS 缺少标准心理声学特征 (mel/bark/chroma/F0)

- **审计发现**：DOC-MFY-001 R13 (Tzanetakis & Cook 2002) 提到 mel/Bark/chroma/MFCC 等标准 MIR 特征，但 Moodify 当前仅使用 FFT 频谱特征。具体缺失：(a) Mel/Bark 尺度频谱——更贴近人耳频率分辨率；(b) Chroma 特征——不能评估和声质量；(c) F0 基频检测——不能评估音高稳定性；(d) MFCC——MIR 中最通用的音色描述符。
- **风险等级**：P1
- **声学/音乐理论原因**：(a) 人耳频率分辨率在低频高 (Δf ≈ 3 Hz at 100 Hz)、高频低 (Δf ≈ 500 Hz at 10 kHz)，线性 FFT 频率仓不能反映这种非线性分辨率；(b) chroma 特征将频谱映射到 12 个半音类——和声分析的基础；(c) AI 生成音乐的一个已知问题是 F0 不稳定（模型不理解"同音高"概念），没有 F0 检测就无法量化这个缺陷；(d) MFCC 是语音/音乐识别中最成熟的音色特征，去相关 (DCT) 使得各系数独立，适合统计建模。
- **科学假设**：添加 mel/Bark 频谱特征 + chroma + F0 + MFCC 后，MRS 的维度从 7 组扩展至 9 组（新增 harmonic 和 tonal 组），对 AI 音乐特有的和声/音高缺陷的检测能力从几乎为零提升至可量化水平。
- **变量定义**：
  - `chroma_stability` = 连续帧间 chroma 向量的余弦相似度均值
  - `F0_std` = 基频的帧间标准差 (cents)
  - `MFCC_distance` = 被测音频 MFCC 与参考分布的马氏距离
- **实验步骤**：
  1. 使用 librosa 提取 mel 频谱、MFCC (13 维)、chroma (12 维)、F0 (YIN 算法)
  2. 计算 chroma_stability 和 F0_std 作为新的 MRS 子维度
  3. 在 50 首 AI 音频 vs 50 首真实录音上对比新特征分布
  4. 评估新特征对 MRS 区分能力的增益
- **工程实现入口**：在 `diagnosis/metrics.py` 或新建 `moodify/features/psychoacoustic.py` 中实现。扩展 `reality_metrics.py` 的参考分布以包含新特征。
- **预期结果**：AI 音频的 chroma_stability 显著低于真实录音（p < 0.01），F0_std 显著高于真实录音（p < 0.001）。新 harmonic 和 tonal 组使 MRS 对 AI 音频的判别 AUC 提升 0.05-0.10。
- **验收标准**：
  - 新特征在 AI vs 真实二分分类任务上 AUC > 0.65
  - 添加新特征后 MRS 总分在真实录音上的分布不发生显著偏移 (< 2 分)
- **后续任务编号**：EXP-MFY-005 / ENG-MFY-005

---

## 中等优先级 (P2)

### DEF-006：频段定义跨模块不一致

- **审计发现**：`bands.py` 定义 Bass 为 60-250 Hz，`diagnosis/metrics.py` 的 `SpectrumAnalyzer` 定义 Bass 为 60-200 Hz。200 Hz 和 250 Hz 的差异约为小三度 (minor third)——在这个频率范围内，许多乐器的基频和人声的低频成分可能落入不同的频段，导致跨模块诊断不一致。
- **风险等级**：P2
- **声学/音乐理论原因**：200-250 Hz 范围是男声基频的上限 (~G3-B3) 和许多乐器的低次泛音区。此频段影响"温暖感"(warmth) 和"泥浆感"(muddiness) 的感知。如果 diagnosis/metrics.py 将 230 Hz 成分归入 Low-Mid（诊断语义：清晰度/咬字感），而 bands.py 将其归入 Bass（诊断语义：重量/温暖），则同一频率成分在两个模块中获得不同的诊断标签。
- **科学假设**：统一 Bass 上界为 250 Hz 后，诊断引擎的 S2 (Bass) 和 S3 (Low-Mid) 参数在跨模块测量中的一致性 (ICC) 从当前估计的 ICC < 0.8 提升至 ICC > 0.9。
- **变量定义**：
  - `ICC_band` = 不同模块对同一音频的同名频段能量测量的组内相关系数
  - `diagnosis_divergence` = 同一音频在不同模块中获得不同诊断（如"Bass 不足" vs "Low-Mid 正常"）的概率
- **实验步骤**：
  1. 在 bands.py 中统一频段边界定义（推荐：Bass 60-250 Hz，与六频段标准的心理声学依据更一致——250 Hz 约等于 Bark 8 的上界）
  2. 更新所有引用频段边界的模块（diagnosis/metrics.py、acoustic_ct.py、visualization 等）
  3. 在 50 首音频上对比统一前后的诊断参数值变化
- **工程实现入口**：修改 `diagnosis/metrics.py` 中 `SpectrumAnalyzer` 的频段边界定义，与 `bands.py` 对齐。添加单元测试验证跨模块频段一致性。
- **预期结果**：统一后 ICC > 0.95。低频段诊断参数的语义明确——"Bass" 在任何模块中都指向 60-250 Hz。
- **验收标准**：
  - `bands.py` 为唯一的频段定义来源（single source of truth）
  - 所有模块的频段能量测量 ICC > 0.95
- **后续任务编号**：ENG-MFY-006

### DEF-007：频谱粗糙度使用非标准代理

- **审计发现**：`reality_metrics.py` 的 `_texture_features()` 使用"卷积局部方差"作为频谱粗糙度的代理，而非 Vassilakis (2007, R20) 或 Zwicker & Fastl (2007) 定义的标准粗糙度模型。标准粗糙度模型基于振幅调制深度和调制频率的感知加权——不同调制频率（~70 Hz 最敏感）的感知粗糙度不同。
- **风险等级**：P2
- **声学/音乐理论原因**：听觉粗糙度 (auditory roughness) 是当两个频率相近的纯音（频率差在 ~20-150 Hz 之间，取决于中心频率）同时响起时感知到的"刺耳/粗糙"质感。标准模型 (Vassilakis 2007) 基于：(a) 振幅调制的深度，(b) 调制频率，(c) 中心频率（Bark 尺度依赖性）。卷积局部方差测量的是频谱的局部方差不考虑感知加权——它对高频波动和低频波动赋予相同权重，但人耳对高频 (~3-5 kHz) 的粗糙度最敏感。
- **科学假设**：使用 Vassilakis (2007) 标准粗糙度模型替换卷积局部方差后，MRS texture 组件与人类听感评分的一致性提升。
- **变量定义**：
  - `roughness_vassilakis` = 按 Vassilakis (2007) 公式计算的频谱粗糙度
  - `roughness_proxy` = 当前的卷积局部方差粗糙度代理
  - `texture_corr` = MRS texture 组件与人类专家 texture 评分的相关系数
- **实验步骤**：
  1. 实现 Vassilakis (2007) 粗糙度模型：相邻临界频带对的振幅调制深度 × 感知加权函数
  2. 在 20 首音频上同时计算两种粗糙度
  3. 对比两种粗糙度与人类粗糙度评分的相关性
- **工程实现入口**：在 `diagnosis/metrics.py` 中添加 `compute_roughness()` 函数。用新模式替换 `reality_metrics.py` 中的 `_texture_features()` 粗糙度部分。
- **预期结果**：Vassilakis 粗糙度与人类评分的相关系数高于当前代理（r > 0.70 vs 当前估计 r ≈ 0.55）。
- **验收标准**：
  - 粗糙度实现在合成测试信号（两个纯音，频率差 0-200 Hz）上产生合理的粗糙度曲线（峰值在 ~30-50 Hz 频率差处）
  - r > 0.65 与人类评分（小样本 n=5）
- **后续任务编号**：EXP-MFY-007 / ENG-MFY-007

### DEF-008：混响输入使用单声道求和丢失空间信息

- **审计发现**：`processing/operators.py:210-248` 的 `apply_reverb()` 对立体声输入先求平均 `mono = result.mean(axis=1)`，再将混响应用于单声道。这意味着输入信号中所有反相成分（side 信号）在混响处理前被消除——立体声宽度信息在混响路径中完全丢失。
- **风险等级**：P2
- **声学/音乐理论原因**：真实空间的混响保留了声源的空间分布信息——来自左侧的声音，其早期反射 (early reflections) 和混响尾音在左耳和右耳之间存在时间差 (ITD) 和电平差 (ILD)。单声道混响将这些空间线索压缩为一个点声源，导致：(a) 声场宽度缩小——混响声像塌缩到中央，(b) 空间定位感减弱，(c) 对于已有宽立体声场的 AI 音频，单声道混响会减小感知声场宽度。
- **科学假设**：改为双声道独立混响（不同延迟参数）后，MRS space 组件提升 3-5 分。
- **变量定义**：
  - `MRS_space_delta` = 双声道 vs 单声道混响的 MRS space 组件差值
  - `interchannel_cross_correlation` = 混响输出左右声道的互相关系数（IACC）——自然混响的 IACC 在低频高、高频低
- **实验步骤**：
  1. 修改 `apply_reverb()` 使左右声道独立运行混响器（不同梳状延迟参数 ±5%）
  2. 测量双声道 vs 单声道混响的 IACC 频率曲线
  3. 在 20 首立体声测试音频上对比 MRS space 组件
- **工程实现入口**：修改 `apply_reverb()` — 对左右声道分别调用 `_schroeder_reverb()`，使用略有不同的延迟长度（原始延迟 × [0.95, 1.05]）。
- **预期结果**：双声道混响的 IACC 在 8 kHz 以上 < 0.3（自然的低空间相关性）。MRS space 组件提升 3+ 分。无明显相位抵消问题（中低频的 IACC 保持 > 0.6）。
- **验收标准**：
  - 单声道输入时，双声道混响输出保持左右声道一致（IACC ≈ 1.0）
  - 立体声输入时，MRS space 组件改善
  - 无相位问题（左右声道在任何频率的相位差 < 90°）
- **后续任务编号**：EXP-MFY-008 / ENG-MFY-008

### DEF-009：压缩器使用单声道 RMS 检测

- **审计发现**：`processing/operators.py:145-203` 的 `apply_compressor()` 的侧链检测使用 `mono = result.mean(axis=1)`（左右声道平均），然后对单声道信号计算 RMS 和增益衰减。这意味着：(a) 左右声道的增益衰减总是相同（stereo-linked 模式），(b) 无法处理立体声不平衡的情况，(c) 对于宽立体声信号，左右声道可能有非常不同的动态特性，应该可以独立压缩。
- **风险等级**：P2
- **声学/音乐理论原因**：专业动态处理器通常提供 stereo-link 控制（0%-100%）。0% = 完全双单声道（左右独立检测和压缩），100% = 完全立体声链接（当前实现）。AI 生成音频的一个特性是立体声相干性低（DOC-MFY-001 §3.2.2）——左右声道可能具有独立且不可预测的动态行为。纯 stereo-linked 压缩在这种情况下可能：(a) 被右声道的峰值触发而压缩左声道（不需要压缩的声道），(b) 反之亦然。
- **科学假设**：添加可配置的 stereo-link 参数（默认 50%）后，AI 音频的处理质量（MRS dynamic 组件）提升 2-4%。
- **变量定义**：
  - `stereo_link` = 立体声链接比例 [0.0, 1.0]，0=双单声道，1=完全链接
  - `gain_reduction_L/R` = 左右声道各自的增益衰减 (dB)
  - `unnecessary_compression` = 因立体声链接导致的非必要压缩的比例
- **实验步骤**：
  1. 实现 dual-mono 压缩模式
  2. 在 10 首宽立体声 AI 音频上对比 stereo-linked vs dual-mono vs 50% linked 的处理效果
  3. 测量各模式下 MRS dynamic 和 space 组件的变化
- **工程实现入口**：修改 `apply_compressor()` — 添加 `stereo_link` 参数。在独立模式下对左右声道分别运行 RMS 检测和增益衰减计算。
- **预期结果**：立体声不平衡的音频在 dual-mono 模式下获得更好的动态处理（各声道的压缩量独立优化）。MRS dynamic 组件提升 2-4%。
- **验收标准**：
  - stereo_link=1.0 时行为与当前实现完全一致（回归测试）
  - dual-mono 模式对左右声道输入独立的压缩参数量
  - 相位一致性检查：左右声道增益曲线差异 > 3 dB 时触发警告
- **后续任务编号**：EXP-MFY-009 / ENG-MFY-009

### DEF-010：无正式主观听感测试协议

- **审计发现**：Moodify 的三评委 AI 评估（`evaluation/judges.py`）借鉴了 BS.1116 的多评估者结构，但未实施任何正式的主观听感测试协议（如 ITU-R BS.1116-5 的三刺激隐藏参考双盲法，或 ITU-R BS.1534 MUSHRA）。DOC-MFY-001 R18 明确指出此差距。
- **风险等级**：P2
- **声学/音乐理论原因**：ITU-R BS.1116-5 是评估音频系统小损伤（small impairments）的标准主观测试方法——适用于高保真音频处理系统。其核心设计：(a) 隐藏参考 (hidden reference)——受试者不知道哪个是原始信号，(b) 三刺激 (triple-stimulus)——受试者可以反复对比参考、隐藏参考和被测信号，(c) 双盲 (double-blind)——实验者和受试者都不知道信号身份。AI 评委虽能规模化，但缺少人类感知的黄金标准校准——我们不知道 AI 评委的"听感"与人类的一致性。
- **科学假设**：实施 BS.1116 风格的听感测试后，可以：(a) 量化 AI 评委与人类评委的系统性偏差，(b) 建立 AI 评委的校准曲线，(c) 为 MRS 权重提供人类感知数据驱动的优化。
- **变量定义**：
  - `SDG` = Subjective Difference Grade — 主观差异等级（BS.1116 的标准输出）
  - `AI_human_bias` = AI 评委评分 − 人类评委评分的系统性差值
  - `listener_agreement` = 不同人类评委之间的评分一致性 (ICC)
- **实验步骤**：
  1. 选择 10 首 AI 音频，每首生成 3 个不同强度的处理版本
  2. 招募 5-10 名听者（音频工程师优先）
  3. 按 BS.1116 简化协议实施：隐藏参考 + 多刺激对比 + 连续质量评分
  4. 相同的音频对也用 AI 评委评分
  5. 计算 AI-human bias 和 listener agreement
- **工程实现入口**：此任务以组织/流程为主。工程侧准备听感测试音频包和评分界面（可基于 Web 或现有 operator_console）。
- **预期结果**：AI 评委对"过度处理"的敏感度低于人类（AI 可能低估混响过度和压缩过度的主观不适感）。AI-human 偏差方向可预测，可通过校准曲线修正。
- **验收标准**：
  - 完成至少 1 轮正式听感测试（n ≥ 5）
  - AI-human 偏差量化至 95% 置信区间
  - 校准曲线文档化并可供后续 AI 评估使用
- **后续任务编号**：EXP-MFY-010

### DEF-011：HPSS margin 参数硬编码

- **审计发现**：`processing/spectral_chain.py` 的 HPSS 分解使用固定 `margin=2.0`。margin 控制谐波/打击乐分离的"硬度"——较小的 margin 倾向于将更多能量分配给打击乐分量，较大的 margin 分配给谐波分量。对于不同音源类型（钢琴独奏 vs 电子舞曲），最优 margin 不同。
- **风险等级**：P2
- **声学/音乐理论原因**：HPSS 基于频谱图在时间轴（打击乐分量：时间上稀疏但宽频）和频率轴（谐波分量：频率上稀疏但持续）上的各向异性平滑。margin 参数定义了两者的分离强度。对于钢琴音乐：大量能量在谐波分量（持续的弦振动），需要较大 margin（2.5-3.0）以避免钢琴音头的瞬态被归入打击乐分量。对于 EDM：鼓组和贝斯的分离是关键，需要较小 margin（1.5-2.0）以确保 kick drum 完整进入打击乐分量。
- **科学假设**：根据音频的频谱通量（spectral flux，瞬态强度的代理）自适应调整 HPSS margin 后，HPSS 分离的"干净度"（分量间能量泄漏 < 10%）在不同音源类型上保持一致。
- **变量定义**：
  - `spectral_flux` = 连续帧间归一化频谱差的 L2 范数
  - `hpss_leakage` = 谐波分量中的打击乐能量 / 总打击乐能量
  - `adaptive_margin` = f(spectral_flux) 的自适应 margin 值
- **实验步骤**：
  1. 在 20 首不同音源类型（钢琴、人声、EDM、管弦乐）的音频上计算平均 spectral_flux
  2. 对每首音频在不同 margin [1.0, 4.0] 下运行 HPSS
  3. 手动标注 5 首的"理想分离"作为参考
  4. 拟合 spectral_flux → optimal_margin 的映射函数
- **工程实现入口**：修改 `spectral_chain.py` — 在 HPSS 分离前计算 spectral_flux，使用查找表或回归模型选择 margin。
- **预期结果**：自适应 margin 使 hpss_leakage 在不同音源类型间的标准差减小 50%。
- **验收标准**：
  - 自适应 margin 处理的音频在盲听测试中不被判别为劣于固定 margin
  - hpss_leakage 跨音源类型的标准差 < 0.05
- **后续任务编号**：EXP-MFY-011 / ENG-MFY-011

### DEF-012：在线校准使用简化最小二乘而非贝叶斯更新

- **审计发现**：`calibration/online.py` 的在线校准使用岭回归更新 B 矩阵，形式为 `B_new = (X^T X + λI)^(-1) X^T Y`。这是一种频率学派 (frequentist) 方法——每次更新等价于从零开始用所有累积数据重新拟合。贝叶斯方法（Kalman filter 或 recursive Bayesian update）可以在每次新数据到达时增量更新，且自然地提供参数不确定性估计。
- **风险等级**：P2
- **声学/音乐理论原因**：B 矩阵的 75 个元素（5×15）在在线校准中不是同等确定的——经常活跃的参数（如 P05 低频增益）的 B 矩阵列收敛快，不常用的参数（如 P10 混响 RT60）收敛慢。岭回归将所有参数视为同等先验，无法反映这种置信度差异。贝叶斯更新维护每个矩阵元素的先验分布——当某个参数的处理数据稀疏时，其后验分布保持宽（高度不确定），系统可以识别"此推荐不可靠"。
- **科学假设**：使用 Kalman filter 替换岭回归后：(a) B 矩阵的不确定性估计使参数推荐质量提升（避免在不确定维度上激进调整），(b) 收敛速度在稀疏数据场景下更快。
- **变量定义**：
  - `B_uncertainty` = B 矩阵每个元素的后验标准差
  - `recommendation_risk` = 基于 B 矩阵不确定性的推荐风险评分
  - `convergence_rate` = B 矩阵 Frobenius 范数误差降至 10% 所需的校准次数
- **实验步骤**：
  1. 实现 Kalman filter 状态空间模型：状态 = B 矩阵向量化 (75 维)，观测 = 波场变化 (5 维)，过程噪声 = B 矩阵的预期漂移速度
  2. 在历史校准数据上对比岭回归和 Kalman filter 的收敛曲线
  3. 测量 B_uncertainty 与真实预测误差的相关性
- **工程实现入口**：在 `calibration/` 目录中新建 `kalman.py`，与现有 `online.py` 并行运行，A/B 对比后切换。
- **预期结果**：Kalman filter 在 30+ 次校准后的预测误差与岭回归持平，但收敛速度快 2-3 倍（在 10 次校准时的误差更小）。
- **验收标准**：
  - B_uncertainty 与未来真实预测误差的 Spearman 相关系数 > 0.5
  - 推荐质量（MRS 改善量）不低于当前岭回归方法
- **后续任务编号**：EXP-MFY-012 / ENG-MFY-012

### DEF-013：无情绪维度映射 (valence-arousal)

- **审计发现**：Moodify 的 8 情绪分类 (GA/SE/UD/LW/HL/DR/WL/CN) 是离散模型，但 DOC-MFY-001 R15 (Russell 1980) 和 R17 (Eerola & Vuoskoski 2011) 指出离散-维度映射可以提高情绪覆盖的精度。当前系统没有显式使用 valence-arousal 维度空间。
- **风险等级**：P2
- **声学/音乐理论原因**：Russell (1980) 的情绪环状模型 (circumplex model) 将情绪定位在效价 (valence, 愉悦-不愉悦) 和唤醒度 (arousal, 活跃-平静) 两个正交维度上。8 个离散情绪在这一空间中有确定的位置（例如 GA ≈ 高效价+高唤醒，WL ≈ 低效价+低唤醒）。维度模型的优势：(a) 可以处理离散类别之间的边界情绪（如"略带忧伤的温柔"）, (b) 工艺参数的插值可以在连续空间中平滑过渡, (c) 为新情绪原型提供坐标系。
- **科学假设**：在开源情绪标注数据集上标定 8 情绪的 (valence, arousal) 坐标后，可以：(a) 实现任意 (VA) 坐标→工艺参数的插值推荐，(b) 处理"混合情绪"的工艺请求。
- **变量定义**：
  - `VA_coords` = 每个情绪在 [valence, arousal] 二维空间中的坐标 [-1, 1] × [-1, 1]
  - `interpolation_weight` = 给定 (V, A) 坐标到各情绪原型的距离加权系数
  - `emotion_granularity` = 可区分的情绪状态数（维度模型理论上无限，离散模型 = 8）
- **实验步骤**：
  1. 收集 8 情绪的 valence-arousal 标注（基于 MUSIC 数据集或自标注）
  2. 将 8 情绪定位到 VA 空间
  3. 实现 VA 坐标 → 工艺参数插值
  4. 验证中间情绪（如 0.5 GA + 0.5 LW）的工艺参数合理性
- **工程实现入口**：在 `knowledge/emotion_targets.py` 中添加 VA 坐标映射。新建 `knowledge/emotion_interpolation.py`。
- **预期结果**：VA 空间中相邻情绪的工艺参数过渡平滑（相邻情绪的参数差异 < 10% per VA unit）。中间情绪的 MRS 改善量不低于最近离散情绪。
- **验收标准**：
  - 8 情绪在 VA 空间的坐标经 3 人标注一致性 ICC > 0.7
  - 参数插值在两个相邻情绪的中点产生的工艺卡不违反任何禁忌症
- **后续任务编号**：EXP-MFY-013 / ENG-MFY-013

---

## 缺陷汇总

| 编号 | 问题 | 风险 | 位置 | 对标标准 |
|------|------|------|------|----------|
| DEF-001 | FFT sigmoid/Gaussian EQ 替代 RBJ biquad | P0 | operators.py:116-138 | R10 (RBJ Audio EQ Cookbook) |
| DEF-002 | Schroeder 混响缺少全通滤波器级 | P0 | operators.py:262-275 | R09 (Schroeder 1962) |
| DEF-003 | 无 PEAQ 感知质量评估 | P1 | reality_metrics.py | R08 (ITU-R BS.1387) |
| DEF-004 | 无频率掩蔽模型 | P1 | 全系统 | R05 (Zwicker & Fastl 2007) |
| DEF-005 | 缺少 mel/bark/chroma/F0 特征 | P1 | reality_metrics.py, metrics.py | R13 (Tzanetakis & Cook) |
| DEF-006 | 频段定义跨模块不一致 | P2 | bands.py vs metrics.py | 自研标准 |
| DEF-007 | 频谱粗糙度使用非标准代理 | P2 | reality_metrics.py:_texture_features() | R20 (Vassilakis 2007) |
| DEF-008 | 混响输入丢失立体声空间信息 | P2 | operators.py:210-248 | R09 (Schroeder 1962) |
| DEF-009 | 压缩器缺少 stereo-link 控制 | P2 | operators.py:145-203 | 工程最佳实践 |
| DEF-010 | 无正式主观听感测试协议 | P2 | 组织/流程 | R18 (ITU-R BS.1116) |
| DEF-011 | HPSS margin 硬编码 | P2 | spectral_chain.py | R12 (Ono et al. 2008) |
| DEF-012 | 校准使用最小二乘而非贝叶斯更新 | P2 | calibration/online.py | 统计学习理论 |
| DEF-013 | 无情绪维度映射 (valence-arousal) | P2 | emotion_targets.py | R15, R17 (Russell, Eerola) |

---

## 验收检查

- [x] 每个缺陷有唯一编号 (DEF-001 ~ DEF-013)
- [x] 每个缺陷标注审计发现、文件路径
- [x] 每个缺陷标注风险等级 (P0/P1/P2)
- [x] 每个缺陷有声学/音乐理论原因
- [x] 每个缺陷有科学假设和变量定义
- [x] 每个缺陷有实验步骤和工程实现入口
- [x] 每个缺陷有预期结果和验收标准
- [x] 每个缺陷有后续 EXP-MFY / ENG-MFY 任务编号
- [x] P0 问题 2 个、P1 问题 3 个、P2 问题 8 个
- [x] 每个缺陷对标参考标准/文献
