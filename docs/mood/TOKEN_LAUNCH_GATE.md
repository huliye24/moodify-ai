# TOKEN_LAUNCH_GATE — MOOD

**Version:** 1.0（MOOD FOUNDATION 011, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [CURRENT_CANON.md](CURRENT_CANON.md) · [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) · [ASSET_CLASSIFICATION.md](ASSET_CLASSIFICATION.md) · [IN_FLIGHT_CHANGE_REGISTER.md](IN_FLIGHT_CHANGE_REGISTER.md) · [SEPTEMBER_BUILD_ROADMAP.md](SEPTEMBER_BUILD_ROADMAP.md)

---

## 1. 总则

```text
MOOD Token Activation (Package 025) is BLOCKED until ALL of G0..G11 PASS.
```

任何进入 025 的尝试都必须显式越过全部 G0–G11；任一未 PASS 即视为越权。

011 **不**实现任何 G 之后的产物；011 **只**冻结 Gate 定义本身。

## 2. Gate 状态机

```text
G0  Canon            ──┐
G1  Public Foundation ─┤
G2  Library          ─┤
G3  Identity         ─┤
G4  Contribution     ─┤── ALL PASS ──▶ 025 Token Activation
G5  Network          ─┤
G6  Governance       ─┤
G7  Transparency     ─┤
G8  Security         ─┤
G9  Public Staging   ─┤
G10 Tokenomics Freeze �
G11 Launch Audit     ─┘
```

每个 Gate 必须有：

- **Status**：`NOT_STARTED` / `IN_PROGRESS` / `PASS` / `BLOCKED`
- **Owner**：人类或人类授权 Agent
- **Evidence**：具体交付物 / 测试 / 报告
- **Reviewer**：决定 PASS 的人类角色
- **Reviewer Time**：决定时间

011 期间 G0 状态 = `IN_PROGRESS`（由 011 推进到 `PASS`）；其余 G = `NOT_STARTED`。

## 3. Gate 定义

### G0 — Canon

```text
STATUS: IN_PROGRESS (011)
OWNER: 011 implementation + human authority
```

**目标：** MOOD WORLD + PROTOCOL + PORTAL Canon 冻结。

**PASS 条件：**

- [ ] `docs/mood/CURRENT_CANON.md` 存在并声明 `MOOD = WORLD + PROTOCOL + PORTAL`
- [ ] `docs/mood/SYSTEM_ARCHITECTURE.md` 存在并明确边界
- [ ] `docs/mood/PRODUCT_RELATIONSHIP.md` 存在并区分 Moodify Music / Player
- [ ] `docs/mood/ASSET_CLASSIFICATION.md` 存在并完成 KEEP / KEEP BUT DARK / FREEZE / SEPARATE
- [ ] `docs/mood/IN_FLIGHT_CHANGE_REGISTER.md` 存在并记录并行分支
- [ ] `docs/mood/TOKEN_LAUNCH_GATE.md`（本文件）存在并定义 G0–G11
- [ ] `docs/mood/SEPTEMBER_BUILD_ROADMAP.md` 存在并锁定 011–025
- [ ] `docs/mood/DECISION_LOG.md` 存在并记录 011 期间决议
- [ ] `docs/canon/CANON_CHANGELOG.md` 增加 011 条目
- [ ] Canon guard 扩展检测 `MOOD = WORLD + PROTOCOL + PORTAL` 与「MOOD ≠ Token」反模式

**PASS Reviewer：** 仓库权威人类。

**011 任务：** 完成本 Gate。

### G1 — Public Foundation

```text
STATUS: NOT_STARTED
OWNER: 012 / 013 / 014 implementation + human authority
```

**目标：** WORLD Home / Product Home 公共品牌语言统一。

**PASS 条件：**

- [ ] `docs/brand/public/` 增加 WORLD Home 章节
- [ ] `crestwavecoin.com` 上线语言通过 PUBLIC_BRAND_CONSTITUTION 复审
- [ ] Product Home 与 WORLD Home 的品牌分层写入 `PUBLIC_BRAND_CONSTITUTION.md`
- [ ] 公共 marketing 中无「Buy MOOD」CTA

### G2 — Library

```text
STATUS: NOT_STARTED
OWNER: 014 implementation + human authority
```

**目标：** MOOD Library（Whitepaper / Docs / Hash / Research）上线。

**PASS 条件：**

- [ ] Library 文档版本化
- [ ] Library docs hash 与 git SHA 锁定
- [ ] 历史 / archive docs 标注 `HISTORICAL`
- [ ] Library 不外露 FREEZE 资产

### G3 — Identity

```text
STATUS: NOT_STARTED
OWNER: 015 implementation + human authority
```

**目标：** MOOD Passport（Resident Identity）可用。

**PASS 条件：**

- [ ] Wallet + Passport 工作流可走通
- [ ] Resident identity 与 public identity 解耦
- [ ] 不强迫 on-chain identity
- [ ] `015` 全部测试 PASS

### G4 — Contribution

```text
STATUS: NOT_STARTED
OWNER: 016 implementation + human authority
```

**目标：** Contribution Network v1 上线（PROTOCOL 实际可跑）。

**PASS 条件：**

- [ ] `016` 全部测试 PASS
- [ ] Contribution 记录与 Reputation 快照可追溯
- [ ] 不自动产生 Token 奖励
- [ ] 不与历史 Genesis v1.0 冲突

### G5 — Network

```text
STATUS: NOT_STARTED
OWNER: 017 / 019 implementation + human authority
```

**目标：** Network Observatory + Nodes Registry 上线。

**PASS 条件：**

- [ ] `017` Network Observatory PASS
- [ ] `019` Nodes Registry PASS
- [ ] Node 类型覆盖 developer / compute / data / storage / validation / gateway
- [ ] 不引入「node reward formula」

### G6 — Governance

```text
STATUS: NOT_STARTED
OWNER: 020 implementation + human authority
```

**目标：** MIP Governance 上线。

**PASS 条件：**

- [ ] `020` MIP Governance PASS
- [ ] MIP 提交 / 评审 / 通过 / 落地的流程可走通
- [ ] 不预先绑定 Token 投票权
- [ ] MIP 不与 Canon 冲突

### G7 — Transparency

```text
STATUS: NOT_STARTED
OWNER: 021 implementation + human authority
```

**目标：** Treasury & Transparency 上线。

**PASS 条件：**

- [ ] `021` Treasury / Transparency PASS
- [ ] 公共政策 / provenance / transparency 报告可读
- [ ] 不外露 pending reward 转为 Token 的逻辑
- [ ] 历史 Genesis v1.0 的 transparency docs 标记历史

### G8 — Security

```text
STATUS: NOT_STARTED
OWNER: 022 implementation + human authority
```

**目标：** Security & Trust Layer 上线。

**PASS 条件：**

- [ ] `022` Threat model / auth / wallet / API / incident PASS
- [ ] GENESIS_SECURITY_REVIEW / THREAT_MODEL / PRIVACY_REVIEW / INCIDENT_RESPONSE 已纳入 022 引用
- [ ] 不引入会覆盖既有安全审查的新部署
- [ ] 不在 launch 前做「Token 智能合约」正式审计

### G9 — Public Staging

```text
STATUS: NOT_STARTED
OWNER: 023 implementation + human authority
```

**目标：** 公网端到端验证。

**PASS 条件：**

- [ ] `023` Public Staging E2E PASS
- [ ] WORLD Home / Product Home 站点可达
- [ ] PROTOCOL API 可被公共客户端读取
- [ ] 不暴露未来官方 CA
- [ ] 不暴露 MOOD Buy / Trade CTA

### G10 — Tokenomics Freeze

```text
STATUS: NOT_STARTED
OWNER: 024 implementation + human authority
```

**目标：** Tokenomics / Flap / Legacy / Risk / Audit 复审。

**PASS 条件：**

- [ ] `024` Genesis Readiness Review PASS
- [ ] Tokenomics 方案由人类批准
- [ ] Flap（首期）参数由人类批准
- [ ] Legacy 处置方案（哪些旧 CA / Genesis v1.0 进入 FREEZE）由人类批准
- [ ] Risk 评估报告存在
- [ ] Audit 计划存在（审计单位由人类决定）

### G11 — Launch Audit

```text
STATUS: NOT_STARTED
OWNER: 025 implementation + human authority
```

**目标：** MOOD Token Activation 之前最终审计。

**PASS 条件：**

- [ ] 全部 G0–G10 PASS 复审
- [ ] Tokenomics 复审
- [ ] Smart contract 审计报告（人类批准单位）
- [ ] Legal review（人类决定）
- [ ] 公共 launch checklist 完成
- [ ] HUMAN 显式授权进入 025

## 4. Gate 失败 / 越权处理

任何下列情形视为 025 越权尝试，立即停止：

1. 任一 G 未 PASS 但尝试 025 任务。
2. 任一 G 在未授权情况下被标记 PASS。
3. 任一 G 试图通过修改本 Gate 定义绕过自身。
4. 任一 G 试图覆盖 Canon 或 [CURRENT_CANON.md](CURRENT_CANON.md)。

越权尝试必须记录到 [DECISION_LOG.md](DECISION_LOG.md) 的 **HUMAN_DECISION_REQUIRED** 章节。

## 5. Gate 修改规则

- Gate 定义修改需要人类授权并记录 [DECISION_LOG.md](DECISION_LOG.md)。
- Gate 数量增加需要新版本号 + 复审。
- Gate 数量减少需要 **HUMAN_DECISION_REQUIRED**（默认不允许）。
- Gate 顺序调整需要人类授权。

## 6. Gate 与 Canon 守卫

Canon guard（`scripts/canon_guard.py`）扩展为：

- 检测 README / AGENTS 顶部是否声明 `MOOD = WORLD + PROTOCOL + PORTAL`。
- 检测 README / AGENTS 是否出现「MOOD Token = product」或「MOOD = single token」反模式。
- 检测 `docs/mood/CURRENT_CANON.md` 是否存在并包含必要声明。
- 检测公共 marketing / UI 路径下是否存在「Buy / Trade MOOD」CTA。
- 不直接验证 G0–G11 状态；Gate 状态由本文件 + DECISION_LOG + commit 记录共同保证。

## 7. 与 011 边界

011 推进 G0 到 PASS。011 不推进 G1–G11。

011 不允许：

- 把 G0 标记为 PASS 而未完成 G0 PASS 条件
- 把任何 G1–G11 标记为任何状态
- 修改本文件 Gate 定义（G11 之前 Gate 定义修改需人类授权）
- 在 011 期间执行任何 025 准备工作
