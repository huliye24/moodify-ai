# PRODUCT_RELATIONSHIP — MOOD

**Version:** 1.0（MOOD FOUNDATION 011, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [CURRENT_CANON.md](CURRENT_CANON.md) · [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) · [TOKEN_LAUNCH_GATE.md](TOKEN_LAUNCH_GATE.md)

---

## 1. 总关系

```text
MOOD  (open Web3 digital world)
  │
  ├── MOOD PORTAL          ← world entry: crestwavecoin.com (PLANNED)
  │
  ├── MOOD PROTOCOL        ← Moodify Protocol (MPF-001..005)
  │       │
  │       └── Genesis Application
  │             └── Moodify Music / Player  (PLAY-first user app)
  │                   │
  │                   └── brand surface: rongjingmusic.com (active)
  │
  └── MOOD TOKEN           ← future Settlement/Incentive/Governance (NOT ACTIVATED)
```

**关系一句话：**

> MOOD 是世界，Moodify Music / Player 是这个世界上第一个应用；`crestwavecoin.com` 是世界入口，`rongjingmusic.com` 是产品入口。

## 2. Moodify Music / Player 是 Genesis Application

### 2.1 定义

Genesis Application 是 WORLD 中第一个具备完整用户体验的应用。它：

- 接受 PROTOCOL 的事实 / 声誉 / 节点目录作为输入。
- 提供 PLAY 等用户动作。
- 不定义 MOOD 的产品哲学（MOOD 不依赖 Moodify Music / Player 存在）。

### 2.2 与 MOOD WORLD 的边界

| 项 | MOOD WORLD | Moodify Music / Player |
|---|---|---|
| **产品身份** | 总体世界身份 | Genesis 应用 |
| **核心用户动作** | 任何协议级动作（contribute、register node、propose MIP 等） | **PLAY** |
| **入口域名** | `crestwavecoin.com`（PLANNED） | `rongjingmusic.com`（active） |
| **品牌语言层** | WORLD 公共语言（`docs/brand/public/` 未来新增 WORLD 章节） | Product 公共语言（`PUBLIC_BRAND_CONSTITUTION.md`） |
| **Token 表面** | FREEZE（未来激活） | FREEZE（不展示 Buy / Trade CTA） |
| **数据权威** | PROTOCOL（MPF-001..005） | 由 PROTOCOL 读取，不复制主权威 |

### 2.3 不混用品牌语言

- WORLD Home（crestwavecoin.com）与 Product Home（rongjingmusic.com）的品牌层 **互不混用**。
- Product Home 上的「Moodify」永远指 Moodify Music / Player，不指 WORLD。
- WORLD Home 上的「Moodify」永远指 MOOD Protocol / WORLD 总体，不是 Moodify Music / Player。
- 共享词「Moodify」在不同 Home 上分别解释；解释规则在 `docs/brand/public/` 的 WORLD 章节未来新增。

## 3. crestwavecoin.com 是 MOOD 世界入口

### 3.1 当前状态

`STATUS: PLANNED`

`crestwavecoin.com` 当前未上线。011 不授权上线。

### 3.2 上线触发条件

必须满足：

- G0 Canon（011 完成后 PASS）
- G1 Public Foundation
- G9 Public Staging（023）已交付
- WORLD Home 公共语言章节已写入 `docs/brand/public/`

上线决策属于 **HUMAN_DECISION_REQUIRED**。

### 3.3 与历史域名角色的关系

- 旧历史文档中出现的 `crestwavecoin.com` 进入 [IN_FLIGHT_CHANGE_REGISTER.md](IN_FLIGHT_CHANGE_REGISTER.md) 的 **SUPERSEDED** 处理。
- 任何在公开材料中提前把 `crestwavecoin.com` 描述为「已上线入口」都进入 **HUMAN_DECISION_REQUIRED** 复审。

## 4. Moodify Protocol 是 PROTOCOL 层

### 4.1 关系

```text
WORLD
  └── PROTOCOL = Moodify Protocol
                 ├── MPF-001 Mainnet Facts
                 ├── MPF-002 Contribution Core
                 ├── MPF-003 Reputation
                 ├── MPF-004 Node Registry
                 └── MPF-005 Protocol API
```

PROTOCOL 是 WORLD 的协议层。PROTOCOL 不等于「Moodify 公司开发的协议」，PROTOCOL = WORLD 上公开的协议事实。

### 4.2 与 Moodify Music / Player 的区别

- **Moodify Music / Player** 是 Genesis Application，使用 PROTOCOL。
- **Moodify Protocol** 是 WORLD 的协议层，不是应用。
- 不允许把 Moodify Music / Player 的产品哲学（如 PLAY-first）反向写进 PROTOCOL。

### 4.3 与「MOOD 公司 / 团队 / 法人」的区别

- MOOD 不等于荣景文川 / Moodify 公司。MOOD 是 WORLD。
- 公司是 WORLD 的一个 **resident**（建设者 + 节点运营者），不是 WORLD 的所有者。

## 5. MOOD TOKEN 是未来的经济层

### 5.1 当前状态

`STATUS: NOT ACTIVATED`

Token 在 011 期间保持未激活。

### 5.2 与 Genesis Application 的关系

- Token 激活后，Genesis Application（Moodify Music / Player）**可选择**集成 Token 体验（PLAY-and-Earn、Tip 等）。
- 在 G0–G11 全部 PASS 前，Genesis Application **不得**展示 Token Buy / Trade CTA。

### 5.3 与 PROTOCOL 的关系

- Token 是 PROTOCOL 的可选子集（future Incentive / Governance Layer）。
- PROTOCOL 文档（如贡献评分、声誉快照、节点注册）**不得**默认引入 Token 奖励。
- 任何把贡献自动转为 Token 的逻辑属于 **FREEZE**（见 [ASSET_CLASSIFICATION.md](ASSET_CLASSIFICATION.md)）。

## 6. AI Agents、Developers、Creators、Nodes 在关系中的位置

| 角色 | 与 WORLD 的关系 | 与 Moodify Music / Player 的关系 |
|---|---|---|
| **Resident**（默认） | WORLD 居民 | 可选使用 Genesis Application |
| **Developer** | WORLD 居民 | 可选贡献代码到 Genesis Application |
| **Creator** | WORLD 居民 | 主要在 Genesis Application 上发布内容 |
| **Node Operator** | WORLD 节点运营者 | 可选为 Genesis Application 提供 compute / data / storage |
| **AI Agent** | WORLD 第一类居民 | 可作为 PROTOCOL contributor |
| **Validator**（future） | WORLD 居民 | 由 020 MIP Governance 显式定义 |

任何角色都 **不拥有** WORLD；WORLD 不拥有任何角色。

## 7. 不做的事

011 不做：

- 不把 Moodify Music / Player 重新定义为「MOOD 核心产品」。
- 不把 PROTOCOL 改名为「Moodify Music Protocol」。
- 不把 crestwavecoin.com 提前描述为「已上线 MOOD 入口」。
- 不把任何 resident 的商业产品声明为 MOOD 官方产品。
- 不混用品牌语言（WORLD Home / Product Home / Company Home）。

## 8. 与既有权威的关系

- `docs/canon/CURRENT_CANON.md`（v1.1 Public Form）：处理 Moodify Music / Player 对外面，本文件不覆盖。
- `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md`：公共品牌语言最高主题权威，本文件不覆盖。
- `docs/mood/CURRENT_CANON.md`（本包）：处理 MOOD 总体身份与 Token Gate。
- 本文件是 MOOD 与 Moodify Music / Player 的关系文档，是 011 在 `PRODUCT_BOUNDARY` 之上的补充。
