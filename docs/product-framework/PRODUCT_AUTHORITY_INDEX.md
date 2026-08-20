# Product Authority Index

**Document ID:** MFY-PRODUCT-AUTHORITY-INDEX-001  
**Version:** 2.1
**Date:** 2026-08-19
**Status:** LIVE — package MFY_PRODUCT_GOVERNANCE_FREEZE_001 (44)  
**Owner:** Human product authority (huliye24)  
**Scope:** 文档权威索引、判断权威矩阵、公开声明成熟度模型、冲突处理流程

## 1. 文档权威索引（谁说什么算数）

| 主题 | 权威文档 | 版本/状态 | 变更流程 |
|---|---|---|---|
| Public Brand 信念、公共语言、站点职责 | `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` + 同目录 authority set | Public Form v0.1 CANONICAL（2026-08-19） | 人类批准 + Canon changelog；高于本表中旧 public identity 文案 |
| 产品身份与边界 | `AGENTS.md` + `docs/canon/CURRENT_CANON.md` + `docs/canon/PRODUCT_BOUNDARY.md` | Canon v1.1（2026-08-19） | `CANON_CHANGE = YES` + 人类批准 + changelog |
| Public/Internal 发布拓扑 | `docs/product-framework/05_PUBLIC_INTERNAL_RELEASE_TOPOLOGY.md` | 1.0 ACTIVE | 人类批准 + 记录 |
| 当前产品资料入口 | `README.md` + `docs/REPOSITORY_STATUS.md` | CURRENT（2026-08-20） | 随 Canon 与验证事实更新 |
| 公开产品设计 | `docs/product-framework/06_MOODIFY_PUBLIC_PRODUCT_DESIGN_20260815.md` | APPROVED DIRECTION（2026-08-15） | 人类批准 + 真实产品验证 |
| 声音优先理念 | `docs/product-framework/07_SOUND_FIRST_PRODUCT_DOCTRINE_20260815.md` | CURRENT PHILOSOPHY（2026-08-15） | 盲听证据 + 人类批准 |
| v1 范围与减法 | `docs/product-framework/08_MOODIFY_V1_SCOPE_AND_SUBTRACTION_20260815.md` | CURRENT V1 SCOPE（2026-08-15） | 上线门 + 减法审计 |
| 官网信息架构与 claim 规则 | `docs/product-framework/02_OFFICIAL_WEBSITE_BLUEPRINT.md` | 1.0 HISTORICAL WHERE CONFLICTING；双产品叙事被宪章 2.0 取代 | 按 05 拓扑重发 |
| Ear 产品范围 | `docs/product-framework/03_MOODIFY_EAR_PRODUCT_FRAMEWORK.md` | 1.0 INTERNALIZED；能力保留，公开产品描述被宪章 2.0 取代 | 内部系统变更流程 |
| Music 产品范围 | `docs/product-framework/04_MOODIFY_MUSIC_PRODUCT_FRAMEWORK.md` | 1.0 APPROVED | 人类批准 + 记录 |
| 本索引 + 术语表 | `docs/product-framework/PRODUCT_AUTHORITY_INDEX.md`、`TERMINOLOGY_AND_CLAIMS.md` | 1.0 LIVE | 包 44 后按冲突处理流程 |
| 仓库工程宪法 | `docs/PHASE1_CONSTITUTION.md` | INTERNAL；身份/边界被 Canon v1.1 覆盖 | 工程契约变更流程；不得覆盖 Canon |
| 产品边界与共享契约 | `docs/contracts/product-boundary.md` | FROZEN（包 35，ec5aac1） | 冻结契约变更流程 |
| Ear 数据协议 | `docs/contracts/DATA_PROTOCOL_V1.md` | FROZEN | 冻结契约变更流程 |
| Ear 测量契约 | 版本化测量契约（MAMSE 系列 + 扫描 profile） | FROZEN/版本化 | 新版本而非覆写 |
| Music 契约 | `docs/contracts/music/` 六份 | FROZEN（包 35） | 冻结契约变更流程 |
| 公开声明 | README.md（公开入口） | 1.1 修正后 | claim 成熟度门 |
| 代理纪律 | AGENTS.md | 判断权威修正后 | 人类批准 |
| 上线总账 | `artifacts/phase1_launch/` 六份 | LIVE LEDGER | 每包完成时更新 |

> Public Form v0.1 决议：`TERMINOLOGY_AND_CLAIMS.md`、旧官网蓝图、旧域名拓扑中与 Public Brand Authority 冲突的公开身份/语言/站点角色均降为历史或迁移上下文；工程契约不会因此自动失效。

### 1.1 数据与状态所有权（44 P0-4：无冲突）

| 状态 | 唯一权威 | 禁止的其他系统行为 |
|---|---|---|
| Ear Production Case 生命周期 | Ear 契约状态机（moodify-core-package） | Music/客户端不得建并行状态图 |
| Ear 测量/判断 | 版本化测量契约 + 规则 | 不得静默升级为公开真相 |
| Music Track/发布状态 | Music 服务（moodify-music-package） | Ear 永不写 |
| Music 所有权 | Music 身份/所有权服务 | 客户端只读 |
| 跨系统分析请求 | requested→…→optionally_attached 交换流程 | 不取代任一状态机 |
| 公共 claim | 产品 owner + publish-safe 证据门 | 自动化不得自行签署 |

## 2. 判断权威矩阵（机器/人类，44 P0-5）

| 判断类型 | 机器可否裁决 | 条件 | 范围外行为 |
|---|---|---|---|
| 测量（WSE/MSE/PPE 可复现观测） | 可 | 命名方法/版本，容差内报告事实 | 不可越界解释 |
| 规则判断（确定性结论） | 可 | 已批准规则范围（如 MFY-ALGORITHMIC-REVIEW-001） | HUMAN_REQUIRED / INCONCLUSIVE / 失败 |
| 模型推断（概率解释） | 仅报告 | 必须给置信度与限制 | 不得伪装成确定性裁决 |
| 人类听音判断（感知/产品权威） | 否 | designated human reviewer | 最终决定 |
| 艺术质量/版权结论 | 否 | — | 永不（技术排名≠艺术质量/版权） |

规则（与 AGENTS.md/宪法一致）：

1. 算法仅在验证、版本化、明确授权范围内裁决；
2. 范围外、证据不足、不确定或未解决感知判断 → `HUMAN_REQUIRED`、`INCONCLUSIVE` 或失败；
3. 人工裁决记录 reviewer、scope、timestamp、evidence；
4. UI、runner、运营脚本不得吞掉升级状态；
5. 无值守运行 ≠ 自治；不得为无人值守而抑制升级。

## 3. 公开声明成熟度模型（44 P0-5，可执行）

| 状态 | 含义 | 公开必备 |
|---|---|---|
| Concept | 产品/研究方向 | 明确标注为意图 |
| Experimental | 有限测试中观察到 | 方法 + 限制 |
| Verified | 通过声明验证 | 验证范围 |
| Human-reviewed | 指定人类权威评审过 | 评审日期 + 范围 |

禁止公开声称：普适音质、保证改进、版权认证、无方法/证据的科学验证、单例外推算法优越性、把路线图当现有功能。

执行点：官网内容（46）、证据索引页（46/52）、README 与公开文案（本包已核）。

## 4. 术语表（详见 TERMINOLOGY_AND_CLAIMS.md）

当前公开术语以 `docs/brand/public/PUBLIC_LANGUAGE_REGISTRY.md` 为准。下游 `TERMINOLOGY_AND_CLAIMS.md` 中 The Ear of AI / 双产品相关条目只保留为历史迁移上下文；内部工程术语仍可在明确的 internal / research / evidence 语境使用。

## 5. 冲突处理流程

1. 发现冲突 → 判断涉及权威域，列出冲突文档与差异；
2. 若涉及冻结契约（科学/数据/共享契约）：走紧急变更流程，不在此处理；
3. 若涉及产品权威：形成决议摘要（影响、选择、证据）交人类产品权威；
4. 人类批准后：同步修订所有涉及文档 + 更新本索引 + DECISION_LOG 登记；
5. 每份修订附批准记录（approver、date、scope、evidence、resolution）；
6. 禁止：只改营销文案不修权威冲突；无记录覆盖冻结契约；批量删除历史文档伪装成当前规范；用同义词重新引入被否身份。

## 6. 执行纪律（来自包 44 Master Task）

- 任何公共声明必须有成熟度标签；
- 任何数据迁移必须有备份、dry-run、幂等、回滚；
- 任一 P0 失败阻止上线，不用 P1 文案掩盖；
- 本索引本身是 LIVE 文档，随包 45–54 落地更新。
