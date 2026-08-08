# DSK-MFY-CAPABILITY-ACCRETION 系列编排（017-021）

**系列文档：** `DSK-MFY-CAPABILITY-ACCRETION-001`（能力引力井架构论文）  
**计划：** 2026-08-02 起，每日一包（LSM 约束下 4 小时/包）  
**执行 Worker：** DeepSeek 串行实施；**最终 Judge：** Codex / 授权用户  
**系列状态：** 五包已全部实施完成（2026-08-02），等待 Codex 逐包独立验收

## 1. 五包依赖链（严格串行）

```text
017 Registry（注册表先行）
  -> 018 Adapter Boundary（适配器边界）
  -> 019 Approved Execution（批准执行）
  -> 020 Validation & Candidate（验证与候选）
  -> 021 Knowledge Feedback（知识反馈）
```

| 包 | 主题 | 论文 Phase | 依赖 | 交付核心 |
|---|---|---|---|---|
| 017 | Capability Registry | Phase 1 | 009 ACCEPT | Registry + manifest schema + 环境探测器 + 首批能力注册 |
| 018 | Adapter Boundary | Phase 2 | 017 ACCEPT | ProviderAdapter + 6 适配器 + 错误分类 |
| 019 | Approved Execution | Phase 3 | 018 ACCEPT | Envelope + Gateway + ExecutionRecord + 未授权检测 |
| 020 | Validation & Candidate | Phase 4 | 019 ACCEPT | 验证规则库 + 候选生成/排序/回退 |
| 021 | Knowledge Feedback | Phase 5 | 020 ACCEPT | 测量/判断记录 + 规则提案 + 政策版本化 |

**串行规则：** 上一包 HANDOFF 可读且 Codex ACCEPT（或明确批准接口稳定）后才
启动下一包；不满足则置 HOLD，禁止隐性并行修改共享 CLI/pyproject。

## 2. 本系列吸收的现有能力（事实清单 2026-08-02）

| 能力 | provider | 版本 | 许可（外部进程） |
|---|---|---|---|
| media.transcode / probe | FFmpeg / ffprobe | 8.1.1 | GPLv3/LGPL |
| notation.render | MuseScore | 4.5.1 | GPLv3 |
| audio.time_stretch | RubberBand | 4.0.0 | GPLv2 |
| audio.measure_loudness | SoX | 14.4.2 | LGPL |
| waveform.region_edit | Audacity | 待探测 | GPLv2 |
| audio.transcribe_midi | Basic Pitch（008） | 0.4.0 | Apache-2.0 |
| score_engine（009） | Moodify 内部 | 2.0.0 | Apache-2.0 |

未安装（只登记 known_missing）：Demucs 分离模型、Verovio/LilyPond/OSMD 后端。

## 3. 每包公共约束

- 禁止 MATLAB 调用、网络下载、修改 008/009/Runtime 实现、处理真实歌曲。
- 禁止 Git reset/clean/stash/checkout/commit/push/切分支。
- 现有 dirty 工作树与未跟踪文件属用户，不得覆盖/还原/整理/暂存。
- 每包输出 `PROGRESS.md`、`VALIDATION_REPORT.md`、`FAILURE_LEDGER.md`、
  `HANDOFF.md`；最终状态只能是 READY_FOR_CODEX_REVIEW / REWORK / HOLD。
- LSM：8 GB / 双核，串行执行，无并行进程。

## 3.4 系列深度维持原则（后期工作模式）

项目已进入"隐性知识密度持续上升"阶段：系统越大，每次改动的相对影响
越小，同样的工作量在前期造成巨大改变、在后期只是微调。这是深度起作用
的表现（判断已被结构保存），不是项目停滞的信号。因此本系列及后续所有
任务编排遵循：

1. **验收以深度维持三问为准，不以改动幅度为准**：
   - 没有失忆——既有边界、失败分类、地质记录未被破坏或遗忘；
   - 边界没有松动——改动未让系统回到需要英雄式记忆的状态；
   - 新增知识被保存——本次执行发现的新区分/新失败被翻译成公共形式。
2. **小步高密度**：任务规模收缩（2-3 个能力/每包），但每个小步携带更高的
   知识密度（测量、判断、失败记录）；不再追求大批量一次性改变。
3. **"影响小"不等于"任务不重要"**：拒绝把"影响小"误判为"不值得做"导致
   纯行政维护；同样拒绝把"看起来大"的无学习重构当成绩。判断任务价值看
   知识积累密度而非变化幅度。
4. 后期节奏允许放缓（LSM 下 4 小时/包不变），但深度不得衰减；若某包产出
   未增加任何地质记录，视为未完成（REWORK）。

## 3.5 系列地质记录原则（POSC-003《系统的隐性深度》）

本系列把"测试作为地质记录"与"负面知识"设为**系列级硬要求**，贯穿五包：

1. **每个测试/规则回答一个历史问题**：它曾经保护什么区分、哪次失败使它
   成为必要边界（020 的 `ValidationRule.historical_source`）。
2. **被拒绝的路径是一等公民**：失败候选、回退、排除的方案必须持久化
   （020 RejectionReason / 021 NegativeKnowledgeRecord），禁止清理为
   "临时事故"——负面知识是复利资产。
3. **规则可改变，不可遗忘**：政策变更必须引用被替代的旧规则及来源；
   已生效记录只可追加 superseded，禁止删除/改写（021 失忆防护）。
4. **注册表从第一天携带失败史**：017 注册每个能力时从 009/008 失败台账
   提取真实 known_failure_modes 作为地质记录种子，不允许空表。
5. **深度不是复杂性**：本系列增加的结构（注册表/适配器/网关/验证/知识）
   必须让未来行动更轻；任何只增加记忆负担的厚度视为官僚沉积，验收时拒绝。

## 4. 完成定义

系列完成 = 五包全 ACCEPT + `CAPABILITY_ACCRETION_ARCHITECTURE.md` 反映
真实实现的六层架构 + 能力矩阵与实际安装一致 + 至少 3 个能力达到
Level 3（受控工作流：注册 + 适配器 + envelope + 验证 + evidence）。
Level 4（多 provider 可替换）与 Level 5（学习）为后续系列目标，不在此承诺。
