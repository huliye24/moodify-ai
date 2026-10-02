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
| MSP/0.2 analyze/compare 作业 + 0.2 报告三件套 + 阈值来源化（Layer C） | EXPERIMENTAL（本地 CLI 已实现，report schema 未冻结；运行时依赖 ffmpeg；16 条判定阈值全部 DEFAULT_UNCALIBRATED） | `sound_protocol.py`、`auditory/protocol_report.py`、`auditory/report_render.py`、`auditory/comparison.py`、`auditory/judgment.py`（THRESHOLD_PROVENANCE，judgment-rules v1.1）、`auditory/sensitivity.py`；`moodify protocol process`（0.2 analyze/compare 作业）与 `moodify report`；证据 `artifacts/msp02_compare_001/`、`artifacts/msp02_calibration_001/` |

Allowed status values: `CANONICAL`, `EXPERIMENTAL`, `LEGACY`, `HISTORICAL`, `ABSENT`, `UNRESOLVED`, plus W01-P00 task states (`IMPLEMENTED_NOT_MERGED` 等) for unmerged work.

Never promote a capability to CANONICAL based only on documentation or an unmerged branch.

## History

- 2026-10-02 (MSP/0.2 Layer C): 阈值来源化——`UNIVERSAL_THRESHOLDS` 16 条全部带 source/date/status（judgment-rules v1.1，纯增量元数据，数值自 5452ff44 冻结未变）；现状诚实记录 0/16 calibrated，全部 DEFAULT_UNCALIBRATED；敏感性报告（生产判定路径翻转点 16/16 一致 + lab 阶梯可达性桥）落 `artifacts/msp02_calibration_001/`。感知显著性校准仍不存在。
- 2026-10-02 (MSP/0.2 Layer B): 协议新增 `compare` 作业（L2 对比层：配对校验 + 响度对齐 + delta 只描述不评级 + Δ 频谱图 + contact-sheet）；证据 `artifacts/msp02_compare_001/`。
- 2026-10-02 (MSP/0.2 Layer A): 协议新增 `analyze` 作业（纯读取分析）与 0.2 报告三件套（report.json/md/html，含指标可见性声明与判断边界）；同时清理双 CLI 入口点冲突（setup.py 不再声明 console_scripts）与 cli_v2/cli_daw 残骸。设计提案见 `docs/plan/2026-10-02_MSP02_ANALYSIS_JOB_AND_DISPLAY_DESIGN.md`。
- 2026-09-20 (Canon v2.0): 身份升级为 Professional Finishing（Generated is not finished）；Player 重新定位为消费端接口 + Preview/A-B/Review/Delivery；Mix Graph v0.1 为下一工程包（当前 ABSENT）。〔2026-10-02 注：该行 status 已过时——Mix Graph v0.1 已实现，见上方能力表 EXPERIMENTAL 行〕
- 2026-08-17 (W01-P01): 从历史静态快照转为 Canon 入口；身份收敛为 Moodify Music / Player。
- 2026-08-14: Brand/Core Identity vs Public Product 记录（已并入上方历史身份说明）。
- 2026-08-08: 原 Ear of AI 身份基线（保留为历史）。
