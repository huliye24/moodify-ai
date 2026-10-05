# Moodify Desktop Phase 2.1 — 深度受阻时显式切换快速完成（实现报告）

**Date:** 2026-10-04
**Status:** IMPLEMENTED — 待主控独立验收（人工复验见 §4）
**Owner / final acceptance:** Codex（主控）
**CANON_CHANGE:** **YES** — `docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md` §3.4 / §4 / §4.2.0 / §9 / §10 +
`docs/canon/CANON_CHANGELOG.md`（2026-10-04 条目）
**MIP_REQUIRED:** NO — Core 音频契约未变，本阶段只改 Studio 的模式选择与门禁语义
**任务包:** [`docs/plan/2026-10-04_DESKTOP_ONE_CLICK_PHASE2_REAL_AB.md`](../plan/2026-10-04_DESKTOP_ONE_CLICK_PHASE2_REAL_AB.md) 的后续裁定（人类批准）
**前置:** [`2026-10-04_DESKTOP_ONE_CLICK_PHASE2_IMPLEMENTATION.md`](2026-10-04_DESKTOP_ONE_CLICK_PHASE2_IMPLEMENTATION.md)

---

## 1. 修改文件清单

**契约与文档**
- `docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md`：新增 §3.4（三个概念）、§4 门禁表（深度/快速分开写）、
  §4.2.0（何时提供快速入口）、§4.2.1 补充、§9（删除死路条目、如实记录现状）、§10（追加裁定行）
- `docs/canon/CANON_CHANGELOG.md`：新增 2026-10-04 条目（why / evidence / authority / migration / rollback）
- `docs/REPOSITORY_STATUS.md`：Studio v4 状态表指向本次裁定
- 本文件

**Desktop**
- `src/pipeline.js`：新增 `modeDecision()`（唯一的模式决策纯函数）、`deepAssetsReady` / `deepExecutable` /
  `fastAvailable` / `deepExecutable` 事实、`deepBlockers`（原因码）+ `DEEP_BLOCKER_LABELS`、
  `modeExecutable`、`tuneCapability`；`gates()` 依据改为 `!deepExecutable`
- `src/session.js`：投影新增 `fastSwitch`（可用性 + **白话总结** + 技术原因 + 确认文案）与
  `blocker.canSwitchToFast`；BLOCKED 文案给出补救路径并明确「需要你确认、系统不会自动切换」；
  `modeExecutable` 原样带出；新增 `PLAIN_DEEP_REASON` / `plainDeepSummary()`——原因码 → 白话一句，
  **产品面不留工程细节**（文件名、路径、MIP 编号只出现在「制作详情」层）
- `src/main.js`：`pipeline:setFinishMode` 允许有 stems/MIDI 的 case 记录快速模式（只写记录，不生成音频），
  并在快速能力不可用时拒绝写入；`tuning:render` 分支按真实处境分四种（快速渲染 / 深度已声明可执行 /
  未检测 / 深度不可执行 + 可切换），`DEEP_NOT_EXECUTABLE` 携带 `canSwitchToFast` 与原因码
- `renderer/index.html`：新增深度受阻补救面板 `#session-remedy`（说明 + 两级确认：
  `#session-remedy-switch` / `#session-remedy-yes` / `#session-remedy-no`），移除 Phase 2 的单按钮
- `renderer/app.js`：`askQuickSwitch()` / `hideQuickConfirm()`；展开确认**不调用任何 IPC**，
  确认才 `chooseQuickFinish()`；面板可见性由投影的 `fastSwitch.available` 决定，
  正文只用投影的白话总结（不拼接技术原因字符串）
- `renderer/style.css`：补救面板样式

**测试**
- `scripts/test-pipeline.js`：§5c 九个场景（任务书 §6.1 逐条）；改写两条旧 Canon 断言
  （「roundtrip 通过即开 ④」「深度优先覆盖快速选择」）
- `scripts/test-session.js`：§10 补救投影（可切换 + 确认文案 + 不谎称自动降级 + 未来/已选/REVIEW 不提示）
- `scripts/test-orchestrator.js`：§6 截图状态（停在真实阻断、不自动切换、不写 finish_mode）
  → 人确认切换 → 一对候选 + 复检 → REVIEW；重启后从 `finish_mode.json` 恢复；失败可重试
- `scripts/test-main-ipc.js`：§8 真实 Core 的 Phase 2.1 闭环（有分轨 + MIDI 的 case）、
  §9 renderer 文案与两级确认契约（静态）

## 2. Canon change（why / evidence / authority / migration / rollback）

- **Why：** `deepAssetsReady`（资产存在）与「深度路径当前可执行」被混为一谈。逐轨 Core 能力未实现时，
  任何 `deepAssetsReady` 的 case 都无法深度完成；旧门禁又用 `!deepAssetsReady` 决定快速入口，
  于是三处门禁同时为假。这违反「第一个产品目标必须形成可靠完成循环」「失败必须可见、可恢复」
  「快速路径可存在但必须由人显式选择」「AI 不得替人改变完成模式」。
- **Evidence（真实 case，只读检查）：** 见 §4。旧规则在同一份事实上 `canTune = canTuneQuick =
  canRequestQuick = false`（死路）；新规则 `canRequestQuick = true` 且原因逐条可读。
- **Affected authority files：** `STUDIO_PRODUCTION_PIPELINE_V4.md`、`CANON_CHANGELOG.md`、
  `REPOSITORY_STATUS.md`；实现见 §1。
- **Migration：** 无需迁移。既有 case 产物不动，`finish_mode.json` schema 不变
  （`moodify.studio.finish-mode/0.1`），阶段仍由磁盘产物推导；已选 FAST 的 case 升级后行为不变。
- **Rollback：** 恢复 `canRequestQuick = baseReady ∧ ¬deepAssetsReady ∧ ¬optIn` 与
  `mode = deepAssetsReady ? DEEP : …`，并隐藏补救面板即可；Core / pair / decision / recheck
  产物与账本完全兼容，无数据迁移。

## 3. 旧门禁与新门禁的精确差异

| | 旧（被取代） | 新（2026-10-04 裁定） |
|---|---|---|
| 快速入口依据 | `canRequestQuick = baseReady ∧ ¬deepAssetsReady ∧ ¬optIn` | `canRequestQuick = fastAvailable ∧ ¬deepExecutable ∧ ¬optIn` |
| 模式 | `mode = deepAssetsReady ? DEEP : (quick ? FAST : null)` | `mode = quick ? FAST : (deepAssetsReady ? DEEP : null)`（**人的选择优先**） |
| 深度 ④ | `canTune = deepAssetsReady ∧ reversible` | `canTune = deepAssetsReady ∧ reversible ∧ deepCoreAvailable`（= `deepExecutable`） |
| 快速生效 | `quick = baseReady ∧ ¬deepAssetsReady ∧ optIn` | `quick = analyzed ∧ fastAvailable ∧ optIn`（有 stems/MIDI 也能生效） |
| 阻断说明 | 一个 `tuneBlockers` | `tuneBlockers`（当前模式）/ `deepTuneBlockers`（深度为何锁着）/ `deepBlockers`（原因码） |
| 死路 | 资产齐备 + 深度跑不通 → 三处全假 | 资产齐备 + 深度跑不通 → `canRequestQuick = true`，入口可见 |
| 产品面文案 | —（原本没有补救面板） | 白话一句（原因 + 可怎么办），工程细节只在「制作详情」；没有分解产物时不说「保留现有分解结果」 |

不变的部分（明确保留）：快速完成仍需**人显式选择**；切换只写 `finish_mode.json`；
快速路径仍走 修音/复合 → 复检 → 选定 → 导出；深度 ④ 不因快速可用而解锁；
`deepCoreAvailable` 由能力清单推导（逐轨能力进 `CAPABILITIES` 的那天，深度自动成为默认可执行路径，
入口也随之不再默认提供）——**没有第二处硬编码开关**。

## 4. 截图 case 的复验结果

**A. 只读状态检查（用户真实 case，未写入任何东西）**

| case | 源文件 | 深度资产 | roundtrip | 旧规则 | 新规则 |
|---|---|---|---|---|---|
| `case_31496475d3ce4199a8fca538431dc955` | `Je ne blesserai pas ta fragilité.wav` | 4 stems + 1 MIDI | 缺文件 | `canTune=false` `canTuneQuick=false` `canRequestQuick=false` → **死路** | `mode=DEEP`、`deepExecutable=false`、**`canRequestQuick=true`**、`deepBlockers=[NO_ROUNDTRIP, DEEP_CORE_UNAVAILABLE]` |
| `case_92b5a1d19b3b4d47a96a5614fc38de4d` | 同名副本 | 4 stems + 1 MIDI | 缺文件 | 同上 → 死路 | 同上 → 入口可见 |
| `case_6aaf85120b5d479a935fc532801b0cc6` / `case_b50f4e852d4141ee8d555be0cf6a9edb` | 同名副本（无资产） | 无 | 缺文件 | 入口本来就可见 | 入口仍然可见 |

**B. 真实歌曲的 Core 端（临时目录，未提交任何音频）**

`moodify tuning render-pair --mode fast-stereo-only` 直接在真实母带上跑通（123.32 s / 48 kHz / 立体声）：

```text
exit=0  用时 21.9 s
A conservative  mix sha256[:16]=e7d7099c90ce1bb2  LUFS −13.20 → −13.70 (Δ −0.50)  峰值门禁 passed
B full          mix sha256[:16]=966384057fb12f59  LUFS −13.20 → −15.21 (Δ −2.01)  峰值门禁 passed
产物：pair.json + A|B/{plan.json,evidence.json,mix.wav,tuned/source.wav}   六条硬门禁全 passed
```

**C. 完整闭环（对该 case 的**副本**、在临时 cases-root 内，用真实 Core 跑）**

见 §6「复验排练」——真实 UI 的最终人工确认仍由主控执行（任务书 §7）。

**D. 产品面文案（2026-10-04 修正）**

首版面板把 `deepReasons` 原样拼上屏，于是主界面出现了
「可逆性未验证（缺 studio/roundtrip.json；Core 尚未产出）；深度路径的逐轨修音 / 复合能力尚未就绪
（Core 未实现，见 MIP-0002）」——工程细节不该由用户来读。现在：

```text
深度完成暂不可用
可逆性验证还没有做、逐轨修音与复合能力还没有就绪。你可以保留现有分解结果，改用整轨两档完成（快速完成：仅立体声）。技术原因见「制作详情」。
[切换到快速完成（仅立体声）]
```

规则：白话来自原因码映射（`PLAIN_DEEP_REASON` / `plainDeepSummary`），四类原因各自成句；
`roundtrip.json`、`MIP-`、`stems/` 等字样**不得**出现在面板正文（有测试钉住）；
只有真的已有分解产物时才说「保留现有分解结果」；技术原文留在「制作详情」层。

## 5. 新增测试与回归结果

```text
cd moodify-desktop && npm test
  → check-contracts ✓（DOM id 133 · 桥接 52 · IPC 51 · 事件 5 · 会话相位 5）
    test-pipeline      61/61（§5c 新增 9 条 + 改写 2 条旧 Canon 断言）
    test-recheck        9/9
    test-session       36/36（§10 新增 5 条）
    test-orchestrator  20/20（§6 新增 4 条）
    test-main-ipc      32/32（§8 真实 Core 5 条 + §9 文案契约 3 条）
    test-studio        21/21
python scripts/check_repo_structure.py → OK
python -m ruff check moodify-core-package/src moodify-core-package/tests → All checks passed
```

禁止行为逐条有测试或实现约束：无自动切换（§8「确认之前」）、点击「开始完成」不静默降级
（§6/§8）、不删深度资产（§6/§8 前后哈希比对）、不伪造 `roundtrip.passed`（§5c-3/7）、
不开放深度 ④（§8）、不改 Core DSP 参数（本阶段未动 Core 代码）、不新增第二套编排器/状态机
（只改 `gates()` 与投影）、不扩大到 server/cloud/account/Android/Network（未触碰）、
不把快速完成说成逐轨修音（§9 文案契约）。

## 6. 复验排练（真实 case 副本，真实 Core）

对该 case 的**副本**（临时 cases-root，未触碰用户归档）用真实 Core 跑完整链路，
输出逐字如下：

```text
BEFORE:  {"mode":"DEEP","deepAssetsReady":true,"deepExecutable":false,"canTune":false,
          "canRequestQuick":true,"deepBlockers":["NO_ROUNDTRIP","DEEP_CORE_UNAVAILABLE"]}
SWITCH VISIBLE: true | 快速完成不会使用分轨进行音准或节奏修正；仍会生成 A/B、复检并由你选择。
SWITCH:  {"ok":true,"mode":"FAST_STEREO_ONLY","canTuneQuick":true,"canRequestQuick":false}
PAIRS RIGHT AFTER SWITCH: []                       ← 切换本身不生成音频
SESSION: {"ok":true,"state":"REVIEW","stage":"RECHECKED","pairs":["tune_20261004124224865_vvrx"]}
RECHECK: {"pair_id":"tune_20261004124224865_vvrx","alignable":51,"not_alignable":0,
          "original_metrics":51,"A_metrics":51,"B_metrics":51,
          "A_changed":38,"B_changed":41}           ← 三方各 51 项指标，全部可比，零缺项
LAYOUT:  A,B,pair.json,recheck.json
DEEP ASSETS AFTER: {"stems":5,"midi":1,"roundtrip":false}   ← 深度资产一个不丢
CHOOSE A: {"ok":true,"kept":"A"}
AFTER CHOICE: {"stage":"CHOSEN","canExport":true}
ELAPSED_S: 51
```

脚本与产物都在系统临时区（`phase21-acceptance` 脚本、`%TEMP%\phase21-accept-*`），
**不进入仓库**，也**不写入**用户的 `~/.moodify/cases` 归档。
真实 UI 的最终人工确认（点击、试听、导出）仍由主控按任务书 §7 执行。

## 7. HUMAN_DECISION_REQUIRED（本轮新增）

1. **是否需要「从快速模式切回深度路径」的 UI 入口？** 当前切换是单向的：一旦写下
   `finish_mode.json`，模式就是 FAST（人的选择优先）。回到深度需要清除该文件，没有 UI 入口。
2. **快速完成是否需要「一键重跑检测」入口？** 当源音频被移动或损坏时，目前只能重新导入
   （检测会建立新的世界）。
3. **快速入口的措辞边界：** 现在深度路径在任何 case 上都不可执行，因此入口对所有已检测的 case
   都成立（如实反映现状）。若人类希望「深度资产齐备时默认不主动展示入口」（只在深度**受阻**
   且用户尝试过之后才出现），那是一条新的产品规则，需要再次裁定。
