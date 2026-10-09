# ThinkPad 004 — Production Graph Parity 表征（只读预备）

**Task:** MOODIFY THINKPAD HEAVY LANE 004 §5A（behavior characterization matrix）
**Branch:** `feat/thinkpad-production-graph-004`（本文件是**唯一**产物；实现未开始，见 §0）
**Date:** 2026-10-09
**方法:** 每个结论标注来源（文件 + 行号 / 测试名）。桌面语义**被表征、不被本线占有**（§4 引用）。未实现的阶段如实标注，不推断。

---

## 0. 依赖门禁状态（§2）—— 这就是实现未开始的原因

| 门禁项 | 状态 | 证据（2026-10-09 复核） |
|---|---|---|
| PR #49 | ✅ MERGED 2026-10-05 | V4 桌面闭环已合入 main |
| PR #48 | ❌ OPEN | tests-only（+371/−1，3 文件，self-described "no production code changes"），`CONFLICTING` 自 2026-10-04，无取代声明；main 无其 `test-pipeline-parity` 等价覆盖（`git ls-tree origin/main` 核实） |
| THINKPAD 002（#66） | ❌ OPEN | compat API 未合并；本任务其 "frozen for this task" 分支未启用（人类 2026-10-09 裁定：等待门禁） |

**人类裁定（2026-10-09）：等待门禁。** 本文件按 §2 "audit/read-only preparation may be done earlier" 产出；实现分支须在门禁解除后从更新后的 main 重新出发（本分支可 rebase 复用）。

## 1. 参考语义来源（characterize, not own）

| 来源 | 角色 | 关键锚点 |
|---|---|---|
| `moodify-desktop/src/pipeline.js`（722 行） | **V4 阶段/事实/门禁的唯一权威**（磁盘推导） | `STAGES` :84、`inspect` :116、`factsOf` :194、`STAGE_TABLE`/`stageOf` :229/:242、`gates` :381、`modeDecision` :325 |
| `moodify-desktop/src/tuning.js`（383 行） | 修音对账本语义（A/B/ORIGINAL、写读共用一道门） | `pairState` :111、`aggregate` :176、`validateDecision` :270、`decisionBacked` :292 |
| `moodify-desktop/src/recheck.js` | 复检契约 schema | `moodify.studio.recheck/0.1` :35 |
| `moodify-desktop/scripts/test-pipeline.js`（812 行，**63 个 pinned check**） | 行为钉住（含回退、quick 不进假、账本门禁） | 见 §6 清单 |
| `moodify-desktop/src/orchestrator.js` + `session.js` | 调度/相位折叠；**自我声明不是第二套状态机**（orchestrator 头注），每轮重新 `snapshot()` | `session.js` `PHASES` :88 |
| `moodify-desktop/src/studio.js` | 旧层（meta / selection / versions）；**不在 V4 阶段推导内** | §10 观察 2 |
| `docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md` | V4 契约（2026-10-04） | §3.4 三概念分离、§4 门禁、§7.1 三出口同门 |

**本机限制（如实）:** ThinkPad 未装 Node.js（`THINKPAD_RUNTIME_ARCHITECTURE.md` §6）——桌面 pinned tests（63 项）只能在 CI（Studio 工作流）或装有 Node 的机器上运行；本线只能跑 Core 侧测试。桌面 parity 的最终验收必须包含一次 CI 全绿记录。

## 2. 阶段矩阵（V4 权威，代码逐行核实）

`STAGES`（pipeline.js:84）与 `STAGE_TABLE`（:229）——每阶段一个 fact，`optional` 表示合法路径可跳过：

| # | 阶段 | fact | 产物前置（磁盘） | optional | 测试锚点（test-pipeline.js） |
|---|---|---|---|---|---|
| 0 | `IMPORTED` | `imported` = caseDir 存在 | `<case>/` 目录本身 | 否（地板） | "a bare directory reports IMPORTED" |
| 1 | `ANALYZED` | `analyzed` = `report.json` 可解析 | `<case>/report.json`（`moodify.msp_report/0.2`） | 否 | "an analysed case reports ANALYZED" |
| 2 | `SEPARATED` | `separated` = `stems/*.wav` ≥1 | `<case>/stems/*.wav`（+`manifest.json` 元数据） | **是**（快速路径跳过） | "deep prerequisites alone reach STRUCTURED…" |
| 3 | `STRUCTURED` | `structured` = `midi/*.{mid,midi}` ≥1 | **MIDI 专属**；MusicXML 永不顶替 | **是** | "score alone is not structure" |
| 4 | `TUNED` | `tuned` = 任一 pair **两侧**各有 `tuned/*.wav` | `<case>/studio/tuning/tune_*/{A,B}/tuned/*.wav` | 否 | "A alone does not reach TUNED" / "both sides reach TUNED…" |
| 5 | `COMPOSED` | `composed` = 任一 pair 两侧各有 `mix.wav` | `<case>/studio/tuning/tune_*/{A,B}/mix.wav` | 否 | "…mixes then reach COMPOSED" |
| 6 | `RECHECKED` | `rechecked` = 任一 pair 有 `recheck.json` | `<case>/studio/tuning/tune_*/recheck.json` | 否 | "a pair with mixes but no recheck stops at COMPOSED" |
| 7 | `CHOSEN` | `chosen` = `decisionBacked`（账本末条**此刻**被完整支撑） | `decisions.jsonl` 末条 + 该 pair 完整 + recheck 三报告在线 | 否 | "a hand-written decision without a backing pair cannot reach CHOSEN" |
| 8 | `EXPORTED` | `exported` = `studio/export/*.json` ≥1 | `<case>/studio/export/*.json` | 否 | （导出路径在 test-studio/export 侧） |

`READY_FOR_TUNE` 被**故意**排除在阶段外（pipeline.js:78 注释）：它是 readiness 事实（`deepReady ∧ reversible`），不是用户做过的事；把它放进游标会让每个分析过的 case 假装前进过。readiness 经 `gates()` 单独报告。

### 2.1 通用阶段名（任务 §5A 例子）↔ V4 现实映射

| 任务例子 | V4 现实 | 状态 |
|---|---|---|
| `OBSERVE` | `ANALYZED`（①检测；findings 在 report 内，②问题已删除） | **READY**（完整） |
| `DECOMPOSE` | `SEPARATED`（快速/预览级 DSP；模型级=可选另一实现） | **PARTIAL**（预览级 grade 自述；母带级未接入默认流） |
| `UNDERSTAND` | 无独立阶段；结构事实在 `studio/structure.json`（bpm/beats/sections 位置编号） | **PARTIAL**（无段落语义标签是设计决策，不是缺口） |
| `PLAN` | 无阶段（V3 ⑤方案已删除；`studio/plans/*.json` 仅旧 case 存在） | **NOT_IMPLEMENTED**（V4 明确删除，非遗漏） |
| `EDIT` | `TUNED`；深度=逐轨（`stem-tuning`，Core 未实现）；快速=整轨两档 pair | **PARTIAL**（快速路径可用；深度被能力门禁锁住，见 §4） |
| `RENDER` | `COMPOSED`；快速=两档 mix；深度=`multi-stem-compose`（Core 未实现） | **PARTIAL**（同上） |
| `VERIFY` | `RECHECKED`（`recheck.json`，三方对齐 original/A/B 报告） | **READY** |
| `COMPARE` | 无独立阶段：A/B/ORIGINAL 比较内嵌于 ⑦ 决策（`EXITS`） | **READY**（以 ⑦ 的一部分存在） |
| `DECIDE` | `CHOSEN`（三出口同一道门，证据支撑才成立） | **READY** |
| `ITERATE` | 无阶段：新开 `tune_*` pair 即迭代；达成度**聚合**（`some`）不倒退 | **READY**（pair 模型 + append-only 账本） |

## 3. 事实推导规则（`factsOf`，pipeline.js:194）

```text
imported   := caseDir 存在
analyzed   := report.json 可解析
separated  := stems/*.wav ≥ 1          （manifest 提供 engine/grade/partition 元数据，不是判据）
structured := midi/*.{mid,midi} ≥ 1     （MusicXML 不顶替）
reversible := studio/roundtrip.json 存在且 passed === true（唯一计分方式；缺/false 均锁）
tuned      := any pair: A.tuned ∧ B.tuned          （单边是半成品，不成事实）
composed   := any pair: A.mix ∧ B.mix
rechecked  := any pair: recheck.json 存在
chosen     := decisionBacked(decisions.jsonl 末条)  （见 §6）
exported   := studio/export/*.json ≥ 1
baseReady  := analyzed                               （readiness 事实）
deepReady  := analyzed ∧ separated ∧ structured      （= deepAssetsReady；readiness 事实）
```

聚合用 `some`（tuning.js:176 `aggregate`），不是"最新一对"：做完一对再开新一对是前进不是后退；`currentPair`（按 `pair.json.created_at`，不按 id——tuning.js:158 注释）只供 UI 显示"现在在操作哪一对"。

## 4. 门禁与三概念分离（V4 §3.4 / §4；pipeline.js:325 `modeDecision`、:381 `gates`）

```text
deepAssetsReady = analyzed ∧ separated ∧ structured          （资产存在）
deepExecutable  = deepAssetsReady ∧ reversible ∧ 深度 Core 能力可用
                  （深度能力 = stem-tuning + multi-stem-compose；两者均在 PLANNED_CAPABILITIES，
                    AVAILABLE_CAPABILITY_IDS 不含 → 今日 deepCoreAvailable 恒 false）
fastAvailable   = analyzed ∧ fast-stereo-pair 能力可用        （今日 true）
```

| 门禁 | 条件 | 今日实况 |
|---|---|---|
| ④ 修音（深度）`canTune` | `deepExecutable` | **锁**（缺 `DEEP_CORE_UNAVAILABLE`；即使 assets+reversible 齐备） |
| ④ 修音（快速）`canTuneQuick` | `fastAvailable ∧ optIn`（optIn=人写的 `studio/finish_mode.json` mode=QUICK_STEREO_ONLY） | 可请求，**绝不自动解锁** |
| 快速入口 `canRequestQuick` | `fastAvailable ∧ ¬deepExecutable ∧ ¬optIn` | 有（且动画徽章必须显示 `快速（仅立体声）`） |
| ⑤ 复合 `canCompose` | `tuned` | 派生 |
| ⑥ 复检 `canRecheck` | `composed` | 派生 |
| ⑦ 选定 `canChoose` | `rechecked`，且 `chooseBlockers = decisionBlockers` | 派生 |
| ⑧ 导出 `canExport` | `chosen`（被完整候选支撑的决策，含 ORIGINAL） | 派生 |

阻断原因码（:299 `DEEP_BLOCKER_LABELS`）：`NOT_ANALYZED` / `NO_STEMS` / `NO_MIDI` / `NO_ROUNDTRIP` / `ROUNDTRIP_FAILED` / `DEEP_CORE_UNAVAILABLE`——每个被锁阶段都带 `*Blockers` 人话数组（"每个被锁的阶段必须说明自己为什么被锁"，V4 §4）。
`mode`（:338）：optIn → `FAST_STEREO_ONLY`（人的选择优先，不被 deepAssetsReady 覆盖回 DEEP）；否则 `deepAssetsReady` → `DEEP`；`modeExecutable` 单独给出"这条路此刻是否真能走完"。

## 5. Quick / Deep parity（§5D 的语义边界）

```text
快速 = 人的显式选择（finish_mode.json）+ 只跳过分解（SEPARATED/STRUCTURED 两个 optional）
       → 仍必须走 ④ TUNED → ⑤ COMPOSED → ⑥ RECHECKED → ⑦ CHOSEN → ⑧ EXPORTED
深度 = 仅当 assets ∧ reversible ∧ 能力三者齐备；缺一即锁，且不因按钮被点而过门
```

钉住的测试：`5. 用户未选择：canTuneQuick=false，且磁盘上不会冒出 pair`、`quick is offered but never auto-unlocked`、`the quick route still must walk 修音→复合→复检→选定`、`8. 深度路径真实可执行时仍默认 DEEP，不自动显示为 FAST`、`9. 已有 pair / recheck / 选定不会被模式选择倒退或破坏`。**结论：新图不得从任何 UI 事件、按钮或 pipeline.json 记录中取 stage——只从 §3 的事实取。**（pipeline.json 自我声明 "记录用，不是权威来源"，:492。）

## 6. 回退语义（§5C）—— 现有代码已被测试钉住的部分

| 回退场景 | 机制 | pinned check |
|---|---|---|
| 删产物 → 游标自行后退 | `snapshot()` 每次重新推导，阶段永不缓存 | "deleting artifacts moves the cursor backwards by itself" |
| 手写 decision 不进 CHOSEN | `decisionBacked` 对账本末条**重新**跑 `validateDecision` | "a hand-written decision without a backing pair cannot reach CHOSEN" |
| 选定后删候选 → CHOSEN 退回 | 同上（候选不在 = 支撑不存在） | "deleting the candidates after a choice takes the CHOSEN stage back" |
| 复检引用的报告被删 → 不算已复检 | `decisionBlockers` 检查 recheck 引用的 original/A/B 三份 report 仍在磁盘 | "a recheck whose referenced reports were deleted is not a recheck" |
| 半成品 pair 不能被选定 | `tuned 单边` / `mixes 无 recheck` 均被拒 | "a half-built pair cannot be chosen" |
| 只读检查、不写盘 | `inspect()` 纯读（:116 注释） | test-pipeline 全量在临时目录复制上运行 |

这五条就是 Core 读模型必须继承的回退不变量；实现阶段的测试类目（§7）与之逐条对应。

## 7. 产物与 schema 清单（表征用；实现时核心读模型的"present_artifacts"）

| 产物 | 路径 | schema（当前 main） | 读取方 |
|---|---|---|---|
| 报告 | `<case>/report.json` | `moodify.msp_report/0.2` | ANALYZED |
| 分轨 | `<case>/stems/*.wav` + `manifest.json` | manifest engine/grade/partition | SEPARATED |
| MIDI / 曲谱 | `<case>/midi/*.{mid,midi}` / `<case>/score/*.{musicxml,xml}` | — | STRUCTURED |
| 可逆性 | `<case>/studio/roundtrip.json` | `moodify.studio.roundtrip/0.1` | reversible 事实 |
| 修音对 | `<case>/studio/tuning/tune_*/pair.json` | `moodify.core.tuning-pair/0.1` | pair 列表 |
| 修音产物 | `…/{A,B}/tuned/*.wav`（快速=单个整轨 wav） | — | TUNED |
| 复合产物 | `…/{A,B}/mix.wav` | — | COMPOSED |
| 复检 | `…/recheck.json` | `moodify.studio.recheck/0.1` | RECHECKED |
| 决策账本 | `<case>/studio/tuning/decisions.jsonl`（append-only） | `moodify.studio.tuning-decision/0.1` | CHOSEN |
| 快速 opt-in | `<case>/studio/finish_mode.json` | `moodify.studio.finish-mode/0.1` | quick 门禁 |
| 记录 | `<case>/studio/pipeline.json` | `moodify.studio.pipeline/0.2` | **无**（非权威） |
| 上下文包 | `<case>/studio/context.json` | `moodify.studio.context/0.2` | 修音输入 |

**观察（留给实现阶段的整合项）：** THINKPAD 002 的 compat 层 `KNOWN_SCHEMAS` 收录的是 `context/0.1`、`pipeline/0.1` 与 `studio.diagnosis/0.1` 等，而当前 V4 写的是 `/0.2`、且 `diagnosis.json` 已无写入方（②⑤删除）。compat 会把 `/0.2` 如实报为 "unknown schema → 不解释"，不算错误但会削弱读模型对**新** V4 case 的归一化。该对齐属于 THINKPAD 002 的 API 演进而非本任务的冻结面——实现阶段须先裁清"冻结的 compat API 是否包含 V4 schema 集合"，否则图对 L3 新 case 的归一化只能退化为按 API 读取的通用产物引用。

## 8. Core 读模型映射草案（Phase B 计划；**未实现**）

原则（REALIGNMENT_001 §11）：`node 语义 = capability_id（或语义角色），provider 身份属于执行策略与 provenance，绝不进入节点语义`。

| 节点（草案） | capability_id / 语义角色 | 状态来源 | 说明 |
|---|---|---|---|
| observe | `audio.analyze` | ANALYZED | findings 留在此节点 evidence |
| decompose.stems | `stem.separate` | SEPARATED | grade 随 manifest 走（预览级/模型级都是同节点） |
| decompose.midi | `midi.transcribe` | STRUCTURED（MIDI half） | |
| decompose.score | `score.generate` | 可选产物 | 永不顶替 MIDI |
| reversibility | 语义角色 `reversibility.check`（Core 侧） | reversible 事实 | 壳侧实现同名不同物，须区分（pipeline.js:521 注释） |
| tune | `pitch.correct` + `timing.correct`（深度，注册表 ABSENT）／语义角色 `tune.pair.fast`（快速） | TUNED | 深度/快速两条实现路径，状态同为 TUNED |
| compose | `mix.render`（快速路径可行）；`multi-stem-compose` 语义角色（深度） | COMPOSED | |
| recheck | `audio.verify` | RECHECKED | |
| choose | 语义角色 `human.decision`（**human_required**） | CHOSEN | 三出口 A/B/ORIGINAL；机器永不代替 |
| export | `delivery.export` | EXPORTED | |

图字段（任务 §5B）：`project_id`、`current_version`（L1 project.json 的资产版本；旧 case = case_id + 无版本语义 → 如实 null）、`nodes`、`next_possible_actions`（= 开放门禁对应的动作，附 blockers 人话）、`human_required`（choose 节点未完成时 true）、`warnings`（unknowns/契约不一致，如 §7 观察）。
L1/L2/L3 经 THINKPAD 002 compat（`inspect_case`）读取；**不新增第二个 legacy parser**（§6F）。compat 未合并期间，图在 main 上无从解析 legacy——这也是门禁项之一。

## 9. 性能预算（Phase B 目标，实测在实现阶段补）

- 图检查 = 目录 stat + 小 JSON 解析（report/roundtrip/pair/recheck/账本），**不含 DSP、不读音频样本**；预期与 `inspect()` 同量级（毫秒级，测试内实测）。
- 哈希复用（§6）：L1 `load_project` 目前每次重验 size+sha256（源文件大则贵）；读模型策略 = **引用已记录哈希**，验证按需触发（e.g. 显式 `--verify` 或完整性事件），绝不在每次图检查时重哈希百 MB 文件。被测对象：empty / partial / deep / legacy 四类各测冷热两组，数字进证据文档。

## 10. 已知问题与待决（实现前须清）

1. **门禁**：#48 与 #66（§0）——本任务是 mainline 处理项，不是本线可自动满足的。
2. **旧层与权威**：`studio.js` 的 `selection.json`/`versions/*`（旧流程）与 V4 的 tuning 账本并存；V4 阶段推导**只**读 tuning 账本（`chosen` 与 selection.json 无关）。实现图时须防止把旧 selection 当 ⑦。留待 parity 报告在实现 PR 中再确认一句"selection.json 不在图中"。
3. **compat schema 集**（§7 观察）。
4. **AGENTS.md 文案**：其 §6 的流程描述仍是 V3（"检测 → 问题 → 分轨 → 结构 → 方案 → 成品"、⑤方案锁定规则），与 V4 canon（②⑤已删除）不一致。AGENTS.md 是权威文件——**不代改**，如实记录，由 mainline 决定措辞同步。→ 已记入 CROSS_LANE_REQUESTS。

## 11. 本文件的范围声明

只读表征：未创建/未修改任何 Core 代码、未触碰 Desktop、未跑桌面测试（本机无 Node）。实现（§5B–§5F）等待 §0 门禁解除后从更新后的 main 开始；届时本矩阵作为 parity 验收清单逐行核对。
