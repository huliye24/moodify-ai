# Moodify Product Entropy Audit v1.0

**审计日期：** 2026-08-24  
**审计类型：** 只读产品减法审计  
**审计基线：** `codex/moodify-classic-reconstruction-001`，`caf6436f`  
**Canon：** v1.1（2026-08-19）  
**CANON_CHANGE：** `NO`——本报告遵循既有产品身份与边界，不改变任何权威。后续若改变 state machine、Job、data 或 cloud authority，执行者必须另行声明 Canon Change。  
**执行状态：** 仅建议；未修改、删除、移动任何业务代码或既有文档。

---

## 0. 结论

Moodify 的核心问题不是功能不够，而是**同一价值被多个产品身份、客户端、API、数据模型、实验包和文档包重复表达**。仓库已有可用的播放表面和强内部音频能力，但两者之间被大量“未来平台”结构稀释。

本审计建议把项目从“展示所有可能性”收敛为：

```text
Cloud-prepared Track -> Moodify Player -> PLAY
```

保留一个公开产品、一个 Web 播放表面、一个 Android 播放表面、一个 Music BFF、一个 Music 数据权威，以及一个内部受控生产入口。其余能力按证据归入 `MERGE / FREEZE / DELETE`，不再同时消耗主线注意力。

最值得立即停止的工作不是某个算法，而是：

1. 停止增加第二公开产品（QA、Pulse、Ear Workbench、Master、Rating、Supply）。
2. 停止扩展 creator marketplace、许可、赞助、积分和企业 API，直到 PLAY 闭环有真实用户证据。
3. 停止并行维护两个 Android、两个 Electron、多个 FastAPI facade 和两套 Music schema。
4. 停止把生成证据、审查包、补丁包和历史快照放在默认 AI/工程上下文中。

---

## 1. 审计范围、方法与限制

### 1.1 已扫描范围

- Git 工作树、远端、分支和 GitHub Actions；
- `apps/web`、`apps/android`、`apps/music-android`、`apps/ear-workbench`；
- `moodify-core-package`、`moodify-music-package`、`engine`、`products`、`shared`、`sdk`、`demo`；
- `moodify-pulse`、`moodify-qa`、未跟踪的 `moodify-qa-desktop`；
- 根 Docker、部署、ops、schema、脚本、测试；
- `docs`、`artifacts`、`审查包`、`windows版本开发`；
- Canon、Public Brand 与现有 runtime reality snapshot。

### 1.2 方法

- 以 Canon 与 runtime evidence 为最高判断依据；
- 追踪 manifest、入口点、路由、import、测试和 CI；
- 比较数据库表、字段、状态枚举和 API surface；
- 使用 Git object hash 查找完全重复文件；
- 把“无静态引用”视为候选证据，而不是自动认定可删除；
- 对私有云、数据库和线上服务不做写入或远程验证。

### 1.3 重要限制

- 本次未登录云主机、数据库或 GitHub 控制台；云端事实沿用 W01-P00 与 `CURRENT_ARCHITECTURE.md`，不能替代新的线上核验。
- 动态 import、CLI、人工运行脚本可能不出现静态引用，因此删除前仍需 30 天调用观测和 owner 签字。
- 工作树已有用户修改和未跟踪文件；本审计不把它们当作已合并、已部署或 Canonical 能力。
- “DELETE”表示**建议进入单独清理任务**，不是授权立即物理删除。

---

## 2. 仓库现实快照

### 2.1 总体规模

| 指标 | 观察值 | 含义 |
|---|---:|---|
| Git tracked files | 3,300 | 单仓库认知面过大 |
| Markdown | 约 772 | 文档数量接近代码文件数量 |
| Python | 686 | 主要集中于 Core、实验与历史执行包 |
| JSON | 527 | 大量为生成证据和运行产物 |
| `artifacts/` | 956 文件，其中约 510 MD | 生成证据占最大单一目录 |
| `moodify-core-package/` | 621 文件，其中约 507 代码 | 真实内部能力中心，同时也容纳大量实验 |
| `审查包/` | 382 文件，其中约 308 MD | 重复任务书、报告包和模板 |
| `windows版本开发/` | 330 文件，其中约 255 MD | 历史开发上下文与主线并存 |
| `docs/` | 275 文件，其中约 246 MD | 权威、现状、设计、计划和历史混放 |
| 活跃本地分支 | 30+ | 多条“主线/产品/迁移”叙事并存 |

### 2.2 当前可验证主链

公开面：

```text
Web / Android -> Music BFF / static media -> Player -> PLAY
```

内部面：

```text
Source -> Analyze -> Judge -> Controlled Intervention -> Verify -> Evidence
```

云端现实仍是静态音乐托管、API 壳与历史批处理；无对象存储、无云端 AI 推理、完整 Ear 链无生产流量。不能用仓库代码量推导生产成熟度。

### 2.3 CI 覆盖失衡

- Python CI 主要覆盖 `moodify-core-package`。
- Web deploy workflow 构建 `apps/web`。
- Android release 只构建 `apps/music-android`，不是 `apps/android`。
- Windows release 构建 `moodify-pulse`，但它仍以“AI Emotional Music Container”作为第二公开产品身份。
- `moodify-music-package`、`moodify-qa`、`moodify-qa-desktop`、`engine/products/shared/sdk` 没有同等级主线发布证明。

这说明“仓库存在”与“受支持产品面”之间已有明显断裂。

---

## 3. 产品价值地图

```yaml
Core Product: Moodify Music / Moodify Player（AI 音乐播放器）
Reason: 唯一对外产品身份与唯一核心用户动作均已被 Canon 冻结为 PLAY；所有内部听觉、生产、判断和验证能力只有在让用户更值得播放同一声音时才产生产品价值。
Evidence:
  - AGENTS.md: External product = Moodify Music / Moodify Player; Core user action = PLAY
  - docs/canon/CURRENT_CANON.md: 一个对外产品身份；PLAY 优先
  - docs/canon/PRODUCT_BOUNDARY.md: 用户不需要理解内部音频工程即可获得播放体验
  - docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md: Sound -> Moodify -> Play
  - docs/canon/CURRENT_ARCHITECTURE.md: 已运行公开主链是静态音乐托管与播放
```

四个候选中只选 **A. AI 音乐播放器**。B、C、D 是内部能力、生产方式或远期基础设施，不是当前公开产品。

### 3.1 核心价值判定式

一项能力进入 v1.0 主线，必须同时满足：

```text
可听见的用户增益
× 服务 PLAY
× 有运行或用户证据
× 不产生第二权威
× 7 天内可维护
```

任何一项为 0，默认 `FREEZE`；明确重复且无独立证据，默认 `MERGE` 或 `DELETE`。

---

## 4. 全功能价值评级

评分：用户价值、商业价值、复杂度均为 1（低）到 5（高）。商业价值只评价当前 12 个月可验证价值，不评价想象空间。

| 功能 | 代码位置 | 用户价值 | 商业价值 | 复杂度 | 建议 | 依据 |
|---|---|---:|---:|---:|---|---|
| Web 播放器与单曲播放 | `apps/web` | 5 | 5 | 3 | KEEP | 直接承载 PLAY；继续减页面而非扩平台 |
| Android 播放器 3.1 | `apps/music-android` | 5 | 4 | 3 | KEEP | Canon 与 release workflow 指向该工程 |
| 第二 Android 应用 | `apps/android` | 3 | 1 | 4 | MERGE | 功能更多但与 release authority 重复；保留可复用播放/缓存/本地化实现后退役工程 |
| Music BFF | `moodify-music-package/.../bff` | 5 | 4 | 3 | KEEP | 为 Web/Android 隐藏内部复杂度 |
| Music Data API | `moodify-music-package/.../api` | 3 | 3 | 4 | MERGE | MVP 不需要 BFF + 大型 internal API 双层全量 surface；保留清晰单一写 authority |
| Music SQLAlchemy schema | `moodify-music-package/models.py`, Alembic | 4 | 4 | 4 | KEEP | 已被文档定义为 Music data authority，执行前需再核验部署 |
| Web Drizzle schema | `apps/web/lib/db/schema.ts` | 4 | 3 | 4 | MERGE | 与 SQLAlchemy 重复 users/tracks/social/intents，且状态枚举漂移 |
| 基础曲库、搜索、播放事件 | Web + BFF + DB | 5 | 4 | 3 | KEEP | 支撑发现、播放与最小学习闭环 |
| 收藏/最近播放 | Web + Android + DB | 4 | 3 | 2 | KEEP | 直接提升重复 PLAY |
| 歌单 | Web + BFF + DB | 3 | 2 | 2 | FREEZE | 可保留已实现能力，但 v1.0 不新增协作/分享/推荐逻辑 |
| Creator Studio/发布 | `apps/web/app/studio`, BFF creator/track routes | 2 | 2 | 5 | FREEZE | 当前没有 creator 产品证据，分散 listener-first 主线 |
| 创作者主页/关注 | `/c/[handle]`, follows | 2 | 2 | 3 | FREEZE | 只有足够供给和用户行为后再恢复 |
| License Intent | Web/BFF/DB | 1 | 1 | 3 | FREEZE | 不是播放核心，且无成交证据 |
| Support/支付意图 | Web/BFF/DB | 1 | 1 | 4 | FREEZE | 无真实支付；避免把 intent 当收入 |
| CWC 积分账本 | Music DB/API | 1 | 1 | 4 | DELETE | 当前无用户闭环，提前引入类货币与账务复杂度 |
| Creation Passport | Music DB/Web | 2 | 2 | 4 | FREEZE | 潜在信任资产，但不是 MVP 首次播放所需 |
| Evidence Bridge | Music DB/API | 2 | 2 | 5 | FREEZE | 保留契约研究；不要在无生产流量时扩展跨域状态 |
| Ear 核心分析/判断/验证 | `moodify-core-package/src/moodify` | 4 | 5 | 5 | KEEP | 内部差异化来源，但只能通过受控生产入口服务 Play |
| `v01_pipeline` / data factory | Core | 4 | 4 | 4 | KEEP | Canonical 且有历史 10/10 pilot 证据 |
| Reconstruction Job | Core | 3 | 3 | 5 | FREEZE | 有实现但包含未实现 billing；在真实生产 case 前不扩状态 |
| Legacy workflow engine | `moodify/orchestration/workflow_engine.py` | 1 | 1 | 5 | DELETE | 已被 Canon 分类 LEGACY；删除需先证明无部署调用并保留迁移记录 |
| MAMSE-001..016 | `moodify_experimental`, scripts, artifacts | 1 | 2 | 5 | FREEZE | 研究资产，不进入默认安装、CI 或 AI 上下文 |
| Physics/LLM/lyric/transcription 等研究域 | Core 子包 | 1 | 2 | 5 | FREEZE | 当前未证明增强首次 PLAY；拆出 research profile |
| Engine facade | `engine` | 1 | 2 | 3 | MERGE | 主要被 demo 使用并反向委托 Core；选择一个包边界，避免永久 shim |
| Products 四模块 | `products/{qa,master,rating,supply}` | 0 | 1 | 3 | DELETE | 主要为空目录、README、config；制造不存在的平台认知 |
| Shared 新架构壳 | `shared` | 0 | 1 | 2 | DELETE | 无实质实现，重复 Core 中已有 contracts/authority/node/safety/api |
| Demo Intelligence Report | `demo`, `engine/report_schema` | 2 | 1 | 2 | FREEZE | 可作内部演示；不能升级为第二产品面 |
| Public SDK | `sdk` | 1 | 1 | 4 | DELETE | client 返回 placeholder，async 明确未实现；无公开 API authority |
| Ear Workbench | `apps/ear-workbench` | 0（外部）/4（内部） | 1 | 4 | FREEZE | 内部研究工具；不得进入公开导航与 MVP 发布 |
| Moodify Pulse Electron | `moodify-pulse` | 2 | 1 | 4 | DELETE | 第二产品身份、mock data、与 Player 重复；先提取必要 Windows 播放代码 |
| Moodify QA API | `moodify-qa` | 1 | 1 | 4 | DELETE | 与 Canon 冲突、复制 Core 分析、含两套 FastAPI 入口和独立 SQLite |
| Moodify QA Desktop | `moodify-qa-desktop`（未跟踪） | 1 | 1 | 4 | DELETE | 第三个桌面面，依赖 QA 第二产品；不应提交 |
| QA/Master/Rating/Supply 商业平台 | docs + products | 0 | 1 | 5 | DELETE | 当前价值来自推演而非用户或收入证据 |
| Root API + worker Docker | `Dockerfile`, `docker-compose.yml` | 2 | 2 | 4 | MERGE | 与真实部署、Core node worker 和多 API facade 对齐后只留一个 compose |
| Ops 静态站/部署脚本 | `ops` | 4 | 3 | 3 | MERGE | 保留实际运行 runbook；删除打包快照和重复站点源 |
| 历史审查/证据包 | `artifacts`, `审查包`, `windows版本开发` | 0（用户）/3（治理） | 1 | 5 | FREEZE | 移出默认主线上下文；按 Evidence Index 只保留索引与不可替代证据 |

---

## 5. 技术熵分析

### 5.1 重复系统

#### A. 两个 Android authority

- `apps/music-android` 是 CI release 的 Android 产品。
- `apps/android` 代码更多，包含搜索、个人资料、歌单、多语言、连接配置等另一套 UI 与播放实现。
- 两者各有 Gradle wrapper、MainActivity、资源和测试。

**建议：** 以 release workflow 和 Canon 指向的 `apps/music-android` 为目标工程；建立功能迁移清单，只移植离线缓存、MediaSession、错误处理和本地化中经过测试的部分。迁移完成后删除 `apps/android` 工程，不能长期双维护。

#### B. 两个 Electron 产品

- `moodify-pulse`：面向用户的“AI Emotional Music Container”。
- `moodify-qa-desktop`：面向 QA API 的分析工具。

它们都与唯一公开 Player 身份竞争。Windows release 当前甚至发布 `moodify-pulse`，造成 Canon 与 CI 不一致。

**建议：** v1.0 不发布 Electron。若真实用户要求 Windows 离线播放器，另行从 `moodify-pulse` 提取最小播放 shell，并命名为 Moodify Player；不得保留 Pulse 身份或 QA 桌面产品。

#### C. 多套 FastAPI

- Core API：`moodify-core-package/src/moodify/api/main.py`。
- Music Data API 与 BFF：`moodify-music-package`。
- QA：`moodify-qa/api.py` 和 `moodify-qa/api/main.py` 两个入口。
- Calibration server、reconstruction routes 等附加服务入口。

**建议：** 对外只暴露 Music BFF；内部只保留一个 Production API 入口。Calibration、QA、demo 等改为离线 CLI/实验 profile，不作为常驻服务。

#### D. 两套 Music 数据模型

`moodify-music-package/models.py` 与 `apps/web/lib/db/schema.ts` 同时定义用户、创作者、曲目、版本、关注、收藏、意图和事件，但存在实质漂移：

- `tracks.status`: `archived` vs `withdrawn`；
- `support_intents.status`: 非支付 intent vs `paid/refunded`；
- `play_events` vs `listen_events`；
- asset key、版本号、passport 字段不一致；
- 一侧含 CWC、audit、idempotency、bridge，另一侧含 publication events。

**建议：** 人类确认单一 Data Authority。基于当前 Canon 文档，优先保留 SQLAlchemy/Alembic；Web 只使用生成类型或 BFF contract，不再拥有平行 schema。该动作涉及 data authority，执行时 `CANON_CHANGE = YES` 或由现有 authority 文件明确证明无需变更。

#### E. 两套引擎结构

- 真正实现位于 `moodify-core-package`。
- `engine` 是部分 facade，通过 compatibility bootstrap 注入 Core 路径。
- `products` 和 `shared` 预先复制未来目录结构，但没有消费方或实现。

**建议：** v1.0 选择 Core 为唯一实现包。`demo` 如需稳定 contract，直接依赖 Core 的版本化 report schema。删除 `products/shared` 空壳，冻结 `engine` 迁移，避免一半迁移形成永久双层。

#### F. 重复文档与证据

- Canon、product-framework、public-form 10 个 package、W01-P00..P09 审查包、补丁包、Windows 开发包并行存在。
- 多处文档自称 `LIVE/CURRENT/APPROVED`，但低于 Canon 且有相互冲突。
- 同一审查包出现嵌套重复目录；Git hash 发现成组相同 JSON 和模板。

**建议：** 根目录只暴露 Canon、状态、运行、开发四类入口；其余历史包按日期归档并从默认检索排除。

### 5.2 死代码与空壳候选

高置信候选：

- `products/*`：23 个代码文件绝大多数是空 `__init__.py`，实质只有 README/config。
- `shared/*`：代码文件为空，只有 README。
- `workers/`：无跟踪文件。
- `sdk/python/client.py`：多处 placeholder 返回和未实现 async client。
- `moodify-qa`：独立复制指标、评分、存储、API；不被主线产品引用。
- `moodify-qa-desktop`：未跟踪，依赖上述旁路 API。
- `moodify-pulse`：使用 mock data 且产品描述与 Canon 冲突。
- `scan_err.txt`：0 字节。
- root 的打包快照、安装器和临时压缩包：不应属于源码根目录；其中未跟踪文件可直接不提交，已跟踪文件先核验发布依赖。

中置信候选（必须观测后删除）：

- `moodify/orchestration/workflow_engine.py` LEGACY；
- Core 的 `cli_v2`、`cli_daw`、calibration server、physics、LLM、transcription、lyric_align 等非主线子系统；
- 16 组 MAMSE runner/benchmark 与大规模生成输出；
- `benchmark/baseline.py` 与 `research/benchmarks/baseline.py` 完全相同；
- `apps/web/app/track/[id]` 仅兼容跳转，可在迁移期结束后删除。

### 5.3 过度设计

1. **平台先于产品：** QA/Master/Rating/Supply、SDK、企业 integration、SSO、API key、计费和 credit ledger 都早于真实播放留存。
2. **状态机过多：** node、data_factory、reconstruction_factory、reconstruction_job、legacy orchestration、Music publication、Evidence Bridge 都在描述跨阶段状态。
3. **数据库过多：** Web SQLite/D1、Music SQLAlchemy/PolarDB、node SQLite、QA SQLite、历史本地数据工厂并行。
4. **公共表面过多：** Product Home、Web Player、两个 Android、Pulse、QA Desktop、Ear Workbench、demo report。
5. **证据系统压过产品：** 证据生成文件数量超过公开产品代码，AI 和工程师首先看到的是治理历史而不是 PLAY 路径。
6. **企业架构无用户验证：** 多租户、复杂角色、审计、idempotency、CWC、license/support intent 形成完整平台成本，却没有生产流量或商业闭环。

---

## 6. Moodify v1.0 MVP

### 6.1 一句话

> Moodify 是一个会先准备声音、再让你直接播放的音乐播放器。

### 6.2 只保留 10 个不可替代能力

1. 打开即看到可播放曲目。
2. 单击 Play。
3. 稳定的播放、暂停、进度、上一首/下一首。
4. 后台播放与锁屏控制（Android）。
5. 最小搜索。
6. 收藏。
7. 最近播放。
8. 本地/弱网缓存。
9. 云端准备后的单一可播放版本交付。
10. 播放失败可恢复，并记录最小匿名播放证据。

明确不在 v1.0：上传分析报告、自动母带、创作者工作台、许可交易、赞助、积分、开放 API、企业 SSO、社交关注、公共 Evidence dashboard、多模型研究界面。

### 6.3 MVP Architecture

```yaml
Frontend:
  Web: apps/web，只保留 Home/Listen、Track、Library 三个用户路由和全局 Player
  Android: apps/music-android，复用必要的缓存、MediaSession 与本地化实现
Backend:
  Music BFF: 唯一公开 API；catalogue、track、playback URL、favorite、recent play
  Production API: 唯一内部入口；不暴露给普通用户
Cloud:
  一个静态/Web origin + 一个 BFF + 一个受控 worker
  MVP 不引入 Redis、微服务网关、企业 API 或第二队列
Database:
  一个 Music authority
  最小表: tracks, track_versions, favorites, play_events
  登录非必须；需要登录时再加入 users/sessions
AI Pipeline:
  离线/批处理 Source -> Analyze -> Human/Scoped Judge -> Render -> Verify -> READY
  只有 READY render 进入 catalogue；不把内部状态机暴露给客户端
User Flow:
  Open -> choose track -> Play -> continue listening
```

### 6.4 7 天工程边界

| 天 | 可交付内容 |
|---|---|
| Day 1 | 冻结路由、契约、数据表和 10 个 MVP 能力 |
| Day 2 | Web catalogue + Track + Player 收敛 |
| Day 3 | BFF catalogue/playback/favorite/recent-play 收敛 |
| Day 4 | Android 对齐同一 contract，补 MediaSession/缓存 |
| Day 5 | 准备 3–10 首 READY 曲目与失败回退 |
| Day 6 | Web/Android E2E、弱网、range、过期 URL 验证 |
| Day 7 | 发布候选、可听验收、回滚演练 |

前提：不重建内部 AI，不迁移全部数据库，不开发新商业面。如果这些前提不成立，7 天目标自动失效。

### 6.5 三类受众的理解测试

- 用户 30 秒：能看到曲目并听到声音，不需要理解 Ear。
- 工程师 7 天：只接触一个 Web、一个 Android、一个 BFF、一份 contract。
- 投资人 3 分钟：差异不是“功能多”，而是 Moodify 用内部声音理解与准备提高每次 Play 的可听价值；商业验证看播放完成率、回访和愿意再次用 Moodify 听的比例。

---

## 7. 决策门槛与删除安全阀

每个 DELETE 在执行前必须满足：

1. `git grep`、CI、部署单元、systemd/nginx/Docker 和 30 天日志均无调用；
2. owner 明确；
3. 可替代路径有测试；
4. 不改变 Canon/Job/data/evidence authority，或已完成 Canon Change；
5. 必要历史被 tag 或归档索引保存；
6. 回滚为 revert commit 或 release artifact，而不是在主线保留第二实现。

遇到不确定听觉判断必须输出 `HUMAN_REQUIRED` 或 `INCONCLUSIVE`，不能为了自动化而移除人类 authority。

---

## 8. 审计最终判断

Moodify 最稀缺的不是另一套架构，而是**一条真实、简单、可反复验证的 Play 链**。

建议的组织原则是：

```text
Public product count      = 1
Primary user action       = 1
Public API boundary       = 1
Music data authority      = 1
Production job authority  = 1
Default documentation path= 1
```

只有当一项新能力能通过真实听觉或播放行为证明增益时，它才应从内部研究区回到主线。
