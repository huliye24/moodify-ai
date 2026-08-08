# T7｜参考文献

> 按学科领域分组，标注与 Moodify 的关联和使用位置。

---

## 7.1 战略管理理论

| 编号 | 文献 | 核心论点 | Moodify 关联 |
|------|------|----------|-------------|
| R01 | Barney, J. (1991). Firm Resources and Sustained Competitive Advantage. *Journal of Management*, 17(1), 99-120. | 企业的持续竞争优势来自其拥有有价值、稀有、难以模仿和不可替代 (VRIN) 的资源 | 非代码化资产的 VRIN 分类框架——理论、实验数据、工艺知识满足全部四个条件 |
| R02 | Teece, D. J., Pisano, G., & Shuen, A. (1997). Dynamic Capabilities and Strategic Management. *Strategic Management Journal*, 18(7), 509-533. | 在快速变化的环境中，企业整合、构建和重新配置内外部能力的能力是关键 | Moodify 的实验飞轮就是动态能力的工程实现——持续感知（诊断）、抓住（处理）、转换（校准） |
| R03 | Cohen, W. M., & Levinthal, D. A. (1990). Absorptive Capacity: A New Perspective on Learning and Innovation. *Administrative Science Quarterly*, 35(1), 128-152. | 组织识别、吸收和利用外部知识的能力取决于其先验知识基础 | L4 元知识层——Moodify 的实验方法论本身就是吸收能力的基础设施 |
| R04 | Nonaka, I. (1994). A Dynamic Theory of Organizational Knowledge Creation. *Organization Science*, 5(1), 14-37. | 知识创造通过 SECI 模型（社会化→外化→组合→内化）在不同形态间转换 | Moodify 知识 L2→L1（隐性→可编码）的工艺链编码过程，以及文档→AI Worker 的知识迁移 |

---

## 7.2 声学与心理声学

| 编号 | 文献 | 核心论点 | Moodify 关联 |
|------|------|----------|-------------|
| R05 | Zwicker, E., & Fastl, H. (2007). *Psychoacoustics: Facts and Models* (3rd ed.). Springer. | 心理声学的标准参考——临界频带、掩蔽效应、响度感知、粗糙度模型 | 当前 MRS 未实现频率掩蔽模型——应作为 MRS v0.4 的理论基础 |
| R06 | ITU-R BS.1770-5 (2023). Algorithms to Measure Audio Programme Loudness and True-Peak Audio Level. | 广播响度测量的国际标准——集成响度 (LUFS)、真峰值、门控测量 | pyloudnorm 集成实现于 processing/pedalboard_chain.py 和 diagnosis/engine.py |
| R07 | EBU Tech 3342 (2016). Loudness Range: A Measure to Supplement Loudness Normalisation. | LRA 作为响度动态范围的补充指标 | 实现于 diagnosis/engine.py:_compute_lra()——3 秒块 + P10/P95 百分位法 |
| R08 | ITU-R BS.1387-2 (2023). Method for Objective Measurements of Perceived Audio Quality (PEAQ). | 感知音频质量客观测量的国际标准——使用心理声学模型比较参考和测试信号 | Moodify 尚未实现 PEAQ 级感知模型——MRS 使用马氏距离而非感知模型 |
| R09 | Schroeder, M. R. (1962). Natural Sounding Artificial Reverberation. *Journal of the Audio Engineering Society*, 10(3), 219-223. | 原始梳状滤波器 + 全通滤波器的人工混响算法 | 实现于 processing/operators.py:_schroeder_reverb()——但缺少全通级（已知缺陷，待修复） |
| R10 | Robert Bristow-Johnson. Audio EQ Cookbook. https://webaudio.github.io/web-audio-api/#filters | 行业标准的双二阶滤波器设计公式——低架、高架、峰值、带通、陷波等 | 当前 FFT EQ 使用 sigmoid/Gaussian 逼近——非标准滤波器形状。craft_processes.py 有正确的双二阶实现，但未用于主 EQ 路径 |

---

## 7.3 音乐信息检索 (MIR) 与音频特征

| 编号 | 文献 | 核心论点 | Moodify 关联 |
|------|------|----------|-------------|
| R11 | McFee, B., Raffel, C., Liang, D., et al. (2015). librosa: Audio and Music Signal Analysis in Python. *SciPy 2015*. | Python 音频分析的标准库——STFT、HPSS、onset detection、chroma、MFCC | HPSS 分解使用 librosa.decompose.hpss()；onset detection 使用 librosa.onset.onset_detect() |
| R12 | Ono, N., Miyamoto, K., Le Roux, J., Kameoka, H., & Sagayama, S. (2008). Separation of a Monophonic Audio Signal into Harmonic and Percussive Components by the Non-Negative Matrix Factorization. *ISMIR 2008*. | 原始的 HPSS 算法——利用频谱图的各向异性平滑分离谐波和打击乐成分 | SpectralDSPChain 使用 HPSS 作为 Demucs 的替代方案 (margin=2.0) |
| R13 | Tzanetakis, G., & Cook, P. (2002). Musical Genre Classification of Audio Signals. *IEEE Transactions on Speech and Audio Processing*, 10(5), 293-302. | 定义并标准化了频谱质心、滚降、通量、过零率等 MIR 特征 | 频谱质心和滚降在 reality_metrics.py 中实现——但未使用 mfcc/chroma 特征 |
| R14 | McAdams, S., Winsberg, S., Donnadieu, S., De Soete, G., & Krimphoff, J. (1995). Perceptual Scaling of Simplified Musical Sounds. *Psychological Research*, 58, 177-197. | 音色多维感知——频谱质心、起音时间、频谱通量是音色感知的核心维度 | MRS 特征选择（spectrum/dynamic/transient/texture/temporal 组）部分与此框架对齐 |

---

## 7.4 音乐情绪与心理模型

| 编号 | 文献 | 核心论点 | Moodify 关联 |
|------|------|----------|-------------|
| R15 | Russell, J. A. (1980). A Circumplex Model of Affect. *Journal of Personality and Social Psychology*, 39(6), 1161-1178. | 情绪的环状模型——两个正交维度（效价-唤醒度）可以描述所有情绪状态 | 8 情绪分类法（GA/SE/UD/LW/HL/DR/WL/CN）可以在效价-唤醒度空间中标定——但当前未显式使用此模型 |
| R16 | Juslin, P. N., & Laukka, P. (2004). Expression, Perception, and Induction of Musical Emotions. *Journal of New Music Research*, 33(3), 217-238. | 音乐情绪的五个机制：脑干反射、评价性条件反射、情绪感染、视觉意象、情景记忆 | 情绪目标的频谱/动态/空间约束具有声学基础——但未涵盖文化/情境因素 |
| R17 | Eerola, T., & Vuoskoski, J. K. (2011). A Comparison of the Discrete and Dimensional Models of Emotion in Music. *Psychology of Music*, 39(1), 18-49. | 离散情绪模型（基本情绪）与连续维度模型（效价-唤醒度）在音乐情感研究中的比较 | Moodify 的 8 情绪原型属于离散模型——未来可添加维度映射以提高覆盖精度 |

---

## 7.5 音频质量评估

| 编号 | 文献 | 核心论点 | Moodify 关联 |
|------|------|----------|-------------|
| R18 | ITU-R BS.1116-5 (2023). Methods for the Subjective Assessment of Small Impairments in Audio Systems. | 小损伤的主观评估标准——三刺激隐藏参考双盲法 | Moodify 的三评委 AI 系统借鉴了多评委结构——但未实施正式的 BS.1116 主观测试协议 |
| R19 | Croghan, N. B. H., Arehart, K. H., & Kates, J. M. (2013). Quality and Loudness Judgments for Music Subjected to Compression. *Journal of the Audio Engineering Society*, 61(11), 892-905. | 压缩对音乐质量和响度感知的影响——过度压缩降低自然度评分 | 动态维度（D1-D4）部分基于此——但 MRS 的 dynamic_range 和 crest_factor 是简化代理 |
| R20 | Vassilakis, P. N. (2007). SRA: A Web-Based Research Tool for Spectral and Roughness Analysis of Sound Signals. *SMC 2007*. | 频谱粗糙度的计算模型——基于振幅调制深度和频率 | reality_metrics.py 的 _texture_features() 使用卷积局部方差作为粗糙度的简化代理——非标准粗糙度模型 |

---

## 7.6 工程与系统文献

| 编号 | 文献 | 核心论点 | Moodify 关联 |
|------|------|----------|-------------|
| R21 | Spotify. pedalboard: A Python Library for Adding Effects to Audio. https://github.com/spotify/pedalboard | 生产级 Python 音频效果库——基于 JUCE 的 C++ 实现 | PedalboardDSPChain 和 SpectralDSPChain 的核心依赖 |
| R22 | Steinmetz, C. J., & Reiss, J. D. (2020). pyloudnorm: A Python Package for Loudness Normalization. *AES Convention 2020*. | ITU-R BS.1770 响度测量的 Python 实现 | 集成于 diagnosis/engine.py 的 LUFS 和 LRA 测量 |

---

## 7.7 文献与 Moodify 模块的交叉引用

| 模块 | 相关文献 |
|------|---------|
| processing/operators.py (EQ, Comp, Reverb) | R09, R10, R19, R21 |
| processing/pedalboard_chain.py | R06, R21, R22 |
| processing/spectral_chain.py (HPSS) | R11, R12 |
| diagnosis/engine.py (18 参数引擎) | R06, R07, R13, R14 |
| reality_metrics.py (MRS) | R05, R08, R13, R14, R20 |
| knowledge/emotion_targets.py | R15, R16, R17 |
| conservation.py (PHYS-007) | R06 |
| fingerprint.py (PHYS-003) | R09, R19 |

---

## 7.8 文献缺口：需要补充阅读的方向

| 方向 | 原因 | 推荐起点 |
|------|------|---------|
| 音乐声学中的掩蔽效应模型 | MRS 需要感知频率加权 | Zwicker & Fastl (2007) 第 7-8 章 |
| 音高感知 (F0 estimation) | 系统缺少音高检测和调性分析 | de Cheveigné & Kawahara (2002). YIN, a Fundamental Frequency Estimator |
| 音乐相似度的客观度量 | MRS 参考分布的有效性需理论支撑 | Pampalk et al. (2002). Content-Based Organization and Visualization of Music Archives |
| 神经网络源分离 (Demucs, Spleeter) | 评估 HPSS vs 深度学习的权衡是否仍然成立 | Défossez et al. (2019). Music Source Separation in the Waveform Domain |
| 主观听感测试方法 (MUSHRA) | 为未来的人类听感验证做准备 | ITU-R BS.1534. Method for the Subjective Assessment of Intermediate Quality Level of Audio Systems |

---

## 验收检查

- [x] 参考文献按学科分组（战略、声学、MIR、情绪、质量、工程）
- [x] 每篇文献有核心论点和 Moodify 关联
- [x] 文献与模块的交叉引用表完整
- [x] 文献缺口清晰——推荐了 5 个需要补充的阅读方向
- [x] 覆盖 DOC-MFY-001 指定的全部方向（Barney, Teece, Nonaka, BS.1770, BS.1387, EBU 3342, RBJ, Schroeder, Zwicker, McFee）
- [x] 总计 22 篇核心文献 + 5 篇推荐补充
