# PRODUCT BOUNDARY — Moodify

> **2026-10-15 Studio library boundary:** 人类授权 Studio 建设内部作品库与 Desktop → Cloud
> → App 发布链。Studio 负责输入与管理封面、音频、歌名、歌词；App 只负责播放。
> 这是荣景文川内部 operator / owner 工具，不把当前阶段扩张为公共 UGC、社交、Marketplace
> 或外部 Studio SaaS。“Web3 概念”只采用可验证的数据主权原则，不恢复历史 token/DAO 产品线。

> **2026-10-08 phase-one business boundary:** external B2B clients buy commercial music and
> production service, not Moodify software. Studio is internal; Play contains only first-party
> catalogue works and explicitly shared private client review sets. General consumer, UGC,
> marketplace, social and public Studio SaaS surfaces are paused. See
> [COMMERCIAL_MUSIC_OPERATING_MODEL.md](COMMERCIAL_MUSIC_OPERATING_MODEL.md).

> **2026-10-06 Wavefield boundary:** Moodify 的核心技术方向由 waveform-only processing 扩展为
> `waveform → observable wavefield → judged wavefield`。Wavefield Profile、条件化 render、实测/模拟/
> 推断分层证据属于 Core；真实录音棚、扬声器、麦克风阵列可作为可替换 field-realization Provider，
> 不形成第二套 Core。未经校准的 stereo projection 不得称为真实三维声场。

> **2026-10-05 Cloud-first override:** 对外首要产品定义为 **Moodify Cloud — Audio Intelligence, powered by GPU computing.** GPU 是计算底座，Cloud 是载体，Audio Intelligence 是产品能力层，API / Agent / Desktop / App 是入口。下文 Sound Protocol / Core / CLI / Studio / App 边界继续有效，但不再各自承担首要公开产品身份。网站可表达平台方向，但未验证能力必须显式限定为 direction / capability-specific availability。

> **2026-10-06 Judge-core boundary:** Moodify 的不可外包核心是处理前与处理后的两次 Judge。处理模型属于可替换 Provider 层；Judge 的契约、证据、校准、数据治理和升级规则属于 Moodify Core。Judge 是技术核心名，不是与 Moodify 并列的新产品品牌。当前成熟 `Judge-1` 尚未实现，不得对外虚构。

**Canon v2.1（Sound Protocol, 2026-09-23；One Core / Two Interfaces 延续）**

## External Product

**Name:** Moodify Sound Protocol（一个 Core，CLI 首要执行，App 播放/审听）。产品命题：**Generated is not finished.** 现有 MSP/0.1 只提供受限预设处理，不可将其表述为已完成的专业 Mix Graph 或自动质量验证。

**Primary user actions:**

- **Listener Side（Moodify App / Player）：`PLAY`** — 消费端，改善音乐被听见的方式；兼完成会话的 Preview / A-B / Review / Delivery。
- **Creator Side（Moodify CLI）：`PROCESS`** — 生产端，专业完成流（Import → Analyze → Diagnose → Plan → Process → Verify → Export），改善音乐本身。

**Public promise（现状声明，非远景承诺）：**
Moodify 提供以 `PLAY` 为核心的消费端聆听体验，同时提供以 `PROCESS` 为核心的生产端专业完成层；两者共享同一个 Moodify Core（声音智能）。完成会话的产出携带 Mix Graph、参数与证据，不是黑箱 wav。云端准备（识别、分析、重建、渲染）是内部生产环节，不要求消费端用户理解。

## Internal Systems

以下均为内部能力，除非人类权威显式改变：

- Moodify Ear / Auditory Intelligence
- audio analysis
- stem separation
- judgment
- controlled intervention
- preset decision
- verification
- evidence
- learning
- cloud production（intake → job → storage → compute → render → delivery）

**Moodify Core** 是跨生产端/消费端的共享资产：analysis / dsp / processing / playback / profiles / verification / contracts 统一来自 Core，interface 不得私藏第二套声音逻辑。

Core 的主要技术对象包含 `Waveform + Wavefield Profile + Reproduction Evidence`。文件域分析、模拟渲染与
真实空间采集必须共享同一证据契约；录音棚连接是 field-realization / measurement Provider，不拥有独立
Judge authority。

Core 的**战略中心**是 Moodify Judge；既有 DSP、processing 与 playback 仍属于共享 Core，但不因在
Core 中实现就自动成为必须自研的模型。第三方/开源 Provider 必须经显式适配层调用，并由同一 Judge
在调用前给出理由、在调用后验收结果。

## User-visible complexity rule

消费端用户不应需要理解内部处理即可获得核心播放体验。生产端（CLI）面向 Codex / Claude / 工程师 / 制作人 / 云服务器，复杂度由 Moodify 承担，不转嫁给消费端用户。

Public Brand 的品牌信念、语言层级和三站职责以 [`docs/brand/public/`](../brand/public/README.md) 为唯一主题权威：

- `rongjingmusic.com`：Moodify Product Home。
- `rongjingwenchuan.com`：荣景文川 Company Home。
- `rongjinwenchuan.xyz`：过渡 Web Player / 历史入口；`play.rongjingmusic.com` 迁移状态当前为 `UNVERIFIED`。

## Non-goals for current public surface

- 公开研究仪表盘
- 把内部状态机暴露为产品 UX
- 强迫用户选择工程预设
- 把 Ear 作为第二个公开产品
- 用未验证的云端能力作为宣传点
- 公共主页 / 关注 / 粉丝 / 动态流 / 排行榜 / 评论 / 点赞 / 公开作品发布平台 / 广告画像
  （2026-10-04 人类批准 Identity / Account / Personal History，但明确不批准上述任何一项）

## Identity / Account / Personal History boundary（2026-10-04 人类批准，Phase 3A）

**允许：** account / login / 受控云端 metadata / Desktop history sync。
**默认禁止上传：** 音频、stems、MIDI、曲谱、report/evidence、频谱图片、Mix Graph 全量参数、
本地绝对路径、源音频 hash、终端日志、搜索历史、收听时长与细粒度行为。

云端只有账户私有、白名单的轻量 metadata（标题、完成时间、最终选择、可选的一句话、粗粒度历史事件）。
跨设备可见历史，**不等于**跨设备可听：没有本地音频必须显示「音频仅在原设备」，且不提供播放按钮。

**Evidence boundary（延续）：** 不得把「账户服务已接入」写成「已上线」——真实账户能力以运行时证据
（两个测试账户的真实登录、RLS 隔离、同步幂等与删除语义）为准；未取得凭据时状态为 `DEPLOYMENT_BLOCKED`。
详细契约见 [MIP-0003](../../protocol/mips/MIP-0003-personal-identity-history.md)。

## Evidence boundary

不得声称云端能力可用，除非 W01-P00 或之后运行时证据已验证。
（P00 现实：静态音乐托管 + API 壳 + 数据工厂批处理 + audiolla 代理为已运行；完整 Ear 链路为仓库代码。）

## 对外命名与角色决议

Public Form Package 01 已解决 CD-011 中的当前阶段品牌表现和域名角色：公开主品牌为 **Moodify**，对外产品面继续为 Moodify Music / Player（该决议自 Canon v2.0 起由 AI-native Professional Audio Finishing System 覆盖，站点角色不变）；三个站点按上方职责收敛。最终收费模型、`.xyz` 迁移后的 301/302/保留策略，以及 Creator 能力的后续可见范围仍为 `HUMAN_DECISION_REQUIRED`。
