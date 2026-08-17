# Moodify

> **Moodify Music / Moodify Player.**

Moodify 的唯一对外产品面是 **Moodify Music / Player**，第一阶段核心用户动作是 **PLAY**。

```text
Source / Cloud-prepared Track
        ↓
      Moodify
        ↓
       PLAY
```

用户不需要理解内部音频工程、Ear、分轨、后处理、Evidence 或状态机。复杂度由 Moodify 承担，不转嫁给用户。

产品与内部边界、权威顺序见 [docs/canon/](docs/canon/)（`CURRENT_CANON.md`、`PRODUCT_BOUNDARY.md`）。

## Internal Systems

Moodify 内部包含听觉智力与云端生产系统，它们不构成对外产品面：

- **Moodify Ear / Auditory Intelligence** — 内部听觉、判断、验证与研究系统：listen → represent → judge → evidence → uncertainty → learn → verify → controlled intervention。它决定何时**不**干预；它不是对外产品。
- **Cloud Production System** — 内部生产环节：Intake → Identify → Analyze → Stem → Judge → Intervene → Preset Decision → Render → Verify → Evidence → Delivery。
- **Classic Reconstruction** — 内部生产哲学（宪法 v1.0）：以决策而非预设驱动的受控重建（诊断 → 决策 → 立体声优先 → 验证 → 渲染）。它是云端如何准备曲目的方式，不是第二个产品。

## Why Moodify Exists

AI 可以生成海量音频，但生成与聆听是不同能力。一个生成模型可能产出一首曲子，却没有可靠的工程系统回答：

- 波形与频谱里实际发生了什么？
- 结果是否稳定、失真、不平衡、有相位问题、过度密集或结构不一致？
- 判断的哪些部分可测量？
- 如果做了干预，是否真的改善了目标状况？
- 本案例的证据能否改进下一个案例？

Moodify 让机器判断显式且可复现。其确定性算法评审器（`moodify.data_factory.algorithmic_review`，公式 `MFY-ALGO-REVIEW-FORMULA-001`）可在其验证过的、版本化的范围内为案例排名；范围外、证据不足或涉及未决感知判断的案例必须升级到人类评审或以 inconclusive 关闭——自动化不制造确定性。

## Three Engineering / Research Disciplines

### WSE — Wave-Spectral Evolution
**问题：** 声音里发生了什么？研究波形、频谱、响度、相位、声道、残差、瞬态等可测量声学行为。

### MSE — Musical-Structural Engineering
**问题：** 音乐结构是什么？研究 MIDI、乐谱、节奏、乐句、段落、歌词、角色与结构关系。

### PPE — Production Process Engineering
**问题：** 如何可靠地生产并验证？研究生产案例、状态转换、证据工件、质量门、可复现性、权威边界、打包、失败与恢复。

## The Learning / Asset Loop

```text
Production Case
  -> Measurement Record
  -> Evidence Artifact
  -> Theory Update
  -> Moodify Rule Update
  -> Next Production Case
```

Moodify 的长期价值来自**可追溯听觉证据与可复用生产知识**的积累。

## Current Implementation Status

**当前状态入口：** [docs/REPOSITORY_STATUS.md](docs/REPOSITORY_STATUS.md)（指向 Canon + 事实状态；不再是静态历史快照）。

现实快照（2026-08-17，W01-P00 只读扫描）要点：

- **对外产品面**：Moodify Music Android 3.1（APK 已发布，deliverables/releases）、music-web（PWA）、云端 music-platform / BFF（LA）。
- **云端现状**：2 台 VPS（LA 核心 + 杭州数据工厂）运行静态音乐托管 + API 壳 + 数据工厂批处理 + lalal 分离代理容器；无对象存储、无云端 AI 推理、队列近空。
- **仓库能力**：`moodify-core-package` 承载测量（BS.1770-4 响度、EBU 3342 LRA、true-peak 等）、诊断、A/B/C 干预方案、算法评审、证据清单、24/7 数据节点、API/CLI 与本地优先 Android 客户端。完整 Listen→Judge→Intervene→Verify 链路在仓库代码完整，云端尚无生产流量。
- **未合并工作**：重建系列（objective / identity guard / era diagnostic / reconstruction factory）与 Music 产品面位于未合并分支（领先 main 154 commits）。
- 实验与遗留系统与 canonical mainline 显式区分（[Legacy & Experimental Policy](docs/LEGACY_AND_EXPERIMENTAL_POLICY.md)）。

## What Moodify Is Not

- 文本转音乐生成模型；
- DAW 替代品；
- 自动母带承诺；
- 保证每个处理过的文件都"更好"；
- 以预设堆砌冒充智能；
- 没有证据的黑箱评分。

## Repository Authority

仓库权威顺序固定（详见 [docs/canon/AUTHORITY_ORDER.md](docs/canon/AUTHORITY_ORDER.md)）：

1. current explicit human instruction
2. root `AGENTS.md`
3. `docs/canon/*`
4. verified runtime evidence
5. canonical main behavior + tests
6. current subsystem docs
7. experimental docs
8. historical / legacy docs

历史文档不能反向覆盖当前 Canon。

## Scientific Release Assets

- **Product / internal boundary:** [docs/canon/](docs/canon/)（CURRENT_CANON / PRODUCT_BOUNDARY / INTERNAL_SYSTEMS / AUTHORITY_ORDER / CURRENT_ARCHITECTURE）
- **Classic Reconstruction Constitution:** [docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md](docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md)（内部生产哲学）
- **Data protocol:** [DATA_PROTOCOL_V1.md](docs/contracts/DATA_PROTOCOL_V1.md) (frozen)
- **Metric registry:** [METRIC_REGISTRY_V1.md](docs/metrics/METRIC_REGISTRY_V1.md)
- **Reference audio suite:** [REFERENCE_SUITE.md](moodify-core-package/benchmarks/reference_audio/REFERENCE_SUITE.md)
- **Golden Production Case:** [examples/golden_case](examples/golden_case/)
- **Citation:** [CITATION.cff](CITATION.cff)

## Scope and Limitations

- 当前主链测量并干预**音频**；音乐结构（MSE）与研究/实验模块不在冻结的 1.0 表面。
- 指标仅在冻结扫描配置（`MFY-WSE-SCAN-PROFILE-001`）下可信；配置变更需要新版本与显式数据分离。
- 算法评审器是已验证范围内的确定性技术排名，不是艺术质量声明；范围外或未决感知案例需要人类评审或 inconclusive。
- 不提交私人音频、API Key 或未授权数据集。

## Core Python Package

当前稳定的本地引擎位于：

```text
moodify-core-package/
```

```bash
cd moodify-core-package
pip install -e .
pip install -e ".[dev]"
```

```bash
moodify presets
moodify analyze song.wav
moodify process song.wav --preset clean_master
```

CLI 示例代表当前窄实现，不是 Moodify 的最终边界。

## Development Principle

> Identity comes before feature expansion.

新增子系统前先问：

1. 它服务于听觉智能的哪一部分？
2. 它产生什么证据？
3. 证据存在哪里？
4. 它是 canonical、experimental 还是 legacy？
5. 它是否改进下一个生产案例？

无法回答这些问题的功能不应自动进入 mainline。改变产品身份、内部/外部边界、状态机权威、证据权威、云控制权威或数据权威的任务必须声明 `CANON_CHANGE = YES`（见 [docs/canon/CURRENT_CANON.md](docs/canon/CURRENT_CANON.md)）。

## Data and Privacy

核心工作流可以本地优先。不提交：私人音频、API Key、未授权数据集、生成的重量级工件、本地 IDE 状态。外部模型、API、音频与数据集保留其自身许可与权利。

## License

Moodify is licensed under **GNU GPL v3.0 only** unless otherwise stated.

See `LICENSE`.
