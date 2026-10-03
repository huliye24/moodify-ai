# Moodify Core Product v1 — 2026-08-24

**任务：** Moodify Entropy Reduction 001 — Establish Mainline Product Boundary
**性质：** 主线产品身份声明（不替代 Canon；不修改 Canon；为下游 Physical Isolation 提供唯一核心产品定义）
**权威层级：** 引用 `AGENTS.md` → `docs/canon/*` → `docs/brand/public/*`；本文件自身不进入 Canon 第 3 级（见 `CURRENT_CANON.md §3 不变量 #1`）。
**CANON_CHANGE：** `NO` —— 本文件**复用** Canon 已确立的对外身份，不引入第二身份。
**执行状态：** 仅声明。本轮**未修改、删除、移动任何业务代码、目录或既有文档**。Phase 1+ 的物理动作由下一轮（Reduction Execution 001）按 `EXECUTION_PLAN_V1.md` 与 `REDUCTION_PLAN.md §0` 安全阀执行。

---

## 1. 唯一公开产品

Moodify 当前唯一公开产品是：

> **Moodify — AI Listening Platform — Player + Cloud Engine — Web + Android — Audio Intelligence**

```text
Moodify
   ↓
AI Listening Platform
   ↓
Player + Cloud Engine
   ↓
Web + Android
   ↓
Audio Intelligence
```

这一行必须同时通过：

1. `CURRENT_CANON.md §1 External Product`：Moodify Music / Moodify Player；
2. `CURRENT_CANON.md §1` 第一阶段用户动作：PLAY；
3. `PRODUCT_BOUNDARY.md §External Product`：以 PLAY 为核心；
4. `PUBLIC_BRAND_CONSTITUTION.md §2.1`：Sound → Moodify → Play；
5. `PUBLIC_BRAND_CONSTITUTION.md §2.2`：禁单（不得以"AI 音乐后处理平台 / Auditory Intelligence Infrastructure / The Ear of AI / 音频 API 平台 / ACU 计算平台 / Creator Platform"作为首要公共定义）；
6. `CURRENT_CANON.md §3 不变量 #1`：一个对外产品身份；
7. `CURRENT_CANON.md §3 不变量 #7`：一个站点一个角色（rongjingmusic.com / rongjingwenchuan.com / .xyz）。

任何第二产品身份候选（QA Web v0.1、QA Desktop、Pulse、Ear Workbench 作为对外产品）必须被否决，参见 `docs/reduction/PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md §2 D-1`。

---

## 2. 为什么保留 Player

| 维度 | 证据 |
|---|---|
| 用户动作 | `CURRENT_CANON.md §1` 第一阶段用户动作 = PLAY；Player 是唯一直接承载 PLAY 的对外工程。 |
| Canon 不变量 | `CURRENT_CANON.md §3 不变量 #1` "一个对外产品身份"；Player 是该身份的载体。 |
| Public Brand §11 公开证明顺序 | Belief → Sound → **Play** → Proof → Explanation → Technology；Player 是 Play 的工程实现。 |
| 既有审计 | `MOODIFY_PRODUCT_AUDIT.md §4 表` —— Web Player (KEEP, 5/5/4) + Android Player 3.1 (KEEP, 5/4/3)。 |
| 现实证据 | `CURRENT_ARCHITECTURE.md §1` —— LA VPS `moodify-music :3100` + `moodify-music-bff :8100` + nginx 已运行；`apps/music-android` 是 release workflow 唯一 Android 工程（`MOODIFY_PRODUCT_AUDIT.md §2.3`）。 |
| 品牌语气 | `PUBLIC_BRAND_CONSTITUTION.md §6`：安静、克制、精确、少解释；Player 是这种语气的工程落点。 |

**结论：** Player 是唯一不分裂身份的对外工程形式。继续减页面、减路由、减 surface；不增加 brand tier D 的内部工程叙事。

---

## 3. 为什么保留 Cloud Engine

| 维度 | 证据 |
|---|---|
| 内部系统 | `CURRENT_CANON.md §2` + `INTERNAL_SYSTEMS.md §1-2` —— Cloud Production System 是内部能力，承担 Intake→…→Delivery 完整链路。 |
| 产品原则 | `PUBLIC_BRAND_CONSTITUTION.md §2.1` "Listen. Then Play." —— "Listen" 的内部实现就是 Cloud Engine。 |
| 复杂度由 Moodify 承担 | `AGENTS.md §Important Distinction` "内部处理复杂度不是对外卖点"。Cloud Engine 是该原则的承载者：不进入公共首屏，但支撑 Player 的"先听后判断"。 |
| 既有审计 | `MOODIFY_PRODUCT_AUDIT.md §4 表` —— Ear 核心 (KEEP, 4/5/5) + v01_pipeline + data_factory (KEEP, 4/4/4)。 |
| 现实证据 | `CURRENT_ARCHITECTURE.md §1` —— LA + 杭州 VPS + data worker + data_factory pilot 10/10 SUCCEEDED。 |
| 不可删除 | `AGENTS.md §Change Discipline` "不要 mass-delete legacy code" + `LEGACY_AND_EXPERIMENTAL_POLICY.md §3 LEGACY` —— Cloud Engine 的已验证部分必须保留。 |

**结论：** Cloud Engine 是 Moodify 的内部差异化来源。**保留为内部系统，不暴露为对外产品面。**

---

## 4. 为什么其他方向暂时冻结

判断原则：`PUBLIC_BRAND_CONSTITUTION.md §13` 5 项测试 + `AGENTS.md §Judgment Authority`（不压制人类 authority）。

| 候选方向 | 当前状态 | 冻结原因 | 恢复条件 |
|---|---|---|---|
| Moodify QA / QA Desktop / QA Web v0.1 | DELETE 候选（`docs/reduction/PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md §2 D-1`） | 违反 Canon 不变量 #1；自描述为"AI Audio Quality Assurance Infrastructure"，命中 `PUBLIC_BRAND_CONSTITUTION.md §2.2` 禁单 | 仅在人类明确 `CANON_CHANGE = YES` 且写入 `docs/canon/CANON_CHANGELOG.md` 后重新评估 |
| Moodify Pulse | DELETE 候选（`MOODIFY_PRODUCT_AUDIT.md §4 表`） | 第二产品身份（"AI Emotional Music Container"）；mock data；与 Player 重复 | 真实 Windows 用户下载量 + 必要播放代码提取后另立 Moodify Player for Windows；不得保留 Pulse 身份 |
| Ear Workbench 作为公开产品 | FREEZE（`MOODIFY_PRODUCT_AUDIT.md §4 表`） | 内部研究工具；不得进入公开导航 | 永远作为 INTERNAL；不进入 PUBLIC |
| Creator Studio / 发布 / 主页 / 关注 | FREEZE（`MOODIFY_PRODUCT_AUDIT.md §4 表`） | 当前没有 creator 产品证据；分散 listener-first 主线 | 供给侧 + 用户行为证据齐备 |
| License / Support intent / CWC 积分 / Creation Passport / Evidence Bridge | FREEZE / DELETE | 无成交证据 / 无用户闭环 / 提前引入货币与账务复杂度 | 商业模式经人类决策（`CANON_CHANGELOG.md CD-011`）后 |
| Reconstruction Job + 重建系列 | FREEZE | 实现含未完成 billing；真实生产 case 出现前不扩状态 | `INTERNAL_SYSTEMS.md §3` 单一 state machine 方案 = `HUMAN_DECISION_REQUIRED` |
| MAMSE-001..016 / Physics / LLM / lyric / transcription | FREEZE | 研究资产，不进入默认安装 / CI / AI 上下文 | 单一研究 profile；不影响主线 |
| 第二 Android 工程 (`apps/android/`) | MERGE 候选 | 与 `apps/music-android` 双 authority；维护成本翻倍 | 必要能力（缓存 / MediaSession / 本地化）迁移后整工程退役 |
| Moodify Data API（与 BFF 平行） + Web Drizzle schema | MERGE 候选 | 与 BFF + SQLAlchemy 双层 surface；状态枚举漂移 | `CANON_CHANGE = YES`（data authority 变更）后合并 |

**冻结的总原则：**

```text
未来所有决策只问：

这个东西是否增强"用户打开 Moodify 后，更愿意播放下一首音乐"？

如果答案：YES → 进入主线。
如果答案：NO  → 冻结。

但该原则不可独立作为决策依据，必须叠加：
- PUBLIC_BRAND_CONSTITUTION.md §13 5 项测试（Identity / Comprehension / Audibility / Complexity / Brand）
- AGENTS.md §Judgment Authority（不压制人类 authority；听觉判断需输出 HUMAN_REQUIRED / INCONCLUSIVE）
- MOODIFY_PRODUCT_AUDIT.md §7 DELETE 安全阀 6 项
```

---

## 5. 一句话重申

> Moodify 是**一个**对外产品面（Player + Cloud Engine 的对外感知），**一个**核心用户动作（PLAY），**两条**播放端交付路径（Web + Android），**一套**内部听觉智力（Ear / Auditory Intelligence，由 Cloud Engine 承担，对用户不可见）。

所有其他工程 / 文档 / 计划必须以此为锚。下一轮（Reduction Execution 001）将按 `EXECUTION_PLAN_V1.md` 的 Phase 1 → 4 顺序执行物理动作。

---

**本文件结束。等待 Reduction Execution 001：物理隔离 archive/freeze。**