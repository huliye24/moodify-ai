# TUNING LOOP 实施计划 V01 — 分轨修音闭环

**Date:** 2026-10-04
**Status:** ACTIVE — P0 已完成，P1 待启动
**Contract:** [docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md](../canon/STUDIO_PRODUCTION_PIPELINE_V4.md)
**MIP:** [protocol/mips/MIP-0002-stem-tuning-loop.md](../../protocol/mips/MIP-0002-stem-tuning-loop.md)
**壳:** `moodify-desktop/`

---

## 1. 起点：审计结论

用户 2026-10-04 提出桌面端流程问题：「检测 → 分轨 → MIDI/曲谱 → 分轨修音 → 再检测对比之前」，
且「每次修音有 A/B 两个方案，最后选择一个」。

审计 `moodify-desktop/` 后确认的 5 条真实缺口：

| # | 缺口 | 证据 |
|---|---|---|
| G1 | 修音作用对象是**整轨母带**，不是分轨；分轨从未进入处理链 | `src/main.js:649` `finishing:run` 与 `:1008` `studio:process` 均以 `resolveCaseSource()`（`:650` / `:1011`）为输入；`stems/*.wav` 全仓只有 `src/pipeline.js:108`（数文件）与 `src/main.js:601`（转 MIDI 的输入）两处用途 |
| G2 | 没有「分轨修音」阶段与工作台 | `src/pipeline.js:509` `CAPABILITIES` 六项中处理类只有 `existing-presets`（作用于整轨） |
| G3 | 现有 A/B 语义是「原版 vs 一条结果」，不是「两个方案」 | `src/main.js:712` `caseSourceRefs` + `:785` `compare:audio`：A 恒为 case 源、B 恒为最新 finishing 产物；`finishing:run` 一次只渲染一个 preset |
| G4 | 复检阶段是空的，`studio/verification/` **无写入方** | 全仓 grep 只命中 `src/pipeline.js` 的 `inspect` / 读取；`STAGES` 中的 `VERIFIED` 永远到不了 |
| G5 | 决策记录只有版本级，没有步骤级 | `src/studio.js:190` `writeSelection` 只记「最后选了哪个版本」 |

**前提事实（决定可行性）：** Core 当前**没有逐轨处理能力，也没有音准修正能力**。
`release_cli` 的处理面只有 `finishing`（整轨 mix graph：EQ / 动态 / 响度 / 立体声）与 `protocol process`；
全仓无 pitch / tune / warp 类算子（`moodify/intervention/` 仅 ±0.5 dB 音色 shelf 修正）。
因此「分轨修音」不是接线，是**新增 Core 能力** → 走 MIP-0002。

---

## 2. 四项已裁定决策（2026-10-04）

| 项 | 裁定 |
|---|---|
| 修音含义 | 两者都要：以 MIDI/曲谱为参考的逐轨音准·节奏修正 **+** 逐轨混音处理 |
| 修音粒度 | 整曲成对 A/B（一次产出两个完整方案，选一） |
| 两案来源 | 系统出两档参数（保守档 / 激进档）自动产 A、B |
| 复检形式 | 对 A、B 重跑完整检测，与原版逐指标对齐 |

契约已定稿于 `docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md`。

---

## 3. 阶段划分

### P0 — 契约定稿（本次完成）

- [x] `docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md`（流程与产物契约）
- [x] `docs/plan/2026-10-04_TUNING_LOOP_PLAN_V01.md`（本文件）
- [x] `protocol/mips/MIP-0002-stem-tuning-loop.md`（Core 能力 MIP 草稿）
- [x] 更新 `AGENTS.md` §6 指向 V4（八阶段 + 可逆性门禁 + 三出口）
- [x] 采纳产品方向「逆向工程 · 多轨复合」，并据此把 ⑤复合 独立成阶段（写入 V4 §1.2）

### P1 — 壳侧阶段模型 + 复检接线（**不依赖 Core 新能力**）

目标：让「检测 → 逆向分解 → 结构 → 修音 → 复合 → 复检 → 选定 → 导出」这条游标真实存在，
且复检是**真的**（Core 已有 `moodify analyze`，只是壳没接线）。

拆成两步：**P1a 内核（已完成）** 与 **P1b 壳侧接线（下一步）**。
之所以拆：`check-contracts.js` 强制 renderer DOM id ↔ preload ↔ IPC 三侧一致，
所以 main / preload / renderer 必须**同一次改完**，不能分半。

#### P1a — 壳侧内核（✅ 已完成 2026-10-04）

| 文件 | 改动 | 状态 |
|---|---|---|
| `src/pipeline.js` | 8 阶段（`TUNED/COMPOSED/RECHECKED` 取代 `PLANNED/RENDERED/VERIFIED`）；`factsOf` 增 `reversible/tuned/composed/rechecked`；`STAGE_TABLE` 增四项；`gates` 增 `canTune/canCompose/canRecheck/canChoose/canExport` 与各自 `*Blockers`；`CAPABILITIES` 去掉三预设、新增 `PLANNED_CAPABILITIES`；②问题/⑤方案 标 RETIRED | ✅ |
| `src/tuning.js`（新） | 修音对产物层 + **三出口**决策账本（`A/B/ORIGINAL`，只追加、`request_id` 幂等）；`aggregate()` 达成度聚合；排序按 `created_at`/mtime 而非 id。**（复验轮补）** ⑦ 准入：`validateDecision` 要求「pair 存在 ∧ A/B 两侧 `mix.wav` 齐 ∧ 复检真实发生」，`decisionBacked` 让读侧同样严格 | ✅ |
| `src/recheck.js`（新） | 三方对齐表，指标取自 `report.json.measurements`；缺 report 拒绝且不产 payload | ✅ |
| `scripts/test-pipeline.js` | 重写为 V4 模型：可逆性门禁（含「只有 `passed===true` 才算」）、成对完整性、阶段链、三出口、快速路径、能力诚实、退场代码不再影响阶段。**（复验轮补）** §5b：⑦ 准入的 7 条（假 pair / 半成品 / 假复检 / 复检报告被删 / `ORIGINAL` 不能绕过 / 读侧不收假记录 / 候选被删则阶段回退） | ✅ 50 断言 |
| `scripts/test-recheck.js`（新） | 9 断言（守恒 / 缺报拒绝 / 非 VALID / 单位不一致 / NaN 不外泄 / 往返） | ✅ |

回归：`check-contracts` ✓、`test-pipeline` 50/50、`test-recheck` 9/9、`test-studio` 21/21、
`check_repo_structure.py` OK（复验轮另加 `test-orchestrator` 11/11、`test-main-ipc` 15/15、`test-session` 24/24，
见 [2026-10-04_DESKTOP_ONE_CLICK_PHASE1.md](2026-10-04_DESKTOP_ONE_CLICK_PHASE1.md) §8）。

**过程中修掉一个真 bug**：pair id 原为秒级时间戳 + 随机后缀，同一秒内建两对时
「最新一对」会随机取错，进而让阶段推导不稳。已改为毫秒时间戳，并把排序权威移到
`pair.json.created_at` / 目录 mtime。

#### P1b — 壳侧接线（✅ 已完成 2026-10-04）

| 文件 | 改动 | 状态 |
|---|---|---|
| `src/main.js` | 删 `pipeline:diagnose/diagnosis/note`、整个 `studio:*` v0.2 段（7 个 IPC）、`./studio` 与 `./backends` 依赖；新增 `tuning:pairs/render/decision/audio/recheck/recheckRun/export`；`pipeline:context` 改为只产 context（不再产「方案」） | ✅ |
| `src/preload.js` | 同步：删 7 个 studio 桥接 + 3 个诊断桥接；加 7 个 tuning 桥接 | ✅ |
| `renderer/index.html` | 删 `view-diagnosis` / `view-plan`；`view-studio` → `view-tuning`（三出口按钮 + 对齐表）；左栏 `rail-studio`→`rail-tuning`、`rail-fix`→`rail-bench` | ✅ |
| `renderer/app.js` | 删诊断/方案两段与 Studio v0.2 段；新增修音段（对列表 / 试听 / 三出口 / 对齐表 / 显式拒绝）；`PIPELINE_STAGES` 改 8 阶段；`stageUnlocked` / `stageLockReason` 接新门禁与 `*Blockers` | ✅ |
| `renderer/style.css` | `.studio-versions/.studio-version` → `.pair-list/.pair-row`；退场的 `.studio-target*` 规则加注记 | ✅ |
| `src/pipeline.js` | RETIRED 段**真正删除**（7 个导出），并由测试锁定「删了而不是留壳」 | ✅ |
| `src/studio.js` / `src/backends/*` | 加 RETIRED 注记；**未删除**（删文件属不可逆动作，待人类确认） | ✅ 注记 |
| `scripts/test-pipeline.js` | §9 改为断言退场 API 确实不存在 | ✅ |

**一个重要的范围修正（我先前判断错了，这里更正）：** 我先前列的「删 `finishing:run`」**没有执行**。
查清后发现它走的是 `moodify finishing new/render`，与已退场的预设产品面
（`backends/local.js` 的 `protocol process`）是**两条不同的代码路径**，而且它是研究侧
「源 vs 结果」A/B 证据的唯一 B 来源。因此把它与 `compare:*` 一并保留为**研究仪器**并加注记，
而不是删掉——于是我之前预告的「render 证据回流中断」**不会发生**。

⚠️ 真实 case 的 `tuning:recheckRun` 验收需要 A、B 两侧都已有 `mix.wav`（P2 才能产出）。
P1b 用静态/合成方式验证了链路与拒绝路径；端到端留到 P4。

### P2 — Core 能力（MIP-0002 通过后）

| 目标 | 落点 |
|---|---|
| 逐轨音准·节奏修正（MIDI 为参考） | 新模块，参考 `moodify/transcription_pipeline/`、`moodify/score_engine/` 现有能力边界 |
| 逐轨混音处理（per-stem finishing） | 扩 `moodify/mix_graph/`，不新建第二套 DSP |
| 两档参数 + 整曲合成 + 修音 evidence | `release_cli` 新增 `tuning` 子命令组 |

约束：**One Core**，新能力必须能被 CLI 与 App 同时调用（`AGENTS.md` 技术宪法）；
两档参数必须标 `UNCALIBRATED_ENGINEERING_DEFAULT`（参数值属于"什么叫更好听"的人类判断）。

### P3 — 壳侧 tuning 接线 + UI 收尾

把 P1 里显式拒绝的 `tuning:render` 替换为真实调用；A/B 双轨试听与盲听流程闭环。

### P4 — 端到端验收 + 证据落账

一次完整 case：检测 → 分轨 → 结构 → 修音(A/B) → 复检 → 选定 → 导出；
`recheck.json` 存档，`decisions.jsonl` 落账，研究侧 evidence 带 delta（复用既有 T2 回流）。

---

## 4. 产物契约速查

```text
<case>/studio/tuning/<pair_id>/
    pair.json              两档参数 + 来源引用（midi / stems）+ calibration_status
    A/  plan.json  stems/*.wav  mix.wav  evidence.json  analysis/report.json
    B/  plan.json  stems/*.wav  mix.wav  evidence.json  analysis/report.json
    recheck.json           ⑥ 三方逐指标对齐表
<case>/studio/tuning/decisions.jsonl    ⑦ 逐步决策（只追加）
<case>/studio/selection.json            ⑧ 最终选定（沿 V3）
```

`pair_id` 形如 `tune_<utcstamp14>_<rand4>`（沿用 `studio.newAttemptId()` 的命名纪律：
唯一性是 load-bearing，Core 拒绝覆盖已存在输出）。

---

## 5. 开放项（阻塞 P2/P3，不阻塞 P1）

见 `STUDIO_PRODUCTION_PIPELINE_V4.md` §10，三项均标 `HUMAN_DECISION_REQUIRED`：

1. 三预设（`clean_master` / `warm_vocal` / `wide_space`）在 V4 里的位置（快速路径终点 / 整轨收尾 / 退场）。
2. 快速完成路径是否保留。
3. ② 问题 是否保留为独立阶段（用户 2026-10-04 的描述未提及 ②）。

**P1 不受这三项阻塞**，因为 P1 只扩阶段游标与复检接线，不决定三预设法。

---

## 6. AGENTS.md 同步（✅ 已完成）

`AGENTS.md` §6 已改为 V4 的八阶段，并写入方向采纳与两条保护机制：

```text
检测 → 逆向分解 → 结构 → 修音 → 复合 → 复检 → 选定 → 导出
```

同步写入的硬约束：

- 产品方向 = 逆向工程 · 多轨复合；其前提**是假设而非事实**，由**可逆性门禁**（仅
  `passed === true` 算通过，不通过则 ④修音 不开）与**第三出口「保留原版」**关住风险；
- ②「问题」不是独立阶段，但「当前规则未发现技术问题」的措辞由 ①检测 承接；
- ④修音 与 ⑤复合 必须分开（否则无法归因「这一步变差是哪一层造成的」）；
- 三预设退场；`preserve` 归 ④修音；两档参数须标 `calibration_status`；
- 成就判定用**聚合**，开一对新实验不得让阶段倒退。

## 7. 风险

| 风险 | 应对 |
|---|---|
| **方向前提可能不成立**（多轨复合未必优于单轨直出，分轨又是预览级） | 可逆性门禁把「坏分解」挡在 ④ 之外；第三出口让「都不如原版」有路可退。**前提仍未被实验验证**，见 V4 §9 |
| Core 能力（P2）迟迟未通过 MIP，壳侧做出无法运行的 UI | `tuning:*` 显式拒绝 `TUNABLE_CORE_NOT_AVAILABLE` 并显示「未实现」，与已退场的 `PLANNED_TARGETS` 同一模式：宁可显示不可用，不做假映射 |
| 两档参数被读成「更好的设置」 | 产物强制携带 `calibration_status`，UI 原样显示 |
| 复检指标集随 Core 版本漂移，对齐表静默缺项 | `not_alignable` 强制列出，缺项不许消失 |
| 分轨是预览级，修音质量受上限约束 | 沿 V3 §5，`engine_note` + `grade` 随产物流动，并在 UI 显示 |
| 门禁「为什么被锁」说不清，显得任意 | 每个阶段都有 `*Blockers`，三种原因分开说 |
| 三预设退场会不会顺手切断研究证据链 | 已核实不会：`finishing:run` 与预设产品面是两条路径，已保留为研究仪器并加注记 |
