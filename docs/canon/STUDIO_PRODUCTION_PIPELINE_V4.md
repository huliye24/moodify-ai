# STUDIO PRODUCTION PIPELINE V4 — Moodify

**Version:** 4.0
**Date:** 2026-10-04
**Status:** **DEFINED** — 流程与产物契约。执行范围见 §8。
**Authority:** root `AGENTS.md` → `docs/canon/*`
**Supersedes:** `STUDIO_PRODUCTION_PIPELINE_V3.md`（V3 保留为历史；「分解先于处理」原则被 V4 继承）
**Human decision:** 2026-10-04，共六项裁定 + 一项方向采纳，见 §1.1 / §1.2
**Related:** [PRODUCT_DEFINITION_V3.md](PRODUCT_DEFINITION_V3.md) · [TECHNOLOGY_PRINCIPLES.md](TECHNOLOGY_PRINCIPLES.md) · [../plan/2026-10-04_TUNING_LOOP_PLAN_V01.md](../plan/2026-10-04_TUNING_LOOP_PLAN_V01.md) · [../../protocol/mips/MIP-0002-stem-tuning-loop.md](../../protocol/mips/MIP-0002-stem-tuning-loop.md)

---

## 0. 核心原则

> **Understand first. Decompose second. Tune third. Compose fourth. Verify fifth.**
> 先理解，再分解，再修音，再复合，最后复检。

V3 的原则是 `Understand → Decompose → Plan → Process`：处理放在最后一步，作用对象是**整轨母带**，
三预设是它的工具。2026-10-04 的裁定与方向采纳拆掉了这条路径的三个支点：

1. 处理的作用对象从**整轨**下移到**分轨**，并且需要 MIDI 作为音准与节奏的参考；
2. **修音与复合分成两个阶段** —— 修音改每根轨，复合决定它们如何叠在一起；
3. 处理之后必须**再检测一次**、与原版逐指标对齐，然后才允许选定；
4. **三个预设退场**，**②「问题」不再是独立阶段**。

**产品方向（2026-10-04 采纳）：逆向工程 → 多轨复合。**
AI 音乐是单轨直出；单轨直出不如多轨复合。所以先把它逆向分解成多轨，逐轨修音，再复合 ——
**多轨复合才是 AI 后处理的核心操作**。

这条方向的**前提是一个假设**（「多轨复合一定优于单轨直出」），而它依赖的分离引擎目前是预览级。
所以 V4 不靠相信来保证它，而是用两道机制把风险关住：

- **可逆性门禁**（§4.1）：分解 → 复合（不处理）必须回到原版。这是分解质量的唯一可测代理
  （原分轨不可知，见 §5.4）。**门禁不通过，④ 修音不开。**
- **第三出口**（§7）：A / B / **保留原版**。若两档都不如原版，必须有路可退。

有了这两条，即使前提只部分成立，系统也不会输出比原版差的东西 —— 这是「按直觉去做」
与「不谎报」能同时成立的地方。

---

## 1. 规范流程

```text
①  检测    ANALYZE     数据 / 频谱 / 图表 → report.json
②  逆向分解 SEPARATE    快速分离（预览级，见 §5.2）→ stems/*.wav + manifest.json
③  结构    STRUCTURE   MIDI / 曲谱 → midi/*.mid（曲谱为派生解读，不顶替 MIDI）
④  修音    TUNE        逐轨音准·节奏修正 + 逐轨处理 → tuning/<pair>/{A,B}/tuned/
⑤  复合    COMPOSE     逐轨混音 + 整曲合成，两档 → tuning/<pair>/{A,B}/mix.wav
⑥  复检    RECHECK     对 A、B 重跑完整检测并与原版对齐 → recheck.json
⑦  选定    CHOOSE      A / B / 保留原版，逐步落账 → decisions.jsonl
⑧  导出    EXPORT      交付编码 → studio/export/
```

### 1.1 六项人类裁定（2026-10-04）

| 项 | 裁定 | 含义 |
|---|---|---|
| 修音含义 | **两者都要** | (a) 以 MIDI 为参考的逐轨**音准·节奏修正**；(b) 逐轨**混音处理** |
| 修音粒度 | **整曲成对 A/B** | 一次产出两个**完整方案**（各含全部轨道 + 整曲合成），A / B 选一 |
| 两案来源 | **系统出两档参数** | 同一条链按**保守档 / 激进档**自动产 A、B；人不编辑参数 |
| 复检形式 | **重跑完整检测对齐原版** | 对 A、B 各自重跑完整 analyze，与原版逐指标对齐 |
| 三预设 | **直接退场** | `clean_master` / `warm_vocal` / `wide_space` 退出产品面 |
| ② 问题 | **去掉** | 不单设阶段；Core `findings` 留在 ①检测 的 report 里 |
| `preserve` | **并入 ④ 修音** | 「该保护什么」迁到 ④ 的输入侧，由人填 |
| 快速完成路径 | **保留** | 引擎 = 对整轨的两档处理（无 MIDI → 只做混音，不做音准修正） |

### 1.2 方向采纳（2026-10-04）

> 「逆向工程 · 多轨复合」作为桌面端产品理念采纳，按此落地。

由此产生三项结构性决定（**本次按此实施**，可否决）：

| 决定 | 理由 |
|---|---|
| **⑤ 复合独立成阶段** | 用户定义「多轨复合是 AI 后处理的核心」；而它若只是 ④ 的副产品 `mix.wav`，就无法回答「这一步变差是哪一层造成的」 |
| **新增可逆性门禁** | 见 §4.1 |
| **⑦ 增加第三出口「保留原版」** | 见 §7 |

---

## 2. 与 V3 的差别

| V3 | V4 | 原因 |
|---|---|---|
| ①检测 → ②问题 → ③分轨 → ④结构 → ⑤方案 → ⑥成品 | ①检测 → ②逆向分解 → ③结构 → ④修音 → ⑤复合 → ⑥复检 → ⑦选定 → ⑧导出 | 裁定与方向重塑了后半程 |
| ② 问题 是独立阶段 | 去掉；findings 留在 ①检测 的 report 里 | 裁定「② 去掉」 |
| ⑤ 方案 = 人 / AI 写 `plans/*.json` | 并入 ④修音（系统生成两档参数集） | 裁定「系统出两档参数」 |
| ⑥ 成品 = 对**整轨**套三预设 | ④修音 + ⑤复合 = 对**分轨**修音再复合 | 裁定「分轨进行修音」 |
| 三预设是 ⑥ 的工具 | **三预设退场** | 裁定「直接退场」 |
| 无分解质量检验 | **可逆性门禁** | 方向采纳；分解质量必须可测，否则前提无法被证伪 |
| `VERIFIED` 阶段无写入方（空阶段） | ⑥ 复检 = 有真实写入方（`src/recheck.js`） | 裁定「最后再检测和对比之前」 |
| A / B = 原版 vs 一条结果 | A / B = 同一步的两个**完整方案**；外加 **ORIGINAL** | 裁定「每次修音有 A/B 两个方案」+ 最小变换 |
| 决策记录只有版本级 `selection.json` | 逐步账本 `tuning/decisions.jsonl`（三出口） | 需要「这一步选了哪案」的可追溯记录 |

---

## 3. 阶段状态由产物推导

```text
ANALYZED    ← report.json 存在
SEPARATED   ← stems/*.wav 非空
STRUCTURED  ← midi/*.mid 非空                  （曲谱不顶替 MIDI）
TUNED       ← studio/tuning/<pair>/{A,B}/tuned/*.wav 两侧都非空
COMPOSED    ← studio/tuning/<pair>/{A,B}/mix.wav 两侧都在
RECHECKED   ← studio/tuning/<pair>/recheck.json 存在
CHOSEN      ← decisions.jsonl 的最新一条**此刻仍被一对完整候选 + 真复检支撑**（§7.1）
EXPORTED    ← studio/export/ 有记录
```

### 3.1 达成度用聚合，不用「最新一对」

`TUNED` / `COMPOSED` / `RECHECKED` 判定为**任一修音对达到即可**，而不是只看最新的一对。
理由：做完一对再去开新的一对，是往前走，不是往回退。若只看最新一对，开一个新实验就会让阶段
倒退 —— 那会谎报「进度丢了」。

`currentPair`（最新一对）仍然存在，但它只回答「现在在操作哪一对」，不参与阶段推导。

### 3.2 「最新一对」按时间判，不按 id 判

pair id 形如 `tune_<YYYYMMDDHHMMSSmmm>_<rand4>`。**id 不是排序权威**：时间戳只到毫秒，
同毫秒内建两个 pair 时随机后缀会让顺序随机，而 `currentPair` 参与 UI 决策。
排序以 `pair.json.created_at` 为准，缺它时退回目录 mtime。

### 3.3 记录不是权威

`<case>/studio/pipeline.json` 只是**记录**。每次读取都从磁盘产物重新推导：
删掉 tuning 目录后状态必须自动退回。一个写着「已修音」而文件已不在的状态就是谎报。

**`READY_FOR_TUNE` 不出现在阶段游标里。** 沿用 V3 的教训：它是就绪度事实
（= `deepAssetsReady ∧ reversible ∧ 深度能力可用`），由 `gates().canTune` 表达。

### 3.4 三个必须分清的概念（2026-10-04 人类裁定）

```text
deepAssetsReady = analyzed ∧ separated ∧ structured          深度前置**资产**存在
deepExecutable  = deepAssetsReady ∧ reversible
                  ∧ 深度 Core 能力可用（stem-tuning + multi-stem-compose）   深度路径**现在能跑**
fastAvailable   = analyzed ∧ fast-stereo-pair 能力可用        快速路径**能跑**（整轨两档）
```

**「有 stems + MIDI」只证明资产存在，不再等价于「深度路径当前可执行」。** 把两者混为一谈，
就会在深度 Core 尚未就绪时制造不可恢复的死路（见 §4.2 与 §9）。
`gates()` 同时给出 `deepAssetsReady` / `deepExecutable` / `fastAvailable` 三个布尔值，
UI 的入口与文案据此决定，不再凭 `deepReady` 一个名字猜。

---

## 4. 门禁

```text
④ 修音（深度）：需要 deepAssetsReady ∧ 可逆性通过 ∧ 深度 Core 能力可用
       —— 三者缺一都不可执行：缺 MIDI 就没有音准·节奏的参考；缺可逆性就没有分解质量的代理；
         缺 Core 能力就没有实现。**当前第三项不成立**（逐轨修音/复合尚未实现，见 §8 C）
④ 修音（快速）：需要 analyzed ∧ 快速整轨两档能力可用 ∧ 人**已显式选择** QUICK_STEREO_ONLY
⑤ 复合：需要 ④ 已产出成对的 tuned 产物（两侧都非空）
⑥ 复检：需要 ⑤ 已产出成对的 mix.wav
⑦ 选定：需要 ⑥ 已完成（recheck.json 存在）**且这一对此刻仍完整**（§7.1）
⑧ 导出：需要 ⑦ 已有一条**被完整候选支撑**的决策记录（A / B / ORIGINAL 皆可）
```

**DIAGNOSED 不再是前置**（② 已去掉）。V3 的
`deepReady = analyzed ∧ diagnosed ∧ separated ∧ structured`
因此收紧为 `analyzed ∧ separated ∧ structured`（= `deepAssetsReady`）。

**每个被锁的阶段必须说明自己为什么被锁。** `gates()` 对每个阶段都给出
`*Blockers` 数组（`tuneBlockers` / `composeBlockers` / `recheckBlockers` / `chooseBlockers` /
`exportBlockers`），因为「缺分轨」「缺 MIDI」「可逆性未通过」是三个不同的问题、三种不同的补救，
把它们压成一个灰按钮就是让门禁显得任意。

### 4.1 可逆性门禁

> 分解是**信息有损**的。既然原分轨不可知（§5.4），"还原得对不对"就无法回答；
> 能回答的是"分解 → 复合（不做任何处理）是否回到原版"。

判据来自 `<case>/studio/roundtrip.json`（由 Core 产出）：

```json
{ "schema": "moodify.studio.roundtrip/0.1",
  "engine": "dsp_center_hpss",
  "grade": "PREVIEW_NOT_MASTERING_GRADE",
  "passed": true,
  "measured": { "max_sample_error_dbfs": -72.4, "correlation": 0.9999 } }
```

```text
reversible = roundtrip.json 存在 ∧ passed === true
```

**只有显式 `passed: true` 才算通过。** 缺文件、`passed: false`、`"true"`、`1` 一律不算 ——
门禁绝不自行推断一个通过。缺文件时 `canTune` 为 false，UI 说明「可逆性未验证（Core 尚未产出）」。

这一条同时是**方向前提的保护阀**：只要引擎无法证明可逆，④ 就不开，
系统就不会在坏分解上叠出比原版更差的复合。

### 4.2 快速完成（仅立体声）

不分解就没有 MIDI，也就无从做音准·节奏修正。快速完成是一个**旁路**，它：

- 必须由人**显式选择**（`<case>/studio/finish_mode.json`，带 `chosen_at`），**绝不自动解锁**；
- 引擎是**对整轨的两档处理**（保守 / 充分），**只做混音处理，不做音准·节奏修正**；
- **不得**打开需要分轨的 ④ 修音（深度意义的修音不成立）；其产物同样落在
  `tuning/<pair>/<side>/tuned/`（单个整轨 wav）与 `mix.wav`，因此阶段判据与深度路径统一；
- 徽章必须显示 `深度完成` / `快速（仅立体声）`。

**快速完成仍然必须走 ⑤复合 → ⑥复检 → ⑦选定 才能 ⑧导出。** 它跳过的是**分解**，不是验证。
否则它就成了「AI 处理完直接交付」，正是本仓库禁止的黑箱路径。

#### 4.2.0 何时提供快速入口（2026-10-04 人类裁定，取代旧规则）

```text
deepExecutable（§3.4）为真   → 默认保持 DEEP，不显示快速入口
deepExecutable 为假          → **提供显式快速完成入口**（canRequestQuick = true）
用户未选择                   → 不生成任何快速候选
用户明确选择                 → 记录 FAST_STEREO_ONLY，模式变为 FAST，按快速路径继续
```

- 判断依据是 `!deepExecutable`，**不再**是 `!deepAssetsReady`。
  旧规则（「只要分轨 + MIDI 存在就隐藏快速入口」）在深度 Core 尚未就绪时会产生不可恢复死路：
  `canTune = false`（无逐轨能力）+ `canRequestQuick = false`（资产已存在）→ 用户拿不到任何候选。
  这不是用户操作错误，而是门禁组合的产品缺陷。
- **人的显式选择优先于 `deepAssetsReady`。** 一旦写下 `QUICK_STEREO_ONLY`，`mode` 就是
  `FAST_STEREO_ONLY`，**不再**因分轨/MIDI 存在而被覆盖回 DEEP；`canTuneQuick === true`。
  人想回到深度路径，需要显式清除该选择（当前无 UI 入口，属未来工作）。
- **切换本身不生成音频**：只写 `finish_mode.json`。候选仍由同一次「开始完成」调用 Core
  `tuning render-pair` 产出。
- **切换不删除、不移动、不覆盖任何深度资产**（stems / MIDI / score / roundtrip / 失败证据）。
  已存在的产物在相位条里显示为 `done`（它确实做过），只有**这条路不经过**的步骤才显示
  `skipped`；把已有资产显示成「不存在」同样是谎报（§4.2.1）。

#### 4.2.1 引擎（2026-10-04 已实现，EXPERIMENTAL）

Core 侧：`moodify tuning render-pair --mode fast-stereo-only --source <wav> --output-dir <pair_dir>`
（实现 `moodify-core-package/src/moodify/tuning.py`，契约 **MIP-0002 附录 A**）。一次调用产生
**一对**完整候选，A = `conservative`、B = `full`；每侧带 `plan.json`（全部实际参数）、
`mix.wav`、`tuned/source.wav`、`evidence.json`（含 source/output sha256、graph digest、
before/after 测量、invariant、peak gate、`review_required: true`、`calibration_status`）。
两档参数目前是**工程默认值**（`UNCALIBRATED_ENGINEERING_DEFAULT`），人类尚未校准；
`full` 只表示「变化更充分」，**不是「更好」**。

发布规则（§4.4 级纪律）：先写临时 attempt 目录，A、B 与 evidence **全部成功**后才原子重命名成正式
`tuning/<pair_id>`；任何一侧失败都不发布，正式目录里绝不会出现半成品；已有目录绝不覆盖；源音频绝不写入。

Desktop 侧（`src/session.js` / `src/main.js`）：显式选择后，一键启动只跑
**修音/复合 → 复检**，当前模式不经过的相位标为 `skipped`（不是待办、不是失败：这条路本来就不经过
它们）；已经存在的深度资产显示为 `done` 并保留在「制作详情」里。**深度路径不因快速可用而解锁**：
`canTune` 仍然要求 `deepExecutable`，深度 ④ 仍返回 `TUNABLE_CORE_NOT_AVAILABLE`。

`gates` 因此同时给出多套说明：`tuneBlockers`（当前模式对 ④ 的阻断，快速路径生效时为空）、
`deepTuneBlockers`（深度路径为什么仍锁着）、`deepBlockers`（逐条原因码），
它们不可互相顶替。

---

## 5. 修音与复合的诚实边界

### 5.1 两档参数未校准

两个档位是人类听觉判断，不是校准过的技术阈值。`pair.json` 的每一档都必须携带
`calibration_status`；未校准时必须为 `UNCALIBRATED_ENGINEERING_DEFAULT`，
UI 与产物不得把它读成「更好的设置」。

### 5.2 分轨是预览级

若输入分轨来自 `dsp_center_hpss`（V3 §5），产物必须继续携带 `engine_note` 与
`grade: PREVIEW_NOT_MASTERING_GRADE`，并且这一点必须**显示给用户**，不能只写在文件里。
**分离质量是整个链条的上限**：MIDI 质量依赖它，修音质量依赖 MIDI，复合质量依赖修音。

### 5.3 `preserve`（该保护什么）挂在 ④ 修音

听觉判断，默认留空由人填。它是修音必须遵守的约束 —— 与「最小变换」一致。
修音不得在未记录 `preserve` 的情况下宣称"保护了音色"。

### 5.4 MIDI 不是真值，也不是单轨的还原物

MIDI 是**符号近似**：它给出音高与节奏结构，给不出音色、气息、咬字、律动微差、混响、力度。
所以它的定位是**修音的参考系**，不是「还原了每一个单轨」。
证据优先级不变（V3 §6）：音频证据 > 分轨音频 > 测量特征 > MIDI / 曲谱解读。

### 5.5 修音与复合必须分开落盘

`tuned/`（逐轨）与 `mix.wav`（整曲）是两个独立产物。合在一起就无法回答
「这一步变差是哪一层造成的」，而**可归因**是本流程的硬要求。

---

## 6. 复检契约（三方对齐）

实现：`moodify-desktop/src/recheck.js`（纯函数，测试：`scripts/test-recheck.js`，9 条断言）。

`studio/tuning/<pair>/recheck.json` 是**逐指标对齐表**，不是一段描述：

```json
{
  "schema": "moodify.studio.recheck/0.1",
  "pair_id": "tune_<utcstamp17>_<rand4>",
  "generated_at": "<iso8601>",
  "mode": "DEEP | FAST_STEREO_ONLY",
  "original": { "report": "…", "measurement_count": 51, "source": {}, "metrics": {} },
  "A": { "report": "…", "measurement_count": 51, "metrics": {}, "delta_vs_original": {} },
  "B": { "report": "…", "measurement_count": 51, "metrics": {}, "delta_vs_original": {} },
  "alignable": ["<三侧都有的指标 id>"],
  "not_alignable": [{ "name": "<id>", "reason": "<为什么不可比>" }],
  "summary": { "alignable_count": 0, "not_alignable_count": 0, "A_changed_metrics": 0, "B_changed_metrics": 0 },
  "note": "本表只对齐 Core 实际产出的指标；缺项如实列出，不补算。"
}
```

纪律（全部由测试逐个断言）：

```text
指标来源       report.json 顶层 measurements: [{id, value, unit, status, group}]
               —— 用「这一次运行」的权威测量集，不用 case 级 measurements.json 快照
alignable      三侧都有 ∧ 单位一致 ∧ 三侧 status 均为 VALID ∧ 三侧均为数值
not_alignable  其余全部，逐条写明原因（缺失于哪一侧 / 单位不一致 / 非 VALID / 非数值）
守恒            alignable ∪ not_alignable = 三侧出现过的全部 id，一个不丢、一个不加
缺 report       返回 MISSING_REPORT 且**不产出任何 payload** —— 不留一张看起来"已复检"的空表
```

**不得发明测量事实**（沿 V3 §9）：新 report 里没有的指标，只能出现在 `not_alignable`。
对齐数量**不代表哪个方案更好** —— 那是听觉判断，属 ⑦ 选定。

---

## 7. 决策记录与第三出口

实现：`moodify-desktop/src/tuning.js`。

- `studio/tuning/decisions.jsonl`：**逐步**记录每次选择，只追加、不可修改：
  `{ schema, pair_id, kept, role, note, at, request_id }`
- **`kept` ∈ `A` / `B` / `ORIGINAL`。第三出口 `ORIGINAL` = 保留原版。**
  若两档都不如原版，用户必须有路可退 —— 否则「最小变换」只是口号。
  系统在净增益为负时**应当主动推荐 `ORIGINAL`**。
- 带 `request_id` 时**幂等**：同一次待决选择重试不会写入第二条。
  同一个 `request_id` 换了 `pair_id` 或 `kept` 是**调用错误**，返回 `REQUEST_ID_CONFLICT`，
  不静默返回旧结果（否则界面会显示「已选 A」而人点的是 B）。
- ⑦ 在已选之后**仍然可进入**（人可以改主意）；账本里最后一条为有效记录。
- **任何一档都不得被自动称为「完成」。** `Generated is not finished.` 不变。

### 7.1 ⑦ 的准入：三个出口用同一道门

`appendDecision()`（写）与 `chosen` 事实（读，经 `decisionBacked()`）共用**同一条规则**
`validateDecision()`。二者必须一致：只写不读会让假记录留在账本里推进阶段，只读不写会让界面与
真实准入脱节（按钮能点、点了被拒）。

一次选择成立，必须同时满足：

```text
1. 修音对存在         <pair>/pair.json 可解析
2. 两侧候选都完整     A、B 各有 mix.wav（「A/B 的语义始终是两个完整候选」，单边是半成品）
3. 复检真的发生过     recheck.json 存在 ∧ schema 匹配 ∧ pair_id 是本对
                      ∧ 它对齐的三份 report 仍在磁盘上
```

**`ORIGINAL` 也在门内。** 它是「两档都不如原版」的出口，不是「还没做过 A/B 就能直接交原版」的
捷径 —— 否则 ⑧导出 可以绕开整个审听把原版交出去，而流程会被推成 CHOSEN/DONE。
这与「未完成不得被显示成完成」是同一条纪律。

**读侧同样严格**：`chosen` 不是「账本里有一行」而是「有一行**此刻仍被**一对完整候选支撑」。
旧版本写的、手写的、或候选后来被删掉的记录都不能把阶段推到 CHOSEN，也**不能**解锁 ⑧导出。
`tuning:export` 除账本一致外还要求 `validateDecision` 仍然通过；候选没了就退回未完成。

---

## 8. 本版本（TASK 003）实现范围

分三层，**不可混淆**：

```text
A. 壳侧内核 —— 已完成 ✓
   ✓ 阶段模型：8 阶段 + 每阶段 *Blockers（src/pipeline.js，测试 40 条断言全过）
   ✓ 可逆性门禁：canTune = deepReady ∧ reversible；只有 passed===true 才算通过
   ✓ 三出口账本：src/tuning.js（幂等、只追加、ORIGINAL 一等公民）
   ✓ 达成度聚合：开新的一对不倒退；currentPair 按时间判不按 id 判
   ✓ ⑥ 复检对齐表：src/recheck.js（9 条断言全过）
   ✓ 能力清单：三预设已移出；未实现的 Core 能力进 PLANNED_CAPABILITIES

B. 壳侧接线 —— 已完成 ✓（2026-10-04）
   ✓ main.js：删除 ②问题 的 3 个 IPC、整个 studio:* v0.2 段（7 个 IPC）、`./studio` 与 `./backends` 依赖
   ✓ main.js：新增 tuning:pairs / render / decision / audio / recheck / recheckRun / export
   ✓ preload.js / renderer：删除 view-diagnosis 与 view-plan；view-studio → view-tuning（三出口 + 对齐表）
   ✓ 三预设：产品面退场（`studio:*` 全部移除）；`src/studio.js` / `src/backends/*` 加 RETIRED 注记后
     留在磁盘上供审阅（删除文件属不可逆动作，待人类确认）
   ✓ pipeline.js：②问题 / ⑤方案 的导出已真正删除（不是留壳），并有测试锁定

B2. 一键完成会话（Phase 1）—— 已完成 ✓（2026-10-04）
   ✓ `src/orchestrator.js`：调度循环。阶段权威仍是 pipeline.js；每轮重新从产物推导，
     已完成的步骤自动跳过（关掉再打开能接着跑）；步骤函数由 main.js 注入，因此可 headless 测
   ✓ `src/session.js`：6 相位投影（检测 → 逆向分解 → 结构 → 可逆性 → 修音/复合 → 复检）、
     两种阻断（`MISSING_CAPABILITY` = 产品缺能力，重试无用 / `STEP_FAILED` = 这一步真实失败，
     修好后可重试）、进程内重入保护
   ✓ main.js：一键与手动按钮走**同一批**真实步骤函数（analyze / separate / structure / tune / recheck）；
     `runLong` 非零退出时带回子进程最后一行输出（失败必须带原因，不能只给退出码）
   ✓ ⑦ 准入三道门（§7.1）同时用在写入侧与读取侧
   ✓ 回归（2026-10-04 复验）：check-contracts ✓（新增「会话相位 → main 步骤」静态合约）、
     test-pipeline 50/50、test-recheck 9/9、test-session 24/24、test-orchestrator 11/11、
     test-main-ipc 15/15、test-studio 21/21、check_repo_structure OK

B3. 快速完成（仅立体声）两档候选（Phase 2）—— 已完成 ✓（EXPERIMENTAL，2026-10-04）
   ✓ Core：`moodify/tuning.py` + `moodify tuning render-pair`（MIP-0002 附录 A）。
     两档 descriptor 显式列出全部节点参数；复用既有 `mix_graph` 会话（一个 DSP 权威）；
     每侧 evidence 内嵌 Core 的 mix-graph evidence 原文；硬门禁（可解码 / 时长 / SR / 声道 /
     finite / 峰值）逐条测量并强制；A、B 全部成功才原子发布；已有目录与源音频绝不覆盖；
     两档输出若逐字节相同则拒绝发布（两个相同候选不是两个候选）
   ✓ Desktop：`sessionTune` 与 `tuning:render` 共用 `renderFastPair()`（一次 Core 调用）；
     模式感知的相位投影（快速路径跳过 ②③ 与可逆性，不假装做过）；模式徽章持续可见；
     未显式选择时绝不走快速路径；深度路径仍 `TUNABLE_CORE_NOT_AVAILABLE`
   ✓ 回归（2026-10-04）：Core `pytest` 1207 passed / 5 skipped（含 `tests/test_tuning_pairs.py` 22 条）、
     Desktop test-session 31/31、test-pipeline 51/51、test-orchestrator 16/16、test-main-ipc 24/24
     （其中 9 条跑真实 Core 的纵向闭环）、test-recheck 9/9、test-studio 21/21、
     check-contracts ✓、check_repo_structure OK
   → 实现报告：[`../reports/2026-10-04_DESKTOP_ONE_CLICK_PHASE2_IMPLEMENTATION.md`](../reports/2026-10-04_DESKTOP_ONE_CLICK_PHASE2_IMPLEMENTATION.md)

C. Core 能力（需要 MIP-0002 通过）
   ✓ **FAST_STEREO_ONLY 两档整轨 pair**（MIP-0002 附录 A）—— 已实现，EXPERIMENTAL，
     参数为未校准的工程默认值
   ✗ 可逆性验证（roundtrip.json）
   ✗ 逐轨音准 · 节奏修正（以 MIDI 为参考）
   ✗ 逐轨混音处理 + 整音合成（⑤复合）+ 整轨两档（快速完成引擎）
   → 见 protocol/mips/MIP-0002-stem-tuning-loop.md

D. 未实现（不得写成已实现）
   ✗ 精细分离引擎
   ✗ 移动端同步 / 网络
```

**Core 能力未就绪时，壳的 `tuning:render` 显式拒绝**（返回 `TUNABLE_CORE_NOT_AVAILABLE` 并附
`PLANNED_CAPABILITIES` 说明），**不写任何文件**。这与 V3「拒绝半成品方案」是同一条纪律。

**一处如实说明（研究仪器的例外）：** `finishing:run` 与 `compare:*` 保留着。它们是**研究侧**
证据采集通道（「源 vs 处理结果」的 A/B + 判断落账），与 V4 的产品流程正交，且
`finishing:run` 走的是 `moodify finishing new/render` 这条**与已退场的预设产品面不同**的代码路径。
两者都已在代码里标注为研究仪器、非产品面；待 Core 的 tuning render 就绪后删除。
**三预设作为产品面已退场这一事实不受影响**——`src/backend` 的 `protocol process` 预设作业已无人调用。

---

## 9. 已知限制（如实记录）

- **诊断仍很薄，且没有独立出口**：Core 只产 `CLIPPING_PRESENT` / `TRUE_PEAK_MARGIN_EXCEEDED`，
  多数真实 case 无 finding。② 去掉后 findings 只在 ①检测 的 report 里可见。
  UI **仍然必须**说「当前规则未发现技术问题」，**绝不**说「这首歌没问题」。
- **复检只能对齐 Core 当次实际产出的指标。** 指标集可能随 Core 版本变化，
  变了的必须靠 `not_alignable` 说出来。
- **分轨是预览级**，④ 与 ⑤ 的绝对质量受此上限约束。
- **两档参数未校准**，A 保守 / B 充分只是工程默认。
- **「多轨复合优于单轨直出」仍是假设**，尚未被实验验证。可逆性门禁 + 第三出口是它的
  安全网，不是它的证明。
- **快速路径的两档参数是未校准的工程默认值。** 机器可以测量 A/B 的差异，但「哪一档更好」
  只能由人听出来；谁是这两档参数的签字人仍未定（MIP-0002 Unresolved #1）。
- **深度路径当前在任何 case 上都不可执行**（逐轨 Core 能力未实现），因此按 §4.2.0
  快速入口对所有已检测的 case 都成立。这是**如实反映现状**，不是把捷径变成默认路径：
  未选择就不生成候选，且人的显式选择优先。
- **已消除的路径死锁（历史记录）：** 2026-10-04 之前，「分轨 + MIDI 已存在但可逆性未通过」
  的 case 三处门禁全为假（`canTune` / `canTuneQuick` / `canRequestQuick`），用户拿不到任何候选。
  人类裁定改为按 `!deepExecutable` 提供快速入口（§4.2.0），
  见 [`CANON_CHANGELOG.md`](CANON_CHANGELOG.md) 2026-10-04 条目。

---

## 10. 裁定记录（2026-10-04）

| 项 | 裁定 | 状态 |
|---|---|---|
| 三预设在 V4 的位置 | **直接退场** | 已裁定 |
| 快速完成路径 | **保留**，引擎 = 整轨两档处理 | 已裁定 |
| ② 问题 是否为独立阶段 | **去掉** | 已裁定 |
| `preserve` 的去处 | **并入 ④ 修音** | 已裁定 |
| 产品方向 | **逆向工程 · 多轨复合** | 已采纳 |
| ⑤ 复合是否独立成阶段 | 独立 | 本次实施，可否决 |
| 是否新增可逆性门禁 | 新增 | 本次实施，可否决 |
| ⑦ 是否增加「保留原版」 | 新增 | 本次实施，可否决 |

**2026-10-04 追加裁定（Phase 2.1，`CANON_CHANGE = YES`）：**

| 项 | 裁定 | 状态 |
|---|---|---|
| 深度受阻时是否提供快速完成入口 | **提供**，且必须由人显式确认（§4.2.0） | **已由人类批准** |
| 快速入口的判断依据 | `!deepExecutable`（不再是 `!deepAssetsReady`） | **已由人类批准** |
| 人的显式 FAST 选择 | 优先于 `deepAssetsReady`，不再被覆盖回 DEEP | **已由人类批准** |
| 切换是否生成音频 / 删除深度资产 | 都不 | **已由人类批准** |

**据此产生、尚待确认的推论：**

1. **快速完成也走 ⑤复合 → ⑥复检 → ⑦选定**（§4.2）—— 否则违反「绝不 AI 处理 → 自动完成」。
2. **① 检测 页承接「当前规则未发现技术问题」的措辞**（§9）—— ② 退场但这条诚实要求不退场。
3. **改进程的判定用聚合、开新实验不倒退**（§3.1）—— 语义选择，可否决。

---

## 11. 一键完成会话的诚实边界（Phase 1）

实现：`src/orchestrator.js`（调度）+ `src/session.js`（相位投影与失败记录）+ main.js 的步骤接线。
产品形态见 [../plan/2026-10-04_DESKTOP_ONE_CLICK_PHASE1.md](../plan/2026-10-04_DESKTOP_ONE_CLICK_PHASE1.md)。

「一键」只简化**用户操作**，不省略内部步骤，也不把未实现的能力伪装成成功。两条具体纪律：

### 11.1 真实失败必须留下原因，并且不能在重新投影时消失

步骤失败时写 `<case>/studio/session_failure.json`，`session:view` 在该相位**此刻仍未完成**时
把视图降级为 `BLOCKED`（`kind: STEP_FAILED`）。规则：

```text
只在该相位仍是「下一个未完成相位」时生效
相位一旦完成 / 流程已走过它 / 已有更强阻断（缺能力）→ 记录立即过期，视图回到真实推导
记录**永远不能**让任何东西变成 done / REVIEW / DONE
记录**不拦控制流**：再次「开始完成」会真的重试那一步
```

它不推进任何阶段，所以不是第二套状态机：阶段与门禁依旧每次由 `pipeline.snapshot()` 从磁盘推导。

### 11.2 「检测」在会话里是核对，不是就地补做

Core 的检测（`analyze_to_case`）**总是新建一个 case**（新 `case_id` + `mkdir(exist_ok=False)`），
无法把 `report.json` 补写进一个已经存在的 case 目录。所以对一个缺 `report.json` 的世界，
「再检测一次」永远不会让这一步完成，只会每轮造出一个孤儿 case（旧实现就是每轮重跑、
最后只报 `NO_PROGRESS`）。会话因此：

- **同一步在一次启动里只尝试一次**；某步声称成功却没留下产物 → 立即停止并如实记 `NO_PROGRESS`；
- 缺 `report.json` 时**如实拒绝**（`CASE_WITHOUT_REPORT`）并让用户重新导入 ——
  检测会建立一个新的世界；壳不会把别的目录的产物搬进来，也不会反复新建世界。
