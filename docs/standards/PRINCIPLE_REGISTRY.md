# Moodify 原理注册表（Principle Registry）

**Created:** 2026-08-02  
**任务来源：** DSK-MFY-KNOWLEDGE-LAYERS-022  
**Purpose:** 记录"为什么必须这样"——每条原理有可核对来源，约束代码层的规则与任务编排。  
**维护规则：** 新条目必须来自真实决策（ADR/战略/架构文档/哲学文献），禁止为凑数编造；条目只可追加，修正以新版本标注 superseded。

---

## PR-001 生产以案例为单元，原始记录不可变

**来源：** `docs/decisions/ADR-003-production-case-as-core-unit.md`；`docs/strategy/MOODIFY_ENGINEERING_THICKNESS_STANDARD.md` §4.1（不覆盖已登记的音频版本）  
**适用范围：** 生产流程、case 系统、记录存储  
**关联经验：** EX-001

## PR-002 证据先于主张：无预注册对照，不宣称优越性

**来源：** `docs/decisions/ADR-004-evidence-before-superiority-claims.md`  
**适用范围：** 评估、发布、对外主张、benchmark 结论  
**关联经验：** EX-002

## PR-003 Moodify 不是自动混音，人工保留艺术方向与最终责任

**来源：** `docs/decisions/ADR-001-moodify-is-not-automated-mixing.md`  
**适用范围：** 产品定位、审批门、交付边界  
**关联经验：** —

## PR-004 声音测量、音乐结构、生产流程分三层（WSE/MSE/PPE），共享证据

**来源：** `docs/decisions/ADR-002-wse-mse-ppe-architecture.md`  
**适用范围：** 架构分层、模块边界、evidence packet  
**关联经验：** —

## PR-005 工具拥有执行，Moodify 拥有解释权

**来源：** 能力引力井论文 DSK-MFY-CAPABILITY-ACCRETION-001 §4.3；`docs/architecture/SCORE_ENGINE_ARCHITECTURE.md`（原点原则）  
**适用范围：** capability_registry、score_engine、外部工具调用  
**关联经验：** EX-003, EX-004

## PR-006 推断不冒充事实：未确认保持 unknown，raw/inferred/confirmed 分层

**来源：** `DSK-MFY-SCORE-ENGINE-009/MOODIFYSCORE_CONTRACT.md` §5；MSE_ARCHITECTURE（置信度必须可生成）  
**适用范围：** score_engine、transcription_pipeline、任何推断字段  
**关联经验：** EX-003

## PR-007 规则可改变，不可遗忘：失败与边界是地质记录

**来源：** POSC-003《The Hidden Depth of Systems》（测试作为地质记录、负面知识）；`MOODIFY_ENGINEERING_THICKNESS_STANDARD.md` §4.10（历史结论可被推翻但不能无痕消失）  
**适用范围：** FAILURE_LEDGER、测试设计、规则版本化、政策演化  
**关联经验：** EX-001, EX-003, EX-005, EX-006, EX-007

## PR-008 深度 = 复杂性转化为形式；厚度 ≠ 复杂度

**来源：** POSC-003《The Hidden Depth of Systems》（Resolved Complexity、Thickness Without Complication）；`MOODIFY_ENGINEERING_THICKNESS_STANDARD.md` §1（工程厚度不是复杂度）  
**适用范围：** 架构评审、任务编排、注册表维护  
**关联经验：** —

## PR-009 每次生产同时产生结果、证据与继承（三重交付）

**来源：** `docs/strategy/MOODIFY_ENGINEERING_THICKNESS_STANDARD.md` §2  
**适用范围：** 所有生产/工程任务的门禁（G-Result/G-Evidence/G-Boundary/G-Inheritance/G-Succession）  
**关联经验：** EX-001, EX-002, EX-008

## PR-010 单指标不得替代专业人员最终判断

**来源：** `docs/standards/FAILURE_LEDGER.md` FL-004；`MOODIFY_ENGINEERING_THICKNESS_STANDARD.md` §4.6  
**适用范围：** MRS 门禁、质量闸、发布审批  
**关联经验：** EX-002, EX-008

## PR-011 深度维持三问：没有失忆、边界未松动、新增知识被保存

**来源：** 用户决策（2026-08-02 后期工作模式）；POSC-003；系列编排 DSK-MFY-CAPABILITY-ACCRETION-017 §3.4  
**适用范围：** 后期任务编排、验收标准、任务包设计  
**关联经验：** EX-001, EX-005

## PR-012 禁止 MATLAB 自动启动、禁止网络下载、禁止 git 破坏性操作

**来源：** 项目既有铁律（用户 2026-06 起）；各任务包硬规则  
**适用范围：** 所有任务包执行约束  
**关联经验：** —

---

## 注册摘要

| ID | 一句话 |
|---|---|
| PR-001 | 生产以案例为单元，原始记录不可变 |
| PR-002 | 证据先于主张 |
| PR-003 | 不是自动混音，人工保留最终责任 |
| PR-004 | WSE/MSE/PPE 三层共享证据 |
| PR-005 | 工具拥有执行，Moodify 拥有解释权 |
| PR-006 | 推断不冒充事实 |
| PR-007 | 规则可改变，不可遗忘（地质记录） |
| PR-008 | 深度 = 复杂性转化为形式 |
| PR-009 | 三重交付：结果、证据、继承 |
| PR-010 | 单指标不得替代人工判断 |
| PR-011 | 深度维持三问 |
| PR-012 | 执行铁律（无 MATLAB/无下载/无 git 破坏） |
