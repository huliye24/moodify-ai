# 本地工作区恢复报告 — 2026-10-03

**任务性质：** 本地 Git 工作区恢复与分类整理（非产品重构、非功能开发）
**CANON_CHANGE = NO**
**执行分支：** `codex/local-workspace-recovery-20261003` · PR #32
**仓库外恢复目录：** `E:\moodify-local-recovery\2026-10-03\`（含 `_manifest.json`）

---

## 0. 基线（开始时重新验证，非引用任务书）

| 项 | 值 |
|---|---|
| 分支 | `codex/professional-finishing-layer-20260920` |
| HEAD | `17daab0d`（Merge origin/main into A-B v0.1 completion） |
| `origin/main` | `c4286189`（PR #31 · A/B compare v0.1） |
| `git merge-base --is-ancestor HEAD origin/main` | **成立** —— 本地分支是 origin/main 的祖先，无分叉 |
| 状态条目 | 768 = 717 tracked deletions (` D`) + 50 untracked (`??`) + 1 modification (` M`) |

A/B CLI-First Compare v0.1 的全部交付物（含 `ab_compare.py`、`tests/test_ab_compare.py`、
`moodify-desktop/scripts/check-contracts.js`、`next_actions`）**均已在 HEAD**，未做任何回滚或重复提交。

### 0.1 会话期间的并发写入（必须记录）

执行期间观察到其他 agent 在本仓库持续作业：

- 15:39:53 出现提交 `2d084300 test(studio): complete A-B compare v0.1`；
- 15:45:09 `git fetch`（FETCH_HEAD）；`.git/codex-artifact-merge-20020.index`（15:32）显示
  codex 侧在做合并工作；
- 15:57:05 出现 `.git/index.lock`（0 字节，创建后无任何 git 进程持有；`.git/index` 最后一次写入为 15:39:53）。

该锁阻断全部写操作。经与人类确认（该锁由本机自身操作遗留）后移除，随后完成全部恢复。
执行期间 HEAD 未再移动；最终 `origin/main` 仍为 `c4286189`。

---

## 1. `git status` 分类计数

### 恢复前

```
D  (tracked deletions, 未暂存)   717
?? (untracked)                     50
 M (tracked modification)           1
                                  768
```

### tracked modification 的完整 diff 摘要

`ops/cloud_audit/la_vps_reality_audit.sh` —— **经查证为幻觉修改（phantom），无实质内容差异**：

- `git diff` 为空；
- HEAD blob = index blob = worktree blob = `588b2ee8…`；
- `git update-index --refresh` 后 ` M` 标记消失；
- 与 `origin/main` 版本亦无差异。

判定原因：`core.autocrlf=true` 下的 stat 缓存陈旧（文件 mtime 11:50:57 晚于索引缓存）。
**未做任何修改、未生成 patch、无需还原。**

敏感信息检查：脚本含 LA VPS 地址 `103.144.246.242`（该地址早已在仓库、`docs/canon/CURRENT_ARCHITECTURE.md`
与提交历史中公开），无私钥块、无密码/token 赋值、无 SSH 私钥。

### tracked deletions 目录分布

| 一级目录 | 数量 | 二级分布（前几项） |
|---|---:|---|
| `审查包/` | 382 | 审查 8.18 版 104 · W01-P09 28 · W01-P08 27 · W01-P04 26 · W01-P05 25 · W01-P06 24 · W01-P07 24 |
| `windows版本开发/` | 330 | 桌面端开发8.21 219 · MFD-008 13 · MFD-010 13 · MFD-007 12 · MFD-009 11 · MFD-005/006 各 10 |
| `工程经验层/` | 5 | README · CONSTRAINT_REGISTRY · constraints/ME-001..003 |
| **合计** | **717** | 无其他目录，**不含 `artifacts/`** |

---

## 2. 恢复（Phase B）

- 清单来源：`git diff --name-only --diff-filter=D -z`（null 分隔，精确 pathspec）；
- 恢复前断言：清单不含 `artifacts/`、一级目录仅上述三项 —— 通过；
- 执行：`git checkout HEAD --pathspec-from-file=… --pathspec-file-nul` → `Updated 717 paths`；
- **不创建提交**（依据任务书 §5.6：这只是清除本地意外缺失，不产生内容变更）。

### 验证

| 检查 | 结果 |
|---|---|
| `git diff --name-only --diff-filter=D \| wc -l` | **0** |
| `git diff --stat -- 审查包 windows版本开发 工程经验层` | 空（工作区 == HEAD） |
| `git hash-object` 抽验 5 个恢复文件 vs `HEAD:<path>` blob | **5/5 一致** |
| 跟踪文件总数 | 2758（未变化） |

> 注：初次抽验用 Python 直接比对字节时出现 5/5 DIFF，经查是 `core.autocrlf=true`
> 下 工作区 CRLF 与 `git show` LF 的表示差异，非内容差异；以 git 自身的 blob 判定为准。

---

## 3. untracked 内容分类（Phase D）

### D1 — 可再生的本机环境 / 缓存

| 路径 | 规模 | 处置 |
|---|---|---|
| `.venv-core/` | 13,333 文件 / 501.78 MB | **保留 + 忽略**。运行中的 Studio 依赖它（`MOODIFY_PYTHON`、`moodify.release_cli` 全走该解释器）；删除会立即打断在用产品 |
| `.venv-score/` | 13,572 文件 / 237.86 MB | **保留 + 忽略**（曲谱工作台 venv） |
| `.tmp/` | 203 文件 / 172.38 MB | **保留 + 忽略**。含 `studio-user-data/`（在用 Electron 用户数据目录）与历史调试文本 |
| `moodify-core-package/.ruff_cache/` | — | 无需处理：ruff 自建 `.gitignore`（内容 `*`）自我忽略 |

**未删除任何缓存或虚拟环境。** 理由：任务优先级为「不丢数据 > … > 减少文件数量」，而加忽略规则已经达成
「工作区干净」这一目标；删除在用 venv 的收益（磁盘）远低于风险（打断在运行的产品）。
如需回收约 740 MB，可在 Studio 关闭后自行删除并按 `start-moodify-studio.bat` 的说明重建。

### D2 — 私有音频 / 用户素材

| 路径 | 规模 | 处置 |
|---|---|---|
| `07Music/` | 127 文件 / 1694.53 MB（57 mp3 · 52 wav · 1 flac · 1 f32 · 11 png） | **不删除、不提交、保留原位 + 精确根忽略 `/07Music/`** |
| `07Music/albums/.auditory_decode_713d2a38.f32` | 听觉解码缓存 | 随 `/07Music/` 一并忽略（缓存本身可再生） |

### D3 — 当前 Moodify 文件

| 路径 | 判定 | 处置 |
|---|---|---|
| `moodify-core-package/scripts/listen_demo_render.py` | **正式工具**：被 `docs/reduction/*`、`ops/web_origin/site/rongjingmusic/runbook_listen_demo_v0.1.README.md` 引用；`--check-syntax` 对真实 5 轨 manifest 实跑通过 | **提交**（`feat(scripts)`），并修正 ruff 报出的 2 处（未用 import、多余 f 前缀） |
| `docs/plan/2026-10-03_EVIDENCE_LOOP_PLAN_V01.md` | 计划文档，DRAFT_FOR_HUMAN_APPROVAL；H1/H2/H3 未裁决，H2=B 触发 `CANON_CHANGE=YES` | **逐字提交** + `HUMAN_DECISION_REQUIRED` |
| `docs/plan/2026-10-03_LOCAL_WORKSPACE_RECOVERY_DEEPSEEK_TASK.md` | 本次任务书，与已跟踪的 A/B 任务书同类 | **提交** |
| `docs/mood/`（87 文件 / 0.33 MB） | **MOOD 项目线**（genesis/token/treasury/security），从未跟踪；有独立分支与 `E:\moodify-*` worktree | **保留原位 + 精确忽略**（人类裁决） |
| `logo/moodify-horizontal.svg`（850,230 B） | **生成型构建产物**：`brand/build-horizontal.mjs` 的输出副本，`brand/assets/` 已有规范版本（差 13 字节，规范版为跟踪文件） | **移出仓库**（`stale-generated/`） |
| `moodify-core-package/debug_ids.py` | contribution 模块手工调试脚本，无断言、无引用 | **移出仓库**（`debug/`） |
| `moodify-core-package/debug_validation.py` | 同上（且函数内 `tempfile` 依赖调用方的 import） | **移出仓库**（`debug/`） |
| `moodify-core-package/test_basic.py` | 手工冒烟脚本，非 pytest（`pytest testpaths=["tests"]` 不采集），无引用 | **移出仓库**（`debug/`） |
| `start-moodify-studio.bat` | 启动器：硬编码 `E:\moodify`；含 `--no-sandbox`；路径全部存在、Python 导入可用，但**未做真实 GUI 启动**（在运行的 Studio 占用同一 user-data-dir） | **移出仓库**（`dev/`）—— 任务书自身门槛为「仅当实测通过」 |

### D4 — 大型历史 / 旁支项目

`web 3.0/`（未跟踪 590 个非忽略文件；`2026.8.29` 134 · `2026.8.30` 353 等）

- **是独立项目线**：MOOD Protocol Genesis 001–008、AGENTS 018、GOVERNANCE 020、SECURITY 022 等；
  拥有独立分支（`codex/mood-agents-018`、`codex/mood-governance-020`、`codex/mood-mainnet-integration-009` …）
  与独立 worktree（`E:\moodify-agents-018` 等）；
- HEAD 已跟踪其中 **37 个** MOOD 包文档（不受忽略规则影响，保持版本化）；
- `MOOD_GOVERNANCE_020_MIP/` 与 `apps/` 内含 `node_modules`（已被全局 `node_modules` 规则忽略）；
- **处置：保留原位 + 精确忽略 `/web 3.0/`**，不并入主仓库（人类裁决）。

### 秘密扫描结果（全 untracked，52,759 文件）

| 检查项 | 结果 |
|---|---|
| 真实 `.env` / 私钥 / 凭据文件 | **无**（仅 2 个 `.env.example`，值经分类全部为 placeholder 或空值） |
| 私钥块 / AWS AK / JWT / 助记词 / 64 位十六进制 | **0 命中** |
| `docs/mood/security/022_SECRET_INVENTORY.md` | 无秘密值，仅清单结构 |
| `.tmp/studio-user-data/Network/Trust Tokens` | 本机 Chromium 信任令牌（浏览器本地状态，随 `/tmp/` 忽略） |

---

## 4. 处置汇总

### 提交（4 个，各自单一主题）

| 提交 | 主题 |
|---|---|
| `3155b17f` | `chore(repo): ignore local environments and private media` |
| `378aa209` | `feat(scripts): add offline Listen Demo render utility` |
| `a71b4800` | `docs(plan): add Evidence Loop v0.1 draft (H1-H3 pending)` |
| `b0d156da` | `docs(plan): record local workspace recovery task` |

其后合并 `origin/main`（`20276320`），分支领先 5、落后 0。

### 移出仓库（`E:\moodify-local-recovery\2026-10-03\`，逐项 SHA-256 校验）

| 原路径 | 恢复路径 | 处置理由 |
|---|---|---|
| `moodify-core-package/debug_ids.py` | `debug/` | 临时调试脚本 |
| `moodify-core-package/debug_validation.py` | `debug/` | 临时调试脚本 |
| `moodify-core-package/test_basic.py` | `debug/` | 手工冒烟脚本 |
| `start-moodify-studio.bat` | `dev/` | 未实测 + 机器特定路径 + `--no-sandbox` |
| `logo/moodify-horizontal.svg` | `stale-generated/` | 生成型构建产物旧副本 |

### 删除

**无。** 未删除任何文件、分支或历史。

### .gitignore 新增规则（全部根锚定、目录级，不隐藏任何源码）

```gitignore
/.venv-core/
/.venv-score/
/.tmp/
/07Music/
/web 3.0/
/docs/mood/
```

验证：`web 3.0/` 下 37 个已跟踪文件仍正常跟踪；跟踪文件总数 2758 未变。

---

## 5. 验证

| 检查 | 结果 |
|---|---|
| `ruff check moodify-core-package/scripts/listen_demo_render.py` | All checks passed |
| `pytest -m v01` | **265 passed, 5 skipped** |
| 全量 `pytest` | **1185 passed, 5 skipped** |
| `node --check` ×3（main.js / preload.js / app.js） | 全部 OK |
| Studio 合约检查（`scripts/check-contracts.js`） | 通过（DOM id 95 · 桥接 40 · IPC 38 · 事件 5） |
| `git status --porcelain` | **空** |
| `git diff --check`（各提交暂存时） | 除任务书 Markdown 硬换行尾空格外干净（仓库内 23 份已跟踪 `.md` 同样如此，属原文语义） |

`artifacts/`：**未恢复**，磁盘上不存在，仍被 `.gitignore:262:/artifacts/` 忽略，未被跟踪。
`temporal-texture` 的 CI 历史基线债务：**未触碰**（不删规则、不降阈值、不伪造基线）。

---

## 6. HUMAN_DECISION_REQUIRED

1. **H1/H2/H3（Evidence Loop v0.1）** —— 判断记录通道形态 / 叙事锚点 / 感知量表。
   H2 选 B 触发 `CANON_CHANGE=YES`。该文档已逐字提交，未按其内容实施任何新代码。
2. **MOOD 项目边界** —— `web 3.0/` 未跟踪部分与 `docs/mood/` 已按人类指示「保留原位 + 精确忽略」；
   是否最终迁出本仓库（或并入 MOOD 侧独立仓库）仍需裁决。
3. **`start-moodify-studio.bat`** —— 现置于仓库外恢复目录。若要入库，需先做真实启动验证，
   并决定是否接受机器特定路径与 `--no-sandbox`。
4. **venv 回收** —— `.venv-core/` + `.venv-score/` 约 740 MB 保持原位未删；是否回收由人类决定。
5. **并发写入** —— 执行期间有其他 agent 在本仓库提交与合并（见 §0.1）。本次未与之冲突，
   但建议确认该并行通道是否应继续。

---

## 7. CANON_CHANGE = NO

未修改对外产品身份、内部/外部能力边界、state machine authority、evidence authority、
cloud control authority 或 data authority。未创建第二套 Core / DSP / 状态机。
`artifacts/` 保持忽略；717 项删除已恢复；A/B v0.1 未回滚或重复提交。
