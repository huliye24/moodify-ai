# DSK-MFY-EAR-V1-CH02-ABSORB-001 — Chapter II 理念吸收差距审计

**审计编号**: DSK-MFY-EAR-V1-CH02-ABSORB-001
**日期**: 2026-08-12
**审计人**: Claude Code（Claude A 交接官协作）
**审计对象**: 《Moodify Ear v1》Chapter II "What Hearing Means for a Machine"（外部路径 `E:\Moodify ear\Moodify_Ear_v1_Chapter_02\`）
**基线**: 当前分支 codex/mfy-data-factory-001（HEAD a0014b4）

## 1. 审计范围与方法

**范围**：将章节 20 节理念逐条映射到 `moodify-core-package/src/moodify/` 现有实现，判定 已实现/部分/缺失，并给出吸收处置。不含章节原文复述（见 `docs/reference/MOODIFY_EAR_V1_CH02_ABSORPTION.md`）。

**方法**：
- 全文阅读章节源文（35KB md）
- 代码检索：gammatone/ERB、masking、soft object/posterior、YIN、embedding、epistemic、WSE/MSE/PPE、measurement registry、lab 扰动
- 对照冻结 manifest（CODE_FREEZE_MANIFEST.json）、补丁包记录与既有架构文档
- 全量回归验证：522 passed / 5 skipped（2026-08-12 实测，3 分 24 秒），ruff 全绿

## 2. 差距矩阵

### A. 已实现（对齐验证，零开发）

| 章节 | 理念 | 代码证据 | 判定 |
|---|---|---|---|
| §2 | 采集/格式元数据 + 内容哈希 | `auditory/manifests.py`（sha256_file）、`auditory/decode.py`（probe） | ALIGNED |
| §3 | 多分辨率时频 | MAMSE-001、rep-v1 四尺度、`auditory/spectrogram.py` | ALIGNED |
| §7 | 物理/标准化/判断三层响度 | `auditory/loudness.py`、`true_peak.py`、LUFS 修复 | ALIGNED |
| §8 | 空间/相位时频化 | `auditory/stereo.py`、MAMSE-004、MAMSE-011 | ALIGNED |
| §11+19 | 不变性/敏感性扰动验证 | `auditory/lab/` 9 扰动算子、矩阵评估 | ALIGNED |
| §17 | 缺失证据/部分可观测 | `auditory/uncertainty.py`、`auditory/evidence/`（U1–U7） | ALIGNED |
| §18 | 传感器契约 | `auditory/measurement_registry.py`、28 指标权威矩阵 | ALIGNED |

### B. 部分实现（阶段 1 补丁候选）

| 章节 | 理念 | 现状 | 缺口 |
|---|---|---|---|
| §14 | MSE 条件化判断 | 架构文档定义 MSE；代码仅 WSE profile（MFY-WSE-SCAN-PROFILE-001） | 无 `J(z_audio, z_structure, c)` 结构条件化路径 |
| §6 | 时间尺度元数据 | 事件定位精度=hop | finding 无来源尺度标注 |
| §17 | epistemic 词表 | 概念散落 evidence models | 未成一等类型 |
| §15 | AI 伪影嫌疑≠因果归因 | algorithmic_review 启发式 + MAMSE-009 负结果 | 未成命名路径 |

### C. 明确缺失（阶段 2 实验算子候选）

| 章节 | 理念 | 立项建议 |
|---|---|---|
| §4 | ERB/Gammatone 滤波器组 | MAMSE-013 |
| §9 | 掩蔽推断 | MAMSE-014 |
| §10 | 软听觉对象 | MAMSE-015 |
| §10A | 多候选音高/谐波证据 | 补 MAMSE-005 短板 |
| §15 | 未命名伪影发现 | 案例聚类 + 干预 |

### D. 显式 DEFER（阶段 3 决策边界）

| 理念 | DEFER 理由 |
|---|---|
| §12 学习嵌入 | CPU-only 架构，无 torch 核心依赖；待云/GPU 架构决策 |
| §16 Auditory State 形式化 | 结构性大改；scan profile + evidence graph 已覆盖部分 |
| §5 mel 前端正式化 | CQT 视图已承担部分角色，无紧急缺口 |

## 3. 事实边界

- **已验证**：章节 §2/3/7/8/11/17/18 对应实现存在且全量回归绿（522 passed）。
- **代码检索确认的缺失**：gammatone/ERB 无实现（auditory 层检索零命中）；掩蔽仅为 numpy 频带 boolean mask，非心理声学推断；soft object/posterior 概念在 auditory 包零命中；YIN 无实现（MAMSE-005 为倒谱 F0，已知对密集混音不可靠）；学习嵌入无实现。
- **环境限制**：检索基于当前工作树（HEAD a0014b4）；未检查非主线分支中的历史实现。
- **不纳入本次审计**：资产注册表登记（asset-registry 主记录 952ab61 位于非主线分支，当前主线未保留该子系统——不复活，另立决策）；章节原文的校对/出版事项。

## 4. 处置建议（按阶段）

- **阶段 0（2026-08-12）**：蒸馏文档 + 本审计报告 + 架构文档交叉引用。**已完成**（2c30ac0）。
- **阶段 1（2026-08-12）**：MSE 条件化接口 + 时间尺度元数据 + epistemic 词表一等化。**已完成**（DSK-MFY-CH02-PHASE1-001，5321680；19 测试，541 全量绿）。
- **阶段 2（进行中）**：MAMSE-013 ERB filterbank **已完成**（c68cbbc，15 测试，556 全量绿）；余下 MAMSE-014 掩蔽推断 → MAMSE-015 软听觉对象 → 音高证据；按 EXPERIMENTAL_ACCEPTED 流程（R1–R3）。
- **阶段 3**：学习嵌入与 Auditory State 重构的架构决策窗口（建议与 Suno 上云规划同步评估）；DEFER 项写入决策记录，不得在无授权时激活。

## 5. 关联

- 蒸馏文档：`docs/reference/MOODIFY_EAR_V1_CH02_ABSORPTION.md`
- 架构文档：`docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md`（§3 WSE/MSE/PPE）
- Suno 喂养计划：§15 未命名伪影发现与阶段 2 算子为规模化喂养前置
