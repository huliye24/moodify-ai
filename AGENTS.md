# AGENTS.md — Moodify Repository Authority

This file defines the canonical context for AI coding agents working in this repository.

## Product Identity

**Phase-one business definition (2026-10-08 human decision, CANON_CHANGE = YES):** Moodify 是
荣景文川内部的 AI 商用音乐生产系统。当前外部网剧等 B2B 客户购买音乐与制作服务，不直接使用
Moodify；不以通用 C 端、外部 Studio SaaS、UGC、社交或 Marketplace 为当前产品目标。Studio 以
Project / Cue 组织内部生产；Play 只展示荣景文川控制的作品，并承载显式创建的私有客户审片。
Cloud-first、Judge 核心、Wavefield、One Core、Protocol 与 `Generated is not finished` 均保持不变。
详细边界见 `docs/canon/COMMERCIAL_MUSIC_OPERATING_MODEL.md`。

**Phase-one operator and website boundary (2026-10-08 human correction, CANON_CHANGE = YES):**
当前官网主要是内部观察、研究出版、实验图像、作品与能力状态入口，不承担接单转化；获客与交易发生在
小红书、抖音、淘宝等外部渠道。不得因 B2B 业务方向把官网重写成销售落地页或删除研究/实验结构。
Moodify Studio 的当前用户是内部受训操作员，因此允许专业复杂度与细分功能；设计目标从“降低首次学习
成本”调整为“提高生产吞吐、控制精度、批量能力、可归因、可复现与交付可靠性”。复杂度必须服务真实
工序，不得形成第二套 Core、状态机或判断权威。

**External product (2026-10-05 human decision):** **Moodify Cloud — Audio Intelligence, powered by GPU computing.** Cloud 是载体，Audio Intelligence 是产品能力层，API / Agent / Desktop / App 是入口。Sound Protocol、Core、Studio 与 App 继续作为同一 Moodify 产品的协议、能力与接口，不得拆成第二个公开产品身份。协议 v0.1 的实际边界见 `docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md`。

**产品命题（Product thesis）：Generated is not finished.（生成 ≠ 完成。）**

**核心技术方向（2026-10-06 human decision，CANON_CHANGE = YES）：从波形到波场。** 数字音频是
触发声音发生的条件，不是声音发生本身。Moodify 的 HEAR / JUDGE / ACT 必须逐步从只观察和修改
waveform，迁移为构建、观测、选择和验证 wavefield；权威边界见
`docs/canon/WAVEFIELD_CORE_PRINCIPLE.md`。Judge 仍是核心模型，Wavefield 是核心技术对象与处理范式。
单个立体声文件不得被表述为真实三维声压场；真实空间结论必须来自校准的播放与采集链。

**首要使用动作（2026-10-06 human decision，CANON_CHANGE = YES）：** Moodify 的核心能力链为
`HEAR → JUDGE → ACT`。当前 Web Studio 首先完成两个用户动作：**上传音乐**，随后由 Moodify
执行 **HEAR + JUDGE**；`ACT` 暂不开放，不得用未实现的处理能力占位。底部对话框是连接模型的
Moodify AI 对话入口，不是上传或“检测”按钮。旧的多阶段侧栏不得继续充当当前首屏信息架构。

**核心模型原则（2026-10-06 human decision，CANON_CHANGE = YES）：**

> **Moodify Judge = Moodify 的核心模型。**
>
> **We don't need to own every audio model. We need to own the judgment.**

Moodify 必须拥有处理前与处理后的两次 Judge：先判断声音发生了什么、是否需要处理、什么必须保护；
再判断处理结果是否真正改善、是否应接受、重试、调整或保留原版。分离、降噪、修音、混音、母带、
生成模型与 foundation encoder 均可先采用第三方/开源/可替换 Provider；Provider 是 Hands，Judge 是
Ear + Brain。`Moodify Auditory Intelligence` 是长期核心资产总称，第一代目标模型名为 `Judge-1`。
Judge 仍属于唯一 Moodify Core，不构成第二个公开产品身份。完整边界见
`docs/canon/JUDGE_CORE_PRINCIPLE.md`。

**生产参数原则（2026-10-11 human decision，CANON_CHANGE = YES）：固定流程，不固定参数。**
每首歌、每次迭代都必须重新 `HEAR → JUDGE → ACT → VERIFY → BLIND COMPARE`。调音、降噪、混音、
母带参数由该次输入、分轨、时间段、问题证据、作品意图与 `preserve` 约束生成；固定参数、预设和历史
工艺卡只能作为安全边界、未校准初始化值或搜索起点，不能作为“更好”的答案。每轮只生成一个新的
**挑战者**，与当前基准在统一编码和严格响度匹配后随机匿名为 A/B；A/B 是盲测槽位，不再表示同时
生成的保守/激进两套参数。Judge 输出必须定位改善与损害、置信度和下一动作；无法证明净收益时保留
当前基准。默认采用**最小可归因干预**：一轮只修一个有证据的问题或一个边界清楚的局部范围；该轮
挑战者通过复检与盲比后才晋升为新的当前基准，否则撤回或局部重试，不把未验证改动继续叠加。
所有输入状态、判断、Mix Graph、参数、局部变化、验证、匿名选择和失败原因进入可治理的
Treatment Record，作为未来 Judge 校准的数据资产。详见 `docs/canon/JUDGE_CORE_PRINCIPLE.md` 与
`docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md` 的 2026-10-11 修订。

**人声身份保护原则（2026-10-12 human decision，CANON_CHANGE = YES）：Voice is identity;
accompaniment is adaptable.** 对 AI 音乐生产，Moodify 默认把人声视为更高身份密度、更难无损重建的
资产；音色、咬字、气息、滑音、颤音、微时值与情绪动态进入 `preserve`。这不是“永不修改人声”的
绝对规则：有明确生成缺陷时仍可局部修复，但修改人声的证据门槛高于修改伴奏。当人声本身正常而在
混合中被遮蔽时，优先让伴奏通过电平、编配、动态 EQ 或空间关系让位，而不是先抬高、压缩、增亮或
重写人声。`V−A` 等相对比值只能定位关系变化，必须拆分人声侧与伴奏侧贡献后才能触发处理动作；
比值异常不得直接等同于人声异常。详见 `docs/canon/JUDGE_CORE_PRINCIPLE.md` 与
`docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md`。

**公共项目原则（Public project principle）：Fork the code. Join the process.（代码可以复制，过程需要参与。）** Moodify 采用开源 + 免费 + 公共协作路线，不把「别人看不到我们的代码」当作壁垒。**代码开源，理论同样开源**：公开问题、假设、定义、公式、方法、证据边界、失败条件与修订历史；理论文档与代码共同进入公共演化过程。代码和理论都可以被复制，产品可以被逆向；真正需要保护的是 continuity、standards、review quality、release trust、history、network density。目标不是「只有我们能更新 Moodify」，而是「任何人都可以改进 Moodify，且改进能够重新进入公共演化过程」。

```text
             Moodify
          Shared Core
        /                \
Creator Side         Listener Side
Moodify CLI          Moodify App
PROCESS              PLAY
```

- **Moodify CLI** — Production Interface（声音生产端，Creator Side）。核心动作 `PROCESS`。专业完成流：Import → Analyze → Diagnose → Plan → Process → Verify → Export。
- **Moodify App / Player** — Listening Interface（声音消费端，Listener Side）。核心动作 `PLAY`；同时承担完成会话的 Preview / A-B / Review / Delivery。
- **Moodify Core** — 二者共享的声音智能（analysis / dsp / processing / playback / profiles / verification / contracts）。

> **Moodify CLI makes music sound better. Moodify App makes music play better. Moodify Core powers both.**
> （中文）CLI 改善音乐本身，App 改善音乐被听见的方式，Core 是二者共同的声音智能。

**Internal systems:**

- Moodify Ear / Auditory Intelligence — 内部听觉、判断、验证与研究系统
- Cloud Production System — Intake → Analyze → Stem → Judge → Intervene → Render → Verify → Evidence
- Classic Reconstruction — 内部生产哲学（宪法 v1.0，决策驱动受控重建）

Ear 是 Moodify 的内部听觉智力，不是对外产品面。Do not regress the repository identity back to "The Ear of AI" as a public product, or to a **black-box** "AI music post-processing / automatic mastering / preset" product that emits an opaque wav without a Mix Graph, evidence, or human review. Professional Finishing（Canon v2.0）是有决策、可编辑、带证据、可回退的完成层——这与被禁止的黑箱后处理是两个东西。Do not create a second public product identity alongside Moodify（one Core, two interfaces）.

## Canon Reference

进入本仓库先读：

1. `AGENTS.md`（本文件）
2. `docs/canon/CURRENT_CANON.md`
3. `docs/canon/PRODUCT_BOUNDARY.md`
4. `docs/canon/AUTHORITY_ORDER.md`
5. `docs/REPOSITORY_STATUS.md`

Public brand language and public-site roles then resolve through `docs/brand/public/README.md` and its authority set. The highest topic-specific Public Brand authority is `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md`.

内部系统权威与既有政策见 `docs/canon/INTERNAL_SYSTEMS.md`、`docs/LEGACY_AND_EXPERIMENTAL_POLICY.md`。

## Network, Governance and Proposals

Moodify 的长期资产不是代码（任何人都可以 fork），而是持续产生下一版的过程：

```text
Moodify Moat ≠ Code
Moodify Moat = Process × History × Network
```

- `GOVERNANCE.md` — Network 定义、角色与权限（Stewards / Maintainers / Working Groups / Contributors / Review Network / AI Agents）、MIP 流程、发布权限、安全流程、冲突解决。
- `MAINTAINERS.md` — 当前角色持有者。多数为 vacant，如实记录，不虚构社区。
- `docs/governance/NETWORK.md` — 过程循环：Problem → Proposal → Experiment → Evidence → Human Review → Merge → Release → Feedback。
- `protocol/mips/` — MIP 模板与流程。改变 protocol / schema / core behavior contract / governance / evidence format / public compatibility 需要 MIP；普通 bug fix 不需要。
- `docs/governance/constraints/` — 工程约束 ME-001…ME-003（起源先于功能 / 证据门控发展 / 整体一致性）。

**NO TOKEN / NO DAO / NO AIRDROP / NO TREASURY GOVERNANCE。** 先建立有效的 contribution、review、evidence、release、governance，再讨论其他经济机制。

历史说明：本仓库曾承载一条**独立的** MOOD Protocol Web3 线（EVM/BSC 主网 BEP-20 代币，已部署合约并有 DEX 交易）。2026-10-03 该线被移出主线，磁盘保留、不再跟踪，见 `docs/ARCHIVE_INDEX.md`。它不是 Moodify Network，两者的历史都不得被静默改写。

## Product Direction（Product Canon v3，2026-10-03）

**Moodify 是一个产品的五层**，不是五个独立产品：

```text
Moodify = Core + Protocol + Studio + App + Network

Core     声音能力        →  moodify-core-package/
Protocol 契约层          →  protocol/ + docs/protocol/
Studio   Creator 工作台  →  moodify-desktop/
App      个人音乐节点     →  见 §6 现状（未实现的部分不得写成已实现）
Network  个人音乐节点之间的连接  →  未实现；V1 仅指 Desktop ↔ 个人手机
```

完整定义见 `docs/canon/PRODUCT_DEFINITION_V3.md`；技术选型规则见 `docs/canon/TECHNOLOGY_PRINCIPLES.md`。

**Agent 必须理解以下五条：**

1. **第一个产品目标是 `Studio → My Phone → Play`。** 即：在桌面完成一首歌 → Publish to My Library → 歌出现在手机 → 立刻能听。这个循环可靠工作，Moodify 就已经是有效产品。完整循环见 `PRODUCT_DEFINITION_V3.md` §3。
2. **Moodify App 是 Personal Music Node（个人音乐节点）**，初期不是另一个流媒体平台。四项职责 My Library / Playback / My Identity / Connections；**最早版本只做前两项**。
3. **Network 功能必须从真实用户循环生长**，不得先建网络再找用途。V1 的「网络」只有两个节点：Desktop ↔ 个人手机。
4. **优先稳定、通用的技术**：`existing > standard library > mature OSS > commodity service > custom > experimental`。举证责任在 custom 与 experimental。（产品战略：可商用 > 技术先进。）
5. **AI 不得自行扩大范围。** 未获人类批准，不得新增 server / login / social / account / cloud storage / P2P / 新框架；不得删除遗留 Android 项目；不得重写 Core 或 desktop。范围扩张需人类批准或走 MIP。
6. **生产流程：先理解，再分解，再修音，再复合，最后复检。**（`Understand first. Decompose second. Tune third. Compose fourth. Verify fifth.`）
   Creator 侧流程固定为 **检测 → 逆向分解 → 结构 → 修音 → 复合 → 复检 → 选定 → 导出**。
   **产品方向（2026-10-04 采纳）：逆向工程 → 多轨复合。** AI 音乐是单轨直出，单轨直出不如多轨复合；
   先逆向分解成多轨、逐轨修音、再复合——**多轨复合才是 AI 后处理的核心操作**。
   该方向的前提（「多轨复合一定优于单轨直出」）**是假设而非事实**，因此由两道机制关住风险：
   - **可逆性门禁**：分解 → 复合（不处理）必须回到原版（`<case>/studio/roundtrip.json`，仅
     `passed === true` 才算通过）。**门禁不通过，④修音不开**，也不得自行推断一个通过。
     这是分解质量的唯一可测代理——原分轨不可知（AI 音乐无原轨客体），"还原得对不对"无法回答。
   - **基准出口**：每轮在“当前基准 / 单个新挑战者”之间选择；净增益为负、证据不足或结论不确定时
     保留当前基准。第一轮的当前基准通常是原版，后续也可以是已接受版本。
   **②「问题」不是独立阶段**（2026-10-04 裁定）：Core `report.json` 的 `findings` 仍在 ①检测 里可见，
   但不得单设阶段或页面；`issues: []` 只能说「当前规则未发现技术问题」，**不得**说「这首歌没问题」——
   这条诚实要求由 ①检测 承接，不随 ② 的退场而消失。
   **④修音与⑤复合必须分开**：修音改每根轨（音准·节奏·逐轨处理），复合决定它们如何叠在一起
   （平衡·空间·响度）。合并就无法归因「这一步变差是哪一层造成的」，而可归因是硬要求。
   **三个预设（`clean_master`/`warm_vocal`/`wide_space`）已退场**（2026-10-04 裁定），
   不得作为产品面、流程起点或「成品」工具重新引入。
   阶段由磁盘产物推导（`moodify-desktop/src/pipeline.js`），未满足前置的阶段不得进入；
   成就判定**用聚合**，开启新迭代不得让已经完成的历史迭代倒退。
   **分解先于修音：④ 修音在 分轨 + MIDI + 可逆性通过 齐备前保持锁定**（曲谱/MusicXML 不能替代 MIDI）。
   **每轮只生成一个挑战者**：先由 Judge Before 判断问题与保护目标，再由 Planner/AI 生成该曲、该轮
   专属参数；不得固定产出“保守 / 激进”两套预设。挑战者必须完整包含本轮涉及的逐轨产物与复合结果。
   **⑥ 复检**：对挑战者重跑完整检测，与当前基准逐指标对齐；缺项只能进 `not_alignable`，**不得补算**，
   **不得发明测量事实**。**绝不** `AI 处理 → 自动完成`；`Generated is not finished.` 不变。
   **盲测**：当前基准与挑战者先统一编码、严格响度匹配，再随机匿名为 A/B；Judge 不得接收来源身份、
   插件或参数提示。**⑦ 选定**将“接受挑战者 / 保留当前基准 / 局部重试”逐步落账
   `<case>/studio/tuning/decisions.jsonl`（只追加、不可修改、带 request_id 幂等）。
   **跳过分解的「快速完成（仅立体声）」必须由人显式选择**
   （记为 `<case>/studio/finish_mode.json`，带 `chosen_at`），**绝不自动解锁**——否则捷径会变成默认路径；
   其处理引擎是**对整轨生成一个挑战者**（无 MIDI → 只做混音处理，不做音准·节奏修正），
   **不得**打开需要分轨的 ④ 修音；但它**仍然必须走 ⑤复合 → ⑥复检 → ⑦选定 才能导出**
   （跳过的是分解，不是验证）。模式徽章必须显示 `深度完成` / `快速（仅立体声）`。
   `preserve`（该保护什么）是听觉判断，挂在 ④ 修音 的输入侧，默认留空由人填。
   **参数不是标准答案**：产物必须记录 Judge/Planner 版本、完整参数、证据与 `calibration_status`；
   未校准时为 `UNCALIBRATED_ENGINEERING_DEFAULT`，不得被读成“更好的设置”。
   Core 的逐轨修音 / 复合 / 可逆性验证能力未就绪时，壳必须显式拒绝（`TUNABLE_CORE_NOT_AVAILABLE`），
   **不得留假产物**。
   参见 `docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md`。

**仍未裁决（不得当作已定论）：** `apps/android` 与 `apps/music-android` 哪一个是 canonical App；Creator 侧首要产品面是 CLI 还是 Studio。两者均记录为 `HUMAN_DECISION_REQUIRED`。

## Repository Structure Guard

`scripts/check_repo_structure.py` 在 CI 中执行，防止历史问题复发。它禁止：

- 重建 `web 3.0/`、`moodify-qa/`、`moodify-pulse/`、`windows版本开发/`、`审查包/`、`products/`、`shared/`、`sdk/`、`engine/`、`demo/`；
- 顶层中文临时任务目录；
- generated artifacts 进入 Git；
- 第二个 `moodify` console entry point；
- 第二套 Core。

**新增任何非 `.py` 文件前先执行 `git check-ignore -v <path>`** —— 本仓库的 `.gitignore` 含大量宽泛模式（`*.png`、`*.html`、`*.wav` 等）与 `!` 白名单例外，已四次静默吞掉新文件。

## Important Distinction

- 对外：Moodify = AI-native Professional Audio Finishing System，一个 Core、两个接口——CLI（生产端，核心动作 `PROCESS` = 专业完成流）/ App（消费端，核心动作 `PLAY`，兼 Preview / A-B / Review / Delivery）。
- 内部：Ear / analysis / stem / judgment / intervention / preset decision / verification / evidence / learning / cloud production。复杂度由 Moodify 承担。
- 内部处理复杂度不是对外卖点。
- Public Form 品牌信念：**每一种声音，都值得被世界听见。 / Every voice deserves to be heard.**
- 产品原则：**Listen. Then Play.**（消费端）；生产端命题：**Generated is not finished.**；消费端动作：**Play.**；生产端动作：**Process.**

## Technical Constitution — One Core, Multiple Interfaces

**最高工程约束（技术宪法级）：一个 Core，多个 Interface。** 禁止出现两套声音逻辑（`CLI DSP Engine` vs `App DSP Engine`）。

- 以下能力**全部来自 Core**，任何 interface 不得私藏一份：audio analysis、DSP primitives、EQ、dynamics、loudness、stereo、spatial、processing、playback、playback profile、device adaptation、validation、verification、identity preservation、shared contracts。
- 依赖方向严格单向：`moodify-core → moodify-cli / moodify-app`。
- 禁止 GUI-only core capability：任何真正影响声音结果的 App 能力，必须能通过 Core API 被其他 interface 调用。
- 跨端一致性：同一版本 Core + 同一输入 + 同一 profile，CLI 与 App 结果需有一致性保证；分三级 `bit-exact / numerical-equivalent / perceptual-equivalent`，不盲目承诺 bit-perfect（以 runtime 实测为准）。
- **Judge authority 单一：** 处理前 Judge 与处理后 Judge 的任务定义、契约、证据、版本、校准与
  人类升级规则只能有一套权威实现。Provider 可替换，但不得各自携带一套互相冲突的“质量判断”。

## Governance Principle — Human Direction / Machine Execution

**AI is an executor of capability, not the authority of product direction.**
（AI 拥有能力执行权，人类保留产品定义权。）

**人类主权（HUMAN AUTHORITY，不可下放）：** Moodify 是什么/不是什么、产品边界、Creator/Listener 定位、什么叫"更好听"、哪些声音特征必须保护、哪些处理被允许、商业模式、用户定义、对外身份、核心资产边界、重大技术路线、是否进入新产品线。

**AI 执行权（可自主）：** implementation、refactor、tests、CLI 实现、schema 实现、性能、bug 修复、文档同步、参数搜索、CI、迁移机制。

任何可能改变产品哲学的工程决策 → 写 `HUMAN_DECISION_REQUIRED`，不得自行裁决。

## Three Disciplines

- **WSE — Wave-Spectral Evolution**: what happened in the sound?
- **MSE — Musical-Structural Engineering**: what is the musical structure?
- **PPE — Production Process Engineering**: how is the result produced, verified and recovered reliably?

## Asset Loop

```text
Production Case
  -> Measurement Record
  -> Evidence Artifact
  -> Theory Update
  -> Rule Update
  -> Next Production Case
```

## Authority Order

When instructions conflict, prefer:

1. current explicit human instruction;
2. root `AGENTS.md`;
3. `docs/canon/*`（CURRENT_CANON / PRODUCT_BOUNDARY / INTERNAL_SYSTEMS / AUTHORITY_ORDER / CURRENT_ARCHITECTURE）;
4. verified runtime evidence（[docs/evidence/](docs/evidence/README.md) W01-P00 Evidence Index 等）;
5. canonical main behavior and tests;
6. current subsystem documentation;
7. experimental documentation;
8. historical / legacy documentation.

Historical documents do not override current Canon. A LEGACY / HISTORICAL document cannot promote itself back to Canon through its own text.

## Agent Rules

- 不创建第二个公开产品身份（Ear 不得再次升级为公开产品）。
- 不创建第二套 authoritative state machine。
- 不创建第二套 Job authority。
- 不创建第二套 Core / 第二套 DSP authority（One Core, Multiple Interfaces）。
- 不把 Player 恢复为唯一产品中心（Player 是 Listener Side 接口 + Preview / A-B / Review / Delivery，不是产品命题本身）。
- 不把 Professional Finishing 退化为黑箱一键处理：完成会话的产出必须携带 Mix Graph / 参数 / 证据 / 可回退路径（目标态见 `docs/MOODIFY_PROFESSIONAL_FINISHING_V1.md`；该文档为 TARGET，不代表已实现）。
- 不以"功能很多"作为产品价值。
- 不把内部处理复杂度暴露给用户作为卖点。
- 不因文档冲突而自行做产品哲学决策——写 `HUMAN_DECISION_REQUIRED`。
- 不把历史文档当作当前 authority。
- 不虚构云端/生产能力：未验证不写成已运行（Canon 与事实分离，R6/R10）。

## Canon Change Rule

改变以下任何内容的任务必须声明 `CANON_CHANGE = YES`，并说明 why / evidence / affected authority files / migration / rollback：

- 对外产品身份
- 内部/外部能力边界
- state machine authority
- evidence authority
- cloud control authority
- data authority

普通功能任务不能静默修改 Canon。变更记录进入 `docs/canon/CANON_CHANGELOG.md`。

## Change Discipline

Before coding:

1. identify the canonical subsystem;
2. identify whether the change is canonical, experimental or legacy;
3. inspect existing tests;
4. preserve evidence and reproducibility.

Do not:

- mass-delete legacy code without an explicit cleanup task;
- merge stale branches wholesale;
- add duplicate orchestration systems;
- introduce a second authoritative state machine;
- claim experimental metrics are validated production truth;
- remove human authority where the system still depends on listening judgment;
- introduce secrets, private audio or generated heavy artifacts.

## Judgment Authority

Moodify uses **scoped machine authority with explicit human escalation**:

- a machine may decide only inside a validated, versioned and explicitly authorized scope;
- an out-of-scope, insufficient-evidence, uncertain or unresolved perceptual case must produce
  `HUMAN_REQUIRED`, `INCONCLUSIVE` or a defined failure state;
- automation must not suppress escalation merely to keep the loop unattended;
- a human decision must record its reviewer, scope, time and supporting evidence.

## Definition of Done

A code change is not complete merely because it runs.

It should answer:

- What case does this serve?
- What is measured?
- What evidence is produced?
- How is the result verified?
- What happens on failure?
- Is the result reusable in the next case?
