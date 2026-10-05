# Repository Status

**Status:** 当前 Canon 与事实状态入口（Canon v3.0 / Personal Music Node，2026-10-03 更新）。
**Authority:** 本文件是状态入口，不是独立权威；权威见 root `AGENTS.md` 与 `docs/canon/*`（[AUTHORITY_ORDER](canon/AUTHORITY_ORDER.md)）。

## Canonical Identity（Canon v2.2，2026-10-03）

> **Moodify — an open protocol and reference implementation for evolving audio intelligence**（Generated is not finished）；Listener Side 核心动作 **PLAY**，Creator Side 核心动作 **PROCESS**（专业完成流）。

- **公共项目原则：** **Fork the code. Join the process.**（代码可以复制，过程需要参与。）Moodify 采用开源 + 免费 + 公共协作路线；`Moodify Moat = Process × History × Network`，不是 Code。三层叙事：**Protocol（规则层）/ Core（能力层）/ Network（过程）**——见 `GOVERNANCE.md`、`docs/governance/NETWORK.md`、`protocol/`。
- **对外产品面：** Listener Side = App/Player，兼 Preview / A-B / Review / Delivery；Creator Side = CLI（生产端完成流）+ Studio（`moodify-desktop/` 人类工作台）。
- **内部系统：** Moodify Ear / Auditory Intelligence（听觉、判断、验证与研究）、Cloud Production System（Intake→…→Render→Delivery）、Classic Reconstruction（内部生产哲学，宪法 v1.0）。
- **治理与证据层（2026-10-03 新增）：** `GOVERNANCE.md`、`MAINTAINERS.md`、`docs/governance/NETWORK.md`、`docs/governance/constraints/`（ME-001…ME-003）、`protocol/mips/`（MIP 流程）、`docs/evidence/`（W01-P00 Evidence Index 等）、`docs/ARCHIVE_INDEX.md`。**NO TOKEN / NO DAO / NO AIRDROP / NO TREASURY GOVERNANCE。**
- **历史身份说明：** 旧表述「The Ear of AI — an Auditory Intelligence System」作为**公开产品身份已失效**（被 W01-P01 Canon 覆盖）；Ear 保留为内部系统资产。完整裁决见 W01-P01 Decision Register CD-001/CD-002。
- **已移出主线的项目线（2026-10-03）：** MOOD Protocol Web3 线（EVM/BSC 主网 BEP-20 代币，已部署合约）**移出主线但磁盘保留**：`mood-web3-protocol/`（原 `protocol/`）、`apps/web`、`e2e/staging`、`web 3.0/`。该线与 Moodify Network 是两件事；历史记录见 `docs/ARCHIVE_INDEX.md`，不静默改写。

## 已退场的旧产品身份（2026-10-03 清理）

`moodify-qa`、`moodify-qa-desktop`、`moodify-pulse`、`products/{qa,master,rating,supply}`、`shared/`、`sdk/`、`plugins/`、`phys-lab/`、`windows版本开发/`、`审查包/`、`engine/`、`demo/` 已从主线移除。QA / Master / Rating / Supply 从来不是四个平级产品身份，最多只能是 Core 内部 capability。逐路径依赖检查与裁决见 [`docs/restructure/CLEANUP_MANIFEST.md`](restructure/CLEANUP_MANIFEST.md)。结构守卫 `scripts/check_repo_structure.py` 防止其重建。

## Product Canon v3 — 2026-10-03（DEFINED / TARGET）

**产品定义：** `Moodify = Core + Protocol + Studio + App + Network`（一个产品的五层，不是五个产品）。完整定义见 [`docs/canon/PRODUCT_DEFINITION_V3.md`](canon/PRODUCT_DEFINITION_V3.md)；技术选型规则见 [`docs/canon/TECHNOLOGY_PRINCIPLES.md`](canon/TECHNOLOGY_PRINCIPLES.md)。

**第一产品循环：**

```text
Studio → Publish to My Library → Phone → Play
（在电脑上完成一首歌 → 歌出现在手机 → 立刻能听）
```

**战略：** `stability > novelty`、`completion > ambition`、`working loop > architecture purity`。

> ⚠️ **下列 TARGET 部分尚未实现。本文不得被读作已实现。**

| 能力 | 状态 | 依据 |
|---|---|---|
| Moodify Core | **IMPLEMENTED** | `moodify-core-package/`（679 文件，v1.0.0-rc.1） |
| Moodify Protocol 0.1 / 0.2 | **IMPLEMENTED**（预设作业 + 报告；可编辑 Mix Graph 仍为目标态） | `moodify protocol validate\|process`；`docs/protocol/` |
| Moodify Studio（Electron 壳） | **IMPLEMENTED（壳）** — 只编排 Core，自身无 DSP；启动脚本仅 `electron .` | `moodify-desktop/`（v1.0.0-rc.1，Electron ^33） |
| Moodify App / Android Player | **IMPLEMENTED（唯一正式移动端）** | `apps/music-android`（com.moodify.music v2.0.1）；GitHub Release 工作流从该目录构建与签名 |
| **Studio → My Library 发布动作** | **TARGET — 不存在** | 全仓库无实现 |
| **Track package / `manifest.json`** | **TARGET — 不存在** | 全仓库无实现 |
| **局域网传输 / 配对 / token** | **TARGET — 不存在** | 全仓库无实现 |
| **Android 接收与本地音乐库** | **TARGET — 不存在** | 全仓库无实现 |
| **App 身份 / 账号 / 设备注册** | **TARGET — 不存在** | 未实现 |
| **Moodify Network（节点互联）** | **TARGET — 不存在** | V1 仅指 Desktop ↔ 个人手机 |
| **远程分享 / relay / 对象存储** | **TARGET — 不存在** | 未实现 |

经仓库检索确认：没有任何 `publish to my library` / `lan sync` / `pairing token` / `local transfer` 实现代码。

**已裁决：** `apps/music-android` 是唯一 canonical App；旧候选 `apps/android` 已于 2026-10-04 按人类指令退役删除。**仍未裁决：** Creator 侧首要产品面是 CLI（现行 `CURRENT_CANON.md`）还是 Studio（v3），继续标记为 `HUMAN_DECISION_REQUIRED`。此前的双线状态与证据保留在 [`docs/reports/PRODUCT_CANON_V3_ALIGNMENT_2026-10-03.md`](reports/PRODUCT_CANON_V3_ALIGNMENT_2026-10-03.md) 作为历史记录。

## Studio 生产流程 v3 — 2026-10-03（DEFINED，已实现流程层）

> **Understand first. Decompose second. Plan third. Process last.**（先理解，再分解，再规划，最后处理。）

Creator 侧流程固定为 **检测 → 问题 → 分轨 → 结构 → 方案 → 成品**。
早期「分析完立刻选预设处理立体声母带」被移除——对母带来说太早。
**分解先于规划**：⑤ 方案 需要 分轨 + MIDI，⑥ 成品还需要一份真实写出的方案产物。

| 项 | 状态 | 依据 |
|---|---|---|
| 流程条 + 阶段推导 + 门禁 | **IMPLEMENTED** | `moodify-desktop/src/pipeline.js`；阶段由磁盘产物推导，未满足前置的阶段锁定 |
| ② 问题（`studio/diagnosis.json`） | **IMPLEMENTED** | 严格投影自 `report.json`，每条 issue 带可解析的 evidence 指针 |
| ⑤ 方案（`studio/context.json`） | **IMPLEMENTED** | 只引用不复制，且只写真实存在的路径 |
| ③ 分轨 / ④ 结构 接入主流程 | **IMPLEMENTED** | 复用既有工作台；分轨 `grade=PREVIEW_NOT_MASTERING_GRADE` |
| 三个预设 | **保留**，已下移到 ⑥ 成品阶段 | 工具不是流程 |
| 诊断丰度 | **受限** — Core 只有 2 种 finding 规则，18 个真实 case 中 17 个为空 | 见下 |
| AI 方案的结构化规划 + 执行（002B/002C） | **TARGET — 未实现** | — |
| 精细分离引擎 | **TARGET — 未实现** | — |

**诊断诚实边界：** `issues: []` 只表示**当前规则未发现问题**，不代表音频被判定为无问题。
UI 与产物均须如此表述。Core 另有 18 参数诊断引擎但桌面够不到，且接入会引入第二诊断权威 → `HUMAN_DECISION_REQUIRED`。

文档：[`docs/canon/STUDIO_PRODUCTION_PIPELINE_V3.md`](canon/STUDIO_PRODUCTION_PIPELINE_V3.md) ·
[`docs/protocol/MOODIFY_STUDIO_CONTEXT_0_1.md`](protocol/MOODIFY_STUDIO_CONTEXT_0_1.md) ·
[`docs/reports/STUDIO_PIPELINE_REALIGNMENT_2026-10-03.md`](reports/STUDIO_PIPELINE_REALIGNMENT_2026-10-03.md)

### Studio 生产流程 v4 — 2026-10-04（DEFINED；流程层已实现，第一条真实 A/B 闭环已打通）

V4 重塑了 v3 的后半程：`① 检测 → ② 逆向分解 → ③ 结构 → ④ 修音 → ⑤ 复合 → ⑥ 复检 → ⑦ 选定 → ⑧ 导出`；
②问题 与 ⑤方案 退场（findings 留在 ① 的 report 里），三预设作为产品面退场。
契约见 [`STUDIO_PRODUCTION_PIPELINE_V4.md`](canon/STUDIO_PRODUCTION_PIPELINE_V4.md)；
Phase 2 实现报告见 [`reports/2026-10-04_DESKTOP_ONE_CLICK_PHASE2_IMPLEMENTATION.md`](reports/2026-10-04_DESKTOP_ONE_CLICK_PHASE2_IMPLEMENTATION.md)。

| 项 | 状态 | 依据 |
|---|---|---|
| 一键完成会话（Phase 1） | **IMPLEMENTED** | `moodify-desktop/src/orchestrator.js` / `session.js`：步骤由产物推导、真实失败可见且可重试、⑦ 选定有严格准入 |
| 快速完成（仅立体声）两档候选（Phase 2） | **IMPLEMENTED（EXPERIMENTAL）** | Core `moodify tuning render-pair`（`moodify/tuning.py`，MIP-0002 附录 A）+ Desktop 接线；A 保守 / B 充分，逐侧 evidence，原子发布，A/B 均完成才发布 |
| 深度受阻时的显式切换（Phase 2.1） | **IMPLEMENTED**（`CANON_CHANGE = YES`） | 入口依据 `!deepExecutable`（不再是 `!deepAssetsReady`）；有 stems/MIDI 也能切换，切换只写 `finish_mode.json`、不生成音频、不删资产；见 [`CANON_CHANGELOG.md`](canon/CANON_CHANGELOG.md) 2026-10-04 条目与 [`reports/2026-10-04_DESKTOP_ONE_CLICK_PHASE2_1_MODE_SWITCH.md`](reports/2026-10-04_DESKTOP_ONE_CLICK_PHASE2_1_MODE_SWITCH.md) |
| A/B 审听工作台（Phase 2.2） | **IMPLEMENTED**（`CANON_CHANGE = NO`） | REVIEW 重建为两个候选标签 + 单 transport（三音源同位置切换）+ 每页「原版 vs 候选」的频谱/指标/图表/处理链；全部数值来自候选自己那次复检的 report 与 Core 的 plan/evidence（只读 IPC `tuning:evidence` / `tuning:charts` 带路径守卫）；见 [`reports/2026-10-04_DESKTOP_PHASE2_2_AB_REVIEW_WORKBENCH.md`](reports/2026-10-04_DESKTOP_PHASE2_2_AB_REVIEW_WORKBENCH.md) |
| 完成层与作品留存（Phase 2.3） | **IMPLEMENTED**（`CANON_CHANGE = NO`） | 选定后进入作品层（标题 / 版本 / 确定性波形印记 / 日期 / 从头听 / 导出 / 作品卡 / 查看制作详情 / 可选的一句话）+ 安静聆听；留存记录 `<case>/studio/keepsake.json` 是**非权威**表现层产物（完成状态仍由产物 + ⑦ 准入推导，keepsake 不能解锁 CHOSEN 或导出）；见 [`reports/2026-10-04_DESKTOP_PHASE2_3_FINISHING_POLISH.md`](reports/2026-10-04_DESKTOP_PHASE2_3_FINISHING_POLISH.md) |
| Identity / Account / Personal History（Phase 3A） | **PARTIALLY IMPLEMENTED · DEPLOYMENT_BLOCKED**（`CANON_CHANGE = YES`） | 已实现并测试：Canon 三权威边界、`MIP-0003`（DRAFT）、Supabase 迁移 + RLS + 受控删除函数、两用户 RLS 套件（**未能执行**：本机无 `psql`/Supabase CLI、Docker daemon 未运行、无凭据 → runner 以 exit 2 显式跳过）、history 事件白名单与数据最小化、离线幂等队列、投影与冲突规则、`account_link.json`。**未实现**：`src/account/*`（登录回调/PKCE/session-store）、`history-sync/sync.js` 编排、main/preload IPC、个人空间 UI、`test-account.js`——**不得**接假登录 UI 充数。真实账户/RLS/端到端验收缺凭据，为 `DEPLOYMENT_BLOCKED`。见 [`reports/2026-10-04_DESKTOP_PHASE3A_IDENTITY_HISTORY.md`](reports/2026-10-04_DESKTOP_PHASE3A_IDENTITY_HISTORY.md) |
| 深度路径：逐轨音准·节奏修正、多轨复合 | **TARGET — 未实现** | Core 无此能力；Desktop 显式拒绝 `TUNABLE_CORE_NOT_AVAILABLE` / `DEEP_NOT_EXECUTABLE` |
| 可逆性验证（`moodify tuning roundtrip`） | **TARGET — 未实现** | 无来源化判据，因此不写 `passed: true`；深度 ④ 保持锁定 |
| ⑥ 复检（三方逐指标对齐） | **IMPLEMENTED** | `moodify-desktop/src/recheck.js`：对 A / B 各重跑一次完整检测 |
| 两档参数 | **UNCALIBRATED_ENGINEERING_DEFAULT** | 人类尚未校准；B 只代表「变化更充分」，不代表「更好」 |

## Current Verified Mainline（仓库侧）

MSP/0.1 仓库侧实现：`moodify protocol validate|process`；JSON 作业 → 既有 Core 预设处理 → WAV、诊断与哈希清单。仅证明执行路径，不证明自动听感验证或云端部署。协议详情见 [`docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md`](protocol/MOODIFY_SOUND_PROTOCOL_0_1.md)。

```text
Import -> Analyze -> Diagnose -> Process -> Export
```

数据侧主链：

```text
SOURCE -> LISTEN -> REPRESENT -> JUDGE -> ABC INTERVENTION -> VERIFY
       -> ALGORITHMIC REVIEW -> DATASET -> NEXT CASE
```

## Reality Snapshot Pointer（2026-08-17，W01-P00）

- 云端现状：2 VPS（LA 核心 + 杭州数据工厂）+ PolarDB（核验 BLOCKED）+ 无对象存储 + 无云端 AI 推理 + 队列近空；完整 Ear 链路仅仓库代码。
- 详见 [docs/evidence/](evidence/README.md)（W01-P00 Evidence Index，E01–E27；E13/E14 为 LA/杭州节点原始扫描）与 [docs/canon/CURRENT_ARCHITECTURE.md](canon/CURRENT_ARCHITECTURE.md)。
- **事实规则：** 本文件与 Canon 不得虚构云端/生产能力；未验证能力不写成已运行。

## Verification Baseline（历史记录，2026-08-08）

```text
commit: 0b355e7
branch: codex/moodify-ai-ear-reconstitution-001 (from origin/main)
pytest: 109 passed, 7 warnings
ruff: all checks passed
date: 2026-08-08
```

> 该基线与当前专题分支已不一致；分支领先数量会持续变化，不作为能力或权威声明；
> 它是历史记录，不作为当前状态声明。当前测试证据见各包 TEST_RESULTS 与 CI 历史。

## Capability Table（当前事实状态，2026-08-17）

| Capability | Status | Evidence / Path |
|---|---|---|
| Audio ingest | CANONICAL | `audio_io.py`; v0.1 tests |
| Wave/spectral analysis | CANONICAL | `v01_analyzer.py`; analyzer tests |
| Diagnosis | CANONICAL | `v01_diagnostics.py`; diagnosis tests |
| Controlled intervention / DSP | CANONICAL | `v01_pipeline.py`, `processing/pedalboard_chain.py` |
| Mix Graph finishing session | EXPERIMENTAL（本地 CLI 已实现，schema 未冻结） | `src/moodify/mix_graph`；`moodify finishing new/render/verify/export`；golden `artifacts/mix_graph_v01/golden`（确定性重放已证：同图同源两次渲染逐位一致，2026-09-29）。MSP/0.1 协议载荷层尚不承载图（目标态 v0.2） |
| Reconstruction objective / identity guard / era diagnostic | IMPLEMENTED_NOT_MERGED | `src/moodify/reconstruction_objective|identity_guard|era_diagnostic`（分支） |
| Data factory | CANONICAL | `data_factory`；10-song pilot 10/10（artifacts/mfy_24x7_data_pipeline_001） |
| Node queue / worker | CANONICAL（云端实跑） | `node`；LA/杭州部署（W01-P00 03 报告） |
| Algorithmic review | CANONICAL | `data_factory/algorithmic_review`（MFY-ALGO-REVIEW-FORMULA-001） |
| Before/after verification | EXPERIMENTAL | Inspector/treatment scripts |
| Treatment records | EXPERIMENTAL | `treatment_records/` |
| Human feedback | EXPERIMENTAL | Treatment record feedback fields |
| Production-case state machine | LEGACY（orchestration）| `orchestration/workflow_engine.py`；统一方案 HUMAN_DECISION_REQUIRED |
| MSE structural analysis | ABSENT | No canonical score/MIDI/lyrics structural subsystem |
| Cloud runtime（Ear 生产流量） | UNRESOLVED | 云端 API 壳运行，无生产流量（W01-P00） |
| App integration | CANONICAL（对外面） | apps/music-android 3.1 + deliverables/releases |
| MAMSE-001..012 | EXPERIMENTAL_ACCEPTED | artifacts/mamse_001..012 |
| MSP/0.2 analyze/compare 作业 + 0.2 报告三件套 + 阈值来源化（Layer C） | EXPERIMENTAL（本地 CLI 已实现，report schema 未冻结；运行时依赖 ffmpeg；16 条判定阈值全部 DEFAULT_UNCALIBRATED） | `sound_protocol.py`、`auditory/protocol_report.py`、`auditory/report_render.py`、`auditory/comparison.py`、`auditory/judgment.py`（THRESHOLD_PROVENANCE，judgment-rules v1.1）、`auditory/sensitivity.py`；`moodify protocol process`（0.2 analyze/compare 作业）、`moodify report`、`moodify demo`（一键到 Moodify 报告窗口）与 `moodify app`（公司桌面软件单壳：选歌 → 检测 → 数据/图表 → 后处理方案；白底 + 公司 logo）；证据 `artifacts/msp02_compare_001/`、`artifacts/msp02_calibration_001/` |
| 私有部署交付（pip 唯一通道，Layer D 裁决） | READY（wheel 构建 + 干净 venv 安装 + doctor 冒烟已证；公开 PyPI 上架待人类指令；商业 = 服务/支持，不卖许可） | `release_cli.py`（`moodify doctor`）、`pyproject.toml`（版本 1.0.0-rc.1 统一）；裁决记录 `docs/plan/2026-10-02_LAYER_D_COMMERCIALIZATION_PROPOSAL.md` §8；证据 `artifacts/msp02_layer_d_001/` |

Allowed status values: `CANONICAL`, `EXPERIMENTAL`, `LEGACY`, `HISTORICAL`, `ABSENT`, `UNRESOLVED`, plus W01-P00 task states (`IMPLEMENTED_NOT_MERGED` 等) for unmerged work.

Never promote a capability to CANONICAL based only on documentation or an unmerged branch.

## History

- 2026-10-03 (MOODIFY_NETWORK_RESTRUCTURE_001，**CANON_CHANGE = YES**): 对外定位扩为**开放声音协议与持续演化网络**（Protocol / Core / Network 三层叙事 + `Fork the code. Join the process.`），并完成仓库结构收敛。**全量 `pytest` 前 1197 passed / 5 skipped / 0 failed，后 1197 passed / 5 skipped（零回归）**；`ruff` 前后皆 clean。基线 `c11bc7f5`（2760 tracked files）→ tag `pre-network-restructure-2026-10-03`。移除：`windows版本开发/`(330) `审查包/`(373，9 份权威证据先迁 `docs/evidence/`) `products/`(32) `shared/`(7) `sdk/`(9) `plugins/`(9) `moodify-qa/`(26) `moodify-qa-desktop/`(8) `moodify-pulse/`(18) `engine/`(19) `demo/`(12) `phys-lab/`(1) `apps/ear-workbench/android/`(24)。移出主线但磁盘保留：MOOD Web3 线（`protocol/`→`mood-web3-protocol/`、`apps/web`、`e2e/staging`、`web 3.0/`）。收敛结果：**仓库内只剩一个 `moodify` console entry point**（`moodify.release_cli:main`，`demo` 的冲突声明随 `demo/` 移除而消失）。新增：`GOVERNANCE.md`、`MAINTAINERS.md`、`docs/governance/NETWORK.md`、`protocol/`（specs/schemas/conformance/mips）、`docs/evidence/`、`docs/ARCHIVE_INDEX.md`、`docs/restructure/**`、结构守卫。详见 [`docs/restructure/RESTRUCTURE_REPORT.md`](restructure/RESTRUCTURE_REPORT.md)。
- 2026-10-02 (W2 修正 wire_api+DeepSeek): codex ≥0.160 硬移除 chat wire API → 全部 provider 改 `wire_api="responses"`；人类指令改用 DeepSeek（原生 Responses API，假路径 404 对照验证），设置卡三选一定为 DeepSeek/OpenAI/自定义，GLM（仅 chat）选项移除；**真轮次打通**（deepseek-v4-pro 经 app-server 流式应答，生效沙箱 readOnly 如实显示）。残余：用户全局 ~/.agents/skills 会被 codex 探测（待隔离）、GLM 转译桥未建、windowsSandbox/setupStart 未接。
- 2026-10-02 (Moodify Studio W2 Mood 编译器): 内核按人类三项裁决换 Codex——**协议嵌入一步到位**（`@openai/codex` 0.160.0 `app-server`，JSON-RPC over stdio，schema 取自二进制自证）/ **模型安装时可选**（GLM/OpenAI/自定义，设置卡录入，仅存本机 `~/.moodify/codex`）/ **claude CLI 完全替换**（claude 通道移除）。流式对话 + 原生审批卡（批准/本次会话批准/拒绝）+ 保存方案为 `case_dir/plan.md`。诚实显示生效沙箱：请求 workspace-write、本机 windowsSandbox notConfigured → 生效 read-only。定义文档 §9 修正案。核心零改动；真模型轮次待 API Key 录入；W3 贡献值账本未开工。
- 2026-10-02 (Moodify Studio W1 布局骨架): 产品定义定稿 `docs/plan/2026-10-02_MOODIFY_STUDIO_PRODUCT_DEFINITION.md`（四裁决：claude CLI 过渡 / 贡献值本地账本 MVP / 一次到位+左侧 dock / 终端共存）并实施 W1——IDE 骨架：44px 图标栏（打开/历史/编译器）+ 历史档案左滑出面板（PS 式）+ 中央工作区四视图（空态仅 logo 水印，无占位文字）+ 底部终端抽屉（拖拽调高度、可收起、cwd 跟随 case）；拖拽音频入工作区即检测。核心零改动；固定流程不变；W2 编译器对话 / W3 贡献值账本未开工。
- 2026-10-02 (方案由 Claude Code 执笔 + 内嵌终端): 人类裁决——数据/图表出来后方案改由 **Claude Code** 生成（`claude -p` 读 case 导出物，流式显示并存 `plan_claude.md`；与核心保守草案并列呈现），报告视图新增**终端页**（node-pty + xterm.js 真实终端，cwd=case 目录，按钮一键 `claude` 交互续写）；空态占位文字全部移除（状态行只在有事发生时出现）。**核心零改动**：方案文本是 Claude Code 产出物，Moodify 核心只供测量事实（责任分离）；DRAFT_PLAN_NOT_EXECUTED 边界不变。仅动 `moodify-desktop/`。
- 2026-10-02 (桌面壳迁 Electron): 人类裁决"做成 electron"——新增 `moodify-desktop/`（Electron 壳：白底 + 公司 logo + 固定流程原样迁移；零 npm 运行时依赖，contextIsolation + CSP 收紧）。壳只编排核心：检测 = `python -m moodify.release_cli demo --no-open`（同 0.2 协议路径）；图表 = `moodify.ui.chart_export` 桥（Tk 同一批图函数，Agg 出 PNG）；档案/报告只读 report.json。python 子进程强制 `PYTHONUTF8=1`（GBK 陷阱）。核心 pip-only 裁决不变；tkinter 壳保留为回退。同批修 `.gitignore` `*.png` 吞品牌资产（第三次同坑类），白名单两处品牌资产目录。
- 2026-10-02 (产品定义定稿): 人类裁决**单壳白底公司桌面软件**——"不要 2 个壳"，实验台（`moodify.ui.lab`，8e32e85e）整体移除；产品 = 档案中枢（选歌/历史）+ 报告视图（数据/图表/后处理方案）同一壳内导航；**固定流程**：选择歌曲 → 检测 → 根据数据和图表给出修音与混音方案。新增 `moodify.ui.theme`（白底主题/公司 logo/窗口图标；品牌资产 `moodify/ui/assets/*.png`，package-data 入包，缺失时优雅降级）。
- 2026-10-02 (实验台 v0.1，已被同日产品定义定稿移除): 人类裁决"先要有科研一样的 GUI"——新增 `moodify.ui.lab`（观测/目录/实验三区，引擎零改动，GUI-first 教义）；人类看过窗口后改裁决"不要 2 个壳"，实验台存活一版即移除；科研可观测性由报告三件套与档案事实承载。
- 2026-10-02 (桌面应用中枢): 新增 `moodify app` 与 `moodify.ui.app`——GUI 操作闭环：文件对话框选歌 → 应用内后台线程分析（Tk 主线程零阻塞，queue 轮询）→ 自动存档 `~/.moodify/cases`（永久档案）→ 历史列表双击秒开（不重新分析）；报告视图内"← 档案"窗口内导航。同批按人类逐项指令完成 UI 简化：删"发现"页签（触发式折叠进方案页）、删"打开 HTML/退出"页脚按钮、删"边界与来源"页签（诚实边界改为上下文行：图表题注 / 方案状态注 / L1-only 页脚文字）；完整细节仍存 report.json/md/html。CLI 侧 `_spawn_ui_module` 泛化（app 与 report_window 共用独立进程派生）。
- 2026-10-02 (Layer D 商业化前置): 人类四项裁决落定——GPL-3.0-only 保持（卖服务不卖许可）、仅 pip 分发、私有部署交付（不上云不计费）、定价延后；D-0 工程前置实施（版本统一 1.0.0-rc.1、`moodify doctor`、sdist+wheel 构建 + 干净 venv 安装冒烟）。裁决记录见 `docs/plan/2026-10-02_LAYER_D_COMMERCIALIZATION_PROPOSAL.md` §8。公开 PyPI 上架待人类另行指令。
- 2026-10-02 (核心时刻一键到屏): 新增 `moodify demo <audio>`——一条命令完成 0.2 analyze 作业（同 validate/execute 协议路径，无新 DSP、无新阈值）+ 渲染报告三件套 + 在 **Moodify 自己的报告窗口**（`moodify.ui`，tkinter 标准库实现，零新依赖）弹出报告；窗口在独立进程运行，CLI 秒回 JSON（agent 永不等待人类关窗）；`--browser` 退回浏览器看 HTML 导出物，`--no-open` 只渲染。窗口含**图表页**（MATLAB 风格 matplotlib 嵌入，TkAgg，零新依赖）：实测频谱 PNG + 频段能量（log 轴）+ 电平响度（dB 域）+ 立体声分布；图表只画实测事实、无阈值着色（0/16 calibrated 边界在图上显式声明）。修音方案以 `DRAFT_PLAN_NOT_EXECUTED` 草案呈现（方案≠执行；执行需显式 process/finishing 作业）。同批修复：ffmpeg/ffprobe 子进程输出显式 UTF-8 解码（中文 Windows GBK 环境下非 ASCII 文件名会导致解码崩溃——真实曲库首发即触发）。
- 2026-10-02 (MSP/0.2 Layer C): 阈值来源化——`UNIVERSAL_THRESHOLDS` 16 条全部带 source/date/status（judgment-rules v1.1，纯增量元数据，数值自 5452ff44 冻结未变）；现状诚实记录 0/16 calibrated，全部 DEFAULT_UNCALIBRATED；敏感性报告（生产判定路径翻转点 16/16 一致 + lab 阶梯可达性桥）落 `artifacts/msp02_calibration_001/`。感知显著性校准仍不存在。
- 2026-10-02 (MSP/0.2 Layer B): 协议新增 `compare` 作业（L2 对比层：配对校验 + 响度对齐 + delta 只描述不评级 + Δ 频谱图 + contact-sheet）；证据 `artifacts/msp02_compare_001/`。
- 2026-10-02 (MSP/0.2 Layer A): 协议新增 `analyze` 作业（纯读取分析）与 0.2 报告三件套（report.json/md/html，含指标可见性声明与判断边界）；同时清理双 CLI 入口点冲突（setup.py 不再声明 console_scripts）与 cli_v2/cli_daw 残骸。设计提案见 `docs/plan/2026-10-02_MSP02_ANALYSIS_JOB_AND_DISPLAY_DESIGN.md`。
- 2026-09-20 (Canon v2.0): 身份升级为 Professional Finishing（Generated is not finished）；Player 重新定位为消费端接口 + Preview/A-B/Review/Delivery；Mix Graph v0.1 为下一工程包（当前 ABSENT）。〔2026-10-02 注：该行 status 已过时——Mix Graph v0.1 已实现，见上方能力表 EXPERIMENTAL 行〕
- 2026-08-17 (W01-P01): 从历史静态快照转为 Canon 入口；身份收敛为 Moodify Music / Player。
- 2026-08-14: Brand/Core Identity vs Public Product 记录（已并入上方历史身份说明）。
- 2026-08-08: 原 Ear of AI 身份基线（保留为历史）。
