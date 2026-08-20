# Repository Status

**Status:** 当前 Canon 与事实状态入口（Canon v1.1 / Public Form v0.1，2026-08-20 更新）。
**Authority:** 本文件是状态入口，不是独立权威；权威见 root `AGENTS.md` 与 `docs/canon/*`（[AUTHORITY_ORDER](canon/AUTHORITY_ORDER.md)）。

## Canonical Identity（P01 Canon，2026-08-17）

> **Moodify Music / Moodify Player** 是对外产品面；第一阶段核心用户动作是 **PLAY**。

- **对外产品面：** Moodify Music / Player（Music Android 3.1 APK、music-web PWA、云端 music-platform/BFF）。
- **内部系统：** Moodify Ear / Auditory Intelligence（听觉、判断、验证与研究）、Cloud Production System（Intake→…→Render→Delivery）、Classic Reconstruction（内部生产哲学，宪法 v1.0）。
- **历史身份说明：** 旧表述「The Ear of AI — an Auditory Intelligence System」作为**公开产品身份已失效**（被 W01-P01 Canon 覆盖）；Ear 保留为内部系统资产。完整裁决见 W01-P01 Decision Register CD-001/CD-002。

## Current Verified Mainline（仓库侧）

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

Allowed status values: `CANONICAL`, `EXPERIMENTAL`, `LEGACY`, `HISTORICAL`, `ABSENT`, `UNRESOLVED`, plus W01-P00 task states (`IMPLEMENTED_NOT_MERGED` 等) for unmerged work.

Never promote a capability to CANONICAL based only on documentation or an unmerged branch.

## History

- 2026-08-17 (W01-P01): 从历史静态快照转为 Canon 入口；身份收敛为 Moodify Music / Player。
- 2026-08-14: Brand/Core Identity vs Public Product 记录（已并入上方历史身份说明）。
- 2026-08-08: 原 Ear of AI 身份基线（保留为历史）。
