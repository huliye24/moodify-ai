# Moodify Delta Entropy Audit — 2026-08-24

**审计类型**：只读 Delta 审计（针对 2026-08-24 既有审计后的新增 / 未跟踪产物）
**审计基线**：
- `MOODIFY_PRODUCT_AUDIT.md` v1.0（2026-08-24，332 行只读审计）
- `REDUCTION_PLAN.md`（2026-08-24，Phase 1-4 减法计划）
- `AI_CONTEXT_OPTIMIZATION.md`（2026-08-24，上下文优化建议）
**Canon**：v1.1（2026-08-19，Public Form Package 01）
**CANON_CHANGE**：`NO` —— 本报告不改变任何对外身份、内外边界、state machine / Job / data / cloud / evidence authority。
**执行状态**：仅建议；本报告不修改任何业务代码、不删除任何文件。
**不做的事**：不创建 4 份新文档；不重复扫描 `MOODIFY_PRODUCT_AUDIT.md` 已经覆盖的目录；不调用 `git rm` / `rm` / `mv`；不修改 `REDUCTION_PLAN.md`。

---

## 0. Delta 结论

3 行总述：

1. 仓库在 2026-08-24 既有审计之后，又冒出了两条**直接违反 Canon 不变量 #1**（一个对外产品身份）的新产物线：**Moodify QA Web v0.1 产品化方向**（`docs/IMPLEMENTATION_PLAN_QA_V0.1_2026-08-24.md` + `docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md`）+ **Moodify QA Desktop**（`moodify-qa-desktop/`，未跟踪）—— 这两条线把已由 `MOODIFY_PRODUCT_AUDIT.md §4` 标 `DELETE` 的 `moodify-qa` 包装为对外产品，必须被明确否决，不得作为 v1.0 实施方向。
2. 同时，Listen Demo v0.1 落地链条（`apps/web/app/listen/`、`apps/web/app/evidence/`、`moodify-core-package/scripts/listen_demo_render.py`、ops runbook、`apps/web/app/page.tsx` 导航扩展）**完整 Canon-aligned**，且其中**关键审查点**（公开 URL 兜底 EmptyState、Human Listening Gate Step 5、Brand Tier §9 合规、Public Form §11 顺序）已写入代码注释与 runbook。这是必须 **KEEP** 的 v1.0 主线。
3. `apps/web/app/page.tsx` 与 `ops/web_origin/site/rongjingmusic/index.html` 的本会话改动是**Brand / Player 收敛动作**（删除 Listen 段缺失前的旧 index.html、加入 Listen / Evidence 导航），与 Canon 一致；但 `moodify-qa/api/main.py` 与 `moodify-qa/qa_storage.db` 的改动发生在已被 `MOODIFY_PRODUCT_AUDIT.md` 标 `DELETE` 的目录内，**不可独立裁决**。

---

## 1. Delta 扫描结果

### 1.1 未跟踪产物（untracked）

| Path | Function | Brand Surface | Canon Evidence | Phase Decision |
|---|---|---|---|---|
| `AI_CONTEXT_OPTIMIZATION.md` | 上下文优化建议（建议保留 8-12 个长期文档） | Internal（治理文档） | `AGENTS.md §Canon 不变量` + `AI_CONTEXT_OPTIMIZATION.md §2` 自陈 | **NOT-IN-SCOPE**（与 `MOODIFY_PRODUCT_AUDIT.md` 平行的治理文档，参见 §6） |
| `MOODIFY_PRODUCT_AUDIT.md` | 只读产品减法审计 v1.0 | Internal（治理文档） | 自身 v1.0 + Canon v1.1 引用 | **NOT-IN-SCOPE**（基线，不动） |
| `REDUCTION_PLAN.md` | Phase 1-4 减法计划 | Internal（治理文档） | `AGENTS.md §Change Discipline` + §0.5 不授权 mass-delete | **NOT-IN-SCOPE**（基线） |
| `apps/web/app/evidence/` | Public Form §11 Proof 段（Evidence Badge / maturity / scope） | **Player**（对外产品面） | `PUBLIC_BRAND_CONSTITUTION.md §9 Tier B` + `apps/web/app/evidence/page.tsx` 注释引用 §11/§13 | **KEEP**（v1.0 主线） |
| `apps/web/app/listen/` | Public Form §4 + §11 Sound 段（Original vs Moodify 对比播放） | **Player**（对外产品面） | `PUBLIC_BRAND_CONSTITUTION.md §4 §11 §13` + `apps/web/app/listen/page.tsx` 注释引用 §4/§11/§13 | **KEEP**（v1.0 主线） |
| `docs/IMPLEMENTATION_PLAN_QA_V0.1_2026-08-24.md` | 把 `moodify-qa` 包装为对外 QA Web v0.1 商业产品面 | **第二公开产品面**（违反 Canon 不变量 #1） | `MOODIFY_PRODUCT_AUDIT.md §4` 表（moodify-qa = DELETE）+ `PUBLIC_BRAND_CONSTITUTION.md §2.2`（禁单）+ `CURRENT_CANON.md §3 不变量 #1` | **DELETE 候选**（详见 §2 D-1） |
| `docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md` | 同上，把 Moodify 重定义为"30 天内可上线 QA Web v0.1" | **第二公开产品面**（违反 Canon 不变量 #1） | 同上 | **DELETE 候选**（详见 §2 D-1） |
| `moodify-core-package/scripts/listen_demo_render.py` | 离线一次性 DSP 渲染脚本（5 首 Cadeau10 → MoodifyDSPChain → wav + manifest sidecar） | Internal（受控生产脚本） | `PRODUCT_BOUNDARY.md §Internal Systems` "cloud production ... render" + `INTERNAL_SYSTEMS.md §2` 受控生产环节 | **KEEP**（v1.0 Listen Demo ops runbook 必需） |
| `moodify-qa-desktop/` | Electron 桌面壳，把 moodify-qa 暴露为独立桌面产品 | **第二公开产品面**（违反 Canon 不变量 #1） | `MOODIFY_PRODUCT_AUDIT.md §4` 表（moodify-qa-desktop = DELETE）+ `PUBLIC_BRAND_CONSTITUTION.md §2.2` | **DELETE 候选**（详见 §2 D-1，与 D-1 同包） |
| `ops/web_origin/site/rongjingmusic/runbook_listen_demo_v0.1.README.md` | ops 端到端 runbook 文档（人类耳机会话 Step 5 必备） | Internal（部署 runbook） | `REDUCTION_PLAN.md §0.3`（30 天观测）+ `MOODIFY_PRODUCT_AUDIT.md §7` DELETE 安全阀 | **KEEP**（v1.0 ops runbook 必需） |
| `ops/web_origin/site/rongjingmusic/runbook_listen_demo_v0.1.sh` | ops runbook 可执行脚本（fail-closed + human gate Step 5） | Internal（部署 runbook） | 同上 + `runbook_listen_demo_v0.1.sh:21-26` 自身约束 | **KEEP**（v1.0 ops runbook 必需） |

### 1.2 2026-08-24 起新增 tracked 修改（`git diff --stat HEAD`）

| Path | Function | Brand Surface | Canon Evidence | Phase Decision |
|---|---|---|---|---|
| `apps/web/app/page.tsx` | Player 主屏导航扩展：加 `/listen` / `/evidence` / `/library` 抽屉；不引入第二身份 | **Player**（对外产品面） | `apps/web/app/page.tsx:147` 注释 "Package 04: Surface convergence — Player focuses on Play" + 抽屉文案"聆听"/"关于"/"信息"分层 | **KEEP**（Player 主屏合理扩展） |
| `moodify-qa/api/main.py` | FastAPI 启动日志去除 emoji（🚀 / 📚 / 👋 → 无） | （位于 DELETE 候选目录内） | `MOODIFY_PRODUCT_AUDIT.md §4` moodify-qa = DELETE | **NOT-IN-SCOPE**（与 D-1 同包裁决，单独删除 main.py 是反模式） |
| `moodify-qa/qa_storage.db` | moodify-qa 独立 SQLite 数据库（45056→53248 bytes 增长） | （位于 DELETE 候选目录内） | 同上 + `MOODIFY_PRODUCT_AUDIT.md §3.4 D` 数据 authority 重复 | **NOT-IN-SCOPE**（与 D-1 同包裁决） |
| `ops/web_origin/site/rongjingmusic/index.html` | Brand Home 从旧版本("AI Audio Player" / schema.org Product)回到 Package 02 完成版("Listen. Then Play." / schema.org WebSite / 含 Listen 段) | **Brand**（rongjingmusic.com） | `PUBLIC_BRAND_CONSTITUTION.md §2 §6 §9 §11 §13` + 本地文件 line 6-7 `<title>Moodify — Listen. Then Play.</title>` | **KEEP**（部署漂移修复，与 `MOODIFY_PRODUCT_AUDIT.md §3.4 F` 文档与证据重复一致） |
| `ops/web_origin/site/rongjingmusic/sitemap.xml` | sitemap 与 index.html 同步修正（与 §11 顺序一致） | **Brand** | 同上 | **KEEP** |

### 1.3 本会话新增未提交（同 1.1，覆盖了未跟踪与已跟踪 M 的并集）

参见 §1.1 + §1.2。无新条目。

---

## 2. 进入 Phase 1 候选（立即可删）

只列高置信、低耦合、空壳、占位、demo 残留、与 Canon 直接冲突的产物。每项包含删除理由（引用 Canon 或宪法条款）、风险、收益、验证方法。

### D-1 Moodify QA Web v0.1 产品化方向（整个方向否决，不是单个文件）

| 项 | 内容 |
|---|---|
| 删除文件 / 目录 | `moodify-qa/`（含 `api/`、`core/`、`tests/`、`Dockerfile`、`docker-compose.yml`、`qa_storage.db`）+ `moodify-qa-desktop/`（未跟踪，含 `src/main/`、`src/preload/`、`src/renderer/`、`package.json`、`package-lock.json`、`README.md`）+ `docs/IMPLEMENTATION_PLAN_QA_V0.1_2026-08-24.md` + `docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md` |
| 删除理由 | `MOODIFY_PRODUCT_AUDIT.md §4` 表已标 `moodify-qa`（值 1,1,4 → DELETE）与 `moodify-qa-desktop`（值 1,1,4 → DELETE）。两份新文档与该审计**完全相反**：把已标 DELETE 的内部旁路服务包装为对外产品面，并自陈 "本次产品化方向涉及 Canon 层面的产品身份变更，必须声明 CANON_CHANGE = YES 并由人类批准"。**这两份文档从未声明 CANON_CHANGE，也没有在 `CANON_CHANGELOG.md` 留痕**。`PUBLIC_BRAND_CONSTITUTION.md §2.2` 明确把 "AI 音乐后处理平台 / Auditory Intelligence Infrastructure / The Ear of AI / 音频 API 平台 / ACU 计算平台" 列为禁单。`moodify-qa/api/main.py` 自描述 "Moodify QA - AI Audio Quality Assurance Infrastructure"，目标用户 "AI Music Platforms / Music Companies / Copyright Owners / Audio Production Studios" —— 正是禁单中"音频 API 平台"的变体。`CURRENT_CANON.md §3 不变量 #1`：一个对外产品身份 = Moodify Music / Player。Ear / Auditory Intelligence 不成为第二个公开产品面。`PRODUCTIZATION_REVIEW` §3.3 自己说"必须声明 CANON_CHANGE = YES 并由人类批准后记入 CANON_CHANGELOG" —— 该步骤未发生。 |
| 风险 | **中**。可能存在 LA VPS systemd / cron / nginx 配置引用 moodify-qa 的 FastAPI 入口（`MOODIFY_PRODUCT_AUDIT.md §7 DELETE 安全阀 #1` 要求"git grep / CI / 部署单元 / systemd/nginx/Docker 和 30 天日志均无调用"）。owner 未签字（`MOODIFY_PRODUCT_AUDIT.md §7 #2`）。`PRODUCTIZATION_REVIEW` 是 2026-08-24 新文档，可能被 ops 误读为已批准方向。 |
| 收益 | 极高。消除第二公开产品面、两个独立 FastAPI facade、独立 SQLite、独立桌面 Electron 维护，回归 Canon 不变量 #1。"QA Web v0.1 / QA Desktop / QA 第三方 API" 这一整套方向若实施，会把 Moodify 从"一个 Play 闭环"扩张为"创作者 / 第三方 API 平台"，与 `MOODIFY_PRODUCT_AUDIT.md §0` "停止增加第二公开产品" 直接冲突。 |
| 验证 | （a）`git grep -l moodify-qa` 全仓引用审计；（b）`grep -r 'localhost:8000' /etc/systemd /etc/nginx /opt/moodify`（LA VPS）；（c）owner 签字（必须由 ops 确认 moodify-qa 无生产调用）；（d）把 `docs/IMPLEMENTATION_PLAN_QA_V0.1_2026-08-24.md` + `docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md` 标记为 `REJECTED / NOT-AUTHORIZED`，保留为历史包；（e）30 天线上调用日志（`MOODIFY_PRODUCT_AUDIT.md §7 #1`）。 |

### D-2 ops/web_origin/site/rongjingmusic/index.html 与 sitemap.xml 的旧版本已通过本会话修复（不属于删除候选）

不在 D-1 中。本会话改动是把 index.html 从部署漂移的旧版本("AI Audio Player" / schema.org Product)改回 Package 02 完成版("Listen. Then Play." / schema.org WebSite / 含 Listen 段)—— 这是 §1.2 中标 KEEP 的 Brand 收敛动作。线上 `https://rongjingmusic.com` 是否同步重部署属于 ops 责任（参见 `REDUCTION_PLAN.md Phase 2` 结构调整），不是 Delta 审计的删除项。

---

## 3. 进入 Phase 2 候选（物理隔离）

| Path | Function | Phase 2 目标 | 理由 |
|---|---|---|---|
| 无新增。 | — | — | 本 Delta 仅覆盖 2026-08-24 后新增 / 未跟踪。Phase 2 物理隔离（archive/）属于 `REDUCTION_PLAN.md Phase 2` 已规划范围（`审查包/` / `windows版本开发/` / `artifacts/` / 重复模板），不在 Delta 范围。 |

---

## 4. 进入 Phase 3 候选（未来考虑）

| Path | Function | HUMAN_DECISION_REQUIRED 的具体问题 |
|---|---|---|
| 无新增。 | — | — | 本 Delta 仅 1 个 Phase 1 候选（D-1 QA 产品化方向整体否决）。Listen Demo v0.1 不在 Phase 3。 |

---

## 5. NOT-IN-SCOPE（扫描后确认不需要进入任何 Phase）

下列产物在本 Delta 中确认**不需要**进入 Phase 1 / 2 / 3，正常保留：

- `AI_CONTEXT_OPTIMIZATION.md`、`MOODIFY_PRODUCT_AUDIT.md`、`REDUCTION_PLAN.md` —— 既有治理文档，参见 §6 与既有 REDUCTION_PLAN.md §0.5。
- `apps/web/app/listen/`、`apps/web/app/evidence/`、`moodify-core-package/scripts/listen_demo_render.py`、`ops/web_origin/site/rongjingmusic/runbook_listen_demo_v0.1.{sh,README.md}` —— Listen Demo v0.1 ops runbook 链条（v1.0 主线）。
- `apps/web/app/page.tsx`、`ops/web_origin/site/rongjingmusic/index.html`、`ops/web_origin/site/rongjingmusic/sitemap.xml` —— Player / Brand 主屏与 sitemap 本会话收敛（v1.0 主线）。

---

## 6. Delta 与 REDUCTION_PLAN.md 的差异

### 6.1 重叠条目

- `moodify-qa-desktop/`：`REDUCTION_PLAN.md Phase 3 §3.5` 已规划（"必要播放代码提取后）+ `REDUCTION_PLAN.md Phase 1 表行 "Canon guard 增加禁用第二公开身份检查 | 未跟踪 `moodify-qa-desktop/` | 阻止第三个桌面产品进入主线 | `git status` 不再出现该目录"）。本 Delta **比 Phase 1 更严**：连 `moodify-qa-desktop/` 整个目录都判定为 Phase 1 候选，原因：D-1 把 moodify-qa 也包含在内。
- `moodify-qa/`：`REDUCTION_PLAN.md Phase 3 §3.4` 已规划（"QA 两个 FastAPI 入口"+"Calibration server 常驻模式"+"legacy orchestration" 同列）。本 Delta **把 moodify-qa 提升到 Phase 1**，原因：D-1 中两份 2026-08-24 新文档把它包装为对外产品面，构成立即 Canon 冲突。

### 6.2 新增条目

- `docs/IMPLEMENTATION_PLAN_QA_V0.1_2026-08-24.md` + `docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md` —— 现有 REDUCTION_PLAN.md **没有**列这两份文档。它们是 2026-08-24 新文档，**未声明 CANON_CHANGE**，**未在 CANON_CHANGELOG.md 留痕**，自陈"必须声明 CANON_CHANGE = YES 并由人类批准"。

### 6.3 现有 Phase 1 条目被本 Delta 审计否决的

- `REDUCTION_PLAN.md Phase 1` 第 4 行 "更新或删除 SDK 引用 | `sdk/` | 中；外部人工用户不可由代码证明 | 删除 placeholder 客户端和虚假 API 预期 | 30 天下载/调用核验 + owner 签字" —— 不在本 Delta 范围（属于既有审计范围），保持原判。
- `REDUCTION_PLAN.md Phase 1` 第 6 行 "把冲突计划标记为 rejected/historical | QA 产品化计划的当前态标签" —— **本 Delta 间接达成此目标**：D-1 把 QA 产品化方向（含两份新文档）整体列入 DELETE 候选，验证项 (d) 即 "标记为 REJECTED / NOT-AUTHORIZED，保留为历史包"。

---

## 7. Canon 一致性自检

- [x] 未创建第二公开产品身份（D-1 主动否决 QA Web v0.1 / QA Desktop）
- [x] 未修改 Brand Tier（§9 A/B/C/D）—— Listen page 与 Evidence page 引用 §11/§13，runbook 引用 §13 Test C 与 Human Listening Gate
- [x] 未把内部能力（Ear / Auditory Intelligence）暴露为对外产品 —— Listen page 与 Evidence page 注释明确区分 Moodify 与内部能力（"Moodify listens before you do. Original 是艺术家提交的原声;Moodify 是 Moodify 理解之后的版本。先听后判断"）
- [x] 未使用 §9 Tier D 禁词（Listen page + Evidence page + runbook 均无 "AI audio" / "Personalized" / "Build with Moodify"）
- [x] 未修改 Canon 5 项（对外身份 / 内外边界 / state machine authority / evidence authority / cloud control authority / data authority）
- [x] 未对 data authority 提出变更（moodify-qa 数据库删除候选不涉及 Music data authority 的结构变更）
- [x] 未声明 CANON_CHANGE（本审计本身 CANON_CHANGE = NO）
- [x] 未授权 mass-delete（D-1 仍需 owner 签字 + 30 天观测）

---

## 8. 给 ops 的执行清单

按 Phase 1 / Phase 2 / Phase 3 分列。每项 ops 决策**必须**要求 owner 签字 + 30 天观测（如适用）。

### Phase 1（今日 ops 决策：方向否决，不立即物理删除）

| 任务 | 动作 | owner | 验证 |
|---|---|---|---|
| **QA 产品化方向否决（Documentation First）** | 把 `docs/IMPLEMENTATION_PLAN_QA_V0.1_2026-08-24.md` + `docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md` 顶部加 `> STATUS: REJECTED / NOT-AUTHORIZED — 2026-08-24 Canon Change 主张未获人类批准, 不进入 v1.0 实施`。**不动文件内容，不删除文件** | 人类 owner | git diff 显示仅追加 STATUS 头 |
| QA Desktop 未跟踪保护 | `.gitignore` 追加 `moodify-qa-desktop/`（或保留 untracked，由 ops 决定是否进入 git） | ops | `git status` 不再出现该目录 OR 维持 untracked 但打 STATUS 标签 |
| `git grep -l moodify-qa` 全仓引用审计 | 报告所有引用 | ops | 输出文件清单 |
| moodify-qa LA VPS systemd / nginx / cron 调用审计 | `grep -r 'moodify-qa' /etc/systemd /etc/nginx /opt/moodify 2>/dev/null` | ops | 输出调用图 |

### Phase 2（本周 ops 决策：物理删除预备）

| 任务 | 动作 | owner | 验证 |
|---|---|---|---|
| moodify-qa `api/main.py` 日志去 emoji 改动回滚 | 若 Phase 1 决议删除 moodify-qa，则 `git checkout HEAD -- moodify-qa/api/main.py` | ops | `git diff HEAD -- moodify-qa/api/main.py` 为空 |
| `moodify-qa/qa_storage.db` 删除预备 | 检查 30 天线上调用日志后，从 git index 移除 | ops + owner | 删除后 `git grep moodify-qa` 为空 |
| `moodify-qa-desktop/` 物理删除 | 在 owner 签字后整目录 `git rm -r moodify-qa-desktop/` 或保留 untracked | ops + owner | `ls moodify-qa-desktop/` 不存在 |
| moodify-qa/ 物理删除 | 在 owner 签字后整目录 `git rm -r moodify-qa/` | ops + owner | `ls moodify-qa/` 不存在 |

### Phase 3（需人类决策）

| 任务 | 动作 | owner | 决策点 |
|---|---|---|---|
| 无 | — | — | 本 Delta 未产生 Phase 3 候选。 |

---

## 9. 给下一位 agent / Cursor 的提示

下一位执行者读本 Delta 报告时，请**只关注 §2 D-1**：那是 2026-08-24 后唯一 Phase 1 候选。其它条目全部 KEEP 或 NOT-IN-SCOPE。

执行 §8 Phase 1 第一步（"QA 产品化方向否决 Documentation First"）**不需要**修改任何业务代码，只需要给两份文档加 STATUS 头。Cursor 可执行此步骤，无需 owner 二次签字。

执行 §8 Phase 1 第二步（`moodify-qa-desktop/` 未跟踪保护）需要 ops 决定 `.gitignore` 策略。

执行 §8 Phase 2 物理删除需要 owner 签字 + 30 天观测，**不可由 Cursor 自动执行**。

---

## 10. 不做的事（再次声明）

- 本报告**不**修改 `REDUCTION_PLAN.md` / `MOODIFY_PRODUCT_AUDIT.md` / `AI_CONTEXT_OPTIMIZATION.md` / `AGENTS.md` / `docs/canon/*` / `docs/brand/public/*`。
- 本报告**不**创建 `CORE_PRODUCT.md` / `REDUCTION_RULES.md`（与既有审计重复）。
- 本报告**不**调用 `git rm` / `rm` / `mv` / `sed` / `awk` / `echo` 写入任何业务文件。
- 本报告**不**给 moodify-qa 物理删除授权（owner 签字后才可）。
- 本报告**不**对 Listen Demo v0.1 主线（`apps/web/app/listen/` + `apps/web/app/evidence/` + `moodify-core-package/scripts/listen_demo_render.py` + ops runbook）做任何裁决（已 KEEP）。

---

**报告结束。等待下一阶段（Documentation First STATUS 头追加）执行。**