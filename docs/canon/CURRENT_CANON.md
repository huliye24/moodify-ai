# CURRENT CANON — Moodify

> **2026-10-15 owner-controlled music library amendment (CANON_CHANGE = YES):** Studio 新增
> 作品管理主界面，用于在电脑端管理歌名、封面、音频、歌词与发布状态；后处理保留为
> 独立生产模块，App 仍是播放端。“数据属于用户”的工程含义是作品按 owner 隔离、原始资产
> 可导出、可删除、发布可追溯与可撤回；不引入 token、DAO、空投或链上作品权威。当前已实现
> 本地 owner 作品库；单用户的 Desktop → LA Cloud → App 发布链已实跑通。多用户同账号
> 身份、RLS 与对象存储仍为 `DEPLOYMENT_BLOCKED`，不得把单用户 SSH owner bridge 写成通用账号系统。

> **2026-10-12 vocal identity preservation amendment (CANON_CHANGE = YES):** 对 AI 音乐生产，Moodify
> 默认采用 `Voice is identity; accompaniment is adaptable.`：人声承载高密度身份与表演信息，修改
> 人声的证据门槛高于修改伴奏。人声自身正常但在混合中被遮蔽时，优先让伴奏让位。相对比值异常必须
> 拆分人声侧与伴奏侧贡献，不能直接触发人声修音。该规则是默认干预优先级，不是“人声永不修改”或
> “乐器可无限替换”的绝对事实；明确的人声生成缺陷仍可在保护约束下局部修复。

> **2026-10-11 song-specific parameters and single-challenger amendment (CANON_CHANGE = YES):**
> Moodify 固定的是生产流程、证据契约、门禁与裁决规则，不是每首歌的调音参数。每轮执行
> `HEAR → JUDGE → ACT → VERIFY → BLIND COMPARE`，参数必须由该曲、该分轨、具体时间段、问题证据、
> 作品意图与保护目标重新生成。固定预设只能作为安全边界或搜索起点。每轮只生成一个新挑战者，
> 与当前基准统一编码、严格响度匹配并随机匿名为 A/B；A/B 是盲测槽位，不再是两套处理强度。
> 无校准证据、净收益不明确或出现局部损害时保留当前基准。Treatment Records 积累判断、动作、参数、
> 验证、盲测与失败证据，构成未来 Judge 的数据资产，而不是积累“万能参数”。默认采用最小可归因
> 干预：每轮只修一个有证据的问题或边界清楚的局部范围；只有通过复检与盲比的挑战者才能成为下一轮
> 基准，未验证改动不得继续叠加。

> **2026-10-08 operator-first correction (CANON_CHANGE = YES):** 第一阶段唯一真实用户是内部受训
> 制作团队，因此 Studio 不再以 C 端学习成本为主要约束，可以发展为高密度、细工序、批量化的工业
> 生产软件；复杂度必须换来吞吐、精度、证据、复现与可靠交付。官网不承担接单，保留研究文档、实验
> 图像、作品与既有浏览习惯；小红书、抖音、淘宝是当前获客/交易渠道。该修订不授权第二套 Core、
> Judge、Job 或 state machine。

> **2026-10-08 internal commercial-music phase amendment (CANON_CHANGE = YES):** Moodify 第一阶段
> 是荣景文川内部的 AI 商用音乐生产系统。外部网剧等 B2B 客户购买音乐与制作服务，不操作 Moodify；
> 当前不建设通用 C 端、外部 B 端 SaaS 或创作者平台。Studio 以 Project / Cue 为工作入口，Play 只承载
> 自有作品目录与私有客户审片。Cloud、Judge、Wavefield、One Core 和 `Generated is not finished`
> 不变。权威边界见 [COMMERCIAL_MUSIC_OPERATING_MODEL.md](COMMERCIAL_MUSIC_OPERATING_MODEL.md)。

> **2026-10-06 Waveform → Wavefield amendment (CANON_CHANGE = YES):** Moodify 的核心技术方向是
> **从波形到波场**。数字文件是声音发生的触发条件；Moodify 将其置入可描述、可重放、可观测、
> 可验证的 Wavefield，再由 Judge 选择目标条件下的佳场。Judge 仍是核心模型，Wavefield 是核心技术
> 对象与处理范式。输出不只是 wav，而是 Wavefield Profile + 条件化 renders + evidence + rollback。
> 单个 mono/stereo 文件只能产生空间投影，不得冒充真实三维声压场。详见
> [WAVEFIELD_CORE_PRINCIPLE.md](WAVEFIELD_CORE_PRINCIPLE.md)。
> 北极星公式为 \(F^\*=\arg\max_F J(\operatorname{Render}(Audio,F))\)；生产实现必须加入身份保护、
> 目标播放条件、跨环境鲁棒性、证据、不确定性、人工权威与 `KEEP_ORIGINAL`，不得把未校准 Judge
> 压成一个可被优化器投机的绝对分数。

> **2026-10-06 Open-theory amendment (CANON_CHANGE = YES):** Moodify 不仅开放代码，也开放理论。
> Technology Notes 公开问题、假设、术语、公式、方法、证据、不确定性、失败条件、版本与修订历史；
> 理论和实现共同接受公共实验、引用、批评与演化。公开不等于把未验证方向写成事实。

> **2026-10-06 HEAR/JUDGE/ACT interaction amendment (CANON_CHANGE = YES):** Moodify 的核心能力链为
> `HEAR → JUDGE → ACT`。当前 Web Studio 的首要体验收敛为“上传音乐 → AI HEAR → AI JUDGE”；
> `ACT` 尚未开放。页面底部是 Moodify AI 模型对话入口，不承担上传或检测动作。该裁决改变公开
> 交互与流程表达，但不改变 One Core、双 Judge、人工升级和 `KEEP_ORIGINAL` 权威边界。

> **2026-10-05 Cloud-first amendment (CANON_CHANGE = YES):** 人类权威将对外首要定位更新为 **Moodify Cloud — Audio Intelligence, powered by GPU computing.** 产品层级为 `GPU Computing → Moodify Cloud → Audio Intelligence → API / Agent / Desktop / App`。本修订覆盖下文中“Sound Protocol 为对外首要身份”的旧表述；Sound Protocol 仍是重要契约层，Core 仍是唯一声音权威，Desktop / App / API / Agent 均是接口。未经运行时验证的云端能力、API、Agent 和第三方集成必须标为方向或逐步可用，不得冒充生产事实。

> **2026-10-06 Judge-core amendment (CANON_CHANGE = YES):** `Moodify Judge` 是 Moodify 的核心模型与长期自有判断权威。每个处理闭环必须包含处理前 Judge（发生了什么、是否需要处理、保护什么）与处理后 Judge（是否改善、接受/重试/调整/保留原版）。分离、降噪、修音、混音、母带、生成模型和 foundation encoder 可以采用可替换 Provider；Moodify 必须拥有 Judge 契约、证据、校准、Treatment Records 与人类升级机制。详见 [JUDGE_CORE_PRINCIPLE.md](JUDGE_CORE_PRINCIPLE.md)。

**Version:** 2.1（Sound Protocol；延续 v2.0 Professional Finishing 与 One Core / Two Interfaces）
**Date:** 2026-09-23
**Authority:** root `AGENTS.md` → `docs/canon/*`
**Supersedes for product identity:** any earlier document that claims Moodify's outward product is "The Ear of AI", that presents Ear as a public product surface, that defines Moodify as **only** a Player with a single `PLAY` action, or that frames AI processing as a black-box one-shot output.
**Related:** [PRODUCT_BOUNDARY.md](PRODUCT_BOUNDARY.md) · [INTERNAL_SYSTEMS.md](INTERNAL_SYSTEMS.md) · [AUTHORITY_ORDER.md](AUTHORITY_ORDER.md) · [CURRENT_ARCHITECTURE.md](CURRENT_ARCHITECTURE.md) · [MOODIFY_PROFESSIONAL_FINISHING_V1.md](../MOODIFY_PROFESSIONAL_FINISHING_V1.md)（目标架构，TARGET）· [Public Brand Authority](../brand/public/README.md) · [Classic Reconstruction Constitution](../CLASSIC_RECONSTRUCTION_CONSTITUTION.md)（内部生产哲学）

---

## 1. External Product（对外产品）

**2026-09-23 协议优先修订：** Moodify 对外首先是 **Sound Protocol**，供 AI / Agent 通过 CLI 提交可校验的声音处理作业。CLI 是首要执行接口；App 保留为播放、预览和人工审听接口。专业完成是协议要服务的生产目标，不再是唯一产品类别名。MSP/0.1 当前只实现预设作业与证据清单；可编辑 Mix Graph 和自动验证仍为目标态，详见 [协议说明](../protocol/MOODIFY_SOUND_PROTOCOL_0_1.md)。下文 v2.0 的双接口结构继续有效，但其产品身份标题由本段覆盖。

> **Moodify — AI-native Professional Audio Finishing System（一个 Core，两个接口）**
>
> **Generated is not finished.（生成 ≠ 完成。）**

```text
             Moodify
          Shared Core
        /                \
Creator Side         Listener Side
Moodify CLI          Moodify App
PROCESS              PLAY
```

- **Moodify CLI = Production Interface**（声音生产端）。核心动作 `PROCESS` = 专业完成流：Import → Analyze → Diagnose → Plan → Process → Verify → Export。改善音乐本身。
- **Moodify App / Player = Listening Interface**（声音消费端）。核心动作 `PLAY`。改善音乐被听见的方式；同时承担完成会话的 Preview / A-B / Review / Delivery。
- **Moodify Core = 共享声音智能**。为二者共同提供 analysis / dsp / processing / playback / profiles / verification / contracts（目标态含 Mix Graph，见下）。

> **Moodify CLI makes music sound better. Moodify App makes music play better. Moodify Core powers both.**
> （中文）CLI 改善音乐本身，App 改善音乐被听见的方式，Core 是二者共同的声音智能。

**PLAY 不删除，而是重新定位：** `PLAY` 保留为 Listener Side（消费端）的核心动作；Creator Side（生产端）核心动作为 `PROCESS`。Player 在产品叙事中不再是唯一中心，而是消费端接口 + 完成会话的 Preview / A-B / Review / Delivery 面。

Public Form 冻结：

- 品牌信念：**每一种声音，都值得被世界听见。 / Every voice deserves to be heard.**
- 产品原则：**Listen. Then Play.**（消费端）
- 生产端命题：**Generated is not finished.**
- 消费端动作：**Play.**；生产端动作：**Process.**
- 研究问题 `Can machines learn to hear?` 属于 Research / internal layer，不承担首屏产品定义。
- 主题权威见 [`docs/brand/public/`](../brand/public/README.md)。

## 2. Internal Systems（内部系统）

Moodify Ear / Auditory Intelligence 是**内部听觉、判断、验证与研究系统**：

- Listen
- Represent
- Judge
- Evidence
- Uncertainty
- Learn

其中 **Judge 是永久核心**：Provider 可以替换，处理前与处理后的 Judge authority 不可外包。
`Moodify Auditory Intelligence` 是能力总称，第一代目标模型为 `Judge-1`；它不是第二个公开产品。
当前实现仍以未充分校准的规则式技术判断为主，不得将目标模型写成已经训练或生产可用。
- Verify
- Controlled Intervention

复杂度由 Moodify 承担，不转嫁给用户。

**Moodify Core** 是跨生产端与消费端的**共享声音智能资产**（不再是「内部 vs 对外」二分的旧对象）：同一套 analysis / dsp / processing / playback / profiles / verification / contracts 同时服务 CLI（生产端）与 App（消费端）。Ear、Cloud Production、Classic Reconstruction 仍为内部系统。Professional Finishing Session / Mix Graph（v0.1 目标态，见 [MOODIFY_PROFESSIONAL_FINISHING_V1.md](../MOODIFY_PROFESSIONAL_FINISHING_V1.md)）属于 Core 生产能力，不是第二个产品身份。

## 3. Canon 不变量

1. **一个产品身份、两个接口**：Moodify = AI-native Professional Audio Finishing System = 共享 Core + 生产端 CLI + 消费端 App/Player。Ear 不成为第二个公开产品面。
2. **PLAY 保留为 Listener Side 核心动作**：消费端一切对外体验围绕播放；生产端 `PROCESS`（Creator Side）承担专业完成流，两者共享同一 Core。Player 不得回升为唯一产品中心。
3. **内部可以复杂**：生产、判断、证据、学习在内部承担。
4. **Canon 不虚构现实**：云端/生产能力以 P00 现实快照与运行时证据为准，未验证不写成已运行。
5. **历史文档不能反向覆盖当前 Canon**（见 [AUTHORITY_ORDER.md](AUTHORITY_ORDER.md)）。
6. **Canon 变更必须可见**：进入 `docs/canon/CHANGELOG.md`（见 [CANON_CHANGELOG.md](CANON_CHANGELOG.md)）。
7. **一个站点一个角色**：`rongjingmusic.com` = Product Home；`rongjingwenchuan.com` = Company Home；`.xyz` = 过渡 Player / 历史入口，目标优先评估 `play.rongjingmusic.com`。
8. **One Core, Multiple Interfaces**：禁止两套声音逻辑；一切声音能力来自 Core（见 AGENTS Technical Constitution）。
9. **Generated is not finished**：对外的处理能力是有决策、可编辑、带证据、可回退的专业完成层；禁止以黑箱一键母带 / 不透明 wav 作为对外产品形态。
10. **Two-Judge invariant**：任何 Provider 产出都不能自证完成；处理前诊断 Judge 与处理后验收 Judge
    均必须存在，并保留 `KEEP_ORIGINAL / HUMAN_REQUIRED / INCONCLUSIVE` 等诚实出口。
11. **Waveform → Wavefield**：Core 的处理对象从孤立 waveform 扩展为 waveform + field target +
    reproduction chain + observations。佳波场必须相对于作品意图、目标条件和人工权威定义。
12. **Mix Graph 为生产中间表示（目标态）**：完成会话的权威表示是可序列化、可重放、可旁路的 Mix Graph + evidence；实现落地前不虚构其运行状态（R6/R10）。
13. **固定流程，不固定参数**：所有处理参数必须具备本轮 Judge 证据、保护目标与作用时间范围；历史参数
    只提供先验，不自动继承为答案。每轮单挑战者与当前基准盲比，不能证明改善就不替换基准；默认一次
    只改变一个可归因问题或局部范围，避免多个未验证处理同时进入作品。
14. **人声身份优先保护**：AI 音乐中默认将人声视为高身份密度资产；修改人声需要人声轨自身证据，
    不能由 `V−A`、遮蔽或其他相对比值单独触发。若异常由伴奏侧驱动，先处理伴奏；明确的人声缺陷
    才进入局部人声修复，并保留音色、咬字、气息、滑音、颤音、微时值与情绪动态。

## 4. Canon Change Rule

任何改变以下内容的任务必须声明 `CANON_CHANGE = YES` 并说明 why / evidence / affected authority files / migration / rollback：

- 对外产品身份
- 内部/外部能力边界
- state machine authority
- evidence authority
- cloud control authority
- data authority

普通功能任务不得静默修改 Canon。

## 5. 本 Canon 与既有宪法

- **Classic Reconstruction Constitution v1.0**（P02，人类批准）保留为**内部生产哲学与工程权威**：Reconstruct 是云端生产系统内部环节（Intake → … → Render → Delivery）。
- 其 Article I 的对外产品表述（"reconstruction-first listening environment" 作为公开身份）已被本 Canon 覆盖：对外身份 = AI-native Professional Audio Finishing System（一个 Core，两个接口）。
- 宪法正文是否更新文本 → `HUMAN_DECISION_REQUIRED`（见 W01-P01 Decision Register CD-014）。

## 6. 现实边界（引用 P00，不虚构）

- 云端现状：2 台 VPS（LA 核心 + 杭州数据工厂）+ PolarDB（BLOCKED 核验）+ 无对象存储 + 无 AI 推理 + 队列近空。
- 完整 Listen→Judge→Intervene→Verify 链路存在于仓库代码，云端尚无生产流量。
- 详见 [CURRENT_ARCHITECTURE.md](CURRENT_ARCHITECTURE.md) 与 [docs/evidence/](../evidence/README.md)（W01-P00 报告）。
