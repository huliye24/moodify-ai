# HEAR / JUDGE 外部能力吸收计划

**Status:** ADOPTED R&D EXECUTION PLAN  
**Date:** 2026-10-06  
**Canon impact:** `CANON_CHANGE = NO` — 本计划执行既有 `JUDGE_CORE_PRINCIPLE.md`，不改变产品身份、协议或 Judge authority。

## 决策

Moodify 不从零训练通用音频 encoder，也不把任何第三方模型升级为 Judge。现有项目按三类吸收：

1. **Sensors / representations**：Essentia、MuQ、MERT、CLAP 只提供可追溯观察；
2. **Hands / auxiliary views**：BS-RoFormer、audio-separator 等只提供分轨或处理视角；
3. **Baselines / benchmarks**：Music Flamingo、Qwen2.5-Omni、MARBLE、MUSE、ViSQOL 等用于对照与评测。

唯一进入 Judge authority 的路径是：`provider observation → Hearing State → versioned Judge task → calibrated evidence → scoped verdict / human escalation`。

## 已落仓边界

- 复用已有 `AuditoryRepresentation`，不创建第二套 Core representation；
- 新增实验性 `HearingState hear-v0.experimental`，统一承载 explicit、latent、semantic、stem 与 quality observations；
- 每条 observation 必须记录 provider/model 版本、代码与权重许可、来源、证据类型、置信度和局限；
- 所有第三方输出均为 `EVIDENCE_ONLY`，不得直接输出“更好听”或接受处理结果；
- Provider catalog 默认全部 `production_eligible = false`，生产采用必须经过逐项许可、来源、校准和盲测门禁；
- 缺失能力显式进入 `missing_capabilities`，不得补算或以零值代替。

## 吸收矩阵

| 项目 | Moodify 角色 | 当前准入 | 关键门禁 |
|---|---|---|---|
| Essentia | acoustic sensor baseline | research only | AGPL/商业许可与部署边界审查 |
| MuQ | music embedding teacher/baseline | research only | 开放权重 CC-BY-NC；生产需替换或授权 |
| MERT | layer probing / representation baseline | research only | 权重非商用；不得成为永久生产依赖 |
| LAION-CLAP | audio-text semantic baseline | candidate | checkpoint、训练数据来源与下游用途逐项审查 |
| Music Flamingo | long-form music reasoning reference | research only | 模型许可；结论不得取得 Judge authority |
| Qwen2.5-Omni | general audio reasoning reference | reference | 模型版本/许可与任务校准 |
| MARBLE | representation evaluation framework | reference | 数据集逐项许可与泄漏隔离 |
| MUSE | core-perception benchmark | evaluation only | stimuli 仅非商用测试，禁止训练 |
| ViSQOL / separation metrics | local quality sensors | candidate | 仅在验证过的域内解释，不合成万能总分 |
| BS-RoFormer / audio-separator | replaceable stem provider | candidate | 逐模型权重许可、roundtrip 门禁、来源记录 |

## 四个工程阶段

### H0 — Contract（本次完成）

- 冻结实验性 Hearing State envelope 与 provenance；
- 建立 fail-closed provider catalog；
- 保持 Sound Protocol 与生产 state machine 不变。

### H1 — Reproducible baselines

- 用获授权、可再分发或仅本地引用的样本建立固定 split；
- 首批跑 existing Core、librosa baseline、MuQ/MERT/CLAP research adapters；
- 输出每次运行的环境、commit、model revision、输入哈希、耗时、显存和失败状态。

### H2 — Benchmark bridge

- MARBLE 用于 representation probe；MUSE 只用于测试不用于训练；
- 增加 Moodify 自有 production tasks：artifact detection、identity preservation、before/after regression、`KEEP_ORIGINAL`；
- 指标按任务和 stem 分开报告，不生成未经校准的 overall quality score。

### J0 — Human-aligned Judge baseline

- 从有权利的 Treatment Records 构造 A/B/ORIGINAL 判断集；
- 标签至少包含 preference、reason、dimension、strength、reviewer scope、uncertainty；
- 按作品/创作者/provider 隔离 train/calibration/blind test；
- 只有在盲测与 fail-closed escalation 达标后，才允许某一窄任务进入机器授权范围。

## 明确不做

- 不下载或提交第三方权重、benchmark 音频、私有音乐；
- 不把 embedding 相似度命名为 warmth/harshness 等已校准感知事实；
- 不让模型自评成为验收证据；
- 不把任何单一客观指标合成为“音乐质量”；
- 不绕过处理前/处理后两次 Judge 和人类 A/B/ORIGINAL 出口。

## 下一完成标准

选择一个获授权小数据集，至少接入一个 explicit baseline 与一个 latent baseline；在相同输入上产出可复现 Hearing State，完成盲化的人类核对，并证明 provider 替换不会改变 Judge 契约。任何对 protocol/schema/core behavior contract 的正式化须另行提交 MIP。

