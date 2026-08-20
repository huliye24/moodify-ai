# Moodify Ear v1 — Chapter II 理念吸收

**来源**: 《Moodify Ear v1: Can Machines Learn to Hear?》Technical Monographs Volume I, Chapter II
"What Hearing Means for a Machine"（2026-08，外部路径 `E:\Moodify ear\Moodify_Ear_v1_Chapter_02\`，24 篇参考文献）
**蒸馏日期**: 2026-08-12
**状态**: 阶段 0（2c30ac0）+ 阶段 1（5321680）+ 阶段 2 MAMSE-013~016 全部完成（c68cbbc/f7e4130/614a87d/128bcc3，证据 5a97e08）——Chapter II 吸收主体完成

> 本文件是章节理念的蒸馏与项目映射，不是章节原文。原文留在外部目录；本文件沉淀可执行的架构原则。

## 章节核心命题

章节的核心主张："听"不是存储波形，而是从声音构建一个可用世界。工程目标不是"模拟耳朵"，而是构造一条计算链，其中每个表示都能回答新一类听觉问题，同时保留足够的物理证据以保持可审计。

章节给出 20 节，可压缩为 10 条原则：

1. **观测条件即证据**：不存在脱离观测条件的"声音"。采样率、位深、编解码、重采样、内容哈希都必须在做出任何高层断言之前被记录（§2）。
2. **时频互补，多分辨率**：单一谱图配置不应被视为真理。不同听觉问题需要不同时频尺度（§3）。
3. **前端多元并存**：线性 STFT、感知滤波器组（ERB/Gammatone）、mel、学习表示应共存；没有任何单一前端有权定义整个听觉本体（§4, §5）。
4. **时间尺度是元数据**：finding 必须知道自己来自 10ms 事件还是全曲统计；证据粒度不同，断言性质不同（§6）。
5. **物理、测量、判断三层分离**：sample 幅度、LUFS、听觉判断是三层，混淆产生虚假确定（§7）。
6. **空间/相位是时频问题**：全局相关只是摘要；局部相干、相位、跨频率行为才是证据（§8）。
7. **掩蔽：测量存在 ≠ 感知可用**：心理声学掩蔽必须作为推断而非频谱能量直读；证据不足时输出"证据不足"而非红色警告（§9）。
8. **软听觉对象**：无需完美分离即可有用；以概率化区域/流组织场景，判断携带不确定性前向传播（§10, §10A）。
9. **不变性按判断族定义**：什么算干扰变换取决于任务；不同表示子空间保留不同敏感性（§11）。
10. **混合表示 + 证据路由**：确定性指标保证可审计，感知变换组织知觉，学习嵌入发现模式；判断必须记录每条主张的证据路径（§12, §13）。

辅助命题：音乐结构改变同一声学事件的意义（§14，MSE 条件化）；AI 生成音乐产生无人类制作先例的伪影，需区分"伪影嫌疑"与"因果归因"（§15）；听觉状态是结构化集合 `A(x) = {M_r, P_r, L_r, S, q}` 而非单体向量（§16）；部分可观测性下区分 observed/inferred/associated/unknown（§17）；传感器需发布契约（输入假设、单位、时间分辨率、确定性状态、配置、输出 schema、已知失败条件、验证测试）（§18）；耳朵用响应模式而非截图验证（§19）。

## 理念 → 项目映射

### 已实现（对齐即验证，零开发）

| 章节 | 理念 | 项目落点（已验证路径） |
|---|---|---|
| §2 | 格式/采集元数据 + 内容哈希 | `moodify/auditory/manifests.py`（sha256）、`auditory/decode.py`（probe）、`contracts` |
| §3 | 多分辨率时频 | MAMSE-001（R 轴多分辨率）、rep-v1 四尺度表示、`auditory/spectrogram.py` |
| §7 | 三层分离 | `auditory/loudness.py` + `true_peak.py`；LUFS 双重偏移修复（补丁包 30） |
| §8 | 空间/相位 | `auditory/stereo.py`（mid/side、相关）、MAMSE-004（相位几何/群延迟）、MAMSE-011（协方差/本征空间） |
| §11+19 | 不变性/敏感性扰动验证 | `auditory/lab/` 9 扰动算子 + 矩阵评估（Recall 1.0，补丁包 24） |
| §17 | 缺失证据/部分可观测 | `auditory/uncertainty.py`、`auditory/evidence/`（U1–U7、fail-closed，补丁包 23） |
| §18 | 传感器契约 | `auditory/measurement_registry.py`、MFY-METRIC-REGISTRY-001、28 指标权威矩阵（补丁包 20） |
| §10 底注 | 不必完美分离才有用 | MAMSE-008 NMF 匿名成分、MAMSE-009 RobustPCA 合成验证 |

### 部分实现（阶段 1 已交付）

| 章节 | 理念 | 交付（DSK-MFY-CH02-PHASE1-001，5321680） |
|---|---|---|
| §14 | MSE 条件化判断 `J(z_audio, z_structure, c)` | ✅ `auditory/structure.py`：Section/StructureContext（重叠校验/查询/置信度门 0.8）；resolver 可选 structure 参数，可靠时标注段落标签+边界标志，不可靠时零标注+PROFILE_UNCERTAINTY |
| §6 | 时间尺度元数据 | ✅ `auditory/evidence/scale.py`：EVIDENCE_SCALES + `scale_for_duration_ms`；EvidenceNode.scale 自动填充（事件按时长，全曲指标 WHOLE_TRACK） |
| §17 | epistemic 词表（observed/inferred/associated/unknown） | ✅ `auditory/evidence/epistemic.py`：一等类型；事件 INFERRED、相关/相位事件 ASSOCIATED、fail-closed 判断 UNKNOWN |
| §15 | AI 伪影嫌疑 ≠ 因果归因 | 已有 algorithmic_review 启发式 + MAMSE-009 负结果；命名路径未立项（下一轮，对 Suno 喂养直接相关） |

### 明确缺失（阶段 2 实验算子候选）

| 章节 | 理念 | 立项建议 |
|---|---|---|
| §4 | ERB/Gammatone 听觉滤波器组 | ✅ MAMSE-013（c68cbbc）：Glasberg-Moore ERB 几何 + 4 阶 gammatone，第三前端 |
| §9 | 频率掩蔽推断 | ✅ MAMSE-014（f7e4130）：ERB 通道扩散掩蔽阈值 + 软可听度 + 掩蔽通道比事件；无内容≠被掩蔽，响音裙边物理保持可听 |
| §10 | 软听觉对象（概率化区域/流） | ✅ MAMSE-015（614a87d）：声学角色假设概率剖面（独立指示器），弱证据→UNRESOLVED |
| §10A | 带置信度的多候选音高状态 | ✅ MAMSE-016（128bcc3）：YIN-lite 多候选 F0 + 谐波支持度 + 稳定音高串 |
| §15 | 未命名伪影发现路径 | 案例聚类 + 受控干预暴露结构；对 Suno 喂养计划直接相关（未立项，下一轮） |

### 显式 DEFER（阶段 3 决策边界，非缺陷）

| 理念 | DEFER 理由 |
|---|---|
| §12 学习嵌入（wav2vec2/PANN/AST/BEATs/MERT） | CPU-only 架构，核心依赖无 torch；需先做"学习嵌入是否需要 GPU/云"的架构决策（关联 Suno 上云计划） |
| §16 Auditory State 形式化 `A(x)={M_r,P_r,L_r,S,q}` | 结构性大改；现有 scan profile + evidence graph 已覆盖部分语义；等阶段 1/2 验证表示演进方向后再定 |
| §5 mel 前端正式化 | mel 目前未成为独立一等前端；现有 CQT 对数频率视图承担部分角色，无紧急缺口 |

## 对 Suno / 预训练计划的直接关系

- §15（AI 音乐未命名伪影）是云服务器喂养场景的正题：Suno 输出需要"伪影嫌疑"发现路径，且应保持"嫌疑 ≠ 归因"的诚实边界（MAMSE-009 已证明低秩假设对 dense AI 制作不成立）。
- §7 三层响度分离是数据工厂评审器的既有语义，喂养数据时无需改动。
- 阶段 2 的软听觉对象（MAMSE-015）与掩蔽推断（MAMSE-014）会直接改善 AI 素材判断质量，建议在规模化喂养前完成。

## 验收

- 本文件可被 `docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md` 的 WSE/MSE/PPE 节引用。
- 审计报告：`docs/audits/DSK-MFY-EAR-V1-CH02-ABSORB-001/REPORT.md`。
