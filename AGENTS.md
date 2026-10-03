# AGENTS.md — Moodify Repository Authority

This file defines the canonical context for AI coding agents working in this repository.

## Product Identity

**External product:** Moodify Sound Protocol — AI / Agent 可通过 CLI 调用的声音处理协议；一个共享 Core，CLI 为首要执行接口，App 为播放/审听接口。协议 v0.1 的实际边界见 `docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md`。

**产品命题（Product thesis）：Generated is not finished.（生成 ≠ 完成。）**

**公共项目原则（Public project principle）：Fork the code. Join the process.（代码可以复制，过程需要参与。）** Moodify 采用开源 + 免费 + 公共协作路线，不把「别人看不到我们的代码」当作壁垒。代码可以被复制，产品可以被逆向；真正需要保护的是 continuity、standards、review quality、release trust、history、network density。目标不是「只有我们能更新 Moodify」，而是「任何人都可以改进 Moodify，且改进能够重新进入公共演化过程」。

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
6. **生产流程：先理解，再分解，最后处理。**（`Understand first. Decompose second. Process last.`）
   Creator 侧流程固定为 **检测 → 问题 → 分轨 → 结构 → 方案 → 成品**。
   **三个预设（`clean_master`/`warm_vocal`/`wide_space`）是成品阶段的工具，不是流程的起点**——
   不得把它们放回「分析完立刻处理」的位置。阶段由磁盘产物推导（`moodify-desktop/src/pipeline.js`），
   未满足前置的阶段不得进入。跳过分离/结构的快速路径必须显式标注 `快速（仅立体声）`。
   诊断严格是 Core `report.json` 的投影：**不得发明测量事实**；
   `issues: []` 只能说「当前规则未发现技术问题」，**不得**说「这首歌没问题」。
   `preserve`（该保护什么）是听觉判断，默认留空由人填。
   参见 `docs/canon/STUDIO_PRODUCTION_PIPELINE_V3.md`。

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
