# Moodify Cloud Execution Checklist v0.1 — Internal

**状态:** INTERNAL（不构成对外产品面）
**日期:** 2026-08-24
**作者:** Reduction Execution 001
**CANON_CHANGE:** NO
**执行状态:** 只列现状 + 内部目标；未实施任何云端修改 / 数据库迁移 / API 重设计

---

## 0. 与 Codex 原始命令的差异说明

Codex 原始命令的 `Current Resources` 列出 `Alibaba ECS / OSS / PolarDB / API Gateway / Cloudflare`。这与 `CURRENT_ARCHITECTURE.md §1` (P00 扫描 2026-08-17) 不一致:

- 没有 "Alibaba ECS" — 杭州是 `120.55.191.146 (阿里云, 2C/1.6G/40G)` VPS,不是 ECS 产品族
- 没有 "OSS" — `CURRENT_ARCHITECTURE.md §1` 显式记录 `OSS/S3/R2: NOT_PROVISIONED`
- 没有 "API Gateway" — `CURRENT_ARCHITECTURE.md §1` 只记录 cloudflared 隧道,无 API Gateway
- PolarDB 存在但 `直接核验 BLOCKED`
- Cloudflare 仅以 cloudflared 隧道出现,不是 API Gateway

→ 本 checklist **以 `CURRENT_ARCHITECTURE.md §1` 为准**。

---

## 1. Current Resources（P00 扫描 2026-08-17, 引用 CURRENT_ARCHITECTURE.md §1）

> **规则 R6/R10:** 本节只记录已由运行时证据支持的现状。任何"未验证不写成已运行"。

### 1.1 已运行

| 资源 | 详情 | 证据 |
|---|---|---|
| LA 核心 VPS（亿速云） | 103.144.246.242, 4C/8G/98G | `CURRENT_ARCHITECTURE.md §1` |
| └ nginx :80（三域名） | rongjingmusic.com / rongjingwenchuan.com / .xyz | 同上 |
| └ cloudflared 隧道 | rongjingmusic.com 等 | 同上 |
| └ moodify-api :8000 | Ear FastAPI, 127.0.0.1 | 同上 |
| └ moodify-music :3100 | node vinext 平台 | 同上 |
| └ moodify-music-bff :8100 | Music BFF | 同上 |
| └ moodify-worker | SQLite 队列, 近空 | 同上 |
| └ moodify-audiolla docker | :18080→8000, lalal.ai 代理（`CONNECTED_UNTESTED`） | 同上 + `INTERNAL_SYSTEMS.md §4` |
| 杭州数据 VPS（阿里云） | 120.55.191.146, 2C/1.6G/40G | `CURRENT_ARCHITECTURE.md §1` |
| └ moodify-api :8000 | 公网, service-key 鉴权 | 同上 |
| └ moodify-data-worker | moodify-node + 4 timers | 同上 |
| └ /var/lib/moodify | SQLite + 历史批处理 6.5GB（10 曲 pilot SUCCEEDED） | 同上 |
| audio asset 部署路径（Listen Demo v0.1） | /opt/moodify/music-media/audio/cadeau10-album1[-moodify]/ | `runbook_listen_demo_v0.1.sh:30-35` |
| 公开 audio URL | https://play.rongjingmusic.com/audio/...（UNVERIFIED 域名） | `CURRENT_CANON.md §3 不变量 #7` |
| State machine authority | 4 个（`workflow_engine LEGACY` / `node CANONICAL` / `data_factory CANONICAL` / `reconstruction_factory EXPERIMENTAL`） | `INTERNAL_SYSTEMS.md §3` |
| Music data authority 候选 | `moodify-music-package/models.py` + Alembic（已被文档定义,部署需再核验）| `MOODIFY_PRODUCT_AUDIT.md §4 表` + `§5.1 D` |

### 1.2 NOT_PROVISIONED / BLOCKED / 在线未用

| 资源 | 状态 | 证据 |
|---|---|---|
| PolarDB MySQL 8.0.13 (172.27.118.106) | BLOCKED 核验 + 空壳 | `CURRENT_ARCHITECTURE.md §1` |
| PolarDB MySQL 8.0.18 (172.27.118.104) | BLOCKED 核验 + moodify_dev 19 表 ≈0 数据 | 同上 |
| PolarDB PG 16.14 (101.133.107.206) | BLOCKED 核验 + 在线未用 | 同上 |
| OSS / S3 / R2 | NOT_PROVISIONED | 同上 |
| 云端 AI 推理 | 无（无 GPU, 无模型 serving） | 同上 |
| API Gateway | 无（cloudflared 隧道承担 TLS, 不是 API Gateway） | 同上 |

### 1.3 外部能力（INTERNAL_SYSTEMS.md §4）

| 能力 | 状态 |
|---|---|
| LALAL.AI / Audiolla | CONNECTED_UNTESTED（已部署, 无自动 pipeline） |
| FFmpeg | DEPLOYED_NOT_VERIFIED（双节点部署） |
| Demucs | PLANNED_ONLY（权重未下载） |
| Basic Pitch | IMPLEMENTED_NOT_MERGED（工具代码） |

---

## 2. Target v0.1 — Internal（Canon 内部已规划目标）

> 本节是 `MOODIFY_PRODUCT_AUDIT.md §6.3 + REDUCTION_PLAN.md Phase 3 + INTERNAL_SYSTEMS.md §2` 已规划的目标。**未实施**,任何实施必须先做 §5 触发条件。

| 项 | Canon 内部已规划 | 现状 | 阻塞 |
|---|---|---|---|
| [ ] Audio storage | OSS / S3 / R2 选型 `HUMAN_DECISION_REQUIRED` | NOT_PROVISIONED | 选型未决 |
| [ ] Processing queue（v1.0 复用 `node`） | `node` 已 CANONICAL（云端队列实跑） | 已运行（LA + 杭州） | — |
| [ ] Worker execution（v1.0 复用 `data_factory`） | `data_factory` 已 CANONICAL（pilot 10/10） | 已运行（杭州） | — |
| [ ] Metadata persistence（v1.0 最小 4 表） | tracks / track_versions / play_events / favorites（`MOODIFY_PRODUCT_AUDIT.md §6.3`） | SQLAlchemy models + Alembic 已有, 部署需核验；PolarDB schema 空转 | data authority 单一化需 `CANON_CHANGE = YES`（CD-015） |
| [ ] READY asset generation | Listen Demo v0.1 已运行（5 wav + manifest sidecar, human gate Step 5） | 已运行（LA 部署路径） | 公开 URL UNVERIFIED 域名 |
| [ ] Web playback | `apps/web/` + Music BFF 已运行 | 已运行（rongjinwenchuan.xyz 过渡 + play.rongjingmusic.com UNVERIFIED） | — |

### 2.1 内部 Pipeline（与 `INTERNAL_SYSTEMS.md §2` 一致）

```text
Intake → Identify → Analyze → Stem → Judge → Intervene
      → Preset Decision → Render → Verify → Evidence → Delivery
```

**v1.0 简化映射**（来自 `MOODIFY_PRODUCT_AUDIT.md §6.3`）:

```text
离线 / 批处理 Source → Analyze → Human/Scoped Judge → Render → Verify → READY
（READY 进入 catalogue；不暴露内部状态给客户端）
```

**当前实现程度:**

- Analyze / Judge / Intervene / Verify / Render: 仓库代码完整（`moodify-core-package/src/moodify/v01_pipeline`）
- 云端生产流量: 无（`CURRENT_ARCHITECTURE.md §1` "完整 Ear 链路仅仓库代码"）
- READY delivery: 通过离线 Listen Demo v0.1 runbook（不是云端 streaming production）

---

## 3. Not Included — Canon 已冻结（不再进入 v1.0）

按 `PUBLIC_BRAND_CONSTITUTION.md §5 + §9 Tier D + CANON_CHANGELOG.md 2026-08-19 v1.1`:

- [ ] **QA Platform** — `MOODIFY_PRODUCT_AUDIT.md §4` `moodify-qa` DELETE 候选；`Delta 报告 §2 D-1` 已否决 QA 产品化方向
- [ ] **AI Platform / Audio API Platform** — `PUBLIC_BRAND_CONSTITUTION.md §2.2` 禁单；§5 已冻结
- [ ] **Enterprise Infrastructure / Auditory Intelligence Infrastructure** — `§2.2` 禁单；§9 Tier D
- [ ] **ACU 计算平台** — `§2.2` 禁单
- [ ] **Creator Platform** — `§2.2` 禁单 + §9 Tier D；`MOODIFY_PRODUCT_AUDIT.md §4` FREEZE（Creator Studio / 创作者主页 / Creation Passport）
- [ ] **Marketplace** — `§5` 已冻结；`MOODIFY_PRODUCT_AUDIT.md §4` FREEZE
- [ ] **Social features** — `MOODIFY_PRODUCT_AUDIT.md §6.2` "明确不在 v1.0"

---

## 4. Not Included — Human Decision Required（暂不冻结,等人类决策）

按 `CANON_CHANGELOG.md` CD-011 + CD-014 + CD-015 + `CURRENT_CANON.md §6 暂不冻结`:

- [ ] **最终收费方式** — `CANON_CHANGELOG.md 2026-08-17 HUMAN_DECISION_REQUIRED`
- [ ] **是否免费听歌** — 同上
- [ ] **皮肤经济的最终形态** — 同上
- [ ] **硬件发布时间** — 同上
- [ ] **Creator 功能是否恢复** — 同上（`PUBLIC_BRAND_CONSTITUTION.md §5` "暂不冻结"）
- [ ] **API 是否未来重新开放** — 同上（§5 "暂不冻结"）
- [ ] **面向 B 端的具体商业模式** — 同上
- [ ] **Storage 选型（OSS vs S3 vs R2）** — CD-011 后续；本 entry 不决策
- [ ] **Music data authority 单一化（删除 Web Drizzle schema）** — `CANON_CHANGE = YES` + CD-015
- [ ] **单一 authoritative state machine 统一方案** — CD-015
- [ ] **`.xyz` 迁移后的 301/302/保留策略** — `CURRENT_CANON.md §3 不变量 #7` 后续
- [ ] **Classic Reconstruction Constitution v1.0 正文是否更新文本** — CD-014
- [ ] **GitHub main 合并策略（未合并分支 154 commits 的去向）** — CD 后续

---

## 5. 触发条件（任何 Cloud Production 实施必须先满足）

按 `MOODIFY_PRODUCT_AUDIT.md §7 DELETE 安全阀 6 项` + `CURRENT_ARCHITECTURE.md R6/R10`：

1. **P00 重新核验当前 LA / 杭州部署** — 不引用 2026-08-17 快照；登录云主机核验当前 listening / queue / worker 状态
2. **PolarDB 核验** — 当前 BLOCKED；必须先解除 BLOCKED 才能谈 schema
3. **OSS / R2 / S3 选型决策** — 人类 owner 决策 + `CANON_CHANGE = YES`（CD-011 后续）
4. **Music data authority 单一化决策** — `CANON_CHANGE = YES` + CD-015
5. **Worker / 队列 authority 决策** — CD-015
6. **owner 签字 + 30 天观测** — `MOODIFY_PRODUCT_AUDIT.md §7 #1 #2`
7. **可替代路径测试** — `MOODIFY_PRODUCT_AUDIT.md §7 #3`
8. **历史保存** — `MOODIFY_PRODUCT_AUDIT.md §7 #5`
9. **回滚准备** — `MOODIFY_PRODUCT_AUDIT.md §7 #6`（revert commit 或 release artifact）

未满足上述任一条件时,**不实施任何 Cloud Production 代码 / 数据库 / API 修改**。

---

## 6. 不做的事（再次声明）

- 不创建第二权威（state machine / data / cloud control / evidence / 对外身份）
- 不实施 mass-delete / archive move
- 不实施 database migration / API redesign
- 不扩大功能范围（Creator / Marketplace / API / Billing / Social 暂不实施）
- 不修改 Canon（`docs/canon/*` / `docs/brand/public/*` / `AGENTS.md`）
- 不引入 QA Platform / AI Platform / Enterprise Infrastructure 命名（`PUBLIC_BRAND_CONSTITUTION.md §2.2` 禁单）
- 不把 Cloud Production 包装为对外产品面（`INTERNAL_SYSTEMS.md §2` 已是内部角色级）

---

**检查清单结束。等待 Cloud Production Implementation 001 触发条件满足。**