# Phase I WSE / MSE / PPE 映射（MFY-PHASE1-FREEZE-001 Step F）

**日期**: 2026-08-08
**来源**: `artifacts/phase1_freeze/repository_inventory.md`（Step A 审计）

## 三域定义

| 域 | 回答的问题 | 覆盖范围 |
|----|-----------|---------|
| **WSE** | 声音里发生了什么？ | 波形、频谱、LUFS、动态、相位、立体声、残差、瞬态、截止/伪影测量 |
| **MSE** | 音乐结构是什么？ | 速度、段落、乐句、歌词对齐、MIDI、音乐结构 |
| **PPE** | 这份分析是如何可靠产出的？ | 运行身份、流水线、门、证据、可复现、恢复、成本/过程元数据 |

## WSE 映射（moodify-core-package/src/moodify/）

| 能力 | 模块 | 关键符号 | 状态 |
|------|------|---------|------|
| 波形/频谱 | `auditory/spectrogram.py` | 线性/对数频谱图生成 | PHASE1_CORE |
| 波形/时间线 | `auditory/timeline.py`、`auditory/service.py` | timeline_metrics.jsonl | PHASE1_CORE |
| LUFS/动态 | `auditory/metrics.py` | integrated_lufs / loudness_range_lu / true_peak_db | PHASE1_CORE |
| 相位/立体声 | `auditory/stereo.py`、`auditory/metrics.py` | phase_risk_ratio / negative_correlation_ratio | PHASE1_CORE |
| 残差 | `auditory/service.py` | analysis_data.npz（残差谱） | PHASE1_CORE |
| 瞬态 | `auditory/metrics.py` | crest_factor_db / 瞬态测量 | PHASE1_CORE |
| 高频截止 | `auditory/metrics.py` | estimated_high_frequency_cutoff_hz | PHASE1_CORE |
| 特征提取 | `features/f0.py` `features/chroma.py` `features/perceptual.py` | analyze_f0 / detect_key / PerceptualSpectrumExtractor | PHASE1_CORE |
| 心理声学 | `perception/masking.py` | MaskingConfig / PsychoacousticFeatures | PHASE1_EXPERIMENTAL |
| 音频 IO/指纹 | `audio_io.py` `fingerprint.py` | SHA-256 源指纹 | PHASE1_CORE |
| 外部传感器 | `adapters/auditory/ocean_listen/` | ocean_listen 映射（enabled:false） | PHASE1_EXPERIMENTAL |
| 物理实验 | `physics/` | 核心假设可复现实验 | PHASE1_EXPERIMENTAL |

## MSE 映射

| 能力 | 模块 | 关键符号 | 状态 |
|------|------|---------|------|
| 歌词对齐 | `lyric_align/` | 音频为时间权威 + whisperx 后端 | PHASE1_CORE |
| 音频转 MIDI | `transcription_pipeline/` | Stem-aware 流水线 v0.2 | PHASE1_CORE |
| 乐谱模型 | `score_engine/` | MoodifyScore + MusicXML 适配 | PHASE1_SUPPORT |
| 段落/结构 | `score_engine/` + `features/` | 结构边界（部分可用） | PHASE1_SUPPORT |

## PPE 映射

| 能力 | 模块 | 关键符号 | 状态 |
|------|------|---------|------|
| 运行身份/流水线 | `capability_registry/execution/` | 批准信封（SHA-256 锁定输入、签名） | PHASE1_CORE |
| 验证门 | `capability_registry/validation/` | 历史驱动的验证规则 | PHASE1_CORE |
| 证据清单 | `auditory/manifests.py` | scan/comparison manifest + hash 校验 | PHASE1_CORE |
| 证据包 | `app/evidence.py` + `app/production_control.py` | EvidenceBundle / REQUIRED_EVIDENCE_FILES（11 个）+ evidence_manifest.json | PHASE1_CORE |
| 可复现 | `conservation.py` `icc.py` `uncertainty.py` `mrs_robust.py` | 守恒审计 / 不确定性 / MRS 鲁棒 | PHASE1_CORE |
| 判断规则版本 | `auditory/judgment.py` | JUDGMENT_RULES_VERSION / UNIVERSAL_THRESHOLDS | PHASE1_CORE |
| 评测策略 | `evaluation/pairwise/` + `configs/pairwise_policy_v1.yaml` | DecisionPolicy / 证据覆盖 | PHASE1_CORE |
| 案例脊柱 | `app/production_control.py` | ProductionCase 16 状态 + 审批链 | PHASE1_CORE |
| 过程元数据 | `app/production_control.py` package 阶段 | evidence_manifest 全链 hash | PHASE1_CORE |
| 学习回馈 | `capability_registry/knowledge/` | 案例→版本化策略 | PHASE1_CORE |

## 映射检查表

- [x] 每个 Phase I 能力域都有项目原生实现（非空壳）
- [x] 证据链：判断 → metrics/manifest → evidence 包 可解析
- [x] 规则版本：UNIVERSAL_THRESHOLDS + pairwise_policy_v1.yaml 版本化
- [x] 运行身份：ApprovedExecutionEnvelope（SHA-256）
- [x] 案例持久化：ProductionCaseStore（文件系统 JSON，原子写）
- [x] 学习循环：learning/ build → review → commit
