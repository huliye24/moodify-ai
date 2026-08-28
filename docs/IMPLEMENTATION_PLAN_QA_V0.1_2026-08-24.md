> **STATUS: REJECTED / NOT-AUTHORIZED**
>
> **DATE:** 2026-08-24
>
> **REASON:** The proposed QA product direction is not part of Moodify v1.0 mainline. No Canon Change approval exists. This document is retained as historical decision record only.
>
> **Canon Reference:**
> - `docs/canon/CURRENT_CANON.md §3 不变量 #1`: One external product identity. Ear / QA / Auditory Intelligence Infrastructure do not become a second public product surface.
> - `docs/canon/PRODUCT_BOUNDARY.md §Internal Systems`: Cloud Production is internal. Moodify Ear is internal.
> - `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md §2.2 禁单`: "AI 音乐后处理平台 / Auditory Intelligence Infrastructure / 音频 API 平台 / ACU 计算平台 / Creator Platform" 不再是 Moodify 的首要公共定义。
> - `docs/canon/CANON_CHANGELOG.md 2026-08-19 v1.1`: Public Brand Authority Freeze; 旧 "AI 美化 / 自动 mastering" 退出公共第一叙事。
> - `MOODIFY_PRODUCT_AUDIT.md §4`: `moodify-qa` 已标 DELETE（值 1, 1, 4）。
> - `docs/reduction/PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md §2 D-1`: 本会话 Delta 审计已否决 QA 产品化方向。
> - `docs/reduction/MAINLINE_DECLARATION.md §5.2`: 标 STATUS 头不需 owner 签字，Cursor 可直接执行。
>
> **本文件状态:** 不删除，不修改正文，不移动目录。仅作为历史决策记录保留。v1.0 不进入实施。

---

# Moodify Web v0.1 实施计划（受控执行模式）

**日期:** 2026-08-24
**模式:** 受控执行 — 第一阶段仅代码扫描与实施计划，**未写任何代码**
**目标:** 30 天内，陌生用户访问 Moodify Web → 上传歌曲 → 获得 AI Audio Intelligence Report → 保存 → 再次上传

---

## 一、实施前状态（代码扫描结论）

### 1. apps/web（产品壳，实际形态比预想更完整）

| 项 | 扫描结论 |
|---|---|
| 框架 | Next.js 16.2.6 + React 19 + vinext（可跑 Cloudflare Workers，也可 self-host 到 VPS node） |
| 数据库 | Cloudflare **D1**（SQLite）+ Drizzle ORM；`db/schema.ts` 11 张表齐全（users/creatorProfiles/tracks/trackVersions/licenseIntents/supportIntents/listenEvents…） |
| 用户系统 | **已存在**：`requireMusicUser()`（`lib/api.ts`）— ChatGPT Sign-in 头注入 → 自动建/取 users 记录；另有 `/beta-login` |
| 对象存储 | **已存在**：Worker 绑定 `env.MEDIA`（**R2 bucket**）；tracks 音频上传已在用 |
| 上传 API 模式 | **已存在**：`PUT /api/v1/tracks/[id]/audio` — mime 白名单 + 100MB 上限 + sha256 校验 + R2 put + D1 事务写入，失败回滚删对象。QA 上传可直接套用此模式 |
| 部署 | LA VPS：moodify-music :3100（vinext）+ bff :8100 + nginx + cloudflared 隧道 |

### 2. moodify-core-package（分析服务，比预想更接近可用）

| 项 | 扫描结论 |
|---|---|
| FastAPI 入口 | `src/moodify/api/main.py`，已在 LA VPS 以 `moodify-api :8000` 运行 |
| 同步分析 | `POST /api/v1/auditory/analyze` — 上传文件 → `analyze_to_case()` → 返回 case + **auditory_report JSON**（metrics + findings + evidence index） |
| 异步任务 | `POST /api/v1/auditory/jobs`（202 入队，SQLite JobQueue）+ `GET /api/v1/auditory/jobs/{id}`（状态查询）；LA 已有 moodify-worker 消费 |
| 任务状态 | `QUEUED / RUNNING / SUCCEEDED / FAILED`（与规划的 queued/running/completed/failed 一一对应，仅命名差异） |
| 指标字段 | `integrated_loudness_lufs`、`loudness_range_lu`、`true_peak_dbfs`、`crest_factor_db`、stereo 相关指标（`compute_stereo_metrics`）、频段能量；findings = 风险旗标（削波/动态压缩/真峰值超限等） |
| CLI | `cli.py`（analyze/v01_analyze/serve 等子命令），MVP 不需要动它 |
| 缺口 | ① 异步 job 成功后**没有暴露取报告的端点**（report 落在 case_dir 但 `GET jobs/{id}` 只给状态）；② 服务间鉴权需确认（杭州节点已有 service-key 模式可抄） |

### 3. 部署环境

- LA VPS 4C/8G：nginx（三域名）+ cloudflared + moodify-api(127.0.0.1:8000) + moodify-music(3100) + bff(8100) + moodify-worker
- 若 apps/web self-host 在 LA VPS，则 **web → moodify-api 可内网直连 127.0.0.1:8000**，无需公网暴露分析服务（最安全路径）

---

## 二、实施前状态汇总（按要求的格式）

```text
实施前状态：

可以直接复用：
  - apps/web 整壳：Next.js 16 + D1 + Drizzle + 认证 + R2 MEDIA 绑定
  - 上传 API 模式（tracks audio route：校验/落桶/事务/回滚）
  - moodify-api 全部分析能力（同步 analyze + 异步 jobs 队列 + 状态查询）
  - 指标体系（LUFS/LRA/True Peak/Crest/Stereo/频段）与 findings 风险旗标
  - LA VPS 部署拓扑（nginx + worker + 隧道）

需要新增：
  - apps/web：/qa 页面组（入口/上传/报告/历史）+ /api/v1/qa/* 路由（纯增量）
  - D1：analysis_jobs + analysis_reports 两张表（用户侧记录；Python 队列不感知用户）
  - moodify-api：GET /api/v1/auditory/jobs/{id}/report（新路由，读 case_dir 里已有的
    auditory_report.json，不改任何分析逻辑）
  - 服务间鉴权：环境变量 service key（抄杭州节点现有模式）
  - Report 页 UI 组件（Score/Loudness/Dynamics/Stereo/Frequency/Problems/Suggestions）

不能触碰：
  - CANONICAL 算法：auditory/、mrs/、v01_*、judgment 规则
  - engine/ 门面层（不迁移、不重构）
  - 现有 tracks/creators/playlists 链路与已上线页面
  - Canon 文档（不修改，不新增产品身份声明）
  - products/ 空壳目录（本阶段不填）
  - 不引入 Redis/Celery/第二个前端项目/第二套用户系统

第一步修改计划：
  Task 1 — 新增 /qa 入口页（app/qa/page.tsx）+ 导航入口；
  同时在 moodify-api 加 jobs report 读取路由（Task 3 的前置，改动最小的服务端新增）。
  两者均为纯增量文件，不修改任何现有文件的行为。
```

---

## 三、关键技术决策（需随计划一并确认）

| 决策点 | 建议 | 理由 |
|---|---|---|
| 同步 or 异步 | **异步**：复用 `POST /jobs` + `GET /jobs/{id}`，前端轮询 | 端点现成、状态机现成、LA worker 现成；同步路径在代理层有超时风险 |
| 音频存储 | 直接用 **R2（MEDIA 绑定）**，不做本地磁盘 fallback | R2 已在用，比"本地存储过渡"更省事；用户侧资产可持久 |
| web→api 通道 | apps/web self-host 于 LA VPS，**内网 127.0.0.1:8000** 直连 + service key | 不暴露公网面；杭州 service-key 模式可直接抄 |
| 报告持久化 | 完整 report JSON 存 R2；D1 存摘要（jobId/score/文件名/时间/objectKey） | 复用 trackVersions.audioObjectKey 模式 |
| 免费配额 | **不加新字段**：直接按月 count 用户的 analysis_jobs 记录（≥3 拒绝并提示 Upgrade） | 零 schema 变更，P1 接计费时再换成订阅状态 |
| 任务状态映射 | 前端统一映射 QUEUED/RUNNING/SUCCEEDED/FAILED → 排队/分析中/完成/失败 | 不改后端枚举 |

---

## 四、任务拆解（每个任务先回答四问，确认后逐个执行）

### Task 1 — QA 产品入口页 `/qa`

```
Task: 新增 app/qa/page.tsx：Moodify QA 介绍 + 上传入口 + 示例报告链接；首页导航加入口
商业价值: 第一个产品面入口，让陌生用户 30 秒理解"上传歌曲→获得专业报告"
技术位置: apps/web 展示层（products/qa 的 UI 面，代码先落在 apps/web，不填 products/ 空壳）
未来扩展: 页面组件独立于音乐社区路由，未来可拆独立域名而不动业务逻辑
风险: 低 — 纯新增文件，唯一修改是在现有导航组件加一个链接
```

### Task 2 — 上传系统 `/api/v1/qa/analyze`（POST）

```
Task: 新增上传路由：mime/大小校验（套 tracks 模式）→ R2 落桶 → 调 moodify-api
      POST /api/v1/auditory/jobs → 写 D1 analysis_jobs 记录 → 返回 jobId
商业价值: 闭环第一步；无上传则无产品
技术位置: apps/web API 层（新增路由文件）；复用 lib/api.ts 的 requireMusicUser/ApiError
未来扩展: 同一路由未来加配额检查、批量参数、master 任务类型（jobType 字段预留）
风险: 中低 — 跨服务调用是本 MVP 唯一新增的架构面；需 service key 环境变量与超时兜底
```

### Task 3 — 分析任务系统（状态链路）

```
Task: ① moodify-api 新增 GET /api/v1/auditory/jobs/{id}/report（读已有 case_dir 的
      auditory_report.json，仅新增路由）；② apps/web 新增 GET /api/v1/qa/jobs/{id}
      （代理状态 + SUCCEEDED 时取报告、算 Overall Score 摘要、写 analysis_reports）
商业价值: 用户必须看到进度与确定性结果，否则等待即流失
技术位置: ① core-package api/routes（新增文件注册路由，不碰 auditory/ 算法）② apps/web API 层
未来扩展: 状态轮询协议即未来 master/rating 任务的通用协议（jobType 字段）
风险: 低 — 两端均为新增读取路径；不修改既有状态机（不创建第二套 Job authority，
      以 moodify-api 队列为唯一权威，D1 记录只是用户侧镜像）
```

### Task 4 — Report 页面 `/qa/report/[id]`

```
Task: Audio Intelligence Report 页：Overall Score（MRS/评分摘要 + 等级）、Loudness（LUFS/
      LRA/True Peak vs 平台标准）、Dynamics（Crest/DR）、Stereo、Frequency 频段、
      Problems（findings 按严重度）、Suggestions（findings → 可执行建议文案）
商业价值: 报告即产品本体，价值感知 100% 在这一页
技术位置: apps/web 展示层 + 组件化（ScoreCard/LoudnessPanel/DynamicsPanel/StereoPanel/
      SpectrumPanel/ProblemList/SuggestionList）
未来扩展: 组件未来供 master/rating 报告复用；报告 JSON 带 schemaVersion
风险: 低 — 纯前端消费 Task 3 契约
```

### Task 5 — 历史记录 `/qa/works`

```
Task: My Reports 列表页：文件名/时间/Overall Score/报告链接 + 再次上传入口
商业价值: 资产沉淀 = 留存 = 离开成本；也是重复使用（配额消耗）的入口
技术位置: apps/web 展示层，查询 D1 analysis_jobs ∪ analysis_reports（本人 userId 过滤）
未来扩展: 预留版本对比（同曲多版本 delta）与导出按钮位
风险: 低 — 只读查询
```

### Task 6 — 免费额度（商业化预留）

```
Task: Task 2 路由内加配额检查：当月 analysis_jobs 计数 ≥ 3 → 429 + "Upgrade Creator Plan"
      引导文案；不接支付
商业价值: 无配额则无付费理由；先建立心智
技术位置: apps/web API 层（Task 2 内嵌逻辑，无新 schema）
未来扩展: P1 接支付后把"count ≥ 3"换成订阅状态查询，调用点不变
风险: 低
```

---

## 五、执行顺序与验收

```text
Task 1 → Task 3①(moodify-api report 路由) → Task 2 → Task 3② → Task 4 → Task 5 → Task 6
                （先打通服务端读链路，前端才有契约可消费）
```

**最终验收（不达标不进入下一阶段）：**

```text
陌生用户：打开网站 → /qa → 上传 mp3/wav/flac → 看到排队/分析中状态
→ 看到 Audio Intelligence Report（Score/Loudness/Dynamics/Stereo/Frequency/
Problems/Suggestions 七区块完整）→ My Reports 能回看 → 能再次上传
```

---

## 六、影响范围声明

- **修改的现有文件**：仅导航组件（加入口链接）+ D1 migration（新表）+ moodify-api main.py（注册一条新路由，约 3 行）。
- **其余全部为新增文件**（app/qa/*、app/api/v1/qa/*、api/routes 下新路由文件、drizzle migration）。
- **不触碰**：CANONICAL 算法、engine/、Canon 文档、现有 tracks 链路、products/ 空壳。
- **每步执行前**会先说明本步影响的文件清单，再动手。

**当前状态：计划完成，等待确认。未写任何代码。**
