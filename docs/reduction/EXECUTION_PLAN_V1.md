# Moodify Execution Plan v1 — 2026-08-24

**任务：** Moodify Entropy Reduction 001 — Establish Mainline Product Boundary
**性质：** Phase 1-4 执行计划（冻结 → 归档 → 删除 → Web + Cloud 开发）；为下一轮（Reduction Execution 001）提供**逐阶段**修改内容 / 风险 / 验证方式。
**权威：** 引用 `REDUCTION_PLAN.md Phase 0-4` + `MOODIFY_PRODUCT_AUDIT.md §7 DELETE 安全阀` + `ENTROPY_MAP_V1.md §1-3` + `PRODUCT_BOUNDARY_V1.md §0` + Delta §8 + `MAINLINE_DECLARATION.md §5-6`。
**CANON_CHANGE：** `NO`（各阶段在执行触及 Canon 5 项时**单独**声明 `CANON_CHANGE = YES`）。
**执行状态：** 仅计划。**未修改、删除、移动任何业务代码、目录或既有文档。**

---

## 0. 全局前置条件（任何阶段都必须满足）

按 `REDUCTION_PLAN.md §0` + `MOODIFY_PRODUCT_AUDIT.md §7` 6 项安全阀 + `MAINLINE_DECLARATION.md §5.1`：

1. **冻结 14 天**新增产品面 / schema / API / state machine / 公开导航。
2. **调用清单**：所有线上 service / CI workflow / 定时任务 / 人工脚本建立调用清单。
3. **30 天观测**：对候选删除路径进行 30 天日志观测；无观测条件时必须由 owner 签字。
4. **清理前 tag + manifest**：每个 phase 独立 commit；可整体 revert。
5. **不授权 mass-delete**；不授权修改云端；不授权改变数据 / Job / evidence authority。
6. **Canon 变更**：若执行内容触及 Canon 5 项（对外身份 / 内外边界 / state machine authority / evidence authority / cloud control authority / data authority），必须 `CANON_CHANGE = YES` + `docs/canon/CANON_CHANGELOG.md` 留痕 + 人类授权 + migration + rollback。
7. **Audit Trail**：每个 commit 引用对应阶段 + 安全阀检查清单；CI 增加 Canon guard 扫描（`Tier D` 禁词 / 第二公开产品身份 / 第二 state machine authority）。

**任意阶段出现以下情况立即停止：**

- 无法确认线上调用；
- 数据迁移无法回滚；
- Evidence Index 无法证明不可替代证据位置；
- 人类听觉判断被自动化替代；
- 需要新增第二 state machine / 数据库 authority / 公开产品；
- MVP 指标被功能数量取代。

---

## 1. Phase 1：冻结（Documentation First / 不删文件）

### 1.1 目标

通过**只追加 STATUS 头**的方式冻结**当前已与 Canon 冲突的方向**与**高置信空壳候选**；不删除任何文件、不修改文件内容、不需 owner 签字（除特别标注外）。

按 Delta §8 Phase 1 + `PRODUCT_BOUNDARY_V1.md §4.1` + `MAINLINE_DECLARATION.md §5.2`。

### 1.2 修改内容

| 任务 | 动作 | 文件 | owner 签字 | Canon Change |
|---|---|---|---|---|
| **1.2.1 QA 产品化方向冻结（Documentation First）** | 顶部追加 STATUS 头 | `docs/IMPLEMENTATION_PLAN_QA_V0.1_2026-08-24.md` + `docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md` | 否 | 否 |
| **1.2.2 第二 Android 冻结** | 顶部追加 `STATUS: FREEZE — 迁移必要能力后退役` | `apps/android/README.md`（如存在）；否则仅记录于 `MAINLINE_DECLARATION.md §2.2` | 否 | 否 |
| **1.2.3 Pulse / QA Desktop 冻结** | 顶部追加 `STATUS: DELETE CANDIDATE / NOT-AUTHORIZED` | `moodify-pulse/README.md` + `moodify-qa-desktop/README.md`（如存在） | 否 | 否 |
| **1.2.4 空壳 / placeholder 冻结** | 顶部追加 `STATUS: DELETE CANDIDATE — 无实质实现` | `products/README.md` + `shared/README.md` + `sdk/README.md`（如存在） | 否 | 否 |
| **1.2.5 中置信 candidates 标记** | 顶部追加 `STATUS: FREEZE — 30 天观测后裁决` | `moodify/orchestration/workflow_engine.py` 模块 docstring；`benchmark/README.md` + `research/benchmarks/README.md`；`scan_err.txt` | 否（仅标注） | 否 |
| **1.2.6 .gitignore 临时保护** | 追加 `moodify-qa-desktop/` + `scratch/` + `temp/` + `tmp/` | `.gitignore` | 否 | 否 |
| **1.2.7 CI Canon guard 增强** | 增加扫描：`grep -r "The Ear of AI\|AI Emotional Music\|Auditory Intelligence Infrastructure\|ACU 计算平台" docs/` 命中时 fail | `.github/workflows/*`（新增或修改） | 是（CI 修改需 owner 签字） | 否（CI 治理） |
| **1.2.8 docs/reduction/ 共享地图入口** | 已建立（5 文件 + Delta + 6 份 v1） | `docs/reduction/` | 否（已完成） | 否 |

### 1.3 风险

| 风险 | 等级 | 缓解 |
|---|---|---|
| QA 产品化方向文档被 ops 误读为已批准方向 | 中 | STATUS 头明确 `REJECTED / NOT-AUTHORIZED`；CI guard 扫描 |
| 现有 Windows / Linux / macOS 下载用户对 Pulse 退役有反弹 | 中 | Pulse 不在 v1.0 发布面；退役仅影响开发 brand identity，不影响 v1.0 主线 |
| CI guard 误伤历史文档 | 中 | guard 仅扫 `docs/`，命中 `archive/` 路径时忽略；旧文档加 `HISTORICAL` 头豁免 |
| `moodify-qa-desktop/` 未跟踪 | 低 | `.gitignore` 保护；保持 untracked |
| owner 未签字冻结动作 | 低 | 1.2.1-1.2.6 全部无需 owner 签字 |

### 1.4 验证方式

| 验证 | 命令 / 方法 | 通过条件 |
|---|---|---|
| STATUS 头追加成功 | `git diff --stat HEAD` | 仅追加，不删除 / 修改原文 |
| Canon guard 通过 | CI 运行 guard | 无命中（除豁免） |
| QA 产品化方向不再被读为已批准 | 人工 review + STATUS 头 | 头明确 `REJECTED / NOT-AUTHORIZED` |
| 默认 AI 加载 5 文件即可理解 Moodify | 模拟 5 文件加载 + 4 个 Canon 内判断 | 满足 `AI_CONTEXT_REDUCTION_PLAN.md §7 验收` |
| `moodify-qa-desktop/` 不进入 Git | `git status` | 不出现该目录 |
| `scratch/` / `temp/` / `tmp/` 不进入 Git | `git status` | 不出现 |
| docs/reduction/ 6 份 v1 文件可见 | `ls docs/reduction/` | 出现 6 份 v1 + Delta + MAINLINE_DECLARATION |

### 1.5 Phase 1 退出条件（DoD）

- [ ] QA 产品化方向 2 份文档 STATUS 头已追加；
- [ ] 第二 Android / Pulse / QA Desktop / 空壳 / 中置信候选已标注；
- [ ] `.gitignore` 临时保护已生效；
- [ ] CI guard 已加入并通过；
- [ ] `docs/reduction/` 6 份 v1 + Delta + MAINLINE_DECLARATION 已建立；
- [ ] `git diff --stat HEAD` 仅追加 / 不删除；
- [ ] 5 文件入口模拟测试通过。

---

## 2. Phase 2：归档（物理隔离 archive/）

### 2.1 目标

把 `ENTROPY_MAP_V1.md §1.6-1.7` 标记为 ARCHIVE 的目录物理隔离到 `archive/`；建立 `docs/ARCHIVE_INDEX.md`；保持 AI 默认检索工具排除 `archive/**`。

按 `REDUCTION_PLAN.md Phase 2` + `AI_CONTEXT_OPTIMIZATION.md §3` + `ENTROPY_MAP_V1.md §1.6-1.7`。

### 2.2 修改内容

| 任务 | 动作 | 源 → 目标 | owner 签字 | Canon Change |
|---|---|---|---|---|
| **2.2.1 ARCHIVE_INDEX.md 建立** | 新建 | `docs/ARCHIVE_INDEX.md` | 是（owner） | 否 |
| **2.2.2 审查包整目录归档** | `git mv` | `审查包/` → `archive/audits/2026-08/` | 是 | 否 |
| **2.2.3 Windows 历史归档** | `git mv` | `windows版本开发/` → `archive/windows-development/` | 是 | 否 |
| **2.2.4 历史补丁包归档** | `git mv` | `补丁包/` → `archive/patches/` | 是 | 否 |
| **2.2.5 Public Form 子包归档** | `git mv` + 仅留决议摘要 | `docs/public-form/package-XX/` → `archive/public-form/2026-08/` | 是 | 否 |
| **2.2.6 product-framework superseded 归档** | `git mv` + 头标记 `SUPERSEDED` | `docs/product-framework/*`（superseded） → `archive/product-framework/` | 是 | 否 |
| **2.2.7 工程笔记归档** | `git mv` | `docs/engineer/YYYY-MM-DD` → `archive/engineering-notes/` | 是 | 否 |
| **2.2.8 artifacts 不可替代证据保留 + 其余归档** | `git mv` + hash manifest | `artifacts/`（不可替代证据保留） + 其余 → `archive/evidence/` | 是 | **若改 evidence authority 则 YES**（默认 NO） |
| **2.2.9 MAMSE / MFY / 历史 batch 归档** | `git mv` + manifest | `artifacts/mamse_*` / `artifacts/mfy_*` → `archive/evidence/mamse/` + `archive/evidence/mfy/` | 是 | 否 |
| **2.2.10 research profile 拆出** | `git mv` | `moodify_experimental/` + `research/benchmarks/` + `physics/` + `calibration_reports/` 等 → `research/` | 是 | 否 |
| **2.2.11 大量生成 / 历史 / 临时 / 中文根目录归档** | `git mv` | 见 `ENTROPY_MAP_V1.md §1.7` → `archive/non-runtime/` + `archive/legacy/` | 是 | 否 |
| **2.2.12 doc root README 收敛** | 新建 5 类入口 | `README.md` / `docs/RUNBOOK.md` / `docs/ARCHIVE_INDEX.md` / `docs/REPOSITORY_STATUS.md` / `AGENTS.md` | 是 | 否（RUNBOOK/INDEX 新建属治理） |
| **2.2.13 README 模板标准化** | 追加 Role/Authority/Entrypoint/Tests/Dependencies/Non-goals/Owner/Last verified | 每个主线目录 `README.md` | 是 | 否 |
| **2.2.14 CI include/exclude 路由（建议）** | 增加 AI include/exclude 路由检查 | `.github/workflows/*`（与 Phase 1.2.7 合并） | 是 | **YES**（写入 AGENTS.md 是 Canon-affecting；但写入 CI 属治理） |
| **2.2.15 Core subpackage import scan** | 验证 default import 不带 research profile | `import scan + full tests` | 是 | 否 |

### 2.3 风险

| 风险 | 等级 | 缓解 |
|---|---|---|
| GitHub 链接断裂 | 中 | redirect map（`docs/ARCHIVE_INDEX.md` 含旧路径 → 新路径）+ link checker |
| Evidence 可复现性下降 | 高 | hash manifest + case id + 再生成命令；不可替代证据保留原路径 |
| ops / cloud 服务引用旧路径 | 中 | 调用清单 + 30 天观测；owner 签字 |
| 路径变化导致 ops runbook 失效 | 中 | `RUNBOOK.md` 同步更新 |
| ROOT_SYSTEM_POLICY（CI）扫描命中 archive | 低 | guard 仅扫默认 include 路径 |
| Core subpackage default import 误删 research 引用 | 高 | import scan + full tests；30 天观测 |
| `archive/` 自身规模仍过大 | 低 | `archive/` 不进入默认 AI 检索；规模不影响 5 文件入口 |

### 2.4 验证方式

| 验证 | 命令 / 方法 | 通过条件 |
|---|---|---|
| ARCHIVE_INDEX.md 完整 | 人工 review + hash 验证 | 覆盖全部 `archive/**` |
| AI 默认检索工具排除 archive | grep `.cursor` / IDE settings | `archive/**` 不在默认 include |
| 链接无断裂 | link checker（CI） | 所有引用路径存在 |
| ops 调用清单无未覆盖引用 | 人工 review + grep | 无未授权引用 |
| Core default import 不带 research | `pytest moodify-core-package` | 全通过 |
| README 模板标准化 | 人工 review | 每个主线目录含 8 字段 |
| 历史 evidence 可重建 | hash manifest + 再生成命令 | 通过 |
| 30 天观测无生产调用 | LA / 杭州 systemd / nginx / Docker logs | 无 |

### 2.5 Phase 2 退出条件（DoD）

- [ ] `docs/ARCHIVE_INDEX.md` 已建立并覆盖全部 `archive/**`；
- [ ] 默认 AI 检索工具排除 `archive/**`；
- [ ] 主线工作集（默认 + 按需）≤ 800 文件（`AI_CONTEXT_OPTIMIZATION.md §7`）；
- [ ] link checker 通过；
- [ ] ops 调用清单覆盖；
- [ ] Core import scan + full tests 通过；
- [ ] README 模板标准化完成；
- [ ] 每个 phase commit 可独立 revert。

---

## 3. Phase 3：删除（高置信 / 中置信候选 + owner 签字）

### 3.1 目标

按 `ENTROPY_MAP_V1.md §1` + `PRODUCT_BOUNDARY_V1.md §4.2-4.3` + `REDUCTION_PLAN.md Phase 3`，执行高置信 / 中置信候选删除；每项执行必须满足 `MOODIFY_PRODUCT_AUDIT.md §7` 6 项安全阀。

### 3.2 修改内容

| 任务 | 动作 | 目标 | owner 签字 | 30 天观测 | Canon Change |
|---|---|---|---|---|---|
| **3.2.1 QA 物理删除** | `git rm -r` | `moodify-qa/`（含 `api/` / `core/` / `tests/` / `Dockerfile` / `docker-compose.yml` / `qa_storage.db`） | 是 | 是 | 否（不在 Canon 5 项） |
| **3.2.2 QA Desktop 物理删除** | `git rm -r` | `moodify-qa-desktop/`（如已 tracked） | 是 | 是 | 否 |
| **3.2.3 QA 产品化方向 2 份文档归档或删除** | `git rm` + 入 archive/ | `docs/IMPLEMENTATION_PLAN_QA_V0.1_2026-08-24.md` + `docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md` | 是 | 是（已 Phase 1 冻结） | 否 |
| **3.2.4 空壳 / placeholder 删除** | `git rm -r` | `products/` + `shared/` | 是 | 是 | 否 |
| **3.2.5 SDK 删除** | `git rm -r` + 检查外部依赖 | `sdk/` | 是 | 是（30 天下载核验） | 否 |
| **3.2.6 Pulse 删除** | `git rm -r`（必要播放代码已提取到 `apps/music-android/` 或 `apps/web/`） | `moodify-pulse/` | 是 | 是 | 否 |
| **3.2.7 Legacy workflow engine 删除** | `git rm`（分支已 bypass；30 天观测） | `moodify/orchestration/workflow_engine.py` | 是 | 是 | 否 |
| **3.2.8 重复 baseline 删除** | `git rm`（保留一份） | `benchmark/baseline.py` 与 `research/benchmarks/baseline.py` 之一 | 是 | 否 | 否 |
| **3.2.9 scan_err.txt 删除** | `git rm` | `scan_err.txt`（0 字节） | 否（空文件） | 否 | 否 |
| **3.2.10 第二 Android 退役** | `git rm -r`（必要功能已迁移） | `apps/android/` | 是 | 是 | 否 |
| **3.2.11 engine facade 删除** | `git rm -r`（demo 已依赖 Core） | `engine/` | 是 | 是 | 否 |
| **3.2.12 Music Data API 退役** | `git rm`（BFF 唯一公开） | `moodify-music-package/.../api/` | 是 | 是 | 否 |
| **3.2.13 Web Drizzle 删除** | `git rm`（Music data authority 单一权威） | `apps/web/lib/db/schema.ts` | 是 | 是 | **YES**（data authority 变更） |
| **3.2.14 Music data authority schema 合并** | Alembic + BFF contract + 生成类型 | `tracks` + `track_versions` + `favorites` + `play_events` 仅 | 是 | 是 | **YES**（data authority 变更） |
| **3.2.15 CWC 积分账本删除** | `git rm`（确认无生产数据） | Music DB CWC 表 | 是 | 是 | 否 |
| **3.2.16 QA 两个 FastAPI 入口删除** | 随 3.2.1 包含 | `moodify-qa/api.py` + `moodify-qa/api/main.py` | 是 | 是 | 否 |
| **3.2.17 calibration server 常驻模式退役** | 改为离线 CLI | calibration server 入口 | 是 | 是 | 否 |
| **3.2.18 Root Docker compose 收敛** | `git rm` 重复 / future 设计 | 重复 `docker-compose.yml` + future Redis/nginx | 是 | 是 | 否 |
| **3.2.19 Root 中文工作包 / 压缩快照 / 安装器** | `git rm` | 见 `ENTROPY_MAP_V1.md §1.7` | 部分（核验发布依赖） | 否 | 否 |
| **3.2.20 单一 state machine 统一** | 删除 / 合并 workflow_engine + reconstruction_factory | 由 `CANON_CHANGELOG.md CD-015` 决定 | 是 | 是 | **YES**（state machine authority 变更） |
| **3.2.21 默认加载 research profile 排除** | 拆出 / 默认不 import | MAMSE / physics / LLM / lyric / transcription | 是 | 是 | 否 |
| **3.2.22 archive/ 默认工具排除** | IDE / AI tool config | `archive/**` 默认排除 | 否 | 否 | 否 |
| **3.2.23 兼容跳转路由退役** | `git rm`（迁移期结束） | `apps/web/app/track/[id]` | 是 | 是 | 否 |

### 3.3 风险

| 风险 | 等级 | 缓解 |
|---|---|---|
| 误删生产依赖 | 高 | owner 签字 + 30 天观测 + 调用清单 + revert commit |
| ops systemd / nginx / cron 直接引用旧入口 | 高 | 调用清单 + 30 天日志 + failure injection + queue recovery |
| PolarDB schema 误删（data authority 变更） | 高 | 备份 + 迁移 dry-run + 双读对账 + 回滚演练 |
| evidence authority 变更（artifacts 迁移） | 高 | ARCHIVE_INDEX.md 完整 + hash manifest + 再生成命令 + owner 签字 |
| 旧 APK 升级失败 | 中 | 旧 APK 测试 + 签名 / 升级路径 + 最后 release artifact 保留 |
| GitHub Releases / DNS 失效 | 中 | redirect map + checksums/manifest |
| 第二 state machine 误删 | 高 | CANON_CHANGE = YES + 人类授权 + changelog + 备份 + 回滚 |
| audit log / evidence 不完整 | 中 | ARCHIVE_INDEX.md + 每个 phase commit 引用安全阀检查清单 |

### 3.4 验证方式

| 验证 | 命令 / 方法 | 通过条件 |
|---|---|---|
| 线上 service inventory 无遗留 | systemd / nginx / Docker | 无未授权引用 |
| 30 天调用日志无遗留 | LA / 杭州 logs | 无 |
| GitHub Actions 全部通过 | CI | pass |
| pytest 全通过 | `pytest` | 109+ passed |
| ruff / lint 全通过 | `ruff check` | pass |
| Link checker 全通过 | CI | pass |
| PolarDB 双读对账（若 data authority 变更） | 数据备份 + 迁移 dry-run + 双读 | 一致 |
| Release 可回滚 | release artifact + revert commit | 可 |
| ARCHIVE_INDEX.md 完整 | 人工 review + hash 验证 | 覆盖全部 archive/ |
| docs/reduction/ 6 份 v1 + Delta + MAINLINE_DECLARATION 可见 | `ls docs/reduction/` | 8 文件 |
| Phase 1+2+3 整体可整体 revert | `git revert` 或独立 commit | 可 |

### 3.5 Phase 3 退出条件（DoD）

- [ ] `MOODIFY_PRODUCT_AUDIT.md §4 表` 中 DELETE 候选全部处理（KEEP / FREEZE / DELETED）；
- [ ] `REDUCTION_PLAN.md Phase 3 §3.1-3.5` 全部任务完成；
- [ ] 每个 DELETE 候选对应 commit 引用 6 项安全阀检查清单；
- [ ] ARCHIVE_INDEX.md 完整；
- [ ] PolarDB（若变）双读对账通过；
- [ ] Release 可回滚；
- [ ] CI 全部通过；
- [ ] 默认 AI 工作集 ≤ 800 文件。

---

## 4. Phase 4：Web + Cloud 开发（Moodify v1.0 主线交付）

### 4.1 目标

在 Phase 1-3 减法后的**单一架构**上完成真正可用的 PLAY 闭环；不恢复被删平台功能。

按 `MOODIFY_PRODUCT_AUDIT.md §6.4 7 天工程边界` + §6.5 三类受众理解测试 + `MOODIFY_MAINLINE_ARCHITECTURE.md`。

### 4.2 修改内容

| 任务 | 修改文件 | 删除文件 | owner 签字 | Canon Change |
|---|---|---|---|---|
| **4.2.1 最小 catalogue** | Web + BFF + Music models | mock catalogue + 重复 fixtures | 是 | 否 |
| **4.2.2 统一 playback contract** | BFF + Web Player + Android player | 旧 URL / 媒体 contract | 是 | 否 |
| **4.2.3 READY-only delivery** | Production adapter + BFF | 客户端可见内部状态 | 是 | 否 |
| **4.2.4 弱网与恢复** | Web/Android cache + retry | 重复缓存实现 | 是 | 否 |
| **4.2.5 最小行为证据** | play_events | 广泛 analytics schema | 是 | 否（privacy） |
| **4.2.6 3-10 首 Golden catalogue** | Production pipeline + manifest | demo / 占位内容 | 是 | 否（rights + quality） |
| **4.2.7 发布与回滚** | CI + runbook + release manifest | 手工打包流程 | 是 | 否 |
| **4.2.8 PolarDB 核验 + data authority 激活** | PolarDB + Alembic | — | 是 | **YES**（data authority 变更） |
| **4.2.9 单一 state machine 统一方案** | orchestration | 多 state machine | 是 | **YES**（state machine authority 变更） |
| **4.2.10 Creator / License / Support 保留但不激活** | BFF + DB + Web routes | 不激活 Creator / License / Support 路由 | 是 | 否（FREEZE 维持） |
| **4.2.11 ops runbook 维护** | `docs/RUNBOOK.md` + `docs/ARCHIVE_INDEX.md` | — | 是 | 否 |

### 4.3 风险

| 风险 | 等级 | 缓解 |
|---|---|---|
| Web / Android 行为不一致 | 中 | 统一 playback contract + 双向 E2E |
| 弱网 / 过期 URL / range 失败 | 中 | 失败可恢复 + 重试 + 错误状态 |
| READY 之外的内部状态泄漏给客户端 | 中 | BFF 唯一公开；Production 唯一内部 |
| play_events 误计数 | 中 | 隐私 + 最小匿名字段 |
| Golden catalogue 权利 / 质量 | 中 | 人类听评 + rights + manifest |
| PolarDB 核验 BLOCKED | 高 | 备份 + 迁移 dry-run + 双读 + 回滚 |
| 单一 state machine 误统一 | 高 | CANON_CHANGE = YES + 人类授权 + 备份 + 回滚 |

### 4.4 验证方式

| 验证 | 命令 / 方法 | 通过条件 |
|---|---|---|
| 新用户 30 秒首次播放成功率 | E2E | ≥ 95% |
| Web / Android 共用同一 contract | contract tests | pass |
| 无第二公开产品名 / QA / Master / Rating / Supply / Pulse 主入口 | route inventory + grep | 无 |
| READY 之外内部状态不泄漏 | BFF contract | 仅 READY 暴露 |
| 断网 / 过期 URL / 媒体缺失恢复 | failure injection | 恢复或失败状态明确 |
| ≥ 3 首合法可验证听评曲目 | 人类听评 + manifest | pass |
| Release 一键回滚 | release artifact + revert | 可 |
| Investor demo 3 分钟 | 人工 review | "打开 → Play → 对比为何值得再听" |
| 7 天边界达成 | timeline | Day 1-7 全部交付 |
| 5 文件入口验收 | 模拟 AI 加载 | 通过 |

### 4.5 Phase 4 退出条件（DoD = v1.0 验收）

- [ ] 新用户 30 秒内首次播放成功率 ≥ 95%；
- [ ] Web 与 Android 共用同一 catalogue/playback contract；
- [ ] 无第二公开产品名 / QA / Master / Rating / Supply / Pulse 主入口；
- [ ] READY 之外的内部状态不泄漏给客户端；
- [ ] 断网 / 过期 URL / 媒体缺失有明确恢复或失败状态；
- [ ] 至少 3 首合法可验证经过人类听评的曲目；
- [ ] Release 一键回滚；
- [ ] Investor demo 3 分钟："打开、Play、对比为何值得再听"；
- [ ] 7 天工程边界达成；
- [ ] 5 文件入口 AI 验收通过。

---

## 5. 建议执行顺序与停止条件

```text
Phase 1 冻结（Documentation First / 不删文件 / 不需 owner 签字）
   ↓
Phase 2 归档（物理隔离 archive/ + ARCHIVE_INDEX.md + owner 签字）
   ↓
Phase 3 删除（高 / 中置信候选 + owner 签字 + 30 天观测）
   ↓
Phase 4 Web + Cloud 开发（Moodify v1.0 主线交付）
```

**任意阶段出现以下情况立即停止：**

- 无法确认线上调用；
- 数据迁移无法回滚；
- Evidence Index 无法证明不可替代证据位置；
- 人类听觉判断被自动化替代；
- 需要新增第二 state machine / 数据库 authority / 公开产品；
- MVP 指标被功能数量取代。

---

## 6. 预期结果

按 `REDUCTION_PLAN.md §6` + `AI_CONTEXT_OPTIMIZATION.md §7`：

| 维度 | 当前 | 目标 |
|---|---|---|
| 公开产品身份 | Music + Pulse + QA + Ear/demo 暗示 | Moodify Music / Player |
| 公开核心动作 | Play + 上传 + 分析 + 发布 + 许可 + 赞助等 | Play |
| Android 工程 | 2 | 1 |
| Desktop 工程 | 2 | 0（真实需求再建 1） |
| Music schema | 2+ | 1 |
| 默认常驻 API | 多个 facade | BFF 1 + 内部 Production 1 |
| 产品模块 | QA/Master/Rating/Supply 空壳 | 0 空壳 |
| 默认 AI 工作集 | 3,300 tracked files | 500-800 主线文件 |
| 核心功能 | 100+ 表述 | 10 个不可替代能力 |
| 默认加载文件数 | 10+ MD | 5 MD |
| 治理入口 | 多份分散 + 第二权威风险 | Canon 4 + Public Brand 1 + MAINLINE_DECLARATION 1 |

---

## 7. 本文件**不**做的事

- **不**修改 `docs/canon/*` / `docs/brand/public/*` / `AGENTS.md` / `MOODIFY_PRODUCT_AUDIT.md` / `REDUCTION_PLAN.md` / `AI_CONTEXT_OPTIMIZATION.md`。
- **不**执行 Phase 1-4 任何物理动作。
- **不**授权 mass-delete。
- **不**对任何 DELETE / ARCHIVE 候选做物理移动 / 删除。
- **不**声明 `CANON_CHANGE`（各阶段在执行触及 Canon 5 项时**单独**声明）。

---

**本文件结束。等待 Reduction Execution 001：物理隔离 archive/freeze。**