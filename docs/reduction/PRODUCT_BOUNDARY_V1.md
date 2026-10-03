# Moodify Product Boundary v1 — 2026-08-24

**任务：** Moodify Entropy Reduction 001 — Establish Mainline Product Boundary
**性质：** 主线产品边界声明（KEEP / FREEZE / ARCHIVE / DELETE CANDIDATES 四级分类）；不替代 `docs/canon/PRODUCT_BOUNDARY.md`；为 Phase 2-4 物理动作提供**唯一分类入口**。
**权威：** 引用 `AGENTS.md` → `docs/canon/*` → `docs/brand/public/*`；复用 `MOODIFY_PRODUCT_AUDIT.md §4 表`、`REDUCTION_PLAN.md Phase 1-3`、`docs/reduction/PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md §2 D-1`、`docs/reduction/MAINLINE_DECLARATION.md §2` 的判定。
**CANON_CHANGE：** `NO`。
**执行状态：** 仅分类。**未修改、删除、移动任何业务代码、目录或既有文档。**

---

## 0. 分类原则（机器可二元判断 + 人类 authority 不被压制）

按 `PUBLIC_BRAND_CONSTITUTION.md §13` 5 项测试 + `AGENTS.md §Judgment Authority`：

1. 直接承载 PLAY 闭环？ → `KEEP`
2. 属于 Tier A/B 公开语言且服务 PLAY？ → `KEEP`
3. 属于 Ear / Cloud Production 等内部系统但已验证？ → `KEEP`（作为内部能力）
4. 属于历史 / 临时 / 重复 / 空壳 / 与 Canon 冲突？ → `ARCHIVE` 或 `DELETE CANDIDATE`
5. 处于 1–4 之间？ → `FREEZE`
6. 任何听觉 / 美学判断 / Canon 变更 / 商业模式 → `HUMAN_DECISION_REQUIRED`

每一项的物理执行仍须 `MOODIFY_PRODUCT_AUDIT.md §7` 6 项安全阀：

```
1. git grep / CI / systemd / nginx / Docker / 30 天日志均无调用
2. owner 签字
3. 可替代路径有测试
4. 不改变 Canon / Job / data / evidence authority
   （若改变，则必须 CANON_CHANGE = YES + 人类授权 + changelog 留痕）
5. 必要历史 tag 或归档索引保存
6. 回滚为 revert commit 或 release artifact（不在主线保留第二实现）
```

---

## 1. KEEP（当前主线）

> 直接承载 PLAY 闭环；已被 Canon / 既有审计 / Delta 报告判定。

| 范畴 | 路径 / 能力 | Canon Evidence |
|---|---|---|
| **对外 Web Player** | `apps/web/`（含 `app/page.tsx`、`app/listen/`、`app/evidence/`、必要 `/library`） | `CURRENT_ARCHITECTURE.md §1` + Delta §1.2 + `MOODIFY_PRODUCT_AUDIT.md §4 表` |
| **对外 Android Player** | `apps/music-android/`（CI release workflow 唯一指向） | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `MOODIFY_PRODUCT_AUDIT.md §2.3` |
| **Music BFF（唯一公开 API）** | `moodify-music-package/.../bff` | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `CURRENT_ARCHITECTURE.md §1` |
| **Music data authority（结构）** | `moodify-music-package/models.py` + Alembic | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `REDUCTION_PLAN.md Phase 3 §3.3`（结构 KEEP；执行 schema 合并需 `CANON_CHANGE = YES`） |
| **Ear 内部核心** | `moodify-core-package/src/moodify/` —— `v01_pipeline` + `data_factory` | `INTERNAL_SYSTEMS.md §1-2` + `MOODIFY_PRODUCT_AUDIT.md §4 表` |
| **Listen Demo v0.1 落地链** | `apps/web/app/listen/` + `apps/web/app/evidence/` + `moodify-core-package/scripts/listen_demo_render.py` + `ops/web_origin/site/rongjingmusic/runbook_listen_demo_v0.1.{sh,README.md}` | Delta 报告 §1.1 + §1.2 KEEP |
| **三站公开表达** | `rongjingmusic.com`（Brand）+ `rongjingwenchuan.com`（Company）+ `rongjinwenchuan.xyz`（过渡 Player）+ `play.rongjingmusic.com`（UNVERIFIED） | `CURRENT_CANON.md §3 不变量 #7` + `PUBLIC_BRAND_CONSTITUTION.md §7` |
| **8-12 个治理入口（默认加载）** | 见 `AI_CONTEXT_OPTIMIZATION.md §2 表` | `AI_CONTEXT_OPTIMIZATION.md §2` |

**KEEP 不变量：**

- Web Player 路由继续收敛到 3-4 个：`/`、`/listen`、`/t/[id]`（compat 期内）、`/library`（抽屉内）。删除 `/studio`、`/drafts`、`/c/[handle]`、`/playlists`、`/console`、`/inbox`、`/evidence` 等 creator / creator 主页 / 创作控制台路由（兼容期内 410 / 退役，最终删除）。
- Music BFF 不为创作者 / license / support / CWC / passport / bridge 暴露新路由。
- Ear 内部核心保留为内部能力；不进入 `apps/web/app/` 公开导航。

---

## 2. FREEZE（冻结但保留）

> 现有能力**保留**，v1.0 不新增 / 不投入主线工程。恢复条件明确。

| 范畴 | 路径 / 能力 | 未来恢复条件 |
|---|---|---|
| **Moodify Ear / Auditory Intelligence** | `moodify-core-package/src/moodify/era_diagnostic` / `identity_guard` / `reconstruction_objective` | PLAY 闭环有真实用户证据；现为 INTERNAL |
| **Reconstruction Job** | `moodify-core-package/.../reconstruction_job` | 真实生产 case + billing 完成；state machine 统一方案（`CANON_CHANGELOG.md CD-015`） |
| **MAMSE-001..016** | `moodify_experimental` / scripts / `artifacts/mamse_*` | 研究资产；不进入默认安装 / CI / AI 上下文 |
| **Physics / LLM / lyric / transcription** | Core 子包 | 同上；隔离为 research profile |
| **Ear Workbench** | `apps/ear-workbench/` | 内部研究工具；**永远不**进入公开导航 |
| **Creator Studio / 发布** | `apps/web/app/studio` + BFF creator/track routes | 供给 + 用户行为证据齐备；当前 FREEZE |
| **创作者主页 / 关注** | `/c/[handle]` + follows | 同上 |
| **License Intent** | Web / BFF / DB | 商业模式决策后（`CANON_CHANGELOG.md CD-014`） |
| **Support / 支付意图** | Web / BFF / DB | 同上 |
| **Creation Passport** | Music DB / Web | 信任资产；非 MVP 首次播放所需 |
| **Evidence Bridge** | Music DB / API | 跨域状态扩展需真实生产流量 |
| **歌单** | Web + BFF + DB | 已实现保留；v1.0 不新增协作 / 分享 / 推荐逻辑 |
| **Music Data API（与 BFF 平行）** | `moodify-music-package/.../api` | BFF 唯一公开；此层 v1.0 不新增 surface |
| **Web Drizzle schema（与 SQLAlchemy 平行）** | `apps/web/lib/db/schema.ts` | data authority 合并需 `CANON_CHANGE = YES` |
| **历史审查 / 证据包** | `artifacts/` / `审查包/` / `windows版本开发/` | 按 Evidence Index 只保留不可替代证据 |
| **Demo Intelligence Report** | `demo/` + `engine/report_schema` | 内部演示；不得升级为第二产品面 |
| **Demo / 配置文件** | `examples/` / `deliverables/` / `data/` / `inspector_reports/` / `listening_test/` / `phys-lab/` / `pre-music/` / `RJWC_VideoPack_System/` / `research/`（部分子包） | 研究 / 历史资产；不进入默认 AI 上下文 |

**FREEZE 共同原则：**

- 保留在 Git 历史；不进入默认 AI / 工程上下文（`AI_CONTEXT_OPTIMIZATION.md §3`）。
- 不删、不重写、不升级为对外产品面。
- 任何恢复动作必须先 `CANON_CHANGE` 验证（恢复 creator / license / API 等都会触发产品身份相关 Canon 项）。

---

## 3. ARCHIVE（历史资产）

> 移出默认 AI / 工程检索；通过 `docs/ARCHIVE_INDEX.md` 定位（**该索引文件按 `REDUCTION_PLAN.md Phase 2` 尚未建立**）。

| 范畴 | 当前路径 | 处理方式 |
|---|---|---|
| 审查包 | `审查包/`（382 文件） | 入 `archive/audits/2026-08/`；每包保留 manifest / 最终报告 / 不可替代证据 |
| Windows 历史开发 | `windows版本开发/`（330 文件） | 入 `archive/windows-development/`；保留 release/tag 对应记录 |
| 生成 artifact | `artifacts/`（956 文件） | 不可替代证据保留；其余入 `archive/evidence/` + hash manifest |
| 07Music / asset-registry / benchmark / calibration_reports / cloud_data / configs / data / deliverables / inspector_reports / listening_test / local_audio_assets / moodify-app / moodify-bridge / moodify-system / moodify_runtime / night / output / outputs / project_analytics / science / scratch / shared-fixtures / temp / third_party / tmp / tools / treatment_records / uploads / video / workers / _github_moodify_ai / Moodify_Deep_Ear_Diagnostic_Pack_v0.1.1 / 中文根目录工作包（`实验图片` / `工程预算` / `项目ppt` / `研究材料` / `投资资料`） | 大量生成 / 历史 / 临时 / 重复资产；按 `AI_CONTEXT_OPTIMIZATION.md §3` 入 archive；建立 ARCHIVE_INDEX.md |

**ARCHIVE 共同原则：**

- **不是删除**。Evidence Index 必须记录：artifact id、case id、hash、生成版本、存储位置、可重建命令、保留策略（`AI_CONTEXT_OPTIMIZATION.md §3`）。
- 归档后 AI 默认检索工具排除；只通过 ARCHIVE_INDEX.md 定位。
- 历史包使用统一目录命名；移除嵌套副本与重复模板。

---

## 4. DELETE CANDIDATES（仅候选，未授权）

> **本节只列**已被以下来源判定的高置信 / 中置信候选：

- `MOODIFY_PRODUCT_AUDIT.md §4 表`（KEEP / MERGE / FREEZE / DELETE 列）
- `MOODIFY_PRODUCT_AUDIT.md §5.2` 死代码与空壳候选
- `REDUCTION_PLAN.md Phase 1-3`
- `docs/reduction/PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md §2 D-1`

**不授权 mass-delete**。每项执行必须满足 §0 安全阀 6 项。

### 4.1 Phase 1 高置信候选（按 Delta 报告）

| 路径 / 范畴 | 理由 | 当前 Phase |
|---|---|---|
| **`moodify-qa/`**（含 `api/`、`core/`、`tests/`、`Dockerfile`、`docker-compose.yml`、`qa_storage.db`） | 自描述"AI Audio Quality Assurance Infrastructure"；命中 `PUBLIC_BRAND_CONSTITUTION.md §2.2` 禁单；Delta D-1 整体否决 | DELETE 候选（Delta D-1） |
| **`moodify-qa-desktop/`**（未跟踪） | Electron 桌面壳，依赖 moodify-qa；`MOODIFY_PRODUCT_AUDIT.md §4 表` DELETE | DELETE 候选（Delta D-1） |
| **`docs/IMPLEMENTATION_PLAN_QA_V0.1_2026-08-24.md`** + **`docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md`** | 把 DELETE 候选目录包装为对外产品面；自陈"必须声明 CANON_CHANGE"但未声明、未留痕 | DELETE 候选（Delta D-1） |

**Delta §8 Phase 1 第一步（Documentation First，可由 Cursor 直接执行）：**

```
把 docs/IMPLEMENTATION_PLAN_QA_V0.1_2026-08-24.md
与 docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md
顶部加 STATUS 头:

> STATUS: REJECTED / NOT-AUTHORIZED — 2026-08-24 Canon Change 主张未获人类批准,
> 不进入 v1.0 实施。
```

**不删文件 / 不改内容 / 不需 owner 签字 / 可由 Cursor 直接执行。**

### 4.2 Phase 1 其他高置信候选（`MOODIFY_PRODUCT_AUDIT.md §4-5` + `REDUCTION_PLAN.md Phase 1`）

| 路径 / 范畴 | 理由 | 当前 Phase |
|---|---|---|
| `products/`（qa / master / rating / supply） | 主要为空目录、README、config；制造不存在的平台认知 | DELETE 候选 |
| `shared/` | 无实质实现；重复 Core 中已有 contracts / authority / node / safety / api | DELETE 候选 |
| `sdk/` | client 返回 placeholder；async 明确未实现；无公开 API authority | DELETE 候选 |
| `moodify/orchestration/workflow_engine.py` | LEGACY；需 30 天日志观测 | DELETE 候选 |
| `benchmark/baseline.py` + `research/benchmarks/baseline.py` | 完全相同；保留一份即可 | DELETE 候选（保留一份） |
| `scan_err.txt` | 0 字节空文件 | DELETE 候选 |
| Root 中文工作包 / 压缩快照 / 安装器 / 临时目录 | 不应属于源码根目录；未跟踪可不提交，已跟踪先核验发布依赖 | DELETE 候选（部分需 owner 签字） |

### 4.3 Phase 3 MERGE / DELETE 候选（结构 / data / API authority 合并）

| 路径 / 范畴 | 理由 | 当前 Phase | Canon Change |
|---|---|---|---|
| `moodify-pulse/` | 第二产品身份 / mock data / 与 Player 重复；先提取必要 Windows 播放代码 | DELETE 候选（Phase 3 §3.5） | NO |
| `apps/android/` | 与 `apps/music-android` 双 Android authority；迁移必要能力后退役 | MERGE 候选（Phase 3 §3.1） | NO |
| `engine/`（仅 facade） | 被 demo 使用并反向委托 Core；选择 Core 为唯一包 | MERGE 候选（Phase 3 §3.4） | NO |
| CWC 积分账本（Music DB/API） | 当前无用户闭环；提前引入类货币与账务复杂度 | DELETE 候选 | NO |
| Root API + worker Docker | 与真实部署、Core node worker、多 API facade 对齐后只留一个 compose | MERGE 候选 | NO |
| `apps/web/app/track/[id]` | 仅兼容跳转；迁移期结束后 | DELETE 候选（迁移期结束） | NO |
| Music data authority 合并（删除 Web Drizzle schema） | data authority 变更 | DELETE 候选 | **YES** |
| 单一 authoritative state machine 统一方案 | `CANON_CHANGELOG.md CD-015 HUMAN_DECISION_REQUIRED` | DELETE / MERGE 候选 | **YES** |
| QA 两个 FastAPI 入口 + calibration server 常驻模式 + legacy orchestration | 与 BFF 唯一公开 + Production 唯一内部冲突 | DELETE 候选（Phase 3 §3.4） | NO |
| MAMSE-001..016 + calibration / physics / LLM / lyric / transcription 默认 import | 默认安装 / CI / AI 上下文过重 | MERGE 候选（拆出 research profile） | NO |

---

## 5. KEEP / FREEZE / ARCHIVE / DELETE 边界判断的最终复核

按 `CURRENT_CANON.md §3 Canon 不变量`：

- 不变量 #1（一个对外产品身份）：KEEP 列表与 §4 Phase 1 高置信候选符合；
- 不变量 #2（PLAY 优先）：KEEP 全部服务 PLAY；
- 不变量 #3（内部可以复杂）：Cloud Engine / Ear / reconstruction / data factory 全部 INTERNAL；
- 不变量 #4（Canon 不虚构现实）：本分类基于 `MOODIFY_PRODUCT_AUDIT.md` + Delta 报告 + Canon 已确立事实，不虚构部署；
- 不变量 #5（历史文档不能反向覆盖当前 Canon）：本文件归类为治理入口，不进入 Canon；
- 不变量 #6（Canon 变更必须可见）：§4.3 已标 CANON_CHANGE = YES 的项必须走 changelog；
- 不变量 #7（一个站点一个角色）：KEEP 三站职责符合。

---

## 6. 本文件**不**做的事

- **不**修改 `docs/canon/*` / `docs/brand/public/*` / `AGENTS.md` / `MOODIFY_PRODUCT_AUDIT.md` / `REDUCTION_PLAN.md` / `AI_CONTEXT_OPTIMIZATION.md`。
- **不**移动任何文件。
- **不**授权 mass-delete。
- **不**对任何 DELETE / ARCHIVE 候选做物理动作（由 `EXECUTION_PLAN_V1.md` Phase 2-3 在 owner 授权下执行）。
- **不**声明 `CANON_CHANGE`。

---

**本文件结束。等待 Reduction Execution 001：物理隔离 archive/freeze。**