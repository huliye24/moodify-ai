# Moodify CLI-First A/B Compare v0.1 — DeepSeek 执行任务书

**日期：** 2026-10-03
**执行者：** Claude Code（DeepSeek 后端）
**任务类型：** 实现 + 验证
**CANON_CHANGE：** NO

> 这是一份执行任务，不是讨论稿。请直接检查现状、完成实现、运行验证并报告结果。

## 1. 人类方向

保留 Moodify Studio 当前已有的全部功能，不回滚，不删除现有工作台。

Moodify 首先是可由 AI / Agent 调用的声音协议与 CLI 软件。Studio GUI 只承担简单操作、状态展示、播放、A/B 审听和人工确认。复杂处理必须来自 Moodify Core，并通过统一 CLI 暴露。GUI 与 AI 必须调用同一条 Core / CLI 路径，不得形成 Electron 私有声音逻辑。

本任务优先解决 Studio 左侧第 6 个图标的 A/B 功能，使它成为第一个完整的 CLI-first 人机协作闭环。

## 2. 开始前必须执行

1. 完整阅读：
   - `AGENTS.md`
   - `docs/canon/CURRENT_CANON.md`
   - `docs/canon/PRODUCT_BOUNDARY.md`
   - `docs/canon/AUTHORITY_ORDER.md`
   - `docs/REPOSITORY_STATUS.md`
2. 执行 `git status --short`，识别当前脏工作区。
3. 确认没有另一个 AI / Agent 正在修改同一批文件。如果存在并发执行，立即停止并报告，不要抢写。
4. 检查当前未提交的 A/B 实现。此前一次中断的执行可能已产生部分代码，尤其包括：
   - `moodify-core-package/src/moodify/ab_compare.py`
   - `moodify-core-package/src/moodify/release_cli.py`
   - `moodify-desktop/src/main.js`
   - `moodify-desktop/src/preload.js`
   - `moodify-desktop/renderer/app.js`
   - `moodify-desktop/renderer/index.html`
   - `moodify-desktop/renderer/style.css`
5. 不得假设这些部分代码正确或完整。先审查，再继续；不要重复创建第二套实现。

## 3. 工作区保护规则

- 仓库当前存在大量与本任务无关的 tracked deletions 和其他修改，全部视为用户资产。
- 禁止使用 `git reset --hard`、`git checkout --`、`git clean` 或批量恢复/删除。
- 不得格式化、移动或修改无关文件。
- 不得提交 commit，不得 push。
- 对疑似临时调试文件，只有确认是本次中断执行创建且无任何交付价值后才能删除；在最终报告中列出。
- 禁止修改产品身份、能力边界、state authority、evidence authority 或其他 Canon 内容。

## 4. 目标架构

```text
人类自然语言
      ↓
AI / Agent
      ↓
Moodify CLI
      ↓
Moodify Core
      ↓
Case + Mix Graph + Audio + Evidence
      ↑
Moodify Studio（读取、播放、展示、人工选择）
```

必须满足：

```text
GUI ─┐
     ├──> 同一 Moodify CLI / Core 能力
AI ──┘
```

不得出现：

```text
GUI -> Electron 私有 DSP / 私有比较算法
AI  -> 另一套 CLI 行为
```

## 5. 实现范围

### 5.1 审计并复用既有权威

先检查并复用：

- `moodify protocol compare`
- `moodify finishing new/render/verify/export`
- 现有 case 目录结构
- Mix Graph、render evidence 和哈希字段
- `release_cli.py` 的命令风格、JSON 输出和退出码
- Studio 当前 research/A-B IPC 与界面

不得创建第二套 compare authority、Job authority、state machine 或 DSP 实现。

### 5.2 CLI A/B 能力

在现有 `moodify-core-package` CLI 体系中提供稳定、机器可读的 A/B 命令。建议接口：

```powershell
moodify compare prepare <case-dir> --json
moodify compare choose <case-dir> --keep A --role creator --json
moodify compare choose <case-dir> --keep B --role listener --json
moodify compare inspect <case-dir> --json
```

如果现有 CLI 架构有更合适的语法，可以调整，但必须：

- 简洁、一致、可发现；
- 适合 AI / Agent 调用；
- 支持 JSON 输出；
- 具有确定的退出码；
- 最终报告列出准确命令。

### 5.3 `compare prepare`

必须完成：

- A 固定为 case 的源音频；
- B 为明确选择的 finishing 渲染产物，默认可选择最新有效产物；
- 校验 A/B 均存在且可读取；
- 计算并记录 A/B SHA-256；
- 记录 B 对应的 preset、Mix Graph、render evidence 和 output hash（存在时）；
- 记录实际响度测量结果以及是否完成试听响度匹配；
- 写出 case 内的 `comparison.json` 或符合现有 artifact 命名规则的等价文件；
- 返回 `next_actions`，供 Agent 判断下一步；
- 缺少 B、证据不足或不可比较时，返回明确 failure、`HUMAN_REQUIRED` 或 `INCONCLUSIVE`，不得伪造成功。

建议 JSON 形状：

```json
{
  "status": "READY_FOR_HUMAN_REVIEW",
  "case_id": "case_xxx",
  "comparison": {
    "a": {"role": "source", "path": "...", "sha256": "..."},
    "b": {"role": "rendered", "path": "...", "sha256": "..."},
    "loudness": {
      "a_lufs": null,
      "b_lufs": null,
      "offset_lu": null,
      "match_status": "NOT_MATCHED"
    }
  },
  "next_actions": [
    {"action": "HUMAN_LISTEN", "reason": "需要人工听感判断"}
  ]
}
```

字段可以按现有 schema 调整，但语义必须明确、可版本化。

### 5.4 响度匹配诚实边界

- 如果 v0.1 只测量响度差，没有真正生成匹配代理，必须写 `NOT_MATCHED`。
- 不允许 GUI 通过用户勾选“已响度匹配”来冒充系统已经执行匹配。
- 如果生成试听代理，必须保留原始 A/B，不得覆盖源文件或正式渲染产物。
- 匹配补偿值、算法版本、代理文件 hash 必须进入 comparison artifact。
- 不引入未经校准的新判断阈值。

### 5.5 `compare choose`

记录一次明确的人工选择：

- `keep`: `A` 或 `B`；
- reviewer role：`creator` / `listener` / `pro`；
- reviewer identity：没有身份系统时允许匿名或本机 reviewer，但必须明确；
- 时间；
- A/B SHA-256；
- comparison artifact 引用；
- Mix Graph / render evidence 引用；
- loudness match 状态；
- 可选备注；
- schema/version。

记录必须追加写入、可追溯，并避免同一请求意外重复写入。不要把未校准的人类选择直接晋升为 canonical truth。

## 6. Studio 第 6 个图标

Studio 必须是薄 GUI。它只负责：

1. 调用 CLI 准备 A/B；
2. 读取 comparison artifact；
3. 播放 A/B；
4. 在同一播放位置切换 A/B；
5. 显示当前正在播放 A 还是 B；
6. 将“保留 A / 保留 B”通过同一 CLI 写入判断记录；
7. 展示 CLI 返回的成功、失败、`HUMAN_REQUIRED` 或 `INCONCLUSIVE`。

不得在 renderer 或 Electron main 中重算响度、比较质量或复制 Core 判断逻辑。

### 6.1 必须修复的已知断裂

- `index.html` 与 `app.js` 使用的 `rp-*` 元素不一致；
- `buildChoiceButtons()` 被调用但不存在；
- `rp-source`、`rp-b-status`、`rp-preset`、`rp-render`、`rp-render-note`、`rp-choice` 等引用必须与真实 DOM 一致；
- judgment IPC 返回值与 UI 使用的 `res.kept` 不一致；
- 不能再用一个手动 checkbox 声称“已响度匹配”；
- 没有 case、没有 B、CLI 失败时不得抛出未捕获异常或留下假成功状态。

### 6.2 最小可用交互

```text
原始 A                         修音 B
source.wav                     clean_master

          [播放/暂停]  01:24 / 03:42

       [ A 原始 ]  ⇄  [ B 修音 ]
          当前正在播放：B

响度状态：NOT_MATCHED / MATCHED（来自 CLI artifact）
[保留 A]                       [保留 B]
```

如果无法在本轮可靠完成真正的同步播放，必须：

- 先完成 DOM、CLI 接入和正确落账；
- 明确标记同步切换为未完成；
- 不用假 UI 冒充完成。

## 7. 路径与安全

- 所有 `caseDir` 必须解析后验证属于允许的 cases root。
- 所有 artifact 路径必须验证属于对应 case；源音频可以通过 case 中受信任的 source reference 解析。
- 禁止新增任意文件读取或任意文件写入 IPC。
- Renderer 不能直接传任意绝对路径要求 main process 读取。
- 保持 `contextIsolation: true` 和 `nodeIntegration: false`。

## 8. 测试要求

至少增加并运行：

### Core / CLI

- prepare 成功；
- 缺少 B；
- A/B 文件不存在或不可读；
- 非法 case 路径；
- choose A；
- choose B；
- 非法选择；
- 非法 reviewer role；
- comparison hash 与 evidence 引用；
- 重复写入策略；
- JSON 输出和退出码。

### Studio

- `node --check src/main.js`
- `node --check src/preload.js`
- `node --check renderer/app.js`
- DOM ID 与 JS 引用静态合约检查；
- 如果已有可复用方式，增加最小 IPC 合约或 renderer smoke test。

### 最终检查

```powershell
git diff --check
```

运行与本任务相关的既有 sound protocol、Mix Graph、CLI 测试，不能只跑新增测试。

## 9. 完成定义

本任务只有同时满足以下条件才算完成：

```text
AI 能通过 CLI 准备 A/B
→ CLI 生成可验证 comparison artifact
→ Studio 能读取并播放 A/B
→ 人能选择保留 A 或 B
→ 选择通过 CLI 写入证据记录
→ 失败状态明确且可恢复
```

不得以“界面能打开”或“命令能运行一次”作为完成依据。

## 10. 最终报告格式

完成后只报告事实：

1. 修改了哪些文件；
2. 最终 CLI 命令及示例；
3. comparison 和 judgment artifact 的路径与 schema/version；
4. Studio 第 6 个图标现在可以完成什么；
5. 运行了哪些测试，准确通过/失败数量；
6. 哪些能力仍未完成或未验证；
7. 是否碰到现有脏工作区或并发修改；
8. `CANON_CHANGE = NO`。

禁止把实验性能力描述为 production-ready，禁止声称未运行的测试已经通过。
