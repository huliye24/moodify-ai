# Repository Status

**Status:** 当前 Canon 与事实状态入口（Canon v2.1 / Sound Protocol，2026-09-23 更新）。
**Authority:** 本文件是状态入口，不是独立权威；权威见 root `AGENTS.md` 与 `docs/canon/*`（[AUTHORITY_ORDER](canon/AUTHORITY_ORDER.md)）。

## Canonical Identity（Canon v2.0，2026-09-20）

> **Moodify — AI-native Professional Audio Finishing System**（Generated is not finished）；Listener Side 核心动作 **PLAY**，Creator Side 核心动作 **PROCESS**（专业完成流）。

- **对外产品面：** Moodify：Listener Side = App/Player（Music Android 3.1 APK、music-web PWA、云端 music-platform/BFF），兼 Preview / A-B / Review / Delivery；Creator Side = CLI（生产端完成流）。
- **内部系统：** Moodify Ear / Auditory Intelligence（听觉、判断、验证与研究）、Cloud Production System（Intake→…→Render→Delivery）、Classic Reconstruction（内部生产哲学，宪法 v1.0）。
- **历史身份说明：** 旧表述「The Ear of AI — an Auditory Intelligence System」作为**公开产品身份已失效**（被 W01-P01 Canon 覆盖）；Ear 保留为内部系统资产。完整裁决见 W01-P01 Decision Register CD-001/CD-002。

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
- 详见 W01-P00 报告（审查包/W01-P00_REPORTS_2026-08-17）与 [docs/canon/CURRENT_ARCHITECTURE.md](canon/CURRENT_ARCHITECTURE.md)。
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
