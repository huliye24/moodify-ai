# CANON_CHANGELOG — Moodify

> 所有产品身份、authority order、内部/外部边界变化必须记录于此（R7）。

## 2026-10-02 — MSP/0.2 compare 作业与 L2 对比层（Layer B，CANON_CHANGE = NO）

- **CANON_CHANGE = NO。** 仍是 v2.1 Sound Protocol 边界内的协议能力新增（设计提案 §6 Layer B 承诺边界），不改产品身份、authority order、One Core 规则；记录于此因新增协议语义与 CLI 表面（R7 可见性）。
- **Why / evidence：** 2026-10-02 人类指令「继续」Layer B（比较层）；仓库已有 `auditory/comparison.py` 的 validate_pair/compute_deltas/Δ 频谱图机器（AS-001），Layer B 只做协议化，不新增 DSP、不新增阈值。
- **Boundary：** compare 作业 = analyze×2（同一扫描剖面）+ 配对校验（profile 哈希/时长 ±50ms/声道，fail-closed）+ 响度对齐 delta（gain-to-before-LUFS）。`judgment_boundary.layer2_comparison` 仅 compare 报告为 EXECUTED；**delta 只描述、不评级**（显著性阈值属 Layer C 校准，`visibility_note` 写入报告本体）。schema 双向强制：analyze 报告不得携带 comparison，compare 报告必须携带。同 case 的 `validate_pair` 语义不变。
- **Affected authority files：** `docs/protocol/MOODIFY_SOUND_PROTOCOL_0_2.md`、`docs/REPOSITORY_STATUS.md`。代码面：`sound_protocol.py`（compare 校验/执行）、`protocol_report.py`（comparison section + build_compare_report + write_compare_bundle）、`report_render.py`（L2 md/html 渲染 + contact-sheet）、`comparison.py`（validate_compare_pair）。
- **Migration：** 无破坏性变更；analyze/process 作业行为不变，report schema 仍为 EXPERIMENTAL 未冻结态下的 0.2 修订。
- **Rollback：** 回退上述四个代码文件的 compare 支面即可；analyze 链路与既有 case/compare 证据包不受影响。

## 2026-10-02 — MSP/0.2 analyze 作业与报告三件套（Layer A，CANON_CHANGE = NO）

- **CANON_CHANGE = NO。** 本条是在 v2.1 Sound Protocol 边界内的协议能力新增，不改产品身份、不改 authority order、不改 One Core 规则；记录于此是因为它新增了对外的协议文档与 CLI 表面（R7 可见性）。
- **Why / evidence：** 2026-10-02 人类指令「把 moodify 核心做出来」并批准设计提案 D1–D5（`docs/plan/2026-10-02_MSP02_ANALYSIS_JOB_AND_DISPLAY_DESIGN.md`）；仓库已有 `release.analyze_to_case`、BS.1770 指标链与判定阈值表，0.2 只是把已有 Core 能力协议化，不新增 DSP。
- **Boundary：** analyze 作业为纯读取分析；报告永远不含单一总分；`judgment_boundary` 机器可读（L1 EXECUTED，L2–L5 NOT_PROMISED）；`plan.status` 恒为 `DRAFT_PLAN_NOT_EXECUTED`，只映射保守可逆算子（true-peak 余量不足 → limiter 草案节点），clipping 明确不可自动修复、只出 note。`analyzed_review_required` 不得当作 `verified`。协议/报告 schema 停留在 EXPERIMENTAL，冻结门 = 三首试点曲金色证据包 + 确定性重放证明。
- **Affected authority files：** `docs/REPOSITORY_STATUS.md`；新增 `docs/protocol/MOODIFY_SOUND_PROTOCOL_0_2.md`。代码面：`sound_protocol.py`（0.2 分发）、`auditory/protocol_report.py`、`auditory/report_render.py`、`release_cli.py`（`protocol process` 0.2 / `report` / `analyze --format summary`）。
- **Migration：** v0.1 作业行为逐字节不变；0.2 新增 `type` 字段（analyze/process），未知键 fail-closed。运行时新增 ffmpeg 依赖声明（解码路径，已在 0.2 协议文档与能力表声明）。
- **Rollback：** 回退 `sound_protocol.py` 0.2 分发与 `release_cli.py` report/analyze-format 支面，删除 `auditory/protocol_report.py`、`auditory/report_render.py`、0.2 协议文档与本条；v0.1 链路与既有 case bundle 不受影响。

## 2026-09-23 — Sound Protocol（v2.1）

- **CANON_CHANGE = YES。** 用户明确要求项目改为声音协议，让 AI / Agent 通过 CLI 调用并处理声音。
- **Why / evidence：** 2026-09-23 人类直接指令；仓库已有 `moodify-core-package`、`v01_pipeline.process_audio` 和 `moodify` CLI 入口，可在同一 Core 上建立协议执行层。
- **Boundary：** CLI 成为首要协议执行接口；App 留作播放/审听接口；不新增第二 DSP Core。MSP/0.1 仅是显式预设处理和执行证据，不声称 Mix Graph、自动质量验收或云端服务已完成。
- **Affected authority files：** `AGENTS.md`、`README.md`、`docs/canon/CURRENT_CANON.md`、`docs/canon/PRODUCT_BOUNDARY.md`、`docs/REPOSITORY_STATUS.md`、本文件；新增 `docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md`。
- **Migration：** 保留既有 `analyze`、`show`、`local-analyze`、`cache` 与 App；新增 `moodify protocol validate|process`。旧 v2.0 双接口文字作为历史背景，但产品身份由 v2.1 覆盖。
- **Rollback：** 移除协议命令和 `sound_protocol.py`，回退本条与上述定位文档至 v2.0；既有 Core 与 App 不受影响。

## 2026-09-20 — Professional Finishing（v2.0）

- **CANON_CHANGE = YES。** 人类已明确产品方向（2026-09-20 指令）：Moodify 不再把 Player 当核心产品，转为 AI 音乐与发行之间的专业完成层。AI 仅执行落地，不重写产品哲学。
- **Why：** 在 v1.2「One Core / Two Interfaces」结构上收敛产品命题：**Generated is not finished.（生成 ≠ 完成。）** 对外身份升级为 **AI-native Professional Audio Finishing System**；生产端 CLI 的 `PROCESS` 落为专业完成流 Import → Analyze → Diagnose → Plan → Process → Verify → Export；Player 重新定位为消费端接口 + 完成会话的 Preview / A-B / Review / Delivery，不再回升为唯一产品中心。
- **产品定义：** 完成会话的权威表示（目标态）是 **Mix Graph**——可序列化、可重放、可旁路、带证据、可回退；产出不是黑箱 wav。被禁止的是黑箱后处理 / 一键母带，不是有决策、可编辑、带证据的专业完成层。
- **Boundary：** 不推翻 PLAY；不删除任何 legacy；Ear 仍为内部系统；One Core, Multiple Interfaces 技术宪法不变；Public Form 品牌信念（每一种声音，都值得被世界听见 / Listen. Then Play.）不变。
- **Evidence：** 人类 2026-09-20 明确指令 + 外部参考研究（[PROFESSIONAL_FINISHING_REFERENCE_MAP_20260920.md](../research/PROFESSIONAL_FINISHING_REFERENCE_MAP_20260920.md)：dasp-pytorch / DeepAFx / pedalboard / matchering / audio-separator 等）+ 仓库现有资产（engine 分析、controlled DSP、evidence 体系、data factory、worker）。
- **Affected authority files：** `AGENTS.md`、`README.md`、`docs/canon/CURRENT_CANON.md`、`docs/canon/PRODUCT_BOUNDARY.md`、`docs/canon/INTERNAL_SYSTEMS.md`、`docs/canon/AUTHORITY_ORDER.md`、`docs/REPOSITORY_STATUS.md`、`scripts/canon_guard.py`、本 changelog；新增 `docs/MOODIFY_PROFESSIONAL_FINISHING_V1.md`、`docs/research/PROFESSIONAL_FINISHING_REFERENCE_MAP_20260920.md`。
- **Migration：** 下一工程包 = Mix Graph v0.1 第一条完整 Stereo Finishing Session（Source → Analyze → EQ → Compressor → Stereo → Limiter → Verify → Export，可序列化 / 可重放 / 可旁路 / 可测试）；未实现前所有文档只写 TARGET，不写 runtime truth（R6/R10）。
- **Rollback：** 回退本条及受影响文件到 Commit A（`c2223dff`，Canon v1.2）即可恢复。

## 2026-09-17 — One Core / Two Interfaces（v1.2）

- **CANON_CHANGE = YES。** 人类已完成产品判断，AI 仅执行落地，不重写产品哲学。
- **Why：** Moodify 从「以 Player / PLAY 为单一公开中心」扩展为「One Core + Production Interface（CLI）+ Listening Interface（App）」。PLAY 保留为 Listener Side 核心动作，新增 Creator Side（CLI，核心动作 PROCESS）。Moodify Core 成为共享核心资产。
- **产品定义：** Moodify CLI makes music sound better；Moodify App makes music play better；Moodify Core powers both。
- **Boundary：** 不推翻 PLAY；不删除任何 legacy；不加第二套 DSP / Core 权威（One Core, Multiple Interfaces 提升为技术宪法级约束）。
- **Evidence：** 人类 2026-09-17 明确指令 + `CURRENT_STATE_AUDIT.md`（仓库现实：engine=PHASE_B_T0_5 facade、demo CLI 仅 analyze、core/playback 与 profiles 为全新 MISSING、data_plane/delivery 仅为交付层）。
- **Affected authority files：** `AGENTS.md`、`docs/canon/CURRENT_CANON.md`、`docs/canon/PRODUCT_BOUNDARY.md`、`docs/canon/AUTHORITY_ORDER.md`、`docs/canon/INTERNAL_SYSTEMS.md`、本 changelog、`README.md`。
- **Migration：** Progressive Migration（Phase 1 core facade/boundary → Phase 2 新代码进 core → Phase 3 engine→core compatibility facade → Phase 4 engine 退役）；products/ 权威降级 + capability mapping，不删除；demo `moodify analyze` 渐进升格为 production CLI 首个正式命令。
- **Rollback：** 回退本条及上述 authority 文件到 Canon v1.1（PLAY 冻结）即可恢复。
- **待人类裁决（HUMAN_DECISION_REQUIRED）：** 跨端一致性等级最终取值；products/ 中 Rating/Supply 是否迁入新 Core；engine→core 命名迁移时点。（已裁决 2026-09-20：提交目标分支 = `codex/professional-finishing-layer-20260920`；后续方向演进见 2026-09-20 Professional Finishing 条目。）

## 2026-08-30 — MOOD World Entrance and Public Slogan

- **CANON_CHANGE = YES。** 人类明确要求将 MOOD 网站理解为“先有入口，然后是结构，像是一个世界”，并提出 `To be yourself` 作为口号方向；公开首屏采用更完整、直接的英文命令式 **`BE YOURSELF.`**，中文叙事为“在这里，成为你自己。”
- **Why：** 现有 `/token` 页面同时承担世界叙事、内容章节、钱包与 Token 信息，但首屏缺少清晰的“进入”体验，MOOD 与 Moodify Music 的层级关系不够明确。
- **Boundary：** MOOD 被定义为数字世界入口；Moodify Music 是进入该世界的一扇音乐之门。此次不改变 Moodify Music / Player 内部的 `Play` 核心动作，也不把 Ear 或内部生产复杂度公开化。
- **Evidence：** 人类 2026-08-30 对指定 MOOD 首屏截图的明确反馈；运行表面为 `apps/web/app/token/page.tsx`。
- **Affected authority/runtime files：** 本 changelog、`apps/web/app/token/page.tsx`、`apps/web/app/token/layout.tsx`、`apps/web/app/globals.css`。
- **Migration：** 首屏建立 `BE YOURSELF.` → `进入 MOOD` → 世界地图 → 具体世界区域的单向信息结构；Token、钱包和合约信息保留在后段。
- **Rollback：** 回退本条记录及上述 `/token` 页面、元数据与样式的同批变更，即可恢复 2026-08-30 调整前入口。

## 2026-08-19 — Public Form Brand Authority Freeze（v1.1）

- **CANON_CHANGE = YES。** 人类通过 Package 01 明确冻结 Public Brand：创始价值原点「弱者的声音也值得被世界听见」；公共表达「每一种声音，都值得被世界听见。 / Every voice deserves to be heard.」；产品原则 `Listen. Then Play.`；动作 `Play.`。
- **站点职责：** `rongjingmusic.com` = Moodify Product Home；`rongjingwenchuan.com` = 荣景文川 Company Home；`rongjinwenchuan.xyz` = 过渡 Web Player / 历史入口；`play.rongjingmusic.com` 为优先迁移目标但当前 `UNVERIFIED`。
- **语言边界：** `The Ear of AI`、Auditory Intelligence Infrastructure、API/ACU/Developers、Creator Platform 与内部处理链退出公共第一叙事；研究与工程上下文可保留。
- **Authority：** 新增 `docs/brand/public/`，其中 `PUBLIC_BRAND_CONSTITUTION.md` 为最高 Public Brand 主题权威；旧 product-framework、站点和域名文档保留但不得覆盖它。
- **Evidence：** Package 清单 SHA-256 全部匹配；三站仓库/线上只读审计见同目录 Inventory、Conflict Matrix、Backlog、Authority Report。
- **Migration：** Package 02 Product Home；Package 03 Company Home；Package 04 Player/域名收敛。本包不提前修改生产表面。
- **Rollback：** 将本条、Canon/索引链接及 `docs/brand/public/` 作为一个文档变更单元回退；因本包未改运行时，无生产回滚步骤。
- **受影响 authority 文件：** `AGENTS.md`、`docs/canon/CURRENT_CANON.md`、`PRODUCT_BOUNDARY.md`、`AUTHORITY_ORDER.md`、本 changelog、`docs/product-framework/PRODUCT_AUTHORITY_INDEX.md`。
- **明确未改：** production website/App/DNS/Cloudflare/API/database/audio chain。

## 2026-08-17 — W01-P01 Canonical Convergence（v1.0）

- **对外产品身份：** Moodify Music / Moodify Player；第一阶段核心用户动作 PLAY。
  - 旧身份（公开产品层面）：「The Ear of AI — an Auditory Intelligence System」、「Reconstruction-first listening environment」均不再作为对外身份。
  - 受影响文件：README.md、AGENTS.md、docs/REPOSITORY_STATUS.md、docs/canon/*（新建）。
- **内部边界：** Moodify Ear / Auditory Intelligence 明确为内部听觉、判断、验证与研究系统；Classic Reconstruction（宪法 v1.0）保留为内部生产哲学。
  - 受影响文件：AGENTS.md、README.md、docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md（INTERNAL 标记）、docs/ASSET_MODEL.md（INTERNAL 标记）。
- **权威顺序：** 固定 8 级 authority order（人类指令 > AGENTS > docs/canon/* > runtime evidence > canonical main behavior+tests > subsystem docs > experimental docs > historical docs）。
- **Canon 不变量：** 一个对外产品身份；PLAY 优先；Canon 不虚构现实；历史文档不反向覆盖 Canon；Canon 变更必须可见。
- **Canon drift guard：** scripts/canon_guard.py + moodify-core-package/tests/test_canon_guard.py（2026-08-17）。
- **决策注册：** W01-P01 Decision Register（CD-001..CD-016）。

### HUMAN_DECISION_REQUIRED（未决，不猜测）

1. CD-011：对外命名细节（Moodify Music vs Player、域名品牌 rongjingmusic.com 等）。
2. CD-014：Classic Reconstruction Constitution v1.0 正文是否更新（其 Article I 对外表述已被本 Canon 覆盖，文本未动）。
3. CD-015：单一 authoritative state machine 统一方案。
4. GitHub main 合并策略（未合并分支 154 commits 的去向）。
