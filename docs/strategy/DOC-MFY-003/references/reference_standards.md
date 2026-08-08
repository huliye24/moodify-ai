# DOC-MFY-003｜参考标准与说明

> 本文件为 DOC-MFY-003 v0.4 声学合规升级项目章程提供参考文献索引。
> 继承 DOC-MFY-001 (R01-R22) 和 DOC-MFY-002 (NEW-01 ~ NEW-05) 的文献体系。
> 新增 v0.4 特有的 AEP 执行参考。

---

## 1. 结构总览

本参考体系分四层：

```text
L0 — 行业标准 (ITU / ISO / EBU / AES)
L1 — 核心文献 (声学 / 心理声学 / 信号处理)
L2 — 算法参考 (YIN / RBJ / HPSS / Chroma / Schroeder)
L3 — 工程依赖 (librosa / pedalboard / pyloudnorm / scipy)
```

---

## 2. L0 — 行业标准

| 编号 | 标准 | 年份 | 用途 (v0.4) | 关联 AEP |
|------|------|------|------------|----------|
| R06 | ITU-R BS.1770-5 — Algorithms to Measure Audio Programme Loudness | 2023 | LUFS 实现审计基准；响度归一化验证 | ACU-005 |
| R07 | EBU Tech 3342 — Loudness Range (LRA) | 2016 | LRA 测量补充 | ACU-005 |
| R08 | ITU-R BS.1387-2 — PEAQ | 2023 | 感知音频质量客观测量——v0.4 仅做前置（掩蔽模型），完整 PEAQ 留给 v0.5 | ACU-007 |
| R18 | ITU-R BS.1116-5 — Subjective Assessment of Small Impairments | 2023 | 主观听感测试标准协议——v0.4 的非正式听感检查参考 | ALL |
| NEW-01 | ISO 532B:1975 — Zwicker Loudness | 1975 | 感知响度模型——优于 LUFS 对非广播内容的适用性 | ACU-006 |
| NEW-04 | ITU-R BS.1771-1 — True-Peak Indicating Meters | 2012 | 真峰值测量标准——v0.4 Limiter 升级的核心参考 | ACU-005 |

---

## 3. L1 — 核心文献

| 编号 | 文献 | 年份 | 用途 (v0.4) | 关联 AEP |
|------|------|------|------------|----------|
| R05 | Zwicker, E. & Fastl, H. *Psychoacoustics: Facts and Models* (3rd ed.) | 2007 | 临界频带、掩蔽效应、响度感知、粗糙度模型。第 7-8 章是 ACU-007 的核心理论来源 | ACU-006, ACU-007 |
| R09 | Schroeder, M. R. "Natural Sounding Artificial Reverberation" | 1962 | 人工混响原始设计——全通滤波器级 + 梳状滤波器级的必要性和参数选择 | ACU-001 |
| R10 | Bristow-Johnson, R. "Audio EQ Cookbook" | — | 双二阶滤波器设计规范——RBJ biquad 的系数计算公式和 Q 值定义 | ACU-002 |
| R12 | Ono, N. et al. "Harmonic/Percussive Sound Separation" | 2008 | HPSS 原始算法——margin 参数和残差分量的处理 | ACU-003 |
| R13 | Tzanetakis, G. & Cook, P. "Musical Genre Classification of Audio Signals" | 2002 | MIR 特征标准定义——频谱质心、频谱滚降、频谱通量、过零率、MFCC | ACU-006/008/009 |
| R14 | McAdams, S. et al. "Perceptual Scaling of Simplified Musical Sounds" | 1995 | 音色多维感知——频谱质心/起音时间/频谱通量作为核心音色维度 | ACU-006 |
| R20 | Vassilakis, P. N. "SRA: Spectral and Roughness Analysis" | 2007 | 频谱粗糙度标准计算模型——v0.5 替换当前粗糙度代理 | POOL-06 (v0.6) |

---

## 4. L2 — 算法参考

| 编号 | 文献/算法 | 用途 (v0.4) | 关联 AEP | 获取状态 |
|------|----------|------------|----------|----------|
| NEW-02 | de Cheveigné, A. & Kawahara, H. "YIN, a Fundamental Frequency Estimator" (JASA, 2002) | F0 检测标准算法——ACU-008 的核心参考 | ACU-008 | 需获取全文 |
| — | Krumhansl-Schmuckler Key-Finding Algorithm | 调性检测——chroma 向量与调性模板相关 | ACU-009 | 公开算法 |
| — | Glasberg & Moore (1990) ERB Scale | `ERB(f) = 24.7 * (4.37 * f/1000 + 1)` | ACU-006 | 公开公式 |
| — | Zwicker (1961) Bark Scale | `Bark(f) = 13 * arctan(0.00076 * f) + 3.5 * arctan((f/7500)^2)` | ACU-006 | 公开公式 |
| — | Stevens (1937) Mel Scale | `Mel(f) = 2595 * log10(1 + f/700)` | ACU-006 | 公开公式 |
| — | Schroeder All-Pass | `y[n] = -g*x[n] + x[n-K] + g*y[n-K]` | ACU-001 | Schroeder (1962) |
| — | RBJ Biquad Coefficients | Audio EQ Cookbook 标准公式 | ACU-002 | R10 |

---

## 5. L3 — 工程依赖

| 编号 | 工具 | 版本要求 | 用途 (v0.4) | 关联 AEP | 许可 |
|------|------|----------|------------|----------|------|
| R21 | Spotify pedalboard | ≥ 0.8 | RBJ biquad EQ (JUCE 后端)、混响、压缩器、限幅器——ACU-002 的推荐方案 A | ACU-001/002/005 | Apache 2.0 |
| R22 | pyloudnorm (Steinmetz & Reiss) | ≥ 0.1 | ITU-R BS.1770 LUFS——ACU-005 响度归一化 | ACU-005 | MIT |
| R11 | librosa | ≥ 0.10 | MIR 特征提取、HPSS 分解、YIN F0、chroma——ACU-003/006/008/009 的参考实现 | ACU-003/006/008/009 | ISC |
| — | numpy | ≥ 1.24 | 数值计算、FFT、统计 | ALL | BSD |
| — | scipy | ≥ 1.11 | 信号处理、滤波器设计、统计检验 | ALL | BSD |
| — | matplotlib | ≥ 3.7 | 图表生成、频谱可视化、诊断报告 | ALL | PSF |
| — | pytest | ≥ 8.0 | 测试框架——MHP 完成标准四道门之一 | ALL | MIT |
| — | ruff | ≥ 0.3 | Linter——MHP 完成标准四道门之一 | ALL | MIT |

---

## 6. v0.4 特有的新增参考资料

| 编号 | 来源 | 内容 | 用途 |
|------|------|------|------|
| ACU-REF-01 | `processing/operators.py:262-275` | 当前 `_schroeder_reverb()` 实现 | ACU-001 修复的基线 |
| ACU-REF-02 | `processing/operators.py:116-138` | 当前 FFT sigmoid/Gaussian EQ 实现 | ACU-002 替换的基线 |
| ACU-REF-03 | `processing/spectral_chain.py` | 当前 HPSS 处理流程 | ACU-003 修复的基线 |
| ACU-REF-04 | `craft_processes.py` | 已有 RBJ biquad 参考实现 | ACU-002 方案 B 的代码来源 |
| ACU-REF-05 | `bands.py` | 当前 6 频段定义 | ACU-004 扩展的基线 |
| ACU-REF-06 | `diagnosis/metrics.py` | 当前频谱分析器和频段能量计算 | ACU-004/006 的修改目标 |
| ACU-REF-07 | `reality_metrics.py` | 当前 MRS 参考统计计算 | ACU-010 的修改目标 |

---

## 7. 文献与 AEP 交叉索引

```text
AEP-ACU-001 (Schroeder Reverb):  R09, R21
AEP-ACU-002 (RBJ Biquad EQ):     R10, R21, ACU-REF-02, ACU-REF-04
AEP-ACU-003 (HPSS 残差守恒):      R12, R11, ACU-REF-03
AEP-ACU-004 (7 频段):            R05, ACU-REF-05, ACU-REF-06
AEP-ACU-005 (True Peak Limiter):  R06, R07, NEW-04, R21, R22
AEP-ACU-006 (感知尺度):          R05, R13, R14, NEW-01
AEP-ACU-007 (掩蔽初版):          R05, R08
AEP-ACU-008 (F0/Pitch):          NEW-02, R11
AEP-ACU-009 (Chroma/Key):        NEW-02, R11
AEP-ACU-010 (MRS 鲁棒化):        ACU-REF-07
```

---

## 8. 获取优先级 (v0.4)

| 优先级 | 文献 | 理由 |
|--------|------|------|
| **P0** | R09 (Schroeder 1962) | ACU-001 的核心算法参考 |
| **P0** | R10 (RBJ Audio EQ Cookbook) | ACU-002 的滤波器设计参考 |
| **P1** | R05 (Zwicker & Fastl 2007) §7-8 | ACU-007 的掩蔽模型理论基础 |
| **P1** | NEW-02 (YIN F0 estimator) | ACU-008 的算法参考 |
| **P1** | NEW-04 (ITU-R BS.1771-1) | ACU-005 的真峰值标准 |
| **P2** | R08 (ITU-R BS.1387 PEAQ) | ACU-007 的上游标准——v0.4 仅做前置 |
| **P2** | R20 (Vassilakis 2007) | v0.6 粗糙度模型替换 |

---

## 验收检查

- [x] L0 行业标准 6 项
- [x] L1 核心文献 7 项
- [x] L2 算法参考 7 项
- [x] L3 工程依赖 8 项
- [x] v0.4 特有代码参考 7 项
- [x] 文献-AEP 交叉索引表
- [x] v0.4 获取优先级表
