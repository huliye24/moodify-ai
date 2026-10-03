# Moodify 双端共享 Core 设计文档（v0.2 草案）

> **状态：待人类权威审阅。** 审阅通过后才改 `AGENTS.md` / `docs/canon/*` / `README.md`。
> **触发：`CANON_CHANGE = YES`（草案）** — 这是一次产品权力结构调整，不是功能迭代。
> **性质：** 设计文档，不是 Canon 变更记录本身。定版后按 `docs/canon/CANON_CHANGELOG.md` 的 R7 规则登记。
> **版本：** v0.2 — 从 v0.1 的"能力优先 + CLI 一等接口"迭代为"**一个 Core，两个出口（生产端 CLI / 消费端 App）**"，并重新解释 PLAY 的定位。

---

## 0. 一句话产品结构

> **Moodify CLI makes music sound better.**
> **Moodify App makes music play better.**
> **Moodify Core powers both.**

中文：**CLI 改善音乐本身，App 改善音乐被听见的方式，Core 是二者共同的声音智能。**

CLI 是生产端，App 是消费端，Core 是产品真正的核心资产。三者不是二选一，也不是重复产品。

---

## 1. 产品结构：一个 Core，两个出口

```text
                    MOODIFY CORE
                 /               \
                /                 \
         Moodify CLI           Moodify App
         Production            Playback
             |                    |
      分析 / 处理 / 验证       动态播放 / 实时适配
             |                    |
        改变音频资产           改变听到的结果
```

| 出口 | 身份 | 回答的问题 | 产出 |
|---|---|---|---|
| **Moodify CLI** | Production Interface（声音生产端） | 这首歌应该是什么样？ | 增强音频 + Moodify Profile |
| **Moodify App** | Listening Interface（声音消费端） | 这首歌此刻应该怎么被听见？ | 动态播放（实时渲染） |

**两个端不是重复产品，是同一个核心能力的两个出口。** CLI 负责"做"，App 负责"听"。

### PLAY 的重新定位（不推翻）

Canon 里的"用户核心动作 = PLAY"**不需要完全推翻**，而是重新解释：

- **PLAY 仍是消费者侧的核心动作**（Listener Side）。
- 但 Moodify 整体已经**不只是 Player**，它新增了 Creator Side。

```text
             Moodify
          Shared Core
        /                \
Creator Side         Listener Side
Moodify CLI          Moodify App
PROCESS              PLAY
```

旧 Canon 冻结的 PLAY 因此被**保留并扩展**：它降级为"消费端的核心动作"，不再是"Moodify 的全部"。

---

## 2. 根本工程原则：One Core, Multiple Interfaces（技术宪法级）

**这一条必须写进技术宪法，是最高优先级的工程约束。**

- **永远只有一套声音逻辑**，禁止出现 `CLI DSP Engine` 与 `App DSP Engine` 两套实现。
- 以下能力**全部来自 Core**，任何 interface 不得私藏一份：

```text
DSP primitives · audio analysis · playback profile schema
EQ · dynamics · loudness · stereo · spatial processing
device adaptation · validation
```

- 依赖方向严格单向：

```text
                 moodify-core
                     |
     ┌───────────────┴───────────────┐
     ↓                               ↓
moodify-cli                     moodify-app
```

**最危险的反例（必须用测试钉死）：** CLI 处理出来的结果，App 不能完全复现。这意味着 `core` 的同一版本 + 同一输入 + 同一 profile → 两个端产出**逐样本一致**的输出。为此，`core/verification` 必须包含一条跨端一致性回归测试。

---

## 3. 两个端的数据流

**CLI（Production）**

```text
Original Audio
    ↓ Analyze
    ↓ Process
    ↓ Verify
Enhanced Audio + Moodify Profile
```

**App（Listening）**

```text
Enhanced Audio + Moodify Profile + Device + Listening Environment
    ↓ Realtime Moodify Core
Dynamic Playback
```

### Moodify Track（资产与智慧的分离）

一个真正的 Moodify Track 不再是单独一个 wav，而是：

```text
track.wav            → 声音资产
track.moodify.json   → 这首歌的"播放智慧"
```

- `track.wav` 是资产；`track.moodify.json` 是播放智慧。
- **CLI 负责生产这个 Profile，App 负责执行这个 Profile。**

---

## 4. Profile Schema — `track.moodify.json` v1.0

```json
{
  "profile_version": "1.0",
  "track_id": "xxx",
  "track": "track.wav",
  "playback": {
    "eq": {},
    "dynamics": {},
    "stereo": {},
    "spatial": {},
    "gain": {}
  },
  "devices": {
    "headphones": {},
    "speakers": {},
    "phone": {}
  },
  "evidence": {
    "analysis_report": "analysis-report.json",
    "processing_report": "processing-report.json",
    "verify_result": "verify-result.json"
  }
}
```

- `playback` 是**设备无关**的播放指令；`devices` 是**设备相关**的适配参数。
- `evidence` 回指它依赖的分析/处理/验证记录，保证可复现、可审计（本设计的额外约束）。
- App 侧的渲染入口是**单一、来自 Core 的 API**：

```python
core.playback.render(audio, track_profile, device_profile, environment)
```

---

## 5. 闭环与学习复利

```text
CLI → Analyze/Process → Profile → App → Dynamic Play
     → Listening Feedback → Core → CLI（下一轮更聪明）
```

若未来用户允许收集反馈，Core 将学习：

```text
歌曲 × 设备 × 播放参数 × 人的听觉偏好
```

这是 Moodify 真正的长期数据与算法复利——CLI 与 App 构成闭环，而不是两条平行线。

---

## 6. 仓库结构收敛（目标）

```text
moodify-ai/
├── core/
│   ├── analysis/        # 理解声音（声学/特征/语义，取代 engine 分析域）
│   ├── dsp/             # EQ/dynamics/loudness/stereo/spatial primitives
│   ├── processing/      # process 管线 + identity gate + 参数搜索
│   ├── playback/        # 动态播放算法（核心 IP，进 Core，不只留在 App）
│   ├── profiles/        # profile schema + 生成/校验
│   ├── verification/    # A/B、合规、identity-preservation、跨端一致性
│   └── contracts/       # evidence、schema 版本、authority 契约
├── cli/
│   ├── analyze / process / profile / verify / inspect
├── apps/
│   ├── android/ · desktop/ · web/
├── sdk/
└── docs/
```

**最值得注意：`core/playback/` 必须进 Core，而不是只存在 App 里。** 因为"动态播放算法"本身是核心知识产权；App 只是 `core.playback.render(...)` 的调用方。

> 未来 `Moodify Android / iOS / Desktop / Car / Speaker` 全部共享同一个声音逻辑。

---

## 7. 迁移映射（现状 → 目标）

> 渐进迁移，不删除代码。映射关系如下：

| 现状 | 目标 | 说明 |
|---|---|---|
| `engine/`（5 模块，分析域组织） | `core/`（能力组织） | 按**能力**重组，而非按"声学/特征/语义/评分/推荐"分析域 |
| `demo/`（`moodify analyze`） | `cli/`（一等接口） | demo 只是编排，升格为 production CLI |
| `products/`（qa/master/rating/supply） | 融入 `core/` 能力 | 四产品降为能力用法，不再是平级产品；API namespace 属 Phase-D 议题 |
| `moodify-core-package/`（legacy，数学实现在此） | 渐进迁入 `core/` | facade 现状 `PHASE_B_T0_5_FACADE_LIVE` |
| `apps/web/`（已存在） | `apps/web/` | 保留；`desktop/`、`android/` 为目标 |
| `sdk/`、`docs/` | `sdk/`、`docs/` | 保留 |

**命名决议（本设计默认采纳，可否决）：** 术语从"Moodify Intelligence Engine / `engine/`"收敛为"Moodify Core / `core/`"；"Engine"一词退役，避免与"生产端/消费端"之外再引入第三套心智。

---

## 8. CLI 命令表（Production Interface，一等接口）

CLI 是唯一权威生产入口，必须 `CLI-callable / scriptable / headless`。禁止 GUI-only feature。

| 命令 | 输入 | 输出 | 依赖 Core | 现状 |
|---|---|---|---|---|
| `moodify analyze <file\|dir>` | 音频 | analysis-report.json/.md | analysis | 已有（demo，单文件） |
| `moodify process <file\|dir> --goal ...` | 音频 + goal | track.moodify.wav + processing-report.json | processing + dsp | 部分（legacy process） |
| `moodify compare <a> <b>` | 双音频 | A/B 差异报告 | verification | 缺失 |
| `moodify profile create <file>` | 处理后音频 | track.moodify.json | profiles | **缺失（全新）** |
| `moodify verify <file> [--against b]` | 音频 | verify-result.json | verification | 缺失（experimental） |
| `moodify inspect <report>` | 报告 | 终端/JSON 摘要 | 无（读取） | 缺失 |
| `moodify render <file> --device headphones` | profile + 设备 | 渲染后音频 | playback | 缺失 |

**收敛原则：** legacy `moodify-core-package` 的旧命令（`identity-guard` / `era-diagnostic` / `crafts` / `serve` / `emotions`）不进入一等面；仍有效的映射进上表，其余标 `LEGACY`。

---

## 9. 治理原则（Human Direction / Machine Execution）

| 范畴 | 人类主权（不可下放） | AI 执行权（可自主） |
|---|---|---|
| 产品定义 | Moodify 是什么/不是什么、双端定位 | 把定义转成工程任务 |
| 声音哲学 | 什么叫"更好听"、哪些特征必须保护 | 搜参、实现、测试、验证 |
| 处理边界 | 哪些处理被允许 | 在边界内选算法与参数 |
| 路线与商业 | 何时进桌面端/车载、商业模式、用户是谁 | 拆解里程碑、排期 |
| 对外身份 | 公开产品面、公开语言 | 落地页面、文案初稿（需审） |
| 核心资产 | `core/` 的边界与 IP 归属 | 在授权范围内实现 |

**保留并加强：** 当前人类明确指令优先于仓库其它 authority；AI 遇产品哲学冲突产生 `HUMAN_DECISION_REQUIRED`，不自行裁决；**One Core, Multiple Interfaces** 作为技术宪法条款。

---

## 10. CANON_CHANGE 草案（审阅后登记）

- **why**：产品权威重新定义 Moodify = 共享 Core 的双端声音智能平台；新增生产端（CLI），消费端（PLAY）保留但降级为"消费端的核心动作"。
- **affected authority files**：`AGENTS.md`、`README.md`、`docs/canon/CURRENT_CANON.md`、`docs/canon/PRODUCT_BOUNDARY.md`、`docs/canon/AUTHORITY_ORDER.md`、`docs/canon/CANON_CHANGELOG.md`。
- **migration**：PLAY 降级为 Listener Side 核心动作（不删除）；新增 Creator Side（CLI）；Profile 概念入 Canon；CLI 列为一等接口；`core/playback/` 与"One Core"写入技术宪法。
- **rollback**：回退到 Canon v1.1 的 PLAY 冻结即可恢复。

---

## 11. 验收标准

> **这个能力，能否被 AI 独立、稳定、可验证地调用？**

- 只能靠 GUI 点出来 → 还不是 Moodify 的能力。
- `moodify <verb> x.wav` 能可靠跑通 → 才成为可被整个 AI 世界复用的生产力积木。
- **跨端一致性**：Core 同一版本 + 同一输入 + 同一 profile → CLI 与 App 逐样本一致（由 `core/verification` 回归测试钉死）。

目标不再是"做一个功能更丰富的软件"，而是：**把专业声音处理能力，从少数会操作复杂软件的人手里，释放给所有能调用 Moodify 的 AI。**
