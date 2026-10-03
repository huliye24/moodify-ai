# Studio 生产流程重排 — 实现报告

**日期：** 2026-10-03
**任务：** `MOODIFY_TASK_002A_STUDIO_PIPELINE_REALIGNMENT`
**分支：** `deepseek/studio-pipeline-realignment`
**基线：** `37234485815c0313e211a8b38f75248fb9d43666`
**范围：** §11 A–F

---

## 0. 一句话

原来的流程允许「分析完立刻选预设处理立体声母带」——**对母带太早了**。
现在流程是 **检测 → 问题 → 分轨 → 结构 → 方案 → 成品**，
预设从第一步下移到**最后一步**，实现保留未删。

---

## 1. 已实现（§11 A–F）

| | 内容 | 落点 |
|---|---|---|
| A | 重排流程；预设不再是分析后的第一动作 | `renderer/app.js` 流程条 + `VIEW_STAGE` |
| B | 新增 ② 问题（`diagnosis.json`） | `src/pipeline.js` `buildDiagnosis()` + `view-diagnosis` |
| C | 既有分轨接进主流程 | 流程条 ③ → 既有 `openStems()` |
| D | 既有 MIDI/曲谱接进主流程 | 流程条 ④ → 既有 `openScore()` |
| E | 构建 `context.json` | `src/pipeline.js` `buildContext()` + `view-plan` |
| F | 预设下移到成品阶段 | `view-studio` 变为 ⑥，带门禁与模式标注 |

**Core 零改动。** 无新音频算法、无分离模型、无移动端同步（§21）。

---

## 2. 实现前发现的两个事实（它们决定了设计）

### 发现 A：分轨的诚实标注**已经存在**

`<case>/stems/manifest.json` 里的 `engine_note` 原文：

> 非模型快速分离：中置声道估计 + HPSS 谱分解；有人声残留与伪影，
> 供快速观察/选段试听/MIDI 前处理，**不构成母带级分轨**。

§14 要求的「必须诚实标注」不需要新写。本 PR 做的是让它**随数据流动**：
`context.json.stems.engine_note` 原样搬运，并加 `grade: PREVIEW_NOT_MASTERING_GRADE`，
使下游消费者无法把预览级分轨误当母带级。

### 发现 B：诊断会**经常是空的**，而这必须如实说

Core 的 `report.json:findings[]` 目前**只能产出两种**：

```text
CLIPPING_PRESENT            (BLOCKING)
TRUE_PEAK_MARGIN_EXCEEDED   (WARNING)
```

**18 个真实 case 中 17 个 `findings` 为空。**

因此 ② 问题 阶段经常无事可说，UI 与产物都必须说
**「当前规则未发现技术问题」**，**绝不**说「这首歌没问题」——
这是两个不同的命题，混同会制造虚假信心。
`diagnosis.json.finding_rule_coverage` 随产物携带这句话。

**未接入 18 参数诊断引擎**：`moodify/diagnosis/` 桌面完全够不到，
且只挂在标着 `(Legacy) Old diagnosis engine` 的 `moodify legacy-analyze` 上。
接入等于引入**第二套诊断权威**，违反 `AGENTS.md`。→ 见 §6。

---

## 3. 两个设计判断

### 3.1 阶段由产物**推导**，不是人手推进

`pipeline.json` 只是记录，读取时永远重新推导。
**删掉 stems 目录，状态自动退回。**
一个写着「已分轨」而文件已不在的状态，正是本仓库反复清理的那类谎报。

### 3.2 快速完成必须由人**显式选择**（人工复查后收紧）

初版只要「分析与诊断」完成就解锁 ⑥，仅给结果**贴一个**「快速（仅立体声）」标签。
人工复查指出这不够：那让仅立体声成了**阻力最小的路径**——用户默认走到成品，
永远不分轨、不提取结构，规范路径反而变成例外。**贴了标签的捷径仍然是捷径。**

现在的门禁：

```text
⑥ 深度完成：需要 ANALYZED + DIAGNOSED + SEPARATED + STRUCTURED
快速完成：需要人点「改用快速完成（仅立体声）」→ 记录 <case>/studio/finish_mode.json
```

深度优先：若先选了快速、之后又完成分轨与结构，`deepReady` 自动接管，无需撤销选择。

对应测试从「analysis + diagnosis may finish」改为十条新断言，覆盖：
不自动解锁 · 只提供入口不发放 · 显式选择后才解锁 · 选择可追溯 · 分轨+结构无需选择即 DEEP ·
只有分轨不够 · 只有结构不够 · DEEP 压过先前的快速选择 · 新 case 无该产物。

### 3.3 `READY_FOR_PLAN` 不作为阶段游标（开发中修正）

初版把 `READY_FOR_PLAN` 放进阶段表，它的条件是 `analyzed ∧ diagnosed`。
结果是：**任何分析+诊断过的 case 都会自称 READY_FOR_PLAN**，
一步跳过 ③ 分轨 与 ④ 结构，**宣称用户没做过的进度**。

测试当场抓到（`stage is derived, so deleting artifacts moves it backwards` 期望 SEPARATED 得到 READY_FOR_PLAN）。
已修正：它是**就绪度**不是阶段，只通过 `gates().canPlan` 表达。

---

## 4. 验证

### 自动验证（可复现）

```bash
cd moodify-desktop && npm test
```

| 套件 | 结果 |
|---|---|
| `check-contracts.js` | 通过 — DOM id 109→125、桥接 47→53、IPC 45→51 |
| `test-pipeline.js` | **22 passed, 0 failed** |
| `test-studio.js` | **21 passed, 0 failed**（无回归） |

§20 七条逐条覆盖：产物可发现 · diagnosis 每条证据指针可解析回真实 finding ·
stems manifest 可发现 · MIDI/曲谱可发现 · context.json 只含真实存在路径 ·
前置未满足不得进深度成品 · 预设处理在成品阶段仍可用。

测试用**合成 fixture**（不是真实 case），断言确定、不依赖 `~/.moodify/cases` 里恰好有什么。
测试工具沿用上一轮教训：`check()` 是 async 且每处调用都 await——
同步助手包 async 回调会报假通过，上次已在 `test-studio.js` 犯过一次。

### 不能自动验证

> **我看不到 Electron 窗口。** 流程条的锁定/灰显、阶段跳转、②⑤ 两页渲染、
> human_notes 输入**都未被自动验证**。

本报告只声明：*合约通过 + 流程逻辑在无头测试下正确 + context 只引用存在路径*，
**不声明界面已工作**。本机确认：

```bash
cd moodify-desktop && npm start
```

---

## 5. 交付物

**新建**
```text
moodify-desktop/src/pipeline.js                     阶段推导 / 门禁 / diagnosis / context
moodify-desktop/scripts/test-pipeline.js            22 项无头测试
docs/canon/STUDIO_PRODUCTION_PIPELINE_V3.md         §19
docs/protocol/MOODIFY_STUDIO_CONTEXT_0_1.md         §19（含 diagnosis.json 契约）
docs/reports/STUDIO_PIPELINE_REALIGNMENT_2026-10-03.md  本文件
```

**修改**
```text
moodify-desktop/src/main.js            +registerPipelineIpc()（6 个 IPC）
moodify-desktop/src/preload.js         +6 个桥接
moodify-desktop/renderer/index.html    +流程条 + view-diagnosis + view-plan
moodify-desktop/renderer/app.js        +流程渲染/门禁/诊断/方案；rail-studio 改进流程入口
moodify-desktop/renderer/style.css     +流程条与证据块样式
moodify-desktop/package.json           npm test 纳入 test-pipeline
.github/workflows/studio.yml           +pipeline 测试步骤
AGENTS.md / docs/REPOSITORY_STATUS.md / docs/canon/PRODUCT_DEFINITION_V3.md   最小更新
```

**未删除**：三个预设、分轨引擎、曲谱工作台、A/B 研究面板全部保留。

---

## 6. HUMAN_DECISION_REQUIRED

1. **诊断丰度。** 当前 Core 只有 2 种 finding 规则，17/18 真实 case 为空。
   两条路都有代价：新增 Core 诊断规则要改 Core（需 MIP）；
   接入 legacy 18 参数引擎会引入第二套诊断权威（与 `AGENTS.md` 冲突）。**本 PR 都没做。**
2. **`preserve` 默认值。** 本 PR 留空由人填——「默认该保护什么」是听觉判断。
3. **精细分离引擎**（§14）。将来是否采用成熟公开模型（如 Demucs）？本 PR 不实现。
4. **②⑤ 两页的视觉与交互**只能由人在本机确认。

---

## 7. 后续（不在本 PR）

```text
TASK 002B  Finishing Context + AI Plan v0.1   （report+diagnosis+stems+MIDI+score → 结构化方案）
TASK 002C  Multi-track Plan Execution + Rebuild
TASK 002D  Verify + A/B + Human Choose
之后回到    Android Canon → Track Package → Studio to Phone
```
