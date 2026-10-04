# PRODUCT DEFINITION V3 — Moodify

**Version:** 3.0（Personal Music Node；在 v2.2 Open Protocol & Network 之上增加产品结构定义）
**Date:** 2026-10-03
**Status:** **DEFINED / TARGET** — 本文定义方向。除「现状」小节明确列出的部分外，以下能力**尚未实现**。
**Authority:** root `AGENTS.md` → `docs/canon/*`（[AUTHORITY_ORDER.md](AUTHORITY_ORDER.md)）
**Related:** [CURRENT_CANON.md](CURRENT_CANON.md) · [PRODUCT_BOUNDARY.md](PRODUCT_BOUNDARY.md) · [TECHNOLOGY_PRINCIPLES.md](TECHNOLOGY_PRINCIPLES.md) · [../governance/NETWORK.md](../governance/NETWORK.md)

> **本文不删除任何历史文档。** 与之冲突的旧表述可由本文覆盖（见 §8 冲突记录），但旧文档的文本保留，依据 `AUTHORITY_ORDER.md` 的「历史文档不能反向覆盖 Canon」。

---

## 0. 产品战略前提

Moodify 不以「技术最先进」作为竞争方式。

> **Use mature, public, common technology to build a stable product quickly.**
> 用成熟、公开、通用的技术，快速做出稳定的产品。

```text
stability      > novelty
completion     > ambition
working loop   > architecture purity
maintainability > technical fashion
```

先进技术只在**已被证明的产品瓶颈**要求时才引入。不因为技术上有趣就建造困难的基础设施。细则见 [TECHNOLOGY_PRINCIPLES.md](TECHNOLOGY_PRINCIPLES.md)。

产品命题不变：

> **Generated is not finished.（生成 ≠ 完成。）**

---

## 1. Moodify 是一个产品的五层

```text
Moodify
│
├── Core
├── Protocol
├── Studio
├── App
└── Network
```

**这不是五个独立产品。** 它们是同一个产品的五个层，各有单一职责。

| Layer | 职责 | Canonical 载体（现状） |
|---|---|---|
| **Moodify Core** | 声音分析、处理、验证、播放相关的声音能力 | `moodify-core-package/` |
| **Moodify Protocol** | Core / Studio / App / Agent 与未来集成之间的稳定契约 | `protocol/` + `docs/protocol/MOODIFY_SOUND_PROTOCOL_0_*.md` |
| **Moodify Studio** | Creator 侧桌面工作台：创建、处理、审听、完成、发布 | `moodify-desktop/` |
| **Moodify App** | **个人音乐节点**：接收、存储、播放，之后分享 | 见 §6 现状 |
| **Moodify Network** | 通过身份、分享与社交关系连接个人音乐节点与创作者 | **未实现**（V1 仅指 Desktop ↔ 个人手机） |

### 依赖方向（单向，不可逆）

```text
Protocol / Contracts
        ↓
       Core
        ↓
 ┌──────┴──────┐
Studio        App
```

一个能力只能有一个 canonical owner。任何 interface 不得私藏一份 Core 的声音算法（`AGENTS.md`「One Core, Multiple Interfaces」）。

### Studio 的规范生产流程（v3.0 补充，2026-10-03）

> **Understand first. Decompose second. Plan third. Process last.**（先理解，再分解，再规划，最后处理。）

```text
①  检测  →  ②  问题  →  ③  分轨  →  ④  结构  →  ⑤  方案  →  ⑥  成品
```

**三个处理预设（`clean_master` / `warm_vocal` / `wide_space`）属于 ⑥ 成品阶段，是工具而非流程起点。**
「分析完立刻处理立体声母带」已从流程中移除——那对母带来说太早了。
**分解先于规划**：⑤ 方案 在 分轨 + MIDI 齐备前保持锁定；⑥ 成品还需要一份真实写出的方案产物。
细则见 [`STUDIO_PRODUCTION_PIPELINE_V3.md`](STUDIO_PRODUCTION_PIPELINE_V3.md) §4。

完整定义见 [STUDIO_PRODUCTION_PIPELINE_V3.md](STUDIO_PRODUCTION_PIPELINE_V3.md)；
产物契约见 [../protocol/MOODIFY_STUDIO_CONTEXT_0_1.md](../protocol/MOODIFY_STUDIO_CONTEXT_0_1.md)。

---

## 2. 产品循环

```text
Create → Finish → Publish → Listen → Share → Feedback → Improve
```

V1 只做前四步。

---

## 3. 第一个真实用户故事（First Product Loop）

V1 **不需要**大型社交网络。它只需要解决一个极其清楚的问题：

> **我在电脑上完成一首歌，按下 Publish to My Library，歌就出现在手机上，我能立刻听。**

```text
Moodify Studio
      │
      │ Finish
      ↓
 Publish to My Library
      │
      │ local transfer
      ↓
 Moodify App
      │
      ↓
     Play
```

**这个循环可靠地工作，Moodify 就已经是一个有效产品。** 社交功能以后从这个循环生长，而不是相反。

---

## 4. Moodify App = 个人音乐节点（Personal Music Node）

App **初期不是另一个流媒体平台**，而是：

> **A personal music node. 个人音乐节点。**

App 拥有四项基本职责：

```text
My Library      我的音乐库
Playback        播放
My Identity     我的身份
Connections     连接
```

**最早版本只需要前两项**（My Library + Playback）。Identity 与社交是后续阶段。这防止过早复杂化。

---

## 5. 关键产品原则：创作者不依赖第三方运营平台

Moodify **不应要求创作者必须通过第三方音乐运营平台才能听见自己的作品**。

默认路径：

```text
Creator → Moodify Studio → My Library → My Phone
```

创作者拥有原始作品，并自行决定它的可见性：

```text
Private    私密
Shared     定向分享
Public     公开
```

### 但：不依赖音乐平台 ≠ 不使用服务器

> **Not depending on a music platform does not mean Moodify must avoid servers.**

未来基础设施可以提供：account service、device registry、authorized relay、object storage、notifications、social graph、public discovery。

**基础设施负责传输与连接。** 它不等于一个「控制创作者能否发布自己作品」的运营平台——这是两者的分界线。

---

## 6. 现状与目标的区分（IMPLEMENTED vs DEFINED）

**这一节是本文最重要的部分。** 以下区分必须被所有 Agent 与文档维护者保持。

### 已经存在（IMPLEMENTED）

```text
Moodify Core                 moodify-core-package/  （679 文件，v1.0.0-rc.1）
Moodify Protocol 0.1/0.2     moodify protocol validate|process；docs/protocol/
Moodify Studio（壳）          moodify-desktop/  （Electron ^33，v1.0.0-rc.1）
  └ 它只编排 Core；自身无 DSP。启动脚本仅 `electron .`
Moodify App（唯一正式移动端）  apps/music-android（com.moodify.music, v2.0.1/code 3）
  └ GitHub Release 工作流实际构建、签名和发布的 Android Player
```

### 还没有（DEFINED / TARGET — 尚未实现）

```text
Studio → My Library 的发布动作         不存在
Track package（manifest.json）          不存在
局域网传输 / 配对 / token               不存在
Android 端接收与音乐库                  不存在
App 身份（My Identity）                 不存在
账号 / 设备注册                         不存在
Moodify Network（节点互联）             不存在
远程分享 / 对象存储 / relay             不存在
```

**经仓库检索确认：** 全仓库没有任何 `publish to my library`、`lan sync`、`pairing token`、`local transfer` 的实现代码。

> **不得把 §6 的 TARGET 部分写成已实现。** 违反此条等同于 Canon 不虚构现实（R6/R10）的违反。

### Android App 裁决（2026-10-04）

人类产品权威已确认：**`apps/music-android` 是唯一 canonical Moodify App**。依据是它的产品职责为 public Android player / `PLAY`，并且 `.github/workflows/release.yml` 实际从该目录构建、签名和发布 APK。旧候选 `apps/android` 已退役删除。

这项裁决只收敛 App authority，不表示 `apps/music-android` 已实现本文件列出的所有 TARGET 能力；功能状态仍以可运行代码、测试和发布证据为准。

---

## 7. V1 范围与非目标

### V1 范围（Studio → My Phone）

```text
Studio publish
Track manifest
LAN transfer
Android receive
Local library
Playback
```

**No login required. No cloud required. No social required.**

### V1 明确不做

```text
Blockchain · Token · DAO · DID system · CRDT
Federated social protocol · Peer-to-peer global file network
Custom cryptography · Custom codec · Custom database
AI recommendation feed · Advanced distributed architecture
Microservice mesh · Kubernetes · Real-time collaborative DAW
Custom streaming protocol
```

完整排除清单与判定顺序见 [TECHNOLOGY_PRINCIPLES.md](TECHNOLOGY_PRINCIPLES.md)。

---

## 8. 冲突记录（Known Conflicts）

本文与既有 Canon 存在**两处真实分歧**。此处如实记录，不静默改写。

### 8.1 Creator 侧的主要产品面：CLI 还是 Studio？

| 来源 | 表述 |
|---|---|
| [CURRENT_CANON.md](CURRENT_CANON.md) §1（v2.1，2026-09-23） | Creator Side = **Moodify CLI**；「CLI 是首要执行接口」 |
| 本文 §1（v3.0，2026-10-03） | Creator Side = **Moodify Studio**（Creator 侧桌面工作台） |

**当前处理（非裁决）：** CLI 与 Studio **同在 Creator 侧**，不构成第二产品身份。CLI 是自动化 / Agent 接口（`PROCESS`），Studio 是人类工作台（`PROCESS`），两者调用同一个 Core。

**但「哪一个是 Creator 侧的首要对外产品面」尚未由人类裁决** → 记为 `HUMAN_DECISION_REQUIRED`（见对齐报告）。

### 8.2 App 的定义：Listening Interface 还是 Personal Music Node？

| 来源 | 表述 |
|---|---|
| [CURRENT_CANON.md](CURRENT_CANON.md) §1 | App / Player = **Listening Interface**（消费端），核心动作 `PLAY` |
| 本文 §4 | App = **Personal Music Node**：My Library / Playback / My Identity / Connections |

**关系：** 本文**扩展**而非否定。`PLAY` 仍是 App 的核心动作；「个人音乐节点」是在 `PLAY` 之上增加「拥有自己的音乐库」与「连接」两层含义。V1 只实现 My Library + Playback，因此 V1 的 App 行为与 v2.1 描述一致。

**结论：** 8.2 属扩展，不属冲突。8.1 是真冲突。

---

## 9. 本文不授权的内容

本文定义方向，**不授权**一次性实现 V1–V2。

- 不新增网络代码
- 不新增 Android 功能
- 不新增云功能
- 不删除任何遗留 Android 项目
- 不新增 server / login / social / account / cloud storage / WebSocket / P2P
- 不重写 Core 或 desktop；不引入 Flutter / React Native；不修改音频算法
- 不 mass-delete 历史目录

开发方法按 `AGENTS.md` 与任务包规则：**一次一个可验证的小步**，一步一 commit，合并后重新审计 `main` 再定义下一步。

---

## 10. Definition of Done（产品级）

一个功能不因为代码存在而完成。完成的条件是：

```text
build passes
tests pass
real user flow works
failure case is visible
documentation matches reality
no duplicate authority is introduced
rollback is possible
```

音频相关行为：**human listening review remains required**（适用处）。`Generated is not finished.`
