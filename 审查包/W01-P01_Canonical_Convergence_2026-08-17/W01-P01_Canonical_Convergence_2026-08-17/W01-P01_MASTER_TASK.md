# W01-P01 — Moodify Canonical Convergence

**Wave:** Moodify Cognitive Wave 01  
**Package:** W01-P01  
**性质:** 权威收敛 / Canonical Convergence / 结构性熵减  
**日期:** 2026-08-17  
**执行对象:** Codex  
**前置依赖:** W01-P00 已执行并通过人类审核  
**后继任务:** W01-P02 Cloud Topology  
**核心目标:** 让下一批 Agent 只需要理解一套 Moodify。

---

# 0. 本包为什么存在

W01-P00 的任务是回答：

> Moodify 此刻真实存在什么？

W01-P01 的任务不同：

> **在已经确认现实之后，哪些现实应成为新的 Canon，哪些应被降级为内部能力、实验、历史或待迁移状态？**

本包不扩展功能。

本包不做新的云端能力。

本包不处理真实歌曲。

本包做的是 AI 原生项目中最重要的一类“结构性熵减”：

- 删除权威冲突；
- 降低 Agent 冷启动理解成本；
- 固定对外产品边界；
- 固定内部系统边界；
- 固定文档权威顺序；
- 固定“历史文档不能反向覆盖当前 Canon”的规则；
- 将模糊的口头方向固化为可继承的 repository authority。

完成以后，新的 Agent 进入 Moodify，不应该再需要重新讨论：

- Moodify 对外到底是什么产品；
- Ear 是产品还是内部能力；
- Player / Music 与 Ear 的关系；
- 旧 README 与新产品方向谁优先；
- 哪些文档只是历史；
- 什么能够进入 1.0 主河道；
- 什么只能作为实验或内部工具存在。

---

# 1. 执行前置门

## GATE P01-0 — P00 Reality Gate

执行者必须先确认 W01-P00 的以下产物存在：

- `00_EXECUTIVE_REALITY_SUMMARY.md`
- `01_GITHUB_REPOSITORY_REALITY.md`
- `02_TASK_PACKAGE_REALITY.md`
- `03_CLOUD_INFRASTRUCTURE_REALITY.md`
- `04_DATA_AND_EXTERNAL_CAPABILITIES.md`
- `05_MOODIFY_TRUTH_TABLE.md`
- `05_MOODIFY_TRUTH_TABLE.csv`
- `06_CONFLICTS_UNKNOWNS_AND_BLOCKERS.md`
- `07_CURRENT_SYSTEM_MAP.mmd`
- `08_EVIDENCE_INDEX.md`

若缺失任一关键产物：

> **STOP — P00_INCOMPLETE**

不得凭历史记忆直接执行 P01。

---

# 2. 当前最高层人类方向

以下内容是本包编排时已经明确的人类产品方向，属于“当前显式人类指令”，优先级高于旧仓库文档：

## 2.1 对外产品

Moodify 的唯一对外产品面收敛为：

> **Moodify Music / Moodify Player**

第一阶段用户外部体验围绕：

> **PLAY**

对外不要求用户理解内部音频工程、Ear、分轨、后处理、Evidence 或状态机。

---

## 2.2 内部能力

`Moodify Ear / Auditory Intelligence` 不再作为独立公开产品面。

它应被重新解释为 Moodify 内部听觉判断、分析、验证、学习与研究能力的一部分。

可以保留其：

- Listen
- Represent
- Judge
- Evidence
- Uncertainty
- Learn
- Verify
- Controlled Intervention

等研究和工程能力。

但不允许继续与 Moodify Music 形成两个对外产品权威。

---

## 2.3 产品表面与内部复杂度

外部应尽可能简单：

```text
Source / Cloud-prepared Track
        ↓
      Moodify
        ↓
       PLAY
```

内部可以复杂：

```text
Intake
→ Identify
→ Analyze
→ Stem
→ Judge
→ Intervene
→ Preset Decision
→ Render
→ Verify
→ Evidence
→ Learn
```

**复杂度由 Moodify 承担，而不是转嫁给用户。**

---

# 3. 本包的 3 个原子任务

# T01-1 — Authority Conflict Adjudication

输入：

- P00 Truth Table
- P00 Conflict List
- current explicit human direction
- current repository authority files
- current main behavior / tests

目标：

建立 `CANONICAL_DECISION_REGISTER.md`。

每一个权威冲突必须属于以下结果之一：

| Decision | 含义 |
|---|---|
| `CANONICAL` | 成为当前权威 |
| `INTERNAL` | 保留，但仅作为内部系统/研究能力 |
| `EXPERIMENTAL` | 允许存在，不得覆盖主线 |
| `LEGACY` | 历史保留，不再指导当前开发 |
| `MIGRATION_PENDING` | 方向已确定，但尚未迁移 |
| `HUMAN_DECISION_REQUIRED` | 现有证据不足，不得猜测 |
| `REMOVE_LATER` | 明确无权威价值，但本包不做大规模删除 |

## 必须裁决的最小对象

- root `README.md`
- root `AGENTS.md`
- `docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md`
- `docs/ASSET_MODEL.md`
- `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md`
- `docs/REPOSITORY_STATUS.md`
- Android 当前产品表面
- Ear / Auditory Intelligence 身份
- Moodify Music / Player 身份
- cloud / runtime 文档
- PR #21 中与产品身份有关的部分
- 任何被 P00 识别为 duplicate authority 的状态机 / orchestration / API 文档

### 禁止

不要因为新 Canon 成立就删除旧代码。

此任务只裁决 authority。

---

# T01-2 — Canon Surface Convergence

目标：

让所有高权威入口对 Moodify 给出**同一个答案**。

## 2.1 必须更新/建立的 Canon Surface

至少包括：

### Root

- `README.md`
- `AGENTS.md`

### Canon Docs

建议建立：

```text
docs/canon/
├── CURRENT_CANON.md
├── PRODUCT_BOUNDARY.md
├── INTERNAL_SYSTEMS.md
├── AUTHORITY_ORDER.md
└── CURRENT_ARCHITECTURE.md
```

若仓库已有等价且更合理结构，可复用，不应为了模板创造第二套权威。

### Repository Status

- `docs/REPOSITORY_STATUS.md`

必须从“历史静态快照”转为指向当前 Canon 与事实状态的入口。

---

## 2.2 README 的目标

README 应回答用户和开发者：

1. Moodify 对外是什么？
2. 第一阶段核心体验是什么？
3. 云端为什么存在？
4. 内部 Ear 是什么角色？
5. 当前哪些能力 production-ready，哪些不是？
6. 哪些复杂度不应该暴露给用户？

README 不需要成为研究论文。

---

## 2.3 AGENTS 的目标

`AGENTS.md` 必须成为未来 Agent 的最高仓库级认知入口。

至少固定：

### Product Identity

```text
External product:
Moodify Music / Player

Core user action:
PLAY

Internal systems:
Ear / auditory intelligence / analysis / processing / evidence / learning
```

### Authority Order

建议：

1. current explicit human instruction
2. root `AGENTS.md`
3. `docs/canon/*`
4. verified runtime evidence
5. canonical main behavior + tests
6. current subsystem docs
7. experimental docs
8. historical / legacy docs

### Agent Rules

- 不创建第二个公开产品身份
- 不把 Ear 再次升级成独立公开产品
- 不创建第二套 authoritative state machine
- 不创建第二套 Job authority
- 不以“功能很多”作为产品价值
- 不把内部处理复杂度暴露给用户作为卖点
- 不因文档冲突而自行做产品哲学决策
- 不把历史文档当作当前 authority

---

## 2.4 旧 Auditory Intelligence 文档的处理

原则：

> **保留研究资产，降低产品权威。**

如果 `AUDITORY_INTELLIGENCE_ARCHITECTURE.md` 中的能力仍有价值：

- 不删除；
- 明确标记为 `INTERNAL`;
- 在顶部写清其当前角色；
- 指向新的 `docs/canon/CURRENT_CANON.md`;
- 删除或修改“它是唯一对外产品身份”的表述。

---

## 2.5 历史文档处理

不要大规模删除历史。

历史文件应采用最小标记：

```text
Status: LEGACY / HISTORICAL / EXPERIMENTAL
Authority: Does not override docs/canon/*
```

如果历史文档数量巨大，不要逐文件改。

优先：

- 通过目录级 policy 收敛；
- 只修改会被 Agent 高频误读的入口文档。

---

# T01-3 — Canon Guardrails & Acceptance

目标：

保证新 Canon 不只是“写了一遍”，而是以后不容易再次漂移。

## 3.1 Authority Conflict Guard

至少增加一种低成本检查机制。

可采用：

- 文档测试；
- grep-based guard；
- Python policy check；
- CI check；
- canonical front-matter validation。

其目的不是查找所有出现 `Ear` 的文本。

正确目标是：

> 防止高权威文件再次把 Ear 定义为独立公开产品，或出现相互冲突的产品身份。

---

## 3.2 Canon Reference Rule

所有未来重要任务包应先读取：

- root `AGENTS.md`
- `docs/canon/CURRENT_CANON.md`
- `docs/canon/PRODUCT_BOUNDARY.md`
- `docs/REPOSITORY_STATUS.md`

如果 P00 后发现仓库已有更合理权威文件，则以最终 Canon 决策为准。

---

## 3.3 Canon Change Rule

以后任何改变以下内容的任务：

- 对外产品身份
- 内部/外部能力边界
- state machine authority
- evidence authority
- cloud control authority
- data authority

都必须明确写：

```text
CANON_CHANGE = YES
```

并说明：

- why
- evidence
- affected authority files
- migration
- rollback

普通功能任务不能静默修改 Canon。

---

# 4. 本包允许修改什么

允许：

- root authority docs
- `docs/canon/*`
- repository status / policy docs
- 对高频误导入口增加 `LEGACY / INTERNAL / EXPERIMENTAL` 标记
- 极小的 CI / policy guard
- 与 Canon 文档直接相关的测试

不允许：

- 大规模代码重构
- cloud deployment
- database migration
- OSS changes
- Android 功能开发
- 音频 pipeline 改造
- state machine 重构
- 合并 PR #21
- 删除大量 legacy code
- 修改真实音频
- 修改 production server

---

# 5. PR #21 的特殊规则

P01 不自动 merge、close、rebase PR #21。

只做：

1. 读取 P00 对 PR #21 的现实判断；
2. 区分其中：
   - 可保留的基础设施能力；
   - 与新 Canon 冲突的产品表述；
   - 尚未验证的运行能力；
3. 输出 `PR21_CANONICAL_COMPATIBILITY.md`。

必须将 PR 处理成：

> **能力与产品哲学分离评估**

不能因为一个 PR 使用旧语言，就否定其中所有工程资产。

也不能因为其中工程资产有价值，就把旧产品身份重新带回 Canon。

---

# 6. Canon 的目标结构

目标不是强制文件名，而是强制“只有一套答案”。

建议逻辑：

```text
Moodify
│
├── External Product
│   └── Moodify Music / Player
│       └── PLAY
│
├── Cloud Production System
│   ├── Intake
│   ├── Job / State
│   ├── Storage
│   ├── Compute
│   ├── Render
│   └── Delivery
│
├── Internal Auditory Systems
│   ├── Ear
│   ├── Analysis
│   ├── Stem
│   ├── Judgment
│   ├── Intervention
│   ├── Preset Decision
│   ├── Verification
│   └── Learning
│
└── Cognitive Infrastructure
    ├── Canon
    ├── Evidence
    ├── Cases
    ├── Rules
    ├── Failures
    └── Task Grammar
```

注意：

这里是 Canon 逻辑图，不是 P02 最终云拓扑。

---

# 7. 必须输出的文件

执行完成后至少输出：

1. `00_P01_EXECUTIVE_SUMMARY.md`
2. `01_CANONICAL_DECISION_REGISTER.md`
3. `02_AUTHORITY_CONFLICT_MATRIX.md`
4. `03_TARGET_CANON_MAP.mmd`
5. `04_PRODUCT_BOUNDARY_DECISION.md`
6. `05_INTERNAL_SYSTEMS_DECISION.md`
7. `06_PR21_CANONICAL_COMPATIBILITY.md`
8. `07_CANON_CHANGELOG.md`
9. `08_CANON_ACCEPTANCE_REPORT.md`

以及实际修改后的：

- `README.md`
- `AGENTS.md`
- canonical docs
- minimal guard / test（如采用）

---

# 8. 验收标准

本包只有满足以下条件才完成：

- [ ] P00 已完整读取
- [ ] 所有关键 authority conflicts 已进入 Decision Register
- [ ] root README 与 AGENTS 对产品身份无冲突
- [ ] Moodify Music / Player 是唯一公开产品面
- [ ] PLAY 被明确为第一阶段核心用户动作
- [ ] Ear 被明确为内部听觉系统/研究能力
- [ ] 内部复杂度与外部产品表面被明确分离
- [ ] 旧 Auditory Intelligence 资产未被粗暴删除
- [ ] legacy / experimental docs 不再覆盖 current Canon
- [ ] PR #21 没有被自动 merge/close
- [ ] 不存在第二套新 Canon
- [ ] 不改变 runtime behavior
- [ ] 不修改服务器、数据库、OSS
- [ ] 至少有一种低成本 Canon drift guard
- [ ] `git diff --check` 通过
- [ ] 相关文档/政策测试通过
- [ ] 所有未决问题明确标记 `HUMAN_DECISION_REQUIRED`
- [ ] 输出 Canon Changelog
- [ ] 完成后停止，不进入 P02

---

# 9. 失败条件

出现以下任一情况，本包不得验收：

- 新增一个与 `AGENTS.md` 并列的根级最高 authority；
- 仍然让 README 与 AGENTS 对产品身份说不同的话；
- 把 Ear 和 Moodify Music 同时描述为对外一级产品；
- 为了“干净”而大规模删除旧工程资产；
- 因为 P00 未知项而猜测真实 runtime；
- 顺手修改 state machine / API / worker；
- 顺手部署云端；
- 自动合并 PR；
- 把理想架构写成当前现实状态；
- 用 Canon 文档覆盖真实证据。

---

# 10. 向 P02 的交接

P01 完成后，P02 不再讨论“我们是谁”。

P02 只回答：

> **在已经固定的 Moodify Canon 下，现有真实服务器应该怎样分工，才能以最低认知摩擦承载 One Song Infrastructure？**

P02 的输入应为：

- P00 Reality Snapshot
- P01 Canon
- 当前云基础设施事实
- 尚未解决的 infrastructure blockers

---

# 11. 最终执行口令

> 执行 W01-P01 Canonical Convergence。  
> 首先核验并读取 W01-P00 全部结果。  
> 以当前显式人类产品方向作为最高产品决策依据，以 P00 事实作为现实依据。  
> 收敛 README、AGENTS、canonical docs 与 repository status，让 Moodify Music / Player 成为唯一对外产品面，让 Ear/Auditory Intelligence 降为内部听觉与研究系统。  
> 保留有价值的历史工程资产，不做大规模删除，不修改 runtime，不部署云端，不修改数据库/OSS，不自动合并 PR。  
> 对无法由人类方向与证据共同解决的冲突写 HUMAN_DECISION_REQUIRED。  
> 完成 Canon drift guard 与验收报告后停止，等待人类审核，不进入 W01-P02。
