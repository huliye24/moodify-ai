# T9｜参考标准与文献

> 整理 DOC-MFY-001 的 22 篇核心文献 + 5 篇推荐补充中与本审计直接相关的条目，以及 DOC-MFY-002 审计过程中引用的额外标准。
> 每项标注：用途（本审计中的具体使用位置）、获取状态。

---

## 9.1 核心声学与心理声学标准

| 编号 | 标准/文献 | 年份 | 用途（本审计） | 使用位置 | 状态 |
|------|----------|------|--------------|----------|------|
| R05 | Zwicker, E. & Fastl, H. *Psychoacoustics: Facts and Models* (3rd ed.) | 2007 | 临界频带、掩蔽效应、响度感知、粗糙度模型的理论基准 | DEF-003/004/007 的科学依据；L2 感知层理论框架 | 需获取全文 |
| R06 | ITU-R BS.1770-5 — Algorithms to Measure Audio Programme Loudness | 2023 | LUFS 实现审计基准 | S-001 合规验证；DEF-001 涉及的真峰值需求 | 公开标准，已获取 |
| R07 | EBU Tech 3342 — Loudness Range: A Measure to Supplement Loudness Normalisation | 2016 | LRA 实现审计基准 | S-002 合规验证 | 公开标准，已获取 |
| R08 | ITU-R BS.1387-2 — Method for Objective Measurements of Perceived Audio Quality (PEAQ) | 2023 | PEAQ 感知质量评估标准 | DEF-003 的核心参考；ENG-MFY-003 实现规范 | 公开标准，需获取 |
| R09 | Schroeder, M. R. "Natural Sounding Artificial Reverberation" | 1962 | 人工混响算法的原始设计 | DEF-002 的全通滤波器要求；DEF-008 的双声道要求 | 需获取全文 |
| R10 | Robert Bristow-Johnson. Audio EQ Cookbook | — | 双二阶滤波器设计的行业标准 | DEF-001 的 RBJ biquad 参考实现 | 公开资源 (Web Audio API spec) |
| R18 | ITU-R BS.1116-5 — Methods for the Subjective Assessment of Small Impairments | 2023 | 主观听感测试的标准协议 | DEF-010 的听感测试设计 | 公开标准，需获取 |
| R20 | Vassilakis, P. N. "SRA: A Web-Based Research Tool for Spectral and Roughness Analysis" | 2007 | 频谱粗糙度的标准计算模型 | DEF-007 的粗糙度模型替换基准 | 需获取全文 |

---

## 9.2 音乐信息检索 (MIR) 标准

| 编号 | 标准/文献 | 年份 | 用途（本审计） | 使用位置 | 状态 |
|------|----------|------|--------------|----------|------|
| R11 | McFee, B. et al. "librosa: Audio and Music Signal Analysis in Python" | 2015 | MIR 特征提取的标准 Python 库 | DEF-005 的特征提取参考实现 | 开源 (MIT)，已集成 |
| R12 | Ono, N. et al. "Separation of a Monophonic Audio Signal into Harmonic and Percussive Components" | 2008 | HPSS 原始算法 | DEF-011 的 HPSS margin 优化参考 | 需获取全文 |
| R13 | Tzanetakis, G. & Cook, P. "Musical Genre Classification of Audio Signals" | 2002 | MIR 特征（频谱质心、滚降、通量、过零率、MFCC）的标准定义 | S-005 的 MRS 特征理论基础；DEF-005 的特征选择参考 | 已获取 |
| R14 | McAdams, S. et al. "Perceptual Scaling of Simplified Musical Sounds" | 1995 | 音色多维感知 — 频谱质心/起音时间/频谱通量作为核心维度 | S-005 的 MRS 特征组设计依据 | 需获取全文 |

---

## 9.3 情绪与感知模型

| 编号 | 标准/文献 | 年份 | 用途（本审计） | 使用位置 | 状态 |
|------|----------|------|--------------|----------|------|
| R15 | Russell, J. A. "A Circumplex Model of Affect" | 1980 | 情绪的效价-唤醒度二维模型 | DEF-013 的情绪维度映射理论基础 | 需获取全文 |
| R17 | Eerola, T. & Vuoskoski, J. K. "A Comparison of the Discrete and Dimensional Models of Emotion in Music" | 2011 | 离散 vs 连续情绪模型在音乐中的比较 | DEF-013 的情绪模型选择依据 | 需获取全文 |

---

## 9.4 工程依赖与工具

| 编号 | 工具 | 版本 | 用途（本审计） | 使用位置 | 许可 |
|------|------|------|--------------|----------|------|
| R21 | Spotify pedalboard | — | 生产级 Python 音频效果库 (基于 JUCE C++) | S-010 (RBJ biquad 合规)；主处理路径 | Apache 2.0 |
| R22 | pyloudnorm (Steinmetz & Reiss) | — | ITU-R BS.1770 响度测量的 Python 实现 | S-001 (LUFS 合规)；diagnosis/engine.py | MIT |
| — | librosa | — | MIR 特征提取、HPSS、onset detection | S-008 (HPSS)；DEF-005 (特征提取) | ISC |
| — | numpy / scipy | — | FFT、信号处理、统计计算 | 全系统 | BSD |

---

## 9.5 DOC-MFY-002 审计中引用的额外标准

以下标准未出现在 DOC-MFY-001 的参考文献中，但在本次审计中被引用：

| 编号 | 标准/文献 | 用途 |
|------|----------|------|
| NEW-01 | ISO 532B:1975 — Acoustics — Method for Calculating Loudness Level (Zwicker method) | L2 感知层的响度感知模型参考——当前仅使用 LUFS（广播标准），应补充 Zwicker 响度模型（感知标准） |
| NEW-02 | de Cheveigné, A. & Kawahara, H. (2002). "YIN, a Fundamental Frequency Estimator for Speech and Music." *JASA*, 111(4), 1917-1930. | DEF-005 的 F0 检测算法参考——YIN 是音高检测的标准算法 |
| NEW-03 | Défossez, A. et al. (2019). "Music Source Separation in the Waveform Domain." (Demucs) | GPU 实验队列第 6 项——评估 Demucs vs HPSS 的深度学习对比 |
| NEW-04 | ITU-R BS.1771-1 — Requirements for Loudness and True-Peak Indicating Meters | DEF-001 涉及的真峰值 (True Peak) 测量标准——当前限幅器使用采样峰值而非真峰值 |
| NEW-05 | Ando, Y. (1985). *Concert Hall Acoustics*. Springer. — 耳间互相关系数 IACC 与感知声源宽度 ASW | DEF-008 的立体声空间感知理论基础 |

---

## 9.6 文献获取优先级

| 优先级 | 文献 | 理由 |
|--------|------|------|
| **P0** | R09 (Schroeder 1962) | DEF-002 修复的原始算法参考——需要确认全通滤波器的精确参数 |
| **P0** | R10 (RBJ Audio EQ Cookbook) | DEF-001 修复的滤波器设计参考——已公开但需要储备为内部设计文档 |
| **P1** | R08 (ITU-R BS.1387 PEAQ) | DEF-003 的实现规范——PEAQ 是复杂的标准，不读原文无法正确实现 |
| **P1** | R05 (Zwicker & Fastl 2007) | DEF-004 的掩蔽模型理论基础——第 7-8 章是关键 |
| **P1** | NEW-02 (YIN F0 estimator) | DEF-005 的 F0 检测算法——需要阅读以正确处理 AI 音频的边缘情况 |
| **P2** | R20 (Vassilakis 2007) | DEF-007 的粗糙度模型——实现复杂度中等 |
| **P2** | R15, R17 (情绪模型) | DEF-013 的理论基础——实现优先级低 |
| **P2** | NEW-01 (ISO 532B) | L2 响度感知模型——可用 Zwicker & Fastl (2007) 替代 |

---

## 验收检查

- [x] 声学/心理声学标准 8 项
- [x] MIR 标准 4 项
- [x] 情绪/感知模型 2 项
- [x] 工程依赖与工具 4 项
- [x] 新增补充标准 5 项 (NEW-01 ~ NEW-05)
- [x] 每项标注用途和使用位置
- [x] 文献获取优先级表 (P0/P1/P2)
- [x] 与 DOC-MFY-001 参考文献的交叉引用 (R05-R22)
