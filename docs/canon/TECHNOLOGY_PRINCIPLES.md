# TECHNOLOGY PRINCIPLES — Moodify

**Version:** 1.0
**Date:** 2026-10-03
**Status:** **DEFINED** — 工程决策规则。适用于所有新代码与技术选型。
**Authority:** root `AGENTS.md` → `docs/canon/*`
**Related:** [PRODUCT_DEFINITION_V3.md](PRODUCT_DEFINITION_V3.md) · [../governance/NETWORK.md](../governance/NETWORK.md)

---

## 1. 核心规则：优先级顺序

每一个工程决策，按以下顺序取用**最靠前**的可行方案：

```text
1. Already exists in the repository
2. Stable standard library / platform API
3. Mature open-source library
4. Mature commodity cloud service / protocol
5. Custom engineering
6. Experimental / frontier technology
```

**举证责任在 5 与 6。** 选择自定义或前沿技术的一方，必须说明为什么 1–4 不能解决问题。

> **If a stable public technology solves the problem, use it.**
> 如果稳定的公开技术能解决问题，就用它。

### 为什么这条规则存在

Moodify 的商业价值来自**可靠地完成音乐**，不来自基础设施的复杂度。一个能稳定传输并播放一首歌的平凡架构，比一个未完成的高级分布式架构更有价值。

```text
stability      > novelty
completion     > ambition
working loop   > architecture purity
maintainability > technical fashion
```

---

## 2. 应当使用的技术（SHOULD USE）

### Desktop

保持：

```text
Electron
Node.js
existing Moodify Desktop shell        moodify-desktop/
Python Moodify Core                   moodify-core-package/
```

**不要**在没有已证明阻塞的情况下把桌面应用重写成新框架。

### Audio Core

保持：

```text
Python
existing Moodify Core
FFmpeg where needed
existing DSP libraries
existing processing pipeline
```

**不要**为了理论性能把可工作的音频逻辑重写成 Rust / C++。

### Android

优先使用已有的原生实现：

```text
Kotlin
Gradle
Android platform APIs
Jetpack / Media3 where appropriate
```

**不要**在已有原生 Android 工程的情况下引入 Flutter 或 React Native——除非未来出现**具体的** iOS 需求。

### Local Transfer（V1）

从最普通的局域网技术开始：

```text
HTTP
JSON
SHA-256
random pairing / session token
LAN IP + port
```

可选的 QR 配对，使用成熟的 QR 库。

**不要**以这些起步：custom transport protocol · WebRTC · P2P overlay network · distributed hash table · IPFS · Bluetooth mesh。

只有当普通局域网传输**被证明不足**时才考虑它们。

### Local Metadata

使用简单稳定的格式：

```text
JSON manifest
SQLite
filesystem
```

**不要**建造分布式数据库。

### Future Backend

当需要远程分享时，优先：

```text
HTTP REST API
PostgreSQL
S3-compatible object storage
standard authentication
push notification services
```

尽量复用 `moodify-music-package/` 的既有资产，而不是从零新建后端。

---

## 3. V1 明确不建造（DO NOT BUILD IN V1）

```text
Blockchain
Token
DAO
DID system
CRDT
Federated social protocol
Peer-to-peer global file network
Custom cryptography
Custom codec
Custom database
AI recommendation feed
Advanced distributed architecture
Microservice mesh
Kubernetes
Real-time collaborative DAW
Custom streaming protocol
```

**这些不是永久禁令。** 只有当出现**具体产品需要**、并且该需要被证据支持时，才重新考虑——且届时需按 `GOVERNANCE.md §6` 走 MIP。

### 特别说明：为什么会列出 Blockchain / Token / DAO

本仓库历史上承载过一条**独立的** MOOD Protocol Web3 线（EVM/BSC 主网 BEP-20 代币，已部署合约）。该线已于 2026-10-03 移出主线（磁盘保留，见 `docs/ARCHIVE_INDEX.md`）。

该排除项针对的是 **Moodify 产品自身的技术选型**，不是对那条历史线的否定。`GOVERNANCE.md §9` 已明确 `NO TOKEN / NO DAO / NO AIRDROP / NO TREASURY GOVERNANCE`。

---

## 4. 商用质量的定义

商用就绪 **不等于** 技术先进。对 Moodify 而言，商用质量主要指：

```text
installable       可安装
predictable       行为可预期
stable            稳定
recoverable       可恢复
understandable    可理解
supportable       可支持
secure enough for its actual threat model
low operating cost
low maintenance cost
```

**Actual threat model** 是关键词：不为不存在的威胁建造防御（例如 V1 的局域网传输不需要端到端加密的自定义密码学，但需要一个随机 token 防止同网段误连）。

---

## 5. 与既有 Canon 的一致性

本文不改变：

- **One Core, Multiple Interfaces**（`AGENTS.md`）——任何 interface 不得私藏一份声音算法
- **依赖方向单向**：`protocol/contracts → core → studio/apps`
- **Canon 不虚构现实**（R6/R10）——未验证的能力不写成已运行
- **人类主权**——技术选型若改变产品边界，属人类裁决范围，Agent 必须写 `HUMAN_DECISION_REQUIRED`

本文**加强**以下既有规则：

- `AGENTS.md` 的「不以功能很多作为产品价值」
- `GOVERNANCE.md §5` 的「不以 commit 数量衡量贡献」
- `docs/governance/constraints/` 的 **ME-001 起源先于功能**（不无边界地拼装功能）与 **ME-003 整体一致性**（不复制一份权威）

---

## 6. 判定流程（决策时怎么用）

面对一个新需求：

```text
1. 仓库里已经有实现吗？          → 复用，不要重写
2. 标准库 / 平台 API 能做吗？     → 用它
3. 有成熟开源库吗？               → 用它
4. 有成熟商用服务/协议吗？        → 用它
5. 必须自己写吗？                 → 写最小的那部分
6. 必须用前沿技术吗？             → 停下来，写 HUMAN_DECISION_REQUIRED
```

第 6 步不是禁止，是**要求人类参与**。前沿技术的成本通常不在实现，而在维护、人员可替代性与故障恢复——这三项正是商用质量的核心。
