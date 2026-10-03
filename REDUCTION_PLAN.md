# Moodify Reduction Plan

**日期：** 2026-08-24  
**依据：** `MOODIFY_PRODUCT_AUDIT.md` 与 `AI_CONTEXT_OPTIMIZATION.md`  
**执行状态：** 待人类批准；本次未执行任何修改。  
**原则：** 先停止新增熵，再删除高置信空壳；先证明单一 authority，再迁移重复实现。

---

## 0. 执行前置条件

1. 冻结 14 天新增产品面、schema、API 和 state machine。
2. 给所有线上 service、CI workflow、定时任务和人工脚本建立调用清单。
3. 对候选删除路径进行 30 天日志观测；无观测条件时必须由 owner 签字。
4. 创建清理前 tag 和 manifest；每个 phase 独立 commit，可整体 revert。
5. 本计划不授权 mass-delete，不授权修改云端，不授权改变数据/Job/evidence authority。
6. 若执行内容改变上述 authority：`CANON_CHANGE = YES`，更新 changelog、迁移和回滚。

---

## Phase 1：立即删除（高置信、低耦合）

目标：删除明确空壳、占位产品和可重建噪声；不碰真实运行主链。

| 修改文件 | 删除文件/目录 | 风险 | 收益 | 验证 |
|---|---|---|---|---|
| `.gitignore`：补充临时包、数据库、构建产物规则 | `scan_err.txt` | 极低 | 清除无意义文件 | Git clean 检查 |
| `docs/ARCHIVE_INDEX.md`：记录替代位置 | `products/` | 低；可能有计划文档引用 | 删除四个不存在的公开产品空壳 | `rg products\.` 无运行引用；CI 通过 |
| 同上 | `shared/` | 低；当前仅空包与 README | 删除第二套未来架构壳 | `rg from shared/import shared` 无运行引用 |
| 更新或删除 SDK 引用 | `sdk/` | 中；外部人工用户不可由代码证明 | 删除 placeholder 客户端和虚假 API 预期 | 30 天下载/调用核验 + owner 签字 |
| `docs/ARCHIVE_INDEX.md` | 完全重复模板、嵌套副本、可重建 JSON | 中；可能破坏 Evidence path | 显著降低文件数和 token | hash manifest + link checker |
| Canon guard 增加禁用第二公开身份检查 | 未跟踪 `moodify-qa-desktop/` | 低；尚未进入 Git | 阻止第三个桌面产品进入主线 | `git status` 不再出现该目录 |
| 把冲突计划标记为 rejected/historical | QA 产品化计划的当前态标签 | 低 | 防止下一位 agent 把 QA 当批准方向 | Canon guard / 文档状态检查 |

Phase 1 不立即删 `moodify-qa`、`moodify-pulse`、第二 Android 或 legacy workflow；它们需要依赖/部署核验和代码提取。

**Phase 1 风险：** 外部未记录消费者、文档链接断裂。  
**Phase 1 收益：** 删除最明显的“未来平台”信号，减少新 agent 误建第二产品的概率。

---

## Phase 2：结构调整

目标：把 Canonical、Experimental、Legacy、Historical 物理隔离，建立单一文档入口。

| 修改文件 | 删除/移动文件 | 风险 | 收益 | 验证 |
|---|---|---|---|---|
| `README.md`, `AGENTS.md`, `docs/REPOSITORY_STATUS.md` | 无 | 中；入口文案影响所有 agent | 5 文件内定位主线 | Canon tests + 人工阅读测试 |
| 新建 `docs/RUNBOOK.md`, `docs/ARCHIVE_INDEX.md` | 合并重复 runbook/status 文档 | 中 | 运行与历史各一个入口 | 命令 dry-run、链接检查 |
| Evidence Index 与 artifact retention policy | `artifacts/*` 大部分移到外部 artifact store/archive | 高；可能影响可复现性 | 最大幅度降低仓库文件数 | hash、case id、再生成测试 |
| Archive redirect map | `审查包/`, `windows版本开发/`, `补丁包/` 移到 `archive/` | 中 | 默认上下文不再加载历史工作包 | 全仓链接检查 |
| Core packaging 配置 | `moodify_experimental`、physics、calibration 等移入 `research/` 或 optional profile | 高；动态 import 风险 | 默认安装和 CI 只包含主线能力 | import scan + full tests |
| `.github/workflows/*` | 删除重复 Python workflow 或合并为一份 | 中 | 一个受支持测试定义 | branch protection 核验 |

**Phase 2 风险：** 路径变化、GitHub 链接和脚本失效，Evidence 可复现性下降。  
**Phase 2 收益：** 默认工作集从全仓 3,300 文件缩到 500–800；历史仍可检索但不再冒充当前 authority。

---

## Phase 3：产品重构

目标：收敛为一个 Player 产品面、一个公开 API、一个 Music data authority。

### 3.1 Android 合并

**修改文件：**

- `apps/music-android/**`：接收经过验证的缓存、MediaSession、错误处理、本地化能力；
- `.github/workflows/release.yml`：继续只构建合并后的工程；
- `docs/contracts/music/shared-client-contract.md`：只保留一个客户端 contract。

**删除文件：** `apps/android/**`（迁移完成后）。

**风险：** applicationId、签名、升级路径、资源、本地化、后台播放回归。  
**收益：** Android 维护面减半；发布 authority 与代码 authority 一致。  
**验证：** 单元/UI 测试、旧 APK 升级测试、后台/锁屏/耳机/弱网真机测试。

### 3.2 Web 表面减法

**修改文件：**

- `apps/web/app/page.tsx` 或 `/listen`：唯一发现入口；
- `/t/[id]`、`/library`、全局 Player；
- BFF catalogue/playback/favorite/recent-play contract。

**冻结/删除：**

- 冻结 `/studio`, `/drafts`, `/c/[handle]`, `/playlists`, `/console`, `/inbox`, `/evidence`；
- 迁移期结束后删除 `/track/[id]` compat route；
- 删除对外 creator、license、support、Evidence 主导航。

**风险：** 已有创作者或内部团队依赖页面。  
**收益：** 首次用户 30 秒理解；公共路由从 14 个收敛到 3–4 个。  
**验证：** route inventory、Play E2E、10 秒理解测试、404/redirect map。

### 3.3 数据 authority 合并

**修改文件：**

- `moodify-music-package/src/moodify_music/models.py`；
- Alembic migration；
- BFF contract 与生成客户端类型；
- `apps/web/lib/db/schema.ts` 改为生成/只读映射，最终删除平行 schema。

**删除/冻结表：**

- v1.0 只激活 `tracks`, `track_versions`, `favorites`, `play_events`；
- users/sessions 按登录需求激活；
- 冻结 creator profile、follows、albums、license/support intents、passport、bridge、audit；
- 删除 CWC account/ledger（确认无生产数据后）。

**风险：** 这是 data authority 变更，高风险；可能有未核验 PolarDB schema。  
**收益：** 消除两套 schema 和状态漂移。  
**验证：** 数据备份、迁移 dry-run、双读对账、回滚演练、运行时 DB 核验。  
**Canon：** 执行前必须明确 `CANON_CHANGE` 判定；若删除/替换 data authority，则为 `YES`。

### 3.4 API 与 Job authority 合并

**保留：** Music BFF（公开）+ 单一 Production API/worker（内部）。

**冻结/删除：**

- `moodify-qa`；
- QA 两个 FastAPI 入口；
- calibration server 常驻模式；
- legacy orchestration；
- reconstruction_factory/job 的重复部分；
- root compose 中未运行的 future Redis/nginx 设计。

**风险：** 云端 systemd/nginx/cron 可能直接引用旧入口。  
**收益：** 公开 API = 1，内部生产入口 = 1，Job authority = 1。  
**验证：** 线上 service inventory、30 天调用日志、failure injection、queue recovery。  
**Canon：** Job/state machine authority 合并属于 `CANON_CHANGE = YES`。

### 3.5 Desktop 决策

默认：v1.0 不发布 Desktop。

**修改文件：** `.github/workflows/release.yml` 移除 Windows Pulse job。  
**删除文件：** `moodify-pulse/**`（必要播放代码提取后）、`moodify-qa-desktop/**`。  
**风险：** 现有 Windows 下载用户失去更新；必须先查 GitHub Releases 下载量和签名/升级路径。  
**收益：** 消除 Pulse/QA 第二产品身份和两套 Electron 维护。  
**回滚：** 保留最后签名 release artifact 和 tag，不在主线保留源码副本。

---

## Phase 4：重新开发 Moodify v1.0

目标：在减法后的单一架构上完成真正可用的 PLAY 闭环，不恢复被删平台功能。

| 工作 | 修改文件 | 删除文件 | 风险 | 收益 |
|---|---|---|---|---|
| 最小 catalogue | Web、BFF、Music models | mock catalogue、重复 fixtures | 内容不足 | 打开即听 |
| 统一 playback contract | BFF、Web Player、Android player | 旧 URL/媒体 contract | range/过期/权限回归 | 两端行为一致 |
| READY-only delivery | Production adapter、BFF | 客户端可见内部状态 | 错误阻止播放 | 内部复杂、外部简单 |
| 弱网与恢复 | Web/Android cache、retry | 重复缓存实现 | 存储占用 | 真实播放可靠性 |
| 最小行为证据 | play events | 广泛 analytics schema | 隐私与误计数 | 可验证商业信号 |
| 3–10 首 Golden catalogue | Production pipeline、manifest | demo/占位内容 | 权利与质量 | 可听的产品证明 |
| 发布与回滚 | CI、runbook、release manifest | 手工打包流程 | 发布中断 | 可重复产业化交付 |

### 4.1 v1.0 验收

- 新用户 30 秒内首次播放成功率 ≥ 95%；
- Web 与 Android 共用同一 catalogue/playback contract；
- 无第二公开产品名、QA/Master/Rating/Supply/Pulse 主入口；
- READY 之外的内部状态不泄漏给客户端；
- 断网、过期 URL、媒体缺失有明确恢复或失败状态；
- 至少 3 首合法、可验证、经过人类听评的曲目；
- release 可一键回滚；
- investor demo 只需 3 分钟：打开、Play、对比为何值得再听。

---

## 5. 建议执行顺序与停止条件

```text
Freeze new entropy
  -> Delete empty shells
  -> Archive historical context
  -> Choose one Android
  -> Choose one Music schema
  -> Choose one Job authority
  -> Reduce Web routes
  -> Ship 3–10 track PLAY MVP
```

任何阶段出现以下情况立即停止：

- 无法确认线上调用；
- 数据迁移无法回滚；
- Evidence Index 无法证明不可替代证据位置；
- 人类听觉判断被自动化替代；
- 需要新增第二 state machine、数据库 authority 或公开产品；
- MVP 指标被功能数量取代。

---

## 6. 预期结果

| 维度 | 当前 | 目标 |
|---|---|---|
| 公开产品身份 | Music + Pulse + QA + Ear/demo 暗示 | Moodify Music / Player |
| 公开核心动作 | Play、上传、分析、发布、许可、赞助等 | Play |
| Android 工程 | 2 | 1 |
| Desktop 工程 | 2 | 0（有真实需求再建 1） |
| Music schema | 2+ | 1 |
| 默认常驻 API | 多个 facade | BFF 1 + 内部 Production 1 |
| 产品模块 | QA/Master/Rating/Supply 空壳 | 0 空壳 |
| 默认 AI 工作集 | 3,300 tracked files | 500–800 主线文件 |
| 核心功能 | 100+ 表述 | 10 个不可替代能力 |

最终判断标准不是“删了多少”，而是用户能否更快、更稳定地完成一次值得重复的 Play。
