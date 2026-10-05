# Moodify Desktop — 一键完成机 Phase 1 任务包

**Date:** 2026-10-04  
**Status:** IMPLEMENTATION BRIEF  
**Owner / final acceptance:** Codex（主控）  
**Implementation delegate:** DeepSeek（通过仓库现有 Mood 编译器通道）  
**CANON_CHANGE:** NO

## 1. 产品目标

Desktop 的第一产品面必须从“工程工具集合”收口为一台封装 AI 制作人的完成机：

```text
放入一首歌 → 一次启动 → 内部自动执行 → 原版 / A / B → 人选择 → 导出
```

“一键”只简化用户操作，不省略内部的检测、逆向分解、结构、修音、复合与复检，也不允许把未实现能力伪装成成功。

## 2. Phase 1 范围

本阶段只完成**产品表面收口与一键编排骨架**，允许视觉粗糙，不实现新的音频算法。

### 必须完成

1. 空态提供唯一清晰入口：拖入或选择一首歌，并说明将生成两个完整候选版本。
2. 导入后提供一个主动作：`开始完成`。不得要求普通用户分别点击检测、分轨、MIDI、修音和复检。
3. 新增一个顶层完成会话编排器，复用现有 IPC 和 `pipeline.js`，不得创建第二套状态机。
4. 编排器按真实门禁前进：检测 → 分解 → MIDI/结构 → 可逆性 → 修音/复合 → 复检。
5. 对已经存在的产物应跳过重复步骤，允许关闭后继续。
6. Core 尚未具备的能力必须停在真实失败态，显示 `TUNABLE_CORE_NOT_AVAILABLE` 对应的用户可读说明；不得生成假 A/B、假进度或占位音频。
7. 主结果面统一为 `原版 / A（保守） / B（充分）`，选择出口为 A、B、保留原版。
8. 现有分轨、曲谱、数据、频谱、研究和终端能力保留，但降到“制作详情/高级”层，不作为主流程入口。
9. 旧研究面板的 `A=原版 / B=预设处理` 不得继续作为产品主语义；三预设不得重新进入主流程。
10. 保持 renderer / preload / main 三层合约一致，补充自动编排的测试。

### 明确不做

- 不实现或伪造逐轨音准、节奏修正。
- 不实现或伪造多轨复合引擎。
- 不引入 server、login、cloud storage、P2P、新框架。
- 不重写 Core 或 Desktop。
- 不删除遗留 Android 项目。
- 不删除旧 Studio 文件；如需退出调用链，只停止新增引用并清楚标记。
- 不修改产品 Canon。

## 3. 交互状态

主界面至少表达四个状态：

```text
EMPTY       放入一首歌
READY       已导入，等待“开始完成”
PROCESSING  AI 正在按内部阶段执行，可展开查看详情
REVIEW      原版 / A / B 同位置试听、选择、导出
BLOCKED     某一步真实失败，说明原因和可采取动作
```

内部仍使用 `pipeline.js` 的产物推导阶段。界面状态只是投影，不是新的权威。

## 4. AI 与 Core 的责任

```text
Desktop       发起与呈现
内部 AI       理解、选择策略、调度完整流程
Moodify Core  分析、DSP、处理、验证和导出
人             听原版/A/B并作最终选择
```

AI 不得直接在 renderer 实现声音算法；任何影响声音结果的能力必须来自 Core。

## 5. 建议改动位置

- `moodify-desktop/renderer/index.html`：主入口、处理中、审听结果、制作详情层。
- `moodify-desktop/renderer/app.js`：完成会话状态投影与一键启动逻辑。
- `moodify-desktop/renderer/style.css`：只做必要布局，不投入视觉精修。
- `moodify-desktop/src/preload.js`：仅在需要新增编排桥接时修改。
- `moodify-desktop/src/main.js`：顶层编排 IPC；复用现有真实步骤。
- `moodify-desktop/src/pipeline.js`：继续作为唯一阶段/门禁权威；除非测试证明需要，否则不要改其语义。
- `moodify-desktop/scripts/`：增加一键编排的成功、续跑、阻断测试。

## 6. 验收标准

### 产品验收

- 新用户能在不理解分轨、MIDI、DSP 的情况下找到唯一主流程。
- 一首歌只需一次显式启动，内部步骤自动前进。
- 普通用户不会被迫进入分轨、曲谱、图表或终端页面。
- A/B 的语义始终是两个完整候选；原版是第三出口。
- 未实现 Core 能力不会被显示成成功或完成。

### 工程验收

- `npm test` 全部通过。
- 新测试覆盖：已有产物续跑、步骤顺序、真实阻断、不生成假产物、重复启动安全。
- `scripts/check_repo_structure.py` 通过。
- 不新增第二状态机、第二 Core、第二 DSP authority。
- 不覆盖用户当前未提交修改。
- 无密钥、音频或生成重文件进入 Git。

## 7. DeepSeek 交付说明

实现完成后必须报告：

1. 修改文件清单；
2. 用户主流程如何变化；
3. 编排器如何复用现有状态机；
4. 尚未实现的能力在哪里诚实阻断；
5. 运行了哪些测试及结果；
6. 任何无法确定的产品决策，标为 `HUMAN_DECISION_REQUIRED`，不得自行扩大范围。

最终是否通过由主控独立验收，DeepSeek 的自评不构成完成。

---

## 8. 复验轮（2026-10-04）：三处 P1 的修复

主控独立验收后给出三处 P1。全部已修复，并各配了**主进程集成测试**（不是模块单测）。

### P1-1 没有 report.json 的世界会被反复「重新检测」

**原因**：Core 的检测（`analyze_to_case`）总是新建 case（新 `case_id` + `mkdir(exist_ok=False)`），
无法就地补写 `report.json`。旧编排器每轮重跑 `analyze`，每轮在 cases-root 里造一个新 case，
最后只报一句 `NO_PROGRESS`。

**修复**（`src/orchestrator.js` / `src/main.js`）：
- 同一步在一次启动里**只尝试一次**；某步声称成功却在磁盘上没留下产物 → 当场停止，
  记 `NO_PROGRESS` 并说明原因，不再重复执行。
- 会话的「检测」步骤改为**核对**：缺 `report.json` 时返回 `CASE_WITHOUT_REPORT`，
  说明 Core 无法就地补写并请用户重新导入（检测会建立新的世界）。**不新建任何 case。**

### P1-2 真实步骤失败（分轨失败 / 缺 Basic Pitch）没有可见的 BLOCKED

**原因**：两处。(a) `runLong` 在非零退出时只回一个 `code`，没有原因，所以「缺少 Basic Pitch /
依赖没装」全都退化成一个没有信息的失败；(b) 失败原因只随那一次返回值回一次，UI 随后重新拉投影
时磁盘没变、状态又变回 `READY`，用户看到的是「什么也没发生」。

**修复**：
- `runLong` 非零退出时带回子进程最后一行非空输出（`lastOutputLine`），失败**必须带原因**。
- 新增失败记录 `<case>/studio/session_failure.json`，`session:view` 在该相位仍未完成时把视图
  降级为 `BLOCKED`（`kind: STEP_FAILED`）。相位一旦完成（产物补上 / 人手动做完）记录立即过期；
  记录**不拦控制流**，再次「开始完成」会真的重试那一步。
- 阻断分两种并在 UI 上区分：`MISSING_CAPABILITY`（缺能力，重试无用）与 `STEP_FAILED`
  （真实失败，修好后可重试——按钮必须给重试，否则用户只能重开应用）。

### P1-3 `appendDecision()` 不校验 pair：假选择能推进到 DONE，`ORIGINAL` 还能绕过审听导出

**修复**（`src/tuning.js` / `src/pipeline.js` / `src/main.js`）：
- 新增唯一准入规则 `validateDecision()` / `decisionBlockers()`：**pair 存在 ∧ A、B 两侧都有
  `mix.wav` ∧ 复检真的发生过**（`recheck.json` 存在、schema 与 `pair_id` 匹配、它对齐的三份
  report 仍在磁盘上）。`appendDecision()` 写之前必须过这道门；`ORIGINAL` 同在门内。
- **读侧同样严格**：`chosen` 事实由 `decisionBacked()` 推导 —— 不是「账本里有一行」，而是
  「有一行此刻仍被完整候选支撑」。旧版本写的、手写的、或候选后来被删掉的记录都不能把阶段推到
  `CHOSEN`，也不能解锁 ⑧导出。`tuning:export` 追加 `CANDIDATES_INCOMPLETE` 守卫。
- 同一个 `request_id` 换了出口或 pair → `REQUEST_ID_CONFLICT`（不静默返回旧结果）。
- UI 的可点状态来自同一份 `decisionBlockers`（`tuning:pairs` 下发），按钮不会比校验更宽松。

### 新增测试

| 测试 | 覆盖 |
|---|---|
| `scripts/test-orchestrator.js`（11 条） | 续跑跳过已完成步骤、缺 report 只尝试一次、谎报成功→`NO_PROGRESS`、失败→BLOCKED 且重新投影仍可见、失败可重试、产物补上后记录过期、相位顺序、能力阻断、重复启动安全、空世界不写文件 |
| `scripts/test-main-ipc.js`（15 条） | 用 stub electron 加载**真实 `main.js`**：会话 IPC 面、守卫、缺 report 不造重复 case、真实步骤失败可见、并发启动被拒、⑦ 的三道门（含手写假记录不能导出）、`tuning:render` 拒绝且不产文件、`tuning:pairs` 的准入 |
| `scripts/check-contracts.js`（第 6 节） | 静态合约：`src/session.js` 的每个相位 `run` 都必须在 `main.js` 的 `SESSION_STEPS` 里有真实实现 |
| `scripts/test-pipeline.js`（+10 条，5b 节） | ⑦ 准入：pair 不存在 / 半成品 / 假复检 / 复检报告被删 / `ORIGINAL` 不能绕过 / 读侧不收假记录 / 候选被删则阶段回退 / request_id 冲突 |

`npm test` 全绿：check-contracts ✓、test-pipeline 50/50、test-recheck 9/9、test-session 24/24、
test-orchestrator 11/11、test-main-ipc 15/15、test-studio 21/21。
