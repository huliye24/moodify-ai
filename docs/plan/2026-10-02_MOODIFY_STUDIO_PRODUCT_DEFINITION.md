# Moodify Studio 产品定义（v0.1 定稿）

- 日期：2026-10-02
- 状态：APPROVED_BY_HUMAN（四项裁决见 §6，实现未启动）
- 前置：桌面壳 Electron 化（fb1cc8f6 tkinter 单壳 → 3098a79b 迁移 → 615bd4f9 终端 + Claude Code 方案批次，五道门绿）
- 人类指令原话要点：布局像 PyCharm，底部终端界面可以拉开；做一个 Mood 编译器，可以像 Claude Code 一样通过 API 调用 AI（mood-protocol = 贡献值协议）；历史档案收起来像 PS 里面的文件，打开/历史这种图标；先有方案，不要写代码。

---

## 1. 一句话定位

**Moodify Studio = 听觉检测的 IDE**：左侧档案 dock（PS 式图标栏）、中央测量工作区、底部可拉伸终端抽屉、内置 Mood 编译器（AI 代理）；每次 AI 协作产出按 mood-protocol 语义记入本地贡献账本。

固定流程**不变**：选歌 → 检测 → 数据/图表 → 修音与混音方案。Studio 是新骨架，不是新产品。

## 2. 布局（PyCharm 骨架 + PS 面板习惯）

```text
┌──┬─────────────────────────────────────────────┐
│图│  源文件名 · case id · 状态徽章        ← 顶栏  │
│标├─────────────────────────────────────────────┤
│栏│           中央工作区（视图切换）               │
│  │     数据表 / 图表 / 方案（Mood 编译器）        │
│打│                                             │
│开│                                             │
│历│                                             │
│史│                                             │
│ ├──┴─────────────────────────────────────────┬───┤
│ ⇅ 终端抽屉（拖动调高度，点击收起/展开）          ⇅   │
└──┴───────────────────────────────────────────┴───┘
```

- **左图标栏**：约 44px 窄条。图标自上而下：打开音频、历史档案、Mood 编译器、设置（后续）。点"历史"→ 档案面板从左侧滑出（历史列表，双击打开 case），再点或失焦收起。
- **中央工作区**：数据 / 图表 / 方案 三视图保留，形态从页签改为工作区状态。未分析时中央区为空白 + 拖入文件提示（**无占位文字**，人类既定规则）。
- **底部终端抽屉**：全局常驻（不再只是报告内页签），标题栏拖拽改高度，双击/箭头收起成条。cwd 跟随当前 case；"在此目录打开 Claude Code"按钮保留。

## 3. Mood 编译器（Mood Compiler）

**是什么：** Moodify 自有 AI 代理面板——输入框 + 对话流 + 工具动作可见。系统提示词固定为"Moodify 后处理方案工程师"角色。工具边界固定：**只读 case 导出物**（report.json / measurements.json / judgment_rules.json / 图表 PNG），**只写 case 目录内文件**（方案 → plan.md、笔记）。不碰引擎、不改阈值、不动核心代码——对应 mood-protocol "Agent execution is bounded"。

**不是什么：** 不是通用聊天窗。无 case 上下文时编译器为空；每次产出都落在当前 case 里。

**与 Claude Code 的关系：** Claude Code 是开发工具，不进产品；编译器是产品内自有实现。今天方案页"生成方案"按钮 = 编译器第一个动作，之后长成完整对话。

## 4. 贡献值协议接入（mood-protocol 语义本地化）

依据 https://github.com/huliye24/mood-protocol （MOOD v0.3：可验证贡献驱动协调节点；概念链 Resident → Submission → Evidence → Review → ReputationEvent）：

| mood-protocol 概念 | Studio 对应物 |
|---|---|
| Submission（声明完成） | 一次 AI 协作产出（方案、修改建议轮次） |
| Evidence（证明材料） | 自动快照：所用 report.json hash + 产出文件 hash + 时间戳 |
| Review（判断过程） | 复用 A/B Judge / 验收指标 / 算法评审（不用人评） |
| ReputationEvent | case 目录 `contributions.jsonl` 追加一条不可变记录 |

**诚实边界（协议原文约束，照办）：** "重复的 AI 调用本身不产生贡献值"——只有落成产出、带证据链的 Submission 记账。贡献值面板只展示本地账本，**v0.1 不连链、不连网络节点**；对齐的是记录形状与语义，为接 MOOD 网络留出口。

## 5. 不变量（沿用，一条不破）

单壳；白色 + 公司 logo；固定流程四步；测量事实（核心）与方案文本（AI）责任分离；DRAFT_PLAN_NOT_EXECUTED（编译器建议 ≠ 执行）；界面无出口；占位文字禁止；核心 pip-only；python 子进程 `PYTHONUTF8=1`。

## 6. 人类裁决（2026-10-02，AskUserQuestion）

| # | 问题 | 裁决 |
|---|---|---|
| 1 | Mood 编译器 AI 通道 v0.1 | **先用 claude CLI 过渡**（本机登录态零成本；W2+ 换直连 API，provider 接口预留） |
| 2 | 贡献值协议 v0.1 深度 | **本地账本 MVP**（contributions.jsonl + 面板；不连链） |
| 3 | 布局落地 | **一次到位 + 档案 dock 放左侧**（图标栏最左，历史面板左滑出） |
| 4 | 终端与编译器关系 | **共存**（编译器 = 产品面；终端 = 工程面，ffmpeg/python/CLI 调试） |

## 7. 分期

- **W1 布局改造**：PyCharm 骨架（图标栏 + 中央区 + 底部抽屉），档案收进 dock。零新能力，纯壳。
- **W2 Mood 编译器 MVP**：claude CLI 内核 + 对话面板 + 工具边界 + 方案生成为第一动作。
- **W3 贡献值记账**：contributions.jsonl + 贡献值面板，协议形状对齐。

## 8. 明确不做（v0.1）

直连大模型 API / 多 provider 抽象（W2+ 评估）；连 MOOD 网络或任何链上操作；编译器执行算子（执行永远走显式作业）；移动端；多语言界面（沿用现有中文）。

## 9. 修正案（2026-10-02 当日）：Mood 编译器内核改为 Codex

人类指令："https://github.com/openai/codex 我希望采用 codex 的源代码，去嵌入 moodify"。三项新裁决（AskUserQuestion）：

| # | 裁决点 | 裁决 |
|---|---|---|
| 5 | 嵌入路径 | **B：协议嵌入一步到位**（codex app-server，JSON-RPC over stdio，编译器面板原生实现；不 fork 源码——上游日更，fork 漂移不可维护；源码仅作审计参考） |
| 6 | 模型提供方 | **安装时可选**（GLM / OpenAI / 自定义 OpenAI 兼容 base_url，首次使用设置卡录入，仅存本机 `~/.moodify/codex`，随时可改） |
| 7 | claude CLI 去留 | **完全替换**（claude 通道从壳代码移除，不再作为回退内核） |

取代 §6 裁决 1（"先用 claude CLI 过渡"）；§6 裁决 2-4 不变。

**实现事实（2026-10-02 验证）：**
- 内核来源：`@openai/codex` npm 0.160.0（Apache-2.0，平台子包 `codex-win32-x64`），`codex.exe app-server` 原生跑通 Windows 10.0.19045；协议形状取自二进制自带的 `generate-json-schema`（权威）。
- 边界执行：thread/start 请求 `sandbox=workspace-write` + `approvalPolicy=untrusted`；审批请求（命令/文件修改）原生进 UI（批准 / 本次会话批准 / 拒绝）。**诚实发现：本机 `windowsSandbox/readiness` = notConfigured，生效沙箱降级为 read-only，UI 如实显示生效边界而非请求值；沙箱配置向导（`windowsSandbox/setupStart`）暂不自动触发，列为残余项。**
- 隔离：`CODEX_HOME=~/.moodify/codex`（config.toml + providers.json），不碰用户自己的 `~/.codex`。
- 方案产物：编译器"保存方案"按钮把最后一条助手消息写为 `case_dir/plan.md`（取代 plan_claude.md）。
