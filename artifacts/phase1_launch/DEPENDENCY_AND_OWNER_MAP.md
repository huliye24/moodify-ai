# Dependency and Owner Map — Phase I Launch

**Document ID:** MFY-PHASE1-DEPENDENCY-OWNER-MAP-001
**Version:** 0.1
**Date:** 2026-08-14
**Package:** MFY_PHASE1_PRODUCT_LAUNCH_MASTERPLAN_001 (43)
**Status:** LIVE LEDGER

## 1. 依赖图（无环性已验证：按 43→44→…→54 单向递增）

```text
43 总控
 └─ 44 治理冻结 ──┬─ 45 设计系统 ──┬─ 46 官网
                  │                └─ 47 Ear 表面 ──┬─ 48 Ear 权威+人工升级
                  └─ 51 身份基线 ──┤                └─ 52 证据桥（需 47/48/50/51）
                                   ├─ 49 Music 聆听 ──┴─ 50 Creator 发布（需 49）
                                   └─ 53 生产运维（需 46–52）
                                        └─ 54 上线验收（需全部）
```

依赖规则：
- 46 依赖 44+45；47 依赖 44+45；49 依赖 44+45。
- 48 依赖 44+47；50 依赖 44+45+49；51 独立于 45（只依赖 44），与 45 并行。
- 52 依赖 47+48+50+51（最多依赖的包）。
- 53 依赖 46–52 全部 P0；54 依赖全部。

## 2. Owner 表

| 领域 | 权威 owner | 工程 owner（实施） | 签字权 |
|---|---|---|---|
| 产品身份与边界 | 人类产品权威（本会话 = 用户） | 执行包分支 | 宪法批准、GO/No-Go |
| 判断权威（机器限定范围） | 人类产品权威 + 版本化规则 | moodify-core-package | 规则版本发布 |
| Ear 案例生命周期 | ProductionCase 状态机（契约） | moodify-core-package | 契约变更走紧急流程 |
| Ear 测量 | 版本化测量契约 | moodify-core-package | 契约变更 |
| Ear 产品表面 | 47 包 | apps/android + 工作台 | 47 P0 |
| Music 发布状态 | Music 服务（独占） | moodify-music-package | 服务契约 |
| Music 所有权 | Music 身份/所有权服务 | moodify-music-package | 服务契约 |
| Music 产品表面 | 49/50 包 | apps/music-web (+android) | 49/50 P0 |
| 官网内容与 claim | 46 包 + claim 成熟度门 | ops/web_origin/site | 46 P0 + 人类 |
| 身份/权限/隐私 | 51 包 | 待定（跨产品服务） | 51 P0 |
| 证据桥 | 52 包（有限交换契约） | moodify-core-package + music-package | 52 P0 |
| 生产运维/回滚 | 53 包 | ops/ | 53 P0 |

## 3. 跨产品状态唯一权威（防止第二状态机）

| 状态 | 唯一权威 | 其余系统角色 |
|---|---|---|
| Ear Production Case 生命周期 | moodify-core-package 契约状态机 | Music 仅外部引用 ID |
| Ear 测量/判断结果 | 版本化测量契约 + 规则 | 永不直接映射发布状态 |
| Music Track 状态 | moodify-music-package 发布契约 | Ear 永不写 |
| Music 所有权 | Music 身份服务 | 客户端只读 |
| 跨系统分析请求 | requested→processing→evidence_ready→human_reviewed→optionally_attached | 不取代任一状态机 |
| 公共 claim | 产品 owner + publish-safe 证据门 | 自动化不得自行签署 |

## 4. 波次与串行约束

| 波次 | 包 | 可并行 | 进入下一波条件 |
|---|---|---|---|
| Wave 0 | 43 | — | 本账建立 |
| Wave 1 | 44 | — | 人类批准四框架 + 权威索引落地 |
| Wave 2 | 45、51 | 45 ∥ 51 | 45/51 P0 |
| Wave 3 | 46、47、49 | 三者并行（各自依赖 45） | 46/47/49 P0 |
| Wave 4 | 48、50 | 48（依赖47）、50（依赖49） | 48/50 P0 |
| Wave 5 | 52、53 | 52（依赖48/50/51）、53（依赖52） | 52/53 P0 |
| Wave 6 | 54 | — | 全部 P0 + 人类 GO |

允许调研/原型并行开工；任何包不得在依赖 P0 前宣称上线就绪。

## 5. 变更纪律（来自 43 §5）

- 每包独立分支/提交或独立变更清单；
- 不合并旧分支整体，只挑选已验证必要变化；
- 不创建第二套 Ear/Music 状态机；
- 公共声明必须有成熟度标签；
- 数据迁移必须有备份、dry-run、幂等、回滚；
- P0 失败即阻止上线，不用 P1 文案掩盖。
