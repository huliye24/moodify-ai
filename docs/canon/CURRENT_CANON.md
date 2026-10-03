# CURRENT CANON — Moodify

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
10. **Mix Graph 为生产中间表示（目标态）**：完成会话的权威表示是可序列化、可重放、可旁路的 Mix Graph + evidence；实现落地前不虚构其运行状态（R6/R10）。

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
- 详见 [CURRENT_ARCHITECTURE.md](CURRENT_ARCHITECTURE.md) 与 W01-P00 报告。
