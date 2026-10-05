# CANON_CHANGELOG — Moodify

> 所有产品身份、authority order、内部/外部边界变化必须记录于此（R7）。

## 2026-10-04 — Identity / Account / Personal History（Phase 3A，CANON_CHANGE = YES）

- **CANON_CHANGE = YES。** 触发的 Canon 控制项：**内部/外部能力边界** + **data authority** +
  **cloud control authority**。依据人类批准（2026-10-04，Phase 3A 任务包「0. 人类产品裁定」）。
  影响文件：`PRODUCT_DEFINITION_V3.md`（§9.1 例外 + §11）、`PRODUCT_BOUNDARY.md`
  （non-goals + 边界节）、`AUTHORITY_ORDER.md`（三种权威）、`REPOSITORY_STATUS.md`。
  契约冻结于 `protocol/mips/MIP-0003-personal-identity-history.md`（`MIP_REQUIRED: YES`）。

- **Why：** 个人作品历史需要跨安装持续存在。Desktop 已能形成 A/B 候选、人工选择、keepsake 与
  完成时刻，但这些历史只存在于单机 case；换电脑、重装或将来换到手机即消失。账户是 continuity
  的承载，**不是**社交增长工具。

- **Evidence：** Phase 2 / 2.1 / 2.2 / 2.3 已在 Desktop 落地并测试通过（一次性完成会话、
  A/B 审听工作台、完成层与 keepsake）；`<case>/studio/` 下已有真实的 decision 账本与留存记录，
  它们构成可同步的白名单 metadata 来源。真实歌曲排练记录见
  `docs/reports/2026-10-04_DESKTOP_PHASE2_3_FINISHING_POLISH.md`。

- **New boundary：**
  - **允许**：account / login / 受控云端 metadata / Desktop history sync；
  - **仍然禁止**：公共主页、关注/粉丝、动态流、排行榜、评论、点赞、公开作品发布平台、广告画像、
    **默认上传音频**；
  - 云端只存白名单 metadata（标题、完成时间、最终选择、可选一句话、粗粒度历史事件）；
    音频 / stems / MIDI / 曲谱 / report / 频谱图片 / Mix Graph 全量参数 / 本地路径 / 源 hash
    默认不上传；
  - 三种权威分离：本地声音生产事实（pipeline + decisions.jsonl）/ 账户身份（认证服务）/
    个人历史同步（append-only events + server projection）；云端**不得**推进本地阶段或改写本地选择；
  - 未登录、断网、服务停机不得阻断本地生产；无本地音频的历史项显示「音频仅在原设备」，无假播放。

- **Migration：** 既有 case 不自动上传。用户登录后必须显式确认（逐项或批量）启用历史同步，
  每个 case 写 `<case>/studio/account_link.json`，并可随时关闭后续同步。没有任何既有 case
  因本变更被修改或上传。

- **Rollback：** 关闭 account / sync 功能后，本地声音流程、case、选择、导出与 keepsake 继续完整工作；
  `account_link.json` 与离线队列可整体删除而不影响任何声音产物。删除云端历史或账户不删除本地 case。

- **状态：** 代码、迁移、RLS 策略与本地可验证部分在仓库内；**真实账户能力为 `DEPLOYMENT_BLOCKED`**
  ——缺生产/测试 Supabase 凭据与可用数据库（本机无 `supabase` CLI / `psql`，Docker daemon 未运行），
  因此 RLS 执行证据、真实登录与端到端验收尚不存在，不得写成已上线。

## 2026-10-04 — Studio 模式门禁：深度受阻时提供显式快速完成（Phase 2.1，CANON_CHANGE = YES）

- **CANON_CHANGE = YES。** 触发的 Canon 控制项：**内部能力边界**（Studio 的模式选择与门禁语义）。
  依据人类批准（2026-10-04，Phase 2.1 任务包「0. 人类裁定」），按 `AGENTS.md` 记录
  why / evidence / affected authority files / migration / rollback。Core 音频契约未变，故 `MIP_REQUIRED: NO`。
- **旧语义（被取代）：** 快速完成的入口条件为 `baseReady ∧ ¬deepReady ∧ ¬optIn`
  （`gates().canRequestQuick`），模式为 `deepReady ? DEEP : (quick ? FAST_STEREO_ONLY : null)`，
  即「只要分轨 + MIDI 存在（`deepReady`）就隐藏快速入口，且深度优先覆盖」。
- **死路证据（真实歌曲复现）：** `Je ne blesserai pas ta fragilité.wav` 在 Desktop 上
  检测 → 自动分轨与 MIDI → 进入 DEEP；此时 `roundtrip.json` 缺失、且逐轨 Core 能力未实现，
  于是 `canTune = false`、`canTuneQuick = false`、`canRequestQuick = false`——三处同时为假，
  用户既不能深度完成，也不能选择快速完成。**这不是用户操作错误，是门禁组合产生的产品死路**，
  违反「第一个产品目标必须形成可靠完成循环」「失败必须可见、可恢复」「AI 不得替人改变完成模式」。
- **Why：** `deepReady`（资产存在）与「深度路径当前可执行」是两件事。Core 的逐轨能力尚未实现，
  所以任何 `deepReady` 的 case 实际上都不可深度完成；用资产存在与否决定入口，就把用户关在门外。
- **新语义（权威，见 `STUDIO_PRODUCTION_PIPELINE_V4.md` §3.4 / §4.2.0）：**

  ```text
  deepAssetsReady = analyzed ∧ separated ∧ structured
  deepExecutable  = deepAssetsReady ∧ reversible ∧ 深度 Core 能力可用（当前不可用）
  fastAvailable   = analyzed ∧ fast-stereo-pair 能力可用（当前可用）

  deepExecutable 为真 → 默认 DEEP，不显示快速入口
  deepExecutable 为假 → canRequestQuick = true（提供显式入口）
  用户未选择          → 不生成任何快速候选
  用户明确选择        → 记录 QUICK_STEREO_ONLY，mode = FAST_STEREO_ONLY，按快速路径继续
  ```

  要点：①入口依据改为 `!deepExecutable`；②**人的显式选择优先于 `deepAssetsReady`**，
  不再被覆盖回 DEEP；③切换只写 `finish_mode.json`，**不生成音频**；
  ④切换**不删除/移动/覆盖**任何深度资产（stems / MIDI / score / roundtrip / 失败证据），
  已存在的产物在相位投影中仍显示为 `done`；⑤绝不自动降级，绝不因此解锁深度 ④修音。
- **Evidence：** 死路状态由 `gates()` 三处布尔值同时为假复现；消除后
  `moodify-desktop/scripts/test-pipeline.js` §5c、`test-session.js` §9、`test-orchestrator.js` §7、
  `test-main-ipc.js` §7 逐条钉住（含「未选择不生成 pair」「确认前不写 finish_mode.json」
  「切换不删资产」「有 stems/MIDI 也能切换」「显式选择后 mode 不再被 deepReady 覆盖」
  「未来深度可执行时仍默认 DEEP」）。全部回归见
  `docs/reports/2026-10-04_DESKTOP_ONE_CLICK_PHASE2_1_MODE_SWITCH.md`。
- **Affected authority files：** `docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md`（新增 §3.4、
  §4 门禁表、§4.2.0、§9、§10）、本文件、`docs/REPOSITORY_STATUS.md`（Studio v4 状态表）。
  实现文件：`moodify-desktop/src/pipeline.js`（`modeDecision()` + `gates()`）、
  `src/session.js`（阻断补救投影）、`src/main.js`（`pipeline:setFinishMode`）、
  `renderer/{app.js,index.html,style.css}`（显式入口 + 确认 + 徽章）。
- **Migration：** 无需迁移。既有 case 产物不动；`finish_mode.json` schema 不变
  （仍是 `moodify.studio.finish-mode/0.1`）；阶段仍由磁盘产物推导。
  既有已选 FAST 的 case 升级后行为不变（本来就该显示 FAST）。
- **Rollback：** 恢复 `pipeline.gates()` 的 `canRequestQuick = baseReady ∧ ¬deepReady ∧ ¬optIn`
  与 `mode = deepReady ? DEEP : …`，并隐藏 renderer 的切换入口即可；
  Core、pair、decision、recheck 产物与账本完全兼容，无需任何数据迁移。
  单一 commit revert 亦可（本轮改动集中在一个 commit 范围内的上述文件）。
- **未裁决（不在本轮）：** 是否提供「从快速模式切回深度路径」的 UI 入口（当前只能清除
  `finish_mode.json`）；快速完成是否需要一个「一键重跑检测」入口。两者均为后续工作，
  本轮按现状如实记录，不自行扩大范围。

## 2026-10-03 — PRODUCT CANON v3：产品定义五层 + 个人音乐节点 + 技术原则（CANON_CHANGE = YES）

- **CANON_CHANGE = YES。** 触发的 Canon 控制项：**对外产品身份**与**内部/外部能力边界**。依据人类任务书 `MOODIFY_PRODUCT_DEFINITION_AND_EXECUTION_001`（2026-10-03）§2/§17，按 `AGENTS.md` L125 记录 why / evidence / affected authority files / migration / rollback。
- **Why：** 人类方向（§0）：Moodify **不以技术最先进作为竞争方式**，产品战略为 `stability > novelty`、`completion > ambition`、`working loop > architecture purity`、`maintainability > technical fashion`——用成熟、公开、通用的技术快速做出稳定产品；先进技术仅在已证明的产品瓶颈要求时引入。
- **产品定义（新增）：** `Moodify = Core + Protocol + Studio + App + Network`，**一个产品的五层，不是五个独立产品**。第一产品循环 = `Studio → Publish to My Library → Phone → Play`（「我在电脑上完成一首歌，按下发布，歌出现在手机上，我能立刻听」）。**App = Personal Music Node（个人音乐节点）**，四项职责 My Library / Playback / My Identity / Connections，**最早版本只做前两项**。
- **新增权威文件：** `docs/canon/PRODUCT_DEFINITION_V3.md`、`docs/canon/TECHNOLOGY_PRINCIPLES.md`（技术优先级 `existing > standard library > mature OSS > commodity service > custom > experimental`；举证责任在 custom/experimental；V1 排除 blockchain/token/DAO/DID/CRDT/P2P/WebRTC/自定义密码学/自定义数据库/microservice mesh/Kubernetes/实时协作 DAW/自定义流协议）。
- **Evidence（关键诚实边界）：** 经全仓库检索确认，**第一产品循环完全不存在实现**——无 `publish to my library`、无 track package / `manifest.json`、无 LAN 传输 / 配对 / token、无 Android 接收入口、无本地音乐库、无身份 / 账号 / 设备注册、无 Network。本文档定义方向，**不授权一次性实现 V1–V2**；TARGET 部分不得被写成已实现（R6/R10）。
- **Affected authority files：** `docs/canon/PRODUCT_DEFINITION_V3.md`（新）、`docs/canon/TECHNOLOGY_PRINCIPLES.md`（新）、`AGENTS.md`（新增 Product Direction 段，五条 Agent 必读）、`docs/REPOSITORY_STATUS.md`（新增 Product Canon v3 段 + DEFINED/TARGET vs IMPLEMENTED 表）、`README.md`（五层架构 + 第一循环 + 「Network」术语消歧）、本文件。
- **Known conflicts（如实记录，不静默改写）：**
  1. **Creator 侧首要产品面：CLI 还是 Studio？** `CURRENT_CANON.md` §1（v2.1）称 Creator Side = **Moodify CLI** 且「CLI 是首要执行接口」；v3 称 Creator Side = **Moodify Studio**。当前**非裁决式**处理为「CLI 与 Studio 同在 Creator 侧，CLI 是自动化/Agent 接口，Studio 是人类工作台，同调一个 Core」，但**「哪一个是首要对外产品面」尚未由人类裁决** → `HUMAN_DECISION_REQUIRED`。
  2. **「Network」一词语义冲突。** 2026-10-03 重构把 `Moodify Network` 定义为**开放协作网络**（`GOVERNANCE.md`、`docs/governance/NETWORK.md`）；v3 §1 把 Network 定义为**产品层：个人音乐节点之间的连接**。两者都在用同一个词。已在 `README.md` 与 `PRODUCT_DEFINITION_V3.md` 显式消歧，但**术语是否需要改名尚未裁决** → `HUMAN_DECISION_REQUIRED`。
  3. v3 §8.2（App：Listening Interface → Personal Music Node）经判定为**扩展而非冲突**：`PLAY` 仍是核心动作，V1 的 App 行为与 v2.1 描述一致。
- **未裁决前置问题：** `apps/android`（com.moodify.app v2.0.0）与 `apps/music-android`（com.moodify.music v2.0.1）**两条并存的 Android 线**，证据互相矛盾，v3 **不指定**哪一个是 canonical App，两者均不删除 → 归 Task 002 审计 + 人类确认（`AGENTS.md` L71）。
- **Migration：** 无破坏性变更。本次为纯文档任务，**未新增任何网络 / Android / 云代码**，未删除任何遗留 Android 项目，未改动 Core、desktop、音频算法。既有 CLI 命令面与 0.1/0.2 协议不变。
- **Rollback：** 回退本 commit 即可；不涉及代码，无数据迁移。

## 2026-10-03 — MOODIFY_NETWORK_RESTRUCTURE_001：对外定位扩为开放声音协议与持续演化网络（CANON_CHANGE = YES）

- **CANON_CHANGE = YES。** 触发的 Canon 控制项：**对外产品身份**与**内部/外部能力边界**。依据为人类任务书 `MOODIFY_NETWORK_RESTRUCTURE_001`（2026-10-03），并按 AGENTS.md L125 记录 why / evidence / affected authority files / migration / rollback。
- **Why：** Moodify 采用**开源 + 免费 + 公共协作**路线，不再把「别人无法看到我们的代码」当作壁垒。长期资产定义为 `Moodify Moat = Process × History × Network`（不是 Code）。产品命题 `Generated is not finished.` 不变；新增公共项目原则 `Fork the code. Join the process.`。目标从「只有我们能更新 Moodify」转为「任何人都可以改进 Moodify，且改进能够重新进入公共演化过程」。
- **身份变化（对外）：** 从「Moodify Sound Protocol — 一个共享 Core + CLI/App」**扩展**为「**An open protocol and reference implementation for evolving audio intelligence**」+ 三层叙事 **Protocol / Core / Network**。**不变**：一个对外产品身份、One Core / Multiple Interfaces、CLI=PROCESS、App=PLAY、`Generated is not finished.`。**未复活**（§27 明确禁止）：Web3 / token economy / 四产品并列平台 / QA 公司 / 自动母带 SaaS / The Ear of AI 公开身份 / 音乐资产交易 / crypto protocol。
- **边界变化（内部/外部）：** ① 新增**治理层**——`GOVERNANCE.md`、`MAINTAINERS.md`、`docs/governance/NETWORK.md`、`protocol/mips/`（MIP 流程）、`docs/governance/constraints/`（ME-001…ME-003，自 `工程经验层/` 迁入）；② 新增**证据层**规范化——`docs/evidence/`（W01-P00 Evidence Index 等迁入）+ `docs/ARCHIVE_INDEX.md`；③ 明确 **NO TOKEN / NO DAO / NO AIRDROP / NO TREASURY GOVERNANCE**；④ 明确 **AI Agent 有执行权、无最终产品主权**（与既有裁决一致，此处正式写入治理文件）。
- **MOOD Protocol Web3 线移出主线（本次最大的边界变更）：** 该线（`protocol/` 113 文件、`apps/web` 201 文件、`e2e/staging` 6 文件、`web 3.0/` 37 文件、以及 `docs/protocol/` 中 5 份 Web3 文档）**移出主线但不删除**。判定依据：这不是历史残留而是**活体基础设施**——`protocol/mainnet.json` 声明 EVM/BSC 主网 BEP-20 代币 MOOD（`0x1BB3115D43E397f7bb586F090831B02cA639e73E`，33,000,000 供应，PancakeSwap 在交易）。人类裁决（2026-10-03）：磁盘保留、取消跟踪。**历史不得被静默改写**，故在此记录该线的存在及其与 Moodify Network 的区别。
- **Evidence：** 基线 `c11bc7f5`（2760 tracked files），安全 tag `pre-network-restructure-2026-10-03`；全量 `pytest` 前 **1197 passed / 5 skipped / 0 failed**，重构后 **1197 passed / 5 skipped**（零回归）；`ruff` 前后皆 clean。逐路径依赖检查与裁决见 `docs/restructure/CLEANUP_MANIFEST.md`；前后树见 `BEFORE_TREE.txt` / `AFTER_TREE.txt`。
- **Affected authority files：** `README.md`、`AGENTS.md`、`CONTRIBUTING.md`、`docs/REPOSITORY_STATUS.md`、`docs/canon/AUTHORITY_ORDER.md`、`docs/canon/CURRENT_ARCHITECTURE.md`、`docs/canon/CURRENT_CANON.md`、`GOVERNANCE.md`、`MAINTAINERS.md`、`docs/governance/NETWORK.md`、`protocol/**`、`docs/evidence/**`、`docs/ARCHIVE_INDEX.md`、`docs/restructure/**`、`.github/workflows/release.yml`。
- **Migration：** 无协议破坏性变更；0.1/0.2 协议、CLI 命令面、`moodify-core-package` 公共 API 未变。新增 CI 结构守卫 `scripts/check_repo_structure.py`。`demo` 与 `engine` 移除后，仓库内**只剩一个 `moodify` console entry point**（`moodify.release_cli:main`）。
- **Rollback：** `git checkout pre-network-restructure-2026-10-03 -- <path>` 可恢复任一被移除路径；完整回退为 revert 本系列 commit。磁盘保留的 MOOD 线亦可通过 `git checkout pre-network-restructure-2026-10-03 -- protocol/ apps/web e2e/staging "web 3.0/"` 重新纳入跟踪。
- **HUMAN_DECISION_REQUIRED（本次未裁决，不猜测）：** ① `apps/android` vs `apps/music-android` 谁是当前版（两者本次均未动）；② `apps/web` 移出后线上站点 `play.rongjingmusic.com` 的部署路径与 `deploy.yml` 处置；③ Core 内 `moodify.contribution`（MOOD 层，14 文件）去留——牵涉 2026-09-29 契约权威裁决；④ `moodify_runtime/`（约 1550 行唯一 commerce 代码）迁入 Core 还是放弃；⑤ `.git` 4.0 GB 历史是否做 history diet（本次按 §3.1 不重写历史）；⑥ `moodify-desktop` 的 Windows 打包能力（electron-builder）由谁补。

## 2026-10-02 — Moodify Studio W2 修正：wire_api=responses + 提供方定稿 DeepSeek（真轮次已验证）（CANON_CHANGE = NO）

- **CANON_CHANGE = NO。** 仍属 W2 编译器实现事实的修正（R7 可见性），产品身份与边界不变。
- **事实修正 1：** codex ≥0.160（2026-02）**硬移除 `wire_api="chat"`**（上游 discussion 7782）；GLM 开放平台仅提供 chat/completions（`/v4/responses` 404），与当前 codex 不可直连。设置卡 GLM 选项移除；GLM key 有效但仅 chat（如需接入须自建转译桥，记 W2 残余）。
- **事实修正 2：** 人类指令"用 deepseek api"。DeepSeek 具备**原生 Responses API**（对照验证：假路径 404 / `/responses` 402 计费位）。提供方三选一定为 **DeepSeek / OpenAI / 自定义（OpenAI 兼容 Responses）**；main.js 全部 provider 一律 `wire_api="responses"`；DeepSeek 一等 kind（`https://api.deepseek.com/`、`DEEPSEEK_API_KEY`、默认 `deepseek-v4-pro`）。
- **端到端验证：** 冒烟脚本真轮次打通——initialize → thread/start（生效沙箱 readOnly）→ turn/start → 流式 delta → turn/completed，`deepseek-v4-pro` 正确应答。密钥仅存本机 `~/.moodify/codex`。
- **新发现残余：** codex 会尝试加载用户全局 `~/.agents/skills/`（本机加载失败，未进上下文；但产品面编译器不应读取用户个人 skills，待配置隔离）。
- **Affected files：** `moodify-desktop/src/main.js`、`renderer/index.html`、`renderer/app.js`、定义文档 §9 修正案 2、`docs/REPOSITORY_STATUS.md`、本文件。

## 2026-10-02 — Moodify Studio W2：Mood 编译器内核换 Codex（app-server 协议嵌入，claude CLI 完全替换）（CANON_CHANGE = NO）

- **CANON_CHANGE = NO。** 产品身份、authority order、One Core 规则不变；记录于此因 Mood 编译器的内核通道整体换轨（R7 可见性）。权威依据：`docs/plan/2026-10-02_MOODIFY_STUDIO_PRODUCT_DEFINITION.md` §9 修正案（人类三项裁决：**B 协议嵌入一步到位 / 模型安装时可选 / claude CLI 完全替换**——取代原裁决 1"先用 claude CLI 过渡"）。
- **Boundary：** W1 的 claude CLI 通道整体移除（PLAN_PROMPT 与 claude IPC 不复存在）。新内核 = `@openai/codex` 0.160.0 的 `codex app-server`（JSON-RPC over stdio，协议形状取自二进制 `generate-json-schema`，非猜测）：main 进程单例 `CodexClient`（initialize → thread/start → turn/start，流式 `item/agentMessage/delta`），审批请求（命令/文件修改）原生化进 UI（批准 / 本次会话批准 / 拒绝 → `codex:respond`）。模型提供方三选一（GLM / OpenAI / 自定义 OpenAI 兼容 base_url），首次使用设置卡录入，仅存本机 `CODEX_HOME=~/.moodify/codex`（config.toml + providers.json，不碰用户 `~/.codex`；密钥只在 spawn 时注入 env，`codex:provider:get` 永不回传明文）。thread 的 cwd=case 目录，系统提示词固定"Moodify 后处理方案工程师"；"保存方案"把最后一条助手消息写为 `case_dir/plan.md`。**核心零改动；DRAFT_PLAN_NOT_EXECUTED 不变。**
- **诚实边界（原样进 UI）：** thread/start 请求 `sandbox=workspace-write` + `approvalPolicy=untrusted`，但本机 `windowsSandbox/readiness` = notConfigured，**生效沙箱降级为 read-only**——UI 显示生效值而非请求值（`Codex 内核 · <model> · Windows 沙箱：<生效>` + 降级说明）。沙箱配置向导 `windowsSandbox/setupStart` 暂不自动触发（W2 残余项）。
- **License：** `@openai/codex` Apache-2.0，单向兼容 GPL-3.0-only，作为 npm 依赖嵌入（不 fork 源码——上游日更，fork 漂移不可维护；源码仅审计参考），NOTICE 归属随依赖分发保留。
- **Affected authority files：** `docs/REPOSITORY_STATUS.md`、本文件、`docs/plan/2026-10-02_MOODIFY_STUDIO_PRODUCT_DEFINITION.md`（§9 修正案）。代码面：`moodify-desktop/src/main.js`（CodexClient + codex IPC）、`src/preload.js`（codex 桥，claude 桥移除）、`renderer/index.html`（编译器面板 + 设置卡）、`renderer/app.js`（编译器对话/审批/设置逻辑）、`renderer/style.css`、`package.json`（+ @openai/codex）。
- **Migration：** npm install 后 `npm start`；旧 plan_claude.md 不迁移（历史上已存 case 不回写）。真模型轮次待人类在设置卡录入 API Key（推荐 GLM）后首验。
- **Rollback：** 回退本 commit 恢复 W1 骨架（无编译器对话）；`~/.moodify/codex` 中的本机配置可独立删除。

## 2026-10-02 — Moodify Studio W1：IDE 布局骨架（图标栏 + 中央工作区 + 终端抽屉）（CANON_CHANGE = NO）

- **CANON_CHANGE = NO。** 产品身份、authority order、One Core 规则不变；记录于此因产品显示面骨架级重构（R7 可见性）。权威依据：`docs/plan/2026-10-02_MOODIFY_STUDIO_PRODUCT_DEFINITION.md`（人类四项裁决：claude CLI 过渡 / 贡献值本地账本 MVP / 一次到位 + 左侧 dock / 终端共存）。
- **Boundary：** `moodify-desktop/` 渲染层重构为 IDE 骨架：44px 左图标栏（打开/历史档案/Mood 编译器，无功能的设置图标不渲染——无用元素必删）；历史档案收进左侧滑出面板（PS 式，双击打开 case）；中央工作区 = 空态/数据/图表/方案四视图（空态只有 logo 水印，**无占位文字**）；底部终端抽屉全局常驻（拖拽调高度、双击/箭头收起、cwd 跟随 case，"在此目录打开 Claude Code"移入抽屉标题栏）。新增拖拽音频入工作区即检测（Electron 32+ 移除 File.path，经 preload webUtils.getPathForFile）。**核心零改动；固定流程四步不变；W2 编译器对话、W3 贡献值账本未开工。**
- **Affected authority files：** `docs/REPOSITORY_STATUS.md`、本文件、`docs/plan/2026-10-02_MOODIFY_STUDIO_PRODUCT_DEFINITION.md`（W1 依据）。代码面：`moodify-desktop/renderer/index.html`（骨架重构）、`renderer/style.css`（IDE 布局）、`renderer/app.js`（视图状态机/历史面板/抽屉/拖放）、`src/preload.js`（pathForFile 桥）。
- **Migration：** 无破坏性变更；CLI 命令面、0.2 报告 schema、核心包无变化。
- **Rollback：** 回退本 commit 即恢复页签式布局（615bd4f9）；定义文档保留。

## 2026-10-02 — 方案由 Claude Code 执笔 + 内嵌终端：测量事实与方案文本的责任分离（CANON_CHANGE = NO）

- **CANON_CHANGE = NO。** 产品身份、authority order、One Core 规则不变；记录于此因固定流程的"方案"一环改变了生成主体（R7 可见性）。人类指令原话要点："数据和图表出来之后，通过 claude code 去给出方案，里面可以加一个终端吗？可以打开 claude code"；同批：空态占位文字（"空闲，选择一首歌开始检测"）一律不要。
- **Why / evidence：** 固定流程（选歌 → 检测 → 数据/图表 → 方案）中，数据与图表是核心测量事实；方案正文改由 Claude Code 基于 case 导出物（report.json / measurements.json / judgment_rules.json）生成——**Moodify 核心只供测量事实，方案文本是 Claude Code 产出物**，两者责任分离。
- **Boundary：** `moodify-desktop/` 新增两能力：① 后处理方案页一键生成——`claude -p <方案提示词> --allowedTools Read,Glob,Grep`（cwd=case 目录，输出流式显示并存为 `case_dir/plan_claude.md`；与既有保守草案 DRAFT_PLAN_NOT_EXECUTED 并列，草案仍来自核心规则）；② 终端页——node-pty + xterm.js 真实终端（cwd=case 目录），"在此目录打开 Claude Code"按钮把 `claude` 敲进 shell，用户可交互续写方案。壳不变承诺：contextIsolation 开、CSP 收紧、零新遥测；pty 环境同样强制 `PYTHONUTF8=1`。空态占位文字全部移除（状态行只在有事发生时出现）。**核心零改动**：本条只动 `moodify-desktop/`，`moodify` 包无 diff。
- **Affected authority files：** `docs/REPOSITORY_STATUS.md`、本文件。代码面：`moodify-desktop/src/main.js`（pty + claude IPC）、`src/preload.js`（桥）、`renderer/index.html`（终端页 + 方案生成区）、`renderer/app.js`、`renderer/style.css`、`scripts/vendor-xterm.js`（postinstall 复制 xterm dist 进 renderer/vendor）、`package.json`（deps: @xterm/xterm、@xterm/addon-fit、node-pty）。
- **Migration：** 无破坏性变更；CLI 命令面、0.2 报告 schema、核心包无变化。`npm install` 后 `npm start`（postinstall 自动 vendor xterm）。
- **Rollback：** 回退本 commit 即移除终端页与方案生成区；plan_claude.md 属 case 导出物，删除不影响核心档案完整性。

## 2026-10-02 — 桌面壳迁 Electron：单壳产品形态不变，壳技术换轨（CANON_CHANGE = NO）

- **CANON_CHANGE = NO。** 产品身份、authority order、One Core 规则不变；记录于此因产品显示面的壳技术换轨（R7 可见性）。人类指令原话要点："这个软件没有做好，我希望做成 electron，你试着去做一下"。
- **Why / evidence：** 2026-10-02 人类看过 tkinter 壳后裁决换 Electron。单壳白底 + 公司 logo + 固定流程（选歌 → 检测 → 数据/图表 → 修音与混音方案）**形态原样迁移**。
- **Boundary：** 新增 `moodify-desktop/`（Electron 壳，main/preload/renderer，零 npm 运行时依赖，contextIsolation 开、nodeIntegration 关、CSP 收紧）。壳只编排核心：检测走 `python -m moodify.release_cli demo --no-open`（同 0.2 validate/execute 路径）；图表走 `moodify.ui.chart_export` 桥（与 Tk 壳同一批图函数，Agg 出 PNG，零新图表语义）；档案扫描/报告渲染在壳内只读 report.json。所有 python 子进程强制 `PYTHONUTF8=1`（GBK 陷阱为产品级缺陷）。**核心 pip-only 裁决不变**：Electron 是公司桌面壳，不是核心分发形态。tkinter 壳保留为回退（同产品、两套渲染端，不是两个产品壳）。同批修复：`.gitignore` `*.png` 吞品牌资产（第三次同坑类：*.tar.gz、*.html、*.png）——白名单 `moodify-core-package/src/moodify/ui/assets/*.png` 与 `moodify-desktop/renderer/assets/*.png`。
- **Affected authority files：** `docs/REPOSITORY_STATUS.md`、本文件。代码面：`moodify-desktop/`（新：package.json、src/main.js、src/preload.js、renderer/）、`moodify/ui/chart_export.py`（新）、`tests/ui/test_chart_export.py`（新）、`.gitignore`（白名单）。
- **Migration：** 无破坏性变更；CLI 命令面、0.2 报告 schema、协议链路不变。`npm start` 运行（`MOODIFY_CASES_ROOT`/`MOODIFY_PYTHON` 可覆写）。
- **Rollback：** 删除 `moodify-desktop/`、回退 chart_export 与 gitignore 白名单即可；Tk 壳始终可用，核心不受影响。

## 2026-10-02 — 产品定义定稿：单壳白底公司桌面软件 + 固定流程；实验台移除（CANON_CHANGE = NO）

- **CANON_CHANGE = NO。** 产品身份、authority order、One Core 规则不变；记录于此因这是产品显示面的定稿决策（R7 可见性）。人类指令原话要点：不要两个壳，实验台去掉；恢复数据/图表/后处理方案的壳；用公司 logo（`E:\moodify\logo`，采用 `moodify-horizontal.png`）做成公司的桌面端软件，采用白色；流程固定：选择歌曲 → 检测 → 根据数据和图表给出修音与混音方案。
- **Why / evidence：** 2026-10-02 人类看过实验台窗口后裁决"我不要 2 个壳"——科研可观测性由报告三件套（json/md/html）与档案事实承载，不设独立研究壳。
- **Boundary：** 删除 `moodify.ui.lab`（上一条目所记实验台，存活一版即被人类裁决移除）；应用回到单壳 = 档案中枢（选歌/历史）+ 报告视图（数据/图表/后处理方案，同壳内导航）。新增 `moodify.ui.theme`（白底主题、公司 logo、窗口图标；品牌资产 `moodify/ui/assets/*.png` 入包，pyproject package-data 声明；资产缺失时优雅降级为文字，不崩测量工具）。固定流程以产品窗口呈现：选歌 → 检测 → 数据/图表 → 后处理方案（修音与混音草案，DRAFT_PLAN_NOT_EXECUTED）。compare/观测能力仍走 CLI 与报告导出物（引擎未动）。
- **Affected authority files：** `docs/REPOSITORY_STATUS.md`、本文件。代码面：`moodify/ui/theme.py`（新）、`moodify/ui/assets/`（品牌资产，公司版权）、`moodify/ui/app.py`（单壳白底）、`moodify/ui/report_window.py`（同壳品牌化）、`pyproject.toml`（package-data）、删除 `moodify/ui/lab.py` 与 `tests/ui/test_lab.py`。
- **Migration：** 无破坏性变更；CLI 命令面不变；0.2 报告 schema 未动。
- **Rollback：** 回退本 commit 即恢复实验台（8e32e85e 仍在历史）；品牌资产与主题模块独立可回退。

## 2026-10-02 — Moodify 实验台：科研 GUI 优先，GUI-first 开发教义（CANON_CHANGE = NO）

- **CANON_CHANGE = NO。** 产品身份、authority order、One Core 规则不变；记录于此因开发教义与人机界面优先级翻转是产品级决策（R7 可见性）。人类指令原话要点：先要有科研一样的 GUI，然后才可以有 CLI——要知道在发生什么、可以发生什么、怎么优化迭代。
- **Why / evidence：** 2026-10-02 人类对实验台三项裁决（AskUserQuestion）：升级现有 app（一个壳两个心智）/ 观测区优先 / 只观测不写入（改阈值=改判定语义，属 L3 决策，显式后置）。
- **Boundary：** 新增 `moodify.ui.lab`（观测/目录/实验三区）：观测区从档案事实（evidence.json、scan_manifest、judgment_rules、report.representation）装配阶段级过程视图，**引擎零改动**；目录区为诚实能力地图（状态取值与 REPOSITORY_STATUS 同族；只有本窗口可达的 analyze/compare 可标"本实验台"入口）；实验区走 0.2 compare 作业同一条 validate/execute 路径，delta 只描述不评级。**开发教义（人类裁决）：新能力默认先进实验台（可观测可迭代），稳定后凝结为 CLI 命令；CLI 仍是 AI 调用面，不删。**
- **Affected authority files：** `docs/REPOSITORY_STATUS.md`、本文件。代码面：`moodify/ui/lab.py`（新）、`moodify/ui/app.py`（实验台入口）、`tests/ui/test_lab.py`（新）。
- **Migration：** 无破坏性变更；CLI 命令面不变。
- **Rollback：** 删除 `moodify/ui/lab.py`、`tests/ui/test_lab.py`、回退 app.py 实验台入口与本条即可；协议链路与档案不受影响。

## 2026-10-02 — Moodify 桌面应用中枢：打开文件 + 历史档案 + 界面内完成分析（CANON_CHANGE = NO）

- **CANON_CHANGE = NO。** 产品身份、authority order、One Core 规则不变；记录于此因产品显示面再次扩展（R7 可见性）。人类指令原话要点：增加打开文件让用户选歌，要有历史记录与保存档案，不用每次重复打开处理——需要一点 GUI 操作。
- **Why / evidence：** 2026-10-02 人类在报告窗口评审后提出应用化需求；单文件命令（`moodify demo`）不承载"回到历史档案"的产品体验。
- **Boundary：** 新增 `moodify.ui.app`（应用中枢）与 `moodify app` CLI 命令：文件对话框选歌 → 后台线程走 0.2 validate/execute 协议路径（无新 DSP）→ 每次分析自动存档 `~/.moodify/cases`（app 自有，跨工作目录稳定）→ 历史列表双击秒开（不重新分析）；报告视图内"← 档案"在窗口内部导航，无出口元素。同批 UI 简化（人类逐项指令）：删除"发现"页签（触发式折叠进方案页）、删除"打开 HTML 报告/退出"页脚按钮、删除"边界与来源"页签（诚实边界改为上下文行：图表题注、方案状态注、L1-only 页脚文字）；完整细节仍存于 report.json/md/html 导出物。
- **Affected authority files：** `docs/REPOSITORY_STATUS.md`、本文件。代码面：`moodify/ui/app.py`（新）、`moodify/ui/report_window.py`（`build_report_frame` 可嵌入化 + 简化）、`release_cli.py`（`app` 命令 + `_spawn_ui_module` 泛化）、`tests/ui/test_app.py`（新）、`tests/ui/test_report_window.py`。
- **Migration：** 无破坏性变更；`moodify demo` 行为不变（`_spawn_report_window` 成为 `_spawn_ui_module` 的薄封装）。
- **Rollback：** 删除 `moodify/ui/app.py`、`tests/ui/test_app.py`、回退 `release_cli.py` app 支面与本条即可；报告窗口简化独立回退不影响协议链路。

## 2026-10-02 — Moodify 报告窗口：产品显示面收归自有壳（CANON_CHANGE = NO）

- **CANON_CHANGE = NO。** 产品身份、authority order、One Core 规则不变；记录于此因新增了对外 UI 表面（R7 可见性）。人类指令原话要点：报告不在浏览器打开，而在 Moodify 自己的 UI 界面打开——否则后续难调整、产权有问题。
- **Why / evidence：** 2026-10-02 人类对核心时刻演示的纠正；此前 report.html 弹在系统浏览器（窗口壳属第三方）。
- **Boundary：** 新增 `moodify.ui` 包（Moodify 未来 UI 的家）+ `moodify.ui.report_window`（tkinter 标准库实现，**零新依赖**）；窗口渲染与 report.md/html 同源同事实（report.json），无新测量、无新判断、不执行方案。窗口在独立进程运行，CLI 恒秒回 JSON（agent 不等人类关窗）。`moodify demo` 窗口优先，`--browser` 降级为查看 HTML 导出物。report.html/md 降级为**导出物**（存证/外发），产品显示面 = Moodify 窗口。
- **Affected authority files：** `docs/REPOSITORY_STATUS.md`、本文件。代码面：`moodify/ui/`（新）、`release_cli.py`（demo 命令 + `_display_report`）、`tests/ui/test_report_window.py`、`tests/test_demo_command.py`。
- **Migration：** 无破坏性变更；0.2 报告 schema 未动（窗口是渲染端）。
- **Rollback：** 删除 `moodify/ui/`、回退 `release_cli.py` demo 支面与本条即可；报告三件套与协议链路不受影响。

## 2026-10-02 — 商业化路径裁决：GPL-only 服务模式 + 仅 pip 私有部署（Layer D，CANON_CHANGE = NO）

- **CANON_CHANGE = NO。** 产品身份、authority order、One Core 规则不变；记录于此因商业化路径是产品级决策（R7 可见性）。
- **Why / evidence：** 2026-10-02 人类对 Layer D 独立提案四项逐一裁决（提案 `docs/plan/2026-10-02_LAYER_D_COMMERCIALIZATION_PROPOSAL.md` §8 裁决记录；AI 推荐的双许可与容器方案被否，按人类裁决执行）。
- **Boundary：** license 保持 **GPL-3.0-only**（可售的是服务与劳动——部署、集成、调优、支持、托管——不是软件许可本身）；**pip/PyPI 为唯一分发形态**（无容器、无单二进制）；交付走**私有部署**（不上云、不建 API key/用量账本/计费）；**定价延后**（计价维度结构占位已落提案 §8，数字永久 HUMAN_DECISION_REQUIRED）。
- **Affected authority files：** `docs/plan/2026-10-02_LAYER_D_COMMERCIALIZATION_PROPOSAL.md`、`docs/REPOSITORY_STATUS.md`、本文件。代码面（D-0 工程前置）：`release_cli.py`（`moodify doctor` 环境探测）、`pyproject.toml`（版本统一至 1.0.0-rc.1）、`tests/test_layer_d_packaging.py`（版本一致钉死 + doctor 测试）。
- **Migration：** 无破坏性变更；doctor 为新增只读诊断命令（恒 exit 0，可用性由 `ready` 字段承载）。
- **Rollback：** 回退 D-0 代码 commit 与本条即可；裁决本身记录于提案 §8，回退代码不回退裁决记录。

## 2026-10-02 — 阈值来源化与敏感性验证（MSP 0.2 Layer C，CANON_CHANGE = NO）

- **CANON_CHANGE = NO。** 判定层能力新增（设计提案 §6 Layer C 承诺边界），不改产品身份、authority order、One Core 规则；记录于此因它修订了判定规则的版本语义（R7 可见性）。
- **Why / evidence：** 2026-10-02 人类指令「Layer C — 阈值来源化与校准」；事实基础：`UNIVERSAL_THRESHOLDS` 16 条值集合自 `5452ff44`（2026-08-02，AS-001）引入以来逐位未变（2026-10-02 全提交历史比对验证）。Layer C 只加来源元数据，不改任何数值。
- **Boundary：** 每条阈值带 `source_class`（STANDARD/EXPERIMENTAL/DEFAULT）、source 引用、date、introduced_in、`calibration_status`、`calibratable`；现状诚实记录为 **0/16 calibrated，全部 `DEFAULT_UNCALIBRATED`**——工程默认值不得当作已验证限值消费，报告内校准计数与 note 对下游显式警示。judgment-rules 版本 1.0→1.1（纯增量元数据，判定行为不变）。敏感性报告 = 生产判定路径 `evaluate_risk_flags` 的翻转点扫描（16/16 与声明阈值一致，纯算术无音频）+ `auditory.lab` 阶梯可达性桥（只映射可达性，不推导校准值；单位不可比显式标 `comparable: false`）。**防重校准护栏：测试钉死全部 16 个数值**；改值 = 重校准，需要实验证据 + 人类决策记录。感知显著性校准（给 delta 定「更好/更坏」）仍不存在。
- **Affected authority files：** `docs/protocol/MOODIFY_SOUND_PROTOCOL_0_2.md`、`docs/REPOSITORY_STATUS.md`。代码面：`auditory/judgment.py`（THRESHOLD_PROVENANCE + calibration_summary + 判定规则 v1.1 + 真峰规则改读表值，行为不变）、`auditory/protocol_report.py`（findings 校准字段 + `provenance.judgment_calibration` + `_ABSOLUTE_CHECK_VERSION` 派生自规则版本）、`auditory/report_render.py`（校准计数与 note 渲染）、`auditory/sensitivity.py`（新）。
- **Migration：** 无破坏性变更。`judgment_rules.json` 增量加键（既有 case bundle 不回写，历史证据保持 v1.0 原貌）；报告 schema 仍为 0.2 EXPERIMENTAL 未冻结态下的增量修订（`judgment_calibration` 与 findings 三个可选字段）；analyze/compare 作业行为不变。
- **Rollback：** 回退上述四个代码文件与本条即可；旧报告无 `judgment_calibration` 字段时渲染按缺省跳过，analyze/compare 链路与既有证据包不受影响。

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
