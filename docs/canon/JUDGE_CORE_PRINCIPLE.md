# JUDGE CORE PRINCIPLE — Moodify

**Status:** CANONICAL PRODUCT AND R&D DIRECTION  
**Effective:** 2026-10-06  
**CANON_CHANGE:** YES  
**Human authority:** explicit founder decision, 2026-10-06

## 1. Core decision

> **Moodify Judge is Moodify's core model.**
>
> **We don't need to own every audio model. We need to own the judgment.**  
> **我们不需要拥有所有声音模型。我们必须拥有判断。**

Moodify 的长期自有核心不是某一个分离、降噪、修音、母带或生成模型，而是：

1. 听见声音中发生了什么；
2. 判断什么构成问题、什么必须保留、是否需要处理；
3. 在处理后判断结果是否改善、是否可接受、是否应重试、调整或保留原版；
4. 知道证据不足或超出授权范围时停止，并升级给人类。

`Moodify Auditory Intelligence` 是这套长期能力的总称；第一代自有模型的目标名称为
`Judge-1`。Judge 不是第二个公开产品，仍属于同一个 Moodify Core，并由 Moodify Cloud、
Protocol、Studio、CLI、API、Agent 与 App 等接口调用。

## 2. The two-Judge invariant

每一次处理闭环必须保留两个不同时间点的 Judge：

```text
Audio
  ↓
Judge Before — What happened? What matters? Should anything be changed?
  ↓
Planner — What bounded treatment should be attempted?
  ↓
Provider Layer — Separation / Denoise / Tuning / Mix / Master / Generation
  ↓
Result
  ↓
Judge After — Is it better? What regressed? Accept, retry, adjust, or keep original?
  ↓
Human A/B decision when required
```

这两个 Judge 不是同一句判断重复两次：

- **Judge Before（诊断 Judge）**：建立原始声音的事实、问题假设、保护目标、处理必要性、
  优先级、置信度与不确定性。
- **Judge After（验收 Judge）**：在可对齐证据上比较原始与结果，检查目标是否改善、身份与
  艺术意图是否受损、是否出现新问题，并输出 `PASS / RETRY / ADJUST / KEEP_ORIGINAL /
  HUMAN_REQUIRED / INCONCLUSIVE` 等受契约约束的结论。

任何流程都不得因为某个 Provider 成功返回文件，就把该文件自动称为完成或更好。

## 3. Core versus provider

### Moodify 必须拥有

- Judge 的任务定义、输入输出契约与版本；
- 听觉表示与判断头中形成 Moodify 判断能力的部分；
- 判定范围、置信度、不确定性与人类升级规则；
- Before/After 对齐、验收与回退逻辑；
- Treatment Record、证据链、人类 A/B 选择与数据治理；
- 用上述记录训练、校准、验证和发布 Judge 新版本的过程。

### 可以采用第三方、开源或可替换实现

- source separation；
- denoise / restoration；
- pitch / timing correction；
- mixing / mastering DSP；
- transcription / MIDI extraction；
- generative audio；
- foundation audio encoder；
- GPU、云服务与专业音频 API。

这些能力是可更换的 **Hands**。Judge 是 Moodify 的 **Ear + Brain**。使用第三方能力不削弱
Moodify 的产品身份；把判断权交给不可审计的第三方、或让 Provider 自己证明自己，则会削弱。

Provider 必须通过显式接口被调用并留下名称、版本、参数、输入输出哈希、失败状态与许可/来源信息。
供应商可替换不等于来源可隐藏。

## 4. Planner boundary

Planner 把 Judge 的判断转成受约束、可编辑、可回退的处理方案。它可以使用通用 Agent、规则、
第三方模型或 Moodify 自有模型，但不得：

- 发明 Judge 没有提供的听觉事实；
- 越过 Judge 的保护目标、置信度与授权范围；
- 把计划写成已经验证的结果；
- 绕过 Judge After 或必要的人类 A/B 决定。

因此 Planner 很重要，但不是 Judge authority 的替代品。

### 4.1 Fixed process, song-specific parameters（2026-10-11 修订）

Moodify 固定的是 `HEAR → JUDGE → ACT → VERIFY → BLIND COMPARE` 及其证据和失败语义，
不是 EQ、压缩、修音、降噪、混音或母带参数。每个参数必须能追溯到：

- 当前歌曲与分轨的 measured facts；
- 具体问题和时间范围；
- 作品意图与 `preserve` 约束；
- Judge Before 的判断、置信度与授权范围；
- Planner/Provider 版本和搜索过程。

历史参数、预设或工艺卡只能作为安全边界、未校准初始化值或搜索先验。它们不得绕过 Judge Before，
也不得因过去曾被接受而自动用于下一首歌。Judge After 必须验证这次实际结果，而不是验证“参数看起来
专业”。

### 4.2 Vocal identity preservation and driver attribution（2026-10-12 修订）

对 AI 音乐生产，默认原则是 `Voice is identity; accompaniment is adaptable.`。人声音色、咬字、气息、
滑音、颤音、微时值和情绪动态具有高身份密度，应进入 `preserve`；这不构成“永不修改人声”的禁令，
而是要求人声修改具有更高证据门槛和更窄作用范围。

Judge Before 必须区分至少两类问题：

1. **人声内部问题**：证据来自人声分轨自身，例如掉音、断裂、异常噪声、分离伪影、局部电平异常、
   明确的音高或节奏缺陷；
2. **混合关系问题**：证据来自人声放回伴奏后的遮蔽、平衡和空间关系。

`V−A`、频带遮蔽率或其他相对比值只说明关系发生变化，不能说明哪一侧应被修改。任何由相对指标触发
的动作必须先输出 `driver_attribution = VOCAL | ACCOMPANIMENT | BOTH | AMBIGUOUS` 及两侧独立证据。
当人声自身正常且问题由伴奏驱动时，Planner 默认先让伴奏通过电平、编配、动态 EQ 或空间关系让位；
不得仅因混合中人声不突出，就先抬高、压缩、增亮或重写人声。`AMBIGUOUS` 必须升级为试听或
`HUMAN_REQUIRED / INCONCLUSIVE`。

## 5. Judgment is not measurement

测量回答 `LUFS = -10.8`、`true peak = -0.3 dBTP` 或某频段能量为多少。Judge 必须回答：

- 该事实在此内容、风格、意图和发行场景中是否构成问题；
- 问题的重要程度、证据与不确定性；
- 可以改变什么、必须保护什么；
- 处理后净收益是否为正。

所有 Judge 输出必须区分：

1. measured fact；
2. inferred condition；
3. evaluative judgment；
4. recommended action；
5. uncertainty / authority state。

不得把测量值、规则命中或模型分数直接伪装成审美事实。

## 6. Treatment Record flywheel

每次有效工作应形成：

```text
Original Audio
  → Judge Before
  → Plan
  → Provider execution trace
  → One Challenger
  → Judge After
  → loudness-matched, identity-blind Baseline/Challenger comparison
  → accept challenger / keep baseline / local retry
  → Treatment Record
```

每轮只引入一个新挑战者。匿名 A/B 只是比较槽位：一侧为当前基准，一侧为挑战者；Judge 不应知道
哪侧是原版、哪侧经过处理，也不应接收插件和参数提示。当前基准第一轮通常是原版，后续可以是已接受
版本。若挑战者被拒绝，记录失败原因同样是数据资产。

默认干预粒度是“一个有证据的问题或一个边界清楚的局部范围”。只有通过技术复检与盲比的挑战者才能
晋升为新的当前基准；证据不足、不可稳定分辨或出现不可接受副作用时保留基准。未通过验证的变更不得
继续叠加，否则 Judge 无法把改善或损害归因到具体动作。多参数联动允许作为一个不可再分的 Mix Graph
变更单元，但必须记录其共同目的、作用范围和旁路路径。

Treatment Record 是未来 Judge 训练数据的候选来源，不自动等同于可训练数据。进入 Dataset 前必须有：

- 权利与隐私许可；
- 来源、版本、处理参数和证据完整性；
- 人类判断者、范围、时间与置信度；
- 防止同一内容、同一作者或同一 Provider 造成数据泄漏与偏差的拆分规则；
- 训练集、校准集、盲测集隔离；
- 可撤回、可追溯与版本化的数据治理。

长期飞轮是 `Treatment Records → governed Dataset → Judge n+1 → better bounded judgment →
more reviewed Records`，不是未经同意收集音频或把用户点击直接当真值。

## 7. Human authority remains

Judge 是 Moodify 必须自有的机器判断能力，不等于机器获得无限审美主权。

- 已验证、版本化且明确授权的范围内，Judge 可以作出机器决定；
- 超出范围、证据不足、置信度不足、艺术意图冲突或感知结论未解决时，必须输出
  `HUMAN_REQUIRED`、`INCONCLUSIVE` 或定义明确的失败状态；
- 人类 A/B 选择与 `KEEP_ORIGINAL` 始终是合法出口；
- 人类结果用于校准 Judge，而不是被系统静默覆盖。

## 8. Current reality — 2026-10-06

本裁决定义的是研发核心与目标架构，不是对当前能力的虚构：

- 仓库已有版本化技术 judgment rules、evidence、comparison、scoped authority 与人工升级机制；
- 当前生产判定主要是规则式技术判断，不是成熟的学习型 `Judge-1`；
- 当前 16 条生产阈值均为 `DEFAULT_UNCALIBRATED`，感知显著性尚未校准；
- Layer 3 musical、Layer 4 production、Layer 5 cultural judgment 仍为 `NOT_PROMISED`；
- 当前系统不得声称已能可靠理解风格、情绪、艺术意图或普遍判断“更好听”；
- `Judge-1` 的模型、数据集、训练、校准与盲测发布门禁仍待实现。

## 9. R&D priority

在不破坏现有产品闭环的前提下，研发排序改为：

1. 冻结 Judge task taxonomy、schema、authority 和 evidence contract；
2. 建立高质量、获授权、可追溯的 Before/After + 人类 A/B Treatment Records；
3. 建立 Judge 基线、校准集、盲测集与 fail-closed evaluation；
4. 基于成熟 audio encoder 研究并训练 `Judge-1`；
5. 让 Planner 和可替换 Provider 接受 Judge 的约束；
6. 只有证据证明外部 Provider 构成关键瓶颈时，才考虑自研对应处理模型。

不得因为本原则而立即删除现有 DSP、Studio 流程、协议、App 或 Provider 实现；它们继续服务产品、
生成证据并形成 Treatment Records。新增或改变 protocol/schema/core behavior contract 时，仍须按治理规则
提交 MIP。
