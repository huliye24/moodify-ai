# Terminology and Claims

**Document ID:** MFY-TERMINOLOGY-AND-CLAIMS-001  
**Version:** 1.0  
**Date:** 2026-08-14  
**Status:** HISTORICAL TERMINOLOGY BASELINE — superseded for public language and product identity

**Owner:** Human product authority (huliye24)  

> **Authority notice (2026-08-20):** Public identity and language now resolve through `AGENTS.md`, `docs/canon/*`, and `docs/brand/public/*`. The table below preserves the 2026-08-14 terminology baseline for migration and provenance. It is not a current public-language registry. Current external product: **Moodify Music / Moodify Player**; Ear is an internal system; “The Ear of AI” is retired from the first public narrative.

## 1. 权威术语表

| 术语 | 定义 | 不是 | 权威文档 |
|---|---|---|---|
| **Moodify** | 主品牌：The Ear of AI，一个听觉智能系统 | 不是自动母带产品、预设浏览器、通用音频编辑器、黑箱质量评分 | 宪法 §2 |
| **The Ear of AI** | Moodify 的产品身份与核心主张：机器不只会生成声音，也真正学会听 | 不是营销口号；是身份声明 | 宪法 §2、官网蓝图 |
| **Auditory Intelligence** | 听→表示→判断→干预→验证→学习的可检查循环（Listen→Represent→Judge→Intervene→Verify→Learn） | 不是生成能力的副产品；生成≠听 | 宪法 §2/§3、Ear 框架 §1 |
| **Ear（Moodify Ear）** | 听觉智能产品：把声音变成可检查的判断、受控干预、验证与可复用证据 | 不是 DAW、不是自动母带、不是音乐质量评分器、不是 Music 的后台母体 | Ear 框架 §1 |
| **Music（Moodify Music）** | 以作品、创作者、来源与有意义连接为中心的聆听与发布环境 | 不是 Ear 仪表盘、不是音频处理台、不是实验指标公开排名 | Music 框架 §1 |
| **Intervention Laboratory（Auditory Intervention Laboratory）** | Ear 的受控干预子系统：创建有理由的候选与证据 | 不是产品身份；不是 Music 的后端母体；不自动承诺"更好" | 宪法 §3.4 |
| **Production Case** | 有目标、状态、输出与闭合的有界听觉任务；Ear 权威对象 | 不是处理记录堆；无 case 的文件不是可复用资产 | Ear 框架 §4 |
| **Evidence** | 从声称到可复现观测的持久链接（Evidence Artifact）；图表是证据的视图不是证据本身 | 不是内部路径/私人音频/prompt/未审日志 | Ear 框架 §4/§9、Music 框架 §11 |
| **Creation Passport** | 创作者对来源与过程的声明 | 不是版权认证、不是法律权属、不是 Ear 验证、不是自动 Moodify Ear 批准 | Music 框架 §7.4、product-boundary |

## 2. 关联术语（非权威术语，避免混淆）

| 术语 | 正确用法 |
|---|---|
| WSE / MSE / PPE | 三个纪律域：声学发生了什么 / 音乐结构 / 如何可复现产生验证 |
| Measurement Record | 命名方法/版本下产生的数值；不是判断 |
| Candidate | 干预的可追溯结果；不是成品承诺 |
| Rule | 从证据接受的版本化操作规则；单例成功不自动成规则 |
| Claim 成熟度 | Concept / Experimental / Verified / Human-reviewed（见 AUTHORITY_INDEX §3） |
| 交换流程 | requested→processing→evidence_ready→human_reviewed→optionally_attached（跨产品，不取代状态机） |

## 3. 统一用词规则（写作与代码注释）

1. 品牌身份统一为 **Moodify — The Ear of AI — an Auditory Intelligence System**；中文定位 **Moodify 是 AI 的耳朵**。
2. 两个产品永远叫 **Moodify Ear** 与 **Moodify Music**；缩写只允许在已定义上下文中使用。
3. 不要用"母带""后期""二次处理"描述 Ear 的产品身份；用"干预"（Intervention）与"受控候选"。
4. 不要用"AI 音乐工具""音频 App"等泛化词替代产品名。
5. 机器判断统一表述为"限定范围内裁决 + 升级路径"，不写"全自动评审"或"机器说了算"。
6. 实验指标永远带成熟度标签；不写"评分"作为产品功能名（除分数=测量分数的明确定义场景）。
7. Creation Passport 出现处（UI 与文档）必须伴随"不是版权认证"声明。

## 4. 判定规则（判断权威摘要）

- 范围外 / 证据不足 / 不确定 / 未解决感知判断 → `HUMAN_REQUIRED` / `INCONCLUSIVE` / 定义失败态；
- 人工裁决记录 reviewer、scope、timestamp、evidence；
- UI / runner / 运营脚本不得吞掉升级状态；
- 技术排名 ≠ 艺术质量 ≠ 版权结论。

## 5. 变更纪律

- 术语变更 = 产品权威变更，走 AUTHORITY_INDEX §5 冲突处理流程；
- 本表随 45–54 包落地维护，不静默覆盖冻结契约。
