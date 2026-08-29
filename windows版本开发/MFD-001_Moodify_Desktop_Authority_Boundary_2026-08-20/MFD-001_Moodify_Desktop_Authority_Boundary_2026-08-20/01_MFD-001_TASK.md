# MFD-001 — Moodify Desktop Authority & Boundary
## Codex 正式执行任务书

**任务编号：** MFD-001  
**日期：** 2026-08-20  
**执行方式：** 分阶段执行  
**默认仓库：** `huliye24/moodify-ai`  
**允许修改类型：** 文档 / 权威声明 / 架构边界文档  
**禁止修改类型：** 功能代码、音频算法、生产基础设施、Android 功能、Electron 客户端实现

---

# 0. 总命令

你的任务不是“开始做 Windows”。

你的任务是：

> **为 Moodify Desktop 建立一个与最新人类产品决策一致、与现有仓库真实状态一致、并且不会产生第二套权威系统的工程入口。**

执行必须分成 A / B / C 三个阶段。

---

# A. 阶段 A — 只读调查

阶段 A 严格只读。

不得：

- 修改文件；
- 创建分支；
- 提交；
- push；
- 创建 PR；
- 删除旧代码；
- 重命名目录；
- 安装 Electron；
- 初始化新项目；
- 修改服务器；
- 修改 Cloud；
- 修改数据库；
- 修改 Android。

## A1. 建立仓库事实快照

至少确认：

- 当前 branch；
- HEAD commit；
- dirty / clean 状态；
- 根目录；
- 根 `AGENTS.md`；
- 根 `README.md`；
- `docs/REPOSITORY_STATUS.md`；
- canonical architecture docs；
- legacy / experimental policy；
- 当前 app / frontend / Android 相关目录；
- Cloud / BFF / API 相关目录；
- 音频 core / Ear / research 相关目录；
- CI / build / release 配置；
- 是否已经存在 Electron、Node desktop、Tauri 或其他桌面客户端痕迹。

要求：

**所有结论必须基于真实文件、真实代码或真实运行证据。**

不得仅凭历史文档推断“现在已经存在某能力”。

---

## A2. 搜索产品身份冲突

搜索以下概念及近义表达：

- `The Ear of AI`
- `Auditory Intelligence`
- `Moodify Ear`
- `Moodify Music`
- `Moodify Player`
- `player`
- `music platform`
- `desktop`
- `windows`
- `android`
- `app`
- `preset`
- `post-processing`
- `automatic mastering`
- `cloud`
- `BFF`
- `playback`

输出：

`identity_conflict_inventory.md`

至少包含：

| 文件 | 当前声明 | 权威级别 | 是否与 2026-08-20 人类决策冲突 | 建议 |
|---|---|---|---|---|

重点不是机械替换词语，而是识别：

> 哪些旧定义仍是内部技术真相，哪些旧定义已经错误地占据“对外产品身份”位置。

---

## A3. 盘点客户端与服务边界

输出真实系统图，不允许从愿景反推现实。

至少区分：

```text
User-facing Client
Playback API / BFF
Cloud Runtime
Storage / DB
Internal Ear / Processing
Research / Experimental
Legacy
```

对每一层标记：

- PRESENT
- PARTIAL
- UNRESOLVED
- ABSENT
- LEGACY
- EXPERIMENTAL

并给证据路径。

---

## A4. 盘点 Android 可复用资产

不要重写 Android。

只回答：

1. Android 当前在仓库哪里？
2. 哪些是产品层资产？
3. 哪些 API contract 可以被 Desktop 复用？
4. 哪些 UI / 状态模型不应该直接移植？
5. Android 是否使用公开用户级认证，还是仍依赖内部 service key？
6. 当前 Android 能否作为 Desktop 协议设计的参考？
7. 是否有共享 schema / types / playback manifest？

输出：

`android_reuse_map.md`

---

## A5. 盘点 Cloud / Playback 的真实接口

只读确认：

- 公开 API；
- 内部 API；
- BFF；
- auth；
- track metadata；
- stream URL / media URL；
- playback version；
- playlist / queue；
- upload；
- processing status；
- service-key；
- CORS / origin assumptions；
- 是否存在适合桌面客户端使用的 endpoint。

严禁在本阶段修改服务器。

输出：

`desktop_cloud_readiness.md`

必须明确区分：

```text
EXISTS_AND_VERIFIED
EXISTS_BUT_INTERNAL
DOCUMENTED_ONLY
HISTORICAL
MISSING
UNKNOWN
```

---

# B. 阶段 B — 权威重建

只有阶段 A 完成后才允许进入。

本阶段仍然禁止功能代码。

允许：

- 新建权威 Markdown；
- 修改根级产品身份文档；
- 将旧身份重新解释为内部技术系统；
- 增加 Desktop 的架构边界说明；
- 修正文档互相冲突的 authority order。

## B1. 新的产品权威必须表达以下结构

```text
Moodify
│
├── Moodify Player / Moodify Music
│   ├── Android
│   ├── Desktop
│   │   └── Windows
│   └── iOS (future)
│
├── Moodify Cloud
│   ├── Playback services
│   ├── User / library services
│   ├── Media / processed assets
│   └── Internal orchestration
│
└── Moodify Ear
    ├── Listen
    ├── Represent
    ├── Judge
    ├── Intervene
    ├── Verify
    └── Learn
```

其中：

### Moodify Player
当前唯一对外产品面。

### Moodify Ear
内部技术 / 研究 /听觉智能系统。

Ear 的研究价值、WSE / MSE / PPE、证据体系、判断、验证、学习循环可以保留。

**不要删除 Ear。**

要做的是改变它的产品层级：

```text
旧：
Moodify = Ear

新：
Moodify contains Ear
Ear serves Player / Cloud internally
```

### Moodify Cloud
不是用户产品品牌，而是 Player 与 Ear 之间的生产基础设施和服务层。

---

## B2. 对“preset”表述做精确修正

禁止从一个极端走向另一个极端。

不得把 Moodify 重新定义成：

> 一个 presets 产品。

正确结构是：

```text
Auditory Intelligence / processing
        ↓
Playback Decision
        ↓
Track-specific Playback Result
        ↓
Play
```

“每首歌一个专属播放预设”可以作为产品机制和阶段性工程表达，但不能覆盖 Moodify 的全部技术身份。

对外体验可以简单。

内部系统仍然可以复杂。

---

## B3. 更新根权威

如果阶段 A 未发现新的更高优先级事实阻止更新，则应对以下至少进行评估：

- `AGENTS.md`
- `README.md`
- `docs/REPOSITORY_STATUS.md`
- 相关 architecture / product authority 文档

目标：

以后 Codex / Agent 读根权威时，首先理解：

> **当前用户产品是 Moodify Player。Moodify Ear 是内部系统。Desktop 是 Player 的客户端，不是第二个产品。**

不得进行无关 README 美化。

不得批量重写历史研究文档。

历史材料可以保留为历史证据。

---

# C. 阶段 C — Desktop 工程边界决策

## C1. 给出仓库策略结论

评估：

### 方案 A
`moodify-ai/apps/desktop`

### 方案 B
独立 `moodify-desktop`

### 方案 C
其他结构

必须基于：

- 当前仓库体积与领域混杂程度；
- 发布周期；
- Node / Electron 依赖与 Python core 的隔离；
- CI；
- secrets；
- 版本管理；
- Android / Cloud 是否已独立；
- GPL / license implications；
- 未来 macOS / Linux 复用；
- Agent authority；
- 部署边界。

**预期倾向不是强制答案：**

> 独立 `moodify-desktop` 更符合薄客户端和独立发布边界。

但若真实仓库证据证明 monorepo 更合理，可以提出反对意见。

不得为了迎合预设而伪造结论。

---

## C2. 定义 Desktop 的责任

Desktop SHOULD：

- 启动 Moodify；
- 用户认证；
- 获取用户可见音乐；
- 请求 playback manifest；
- 播放；
- pause / seek / next / previous；
- 显示最少必要信息；
- 保存客户端本地状态；
- 处理网络与播放错误；
- 后续支持 Windows system integration。

Desktop SHOULD NOT：

- 成为 Ear；
- 在 renderer 中执行重型音频分析；
- 保存内部 service key；
- 直接连数据库；
- 复制 Cloud 业务状态机；
- 创建第二套 track authority；
- 暴露 stems / internal judgment / processing graph；
- 在首版承担训练；
- 在首版实现复杂 DSP；
- 在首版实现 WASAPI exclusive；
- 在首版实现皮肤市场 / 社区。

---

## C3. 定义边界接口草案

只定义 contract，不实现。

建议概念：

```text
Desktop
  ↓
Public Desktop / Player API
  ↓
BFF
  ↓
Internal Moodify services
```

至少定义未来 MFD-003 需要确认的资源：

```text
Session
Library
Track
PlaybackManifest
Queue
PlaybackError
ClientCapability
```

不要擅自承诺 endpoint 已经存在。

如果不存在，应标 `MISSING`，留给 MFD-003。

---

# 1. 禁止项

本包内严禁：

- `npm create electron-*`
- `npm install electron`
- 新 Electron 窗口
- React UI
- Vite
- Windows installer
- Electron Forge
- native audio
- WASAPI
- FFmpeg 新集成
- 新 DSP
- 新 preset algorithm
- 修改 Audiolla / LALAL pipeline
- 修改生产 Cloud
- 修改 PolarDB
- 修改 OSS
- 修改服务器 systemd / nginx / Cloudflare
- 修改 Android 行为
- 批量删除 Ear / legacy
- 创造第二套 production case / evidence / state machine
- 把未经验证能力写成“已生产可用”
- 泄露 service key / token / secret

---

# 2. 必须保留的工程原则

## 单一权威

一个概念只能有一个 canonical authority。

## 薄客户端

Desktop 是 Playback terminal，不是第二个 Cloud。

## Cloud Authority

业务资产与用户业务状态由 Cloud 掌握。

## Ear Internal

Ear 的复杂度留在系统内部。

## Play First

后续 Desktop MVP 最重要的行为是：

> Play.

## Evidence Before Claim

没有代码 / API / 运行证据，就不能标成 READY。

## No Mass Rewrite

新方向不意味着删除过去的研究资产。

---

# 3. 完成条件

本任务只有在以下全部完成后才算结束：

1. 有真实仓库快照；
2. 有 identity conflict inventory；
3. 有 Android reuse map；
4. 有 Desktop–Cloud readiness map；
5. 根 authority 已与最新产品决策一致，或明确说明为何不能修改；
6. 有新的 Moodify system boundary；
7. 有 Desktop responsibility boundary；
8. 有 repo strategy decision；
9. 有 open questions；
10. 有 MFD-002 prerequisites；
11. 没有新增 Electron 功能代码；
12. 没有修改生产环境；
13. 所有变更可被清楚审计。

---

# 4. 最终回报格式

最终回复人类时，只报告：

1. **你实际发现了什么**
2. **你修改了什么**
3. **新的权威结构是什么**
4. **Desktop 放在哪里**
5. **Cloud / API 目前有哪些真实缺口**
6. **有哪些阻塞 MFD-002**
7. **验证结果**
8. **commit / branch / diff summary（如有）**

不要写泛泛而谈的项目愿景。
