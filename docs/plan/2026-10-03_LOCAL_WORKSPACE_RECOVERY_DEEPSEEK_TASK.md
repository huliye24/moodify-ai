# Moodify 本地工作区恢复与整理任务（交给 DeepSeek 执行）

> 执行位置：`E:\moodify`  
> 日期：2026-10-03  
> 执行者：DeepSeek / Claude Code 兼容 CLI  
> `CANON_CHANGE = NO`

## 0. 任务性质

这是一次**本地 Git 工作区恢复与分类整理**，不是产品重构，也不是功能开发。

Moodify Studio、CLI-First A/B Compare v0.1 和根目录 `artifacts/` 清理均已进入 GitHub `main`。不要重做、回滚或重新设计这些成果。

最终目标：

1. 本地工作区安全回到可理解、可复现、可继续开发的状态；
2. 未经人类明确授权的删除必须恢复；
3. 有价值的未跟踪源码不得丢失；
4. 缓存、虚拟环境、私有音频和生成物不得提交；
5. 每类变更单独处理、单独验证、单独提交；
6. 最终本地分支安全同步到最新 `origin/main`；
7. 输出完整证据报告，禁止只说“已清理”。

## 1. 必须先读的权威文件

开始操作前，完整阅读：

1. `AGENTS.md`
2. `docs/canon/CURRENT_CANON.md`
3. `docs/canon/PRODUCT_BOUNDARY.md`
4. `docs/canon/AUTHORITY_ORDER.md`
5. `docs/REPOSITORY_STATUS.md`

遵守 One Core, Multiple Interfaces。不得创建第二套 Core、DSP、状态机或公开产品身份。

## 2. 已知可靠基线

开始时重新验证，不要盲信下面的数字：

- 当前本地分支：`codex/professional-finishing-layer-20260920`
- 已进入远端 `main` 的 A/B 合并提交：`c4286189`
- 本地 A/B 工作提交已经是 `origin/main` 的祖先；不要重复提交 A/B 文件。
- 当前预计脏状态：
  - 717 个 tracked deletions；
  - 1 个 tracked modification：`ops/cloud_audit/la_vps_reality_audit.sh`；
  - 49 组 untracked entries；
  - 总计约 767 项状态记录。
- 717 个删除的大致分布：
  - `审查包/`：382 项；
  - `windows版本开发/`：330 项；
  - `工程经验层/`：5 项。
- 根目录 `artifacts/` 已被有意删除并加入 `.gitignore`，**不得恢复**。
- 已知 CI 中 `temporal-texture` 存在历史基线债务；不要为了让它变绿而删除规则、降低阈值或伪造基线。

## 3. 绝对禁止事项

禁止执行：

- `git reset --hard`
- `git clean -fd`、`git clean -fdx` 或任何面向仓库根目录的 clean
- `git checkout -- .`
- 对整个仓库执行无差别删除、覆盖或格式化
- 删除 `07Music/` 内的音频或用户素材
- 删除未跟踪源码，尤其是 `web 3.0/`、`docs/`、`moodify-core-package/` 下的内容
- 把 `.env`、密钥、私有音频、WAV、NPZ、数据库、虚拟环境或大型生成物提交到 Git
- 将 717 个缺失文件直接提交成删除
- 修改 Canon、产品身份或能力边界
- 强推 `main`
- 绕过受保护分支、跳过必要测试或隐藏失败
- 把不确定项擅自判为“垃圾”

如果出现无法判断的产品/资料归属，记录 `HUMAN_DECISION_REQUIRED`，但继续完成其他安全项目。

## 4. Phase A — 只读审计与恢复清单

先做只读审计，生成：

`docs/reports/2026-10-03_LOCAL_WORKSPACE_RECOVERY_REPORT.md`

报告至少记录：

- `git status --porcelain=v1` 分类计数；
- 当前 HEAD、分支、`origin/main`；
- `git merge-base --is-ancestor HEAD origin/main` 结果；
- tracked modification 的完整 diff 摘要；
- tracked deletions 按一级和二级目录统计；
- 每个 untracked 顶层项目的文件数、总大小、主要扩展名；
- 是否发现密钥、`.env`、音频、模型、数据库、构建产物；
- 每一类内容的处置建议和恢复路径。

报告中不要粘贴密钥值，只记录文件路径和风险类型。

## 5. Phase B — 恢复 717 个未经授权的 tracked deletions

这些删除不是本轮得到授权的仓库清理。`artifacts/` 才是已授权删除范围。

因此：

1. 只针对 `git diff --name-only --diff-filter=D` 返回的 tracked deletion 路径；
2. 确认其中不包含 `artifacts/`；
3. 使用精确 pathspec 从当前 `HEAD` 恢复工作树文件；
4. 不修改其他 modified/untracked 文件；
5. 恢复后验证 tracked deletion 数量为 0；
6. 不为“恢复到 HEAD”创建提交，因为这只是清除本地意外缺失。

如果删除列表中出现当前任务之外的新目录或 `artifacts/`，立即停止该子步骤并报告。

## 6. Phase C — 审查唯一 tracked modification

目标文件：

`ops/cloud_audit/la_vps_reality_audit.sh`

必须：

1. 阅读 diff 和相邻脚本；
2. 判断它属于：有效修复、临时调试、机器环境差异或无法判断；
3. 检查是否包含 IP、token、密码、私钥、主机名或其他敏感信息；
4. 若是明确、通用、无秘密的有效修复，运行相关 shell/static checks，并创建独立提交；
5. 若属于临时/本机内容，保存 patch 到仓库外的恢复目录后还原该文件；
6. 若无法判断，保持文件不变并写 `HUMAN_DECISION_REQUIRED`，不要混入其他提交。

仓库外恢复目录建议：

`E:\moodify-local-recovery\2026-10-03\`

该目录必须带 `MANIFEST.md`，记录原路径、大小、SHA-256、处置动作和恢复方法。

## 7. Phase D — 分类 49 组 untracked 内容

逐项分类，不得只看目录名。

### D1. 明确可再生的本机环境/缓存

重点检查：

- `.tmp/`
- `.venv-core/`
- `.venv-score/`
- Python/Node 缓存、build、dist、coverage、日志

动作：

1. 验证确实可再生；
2. 补充最小必要 `.gitignore` 规则；
3. 只删除已经核实的缓存或虚拟环境；
4. `.gitignore` 变更单独提交；
5. 不添加过宽规则，不能隐藏正常源码。

### D2. 私有音频或用户素材

重点检查：

- `07Music/`

动作：

- 不删除；
- 不提交；
- 检查是否应加入精确根目录忽略规则 `/07Music/`；
- 如需移动，只能移动到仓库外恢复目录，并写 manifest；
- 未得到额外人类指令时，优先“保留原位 + 精确忽略”。

### D3. 可能有价值的当前 Moodify 文件

重点检查：

- `docs/mood/`
- `docs/plan/2026-10-03_EVIDENCE_LOOP_PLAN_V01.md`
- `logo/moodify-horizontal.svg`
- `moodify-core-package/debug_ids.py`
- `moodify-core-package/debug_validation.py`
- `moodify-core-package/scripts/listen_demo_render.py`
- `moodify-core-package/test_basic.py`
- `start-moodify-studio.bat`

动作：

1. 阅读内容和引用关系；
2. 检查与 Canon、现有实现、现有测试是否重复或冲突；
3. 正式产品源码/文档：验证后按主题拆成小提交；
4. 临时 debug/test 文件：不要直接提交，移到仓库外恢复目录或删除可再生文件；
5. 启动脚本必须检查路径硬编码、安全性和实际启动结果；
6. 任何可能改变产品方向的文档标记 `HUMAN_DECISION_REQUIRED`。

### D4. 大型历史或旁支项目

重点检查：

- `web 3.0/`

动作：

1. 建立完整 inventory，包括嵌套 Git 仓库、Node 项目、数据库迁移、`.env.example` 和潜在秘密；
2. 判断是否属于当前 Moodify Sound Protocol 主线；
3. 不允许把整个目录一股脑提交到主仓库；
4. 默认将其视为“待归档/待人类裁决”，保留原位或可恢复地移动到仓库外恢复目录；
5. 若移动，必须先生成 SHA-256 manifest，并验证移动后文件数与哈希一致；
6. 未获得人类决定前，不永久删除。

## 8. Phase E — 提交纪律

允许的提交必须小而单一，例如：

1. `chore(repo): ignore local environments and private media`
2. `fix(ops): <明确说明 audit 脚本修复>`（仅当验证为有效修复）
3. `docs: <明确说明保留的当前文档>`
4. `chore(dev): add verified Studio launcher`（仅当实测通过）

每个提交前必须确认：

```powershell
git diff --cached --name-only
git diff --cached --check
```

不得提交：

- 仓库外恢复目录；
- 私有音频；
- 密钥和 `.env`；
- 虚拟环境、缓存、构建结果；
- 未经裁决的 `web 3.0/` 大型历史项目；
- 与该提交主题无关的文件。

## 9. Phase F — 验证与同步

完成安全整理后：

1. 运行受影响范围的 lint、语法检查和测试；
2. 至少运行 Moodify v0.1 测试集；
3. 若成本允许，运行全量 pytest；
4. 检查 Studio JavaScript 语法和合约检查；
5. `git fetch origin main`；
6. 在不覆盖任何未解决文件的前提下，使工作分支包含最新 `origin/main`；
7. 禁止强推 `main`；
8. 有需要提交的改动时创建新分支和 PR；
9. 等必要 CI 通过后再合并；
10. 最终本地应切到或明确对齐 `main`，且 `git status` 应为空；如果因 `HUMAN_DECISION_REQUIRED` 无法为空，必须逐项列出，不能声称完成。

## 10. 验收标准

任务只有满足以下条件才算完成：

- [ ] `artifacts/` 未恢复且仍被忽略；
- [ ] 717 个未经授权的 tracked deletions 已恢复，数量为 0；
- [ ] A/B v0.1 文件没有回滚或重复提交；
- [ ] `ops/cloud_audit/la_vps_reality_audit.sh` 已审查并有明确处置；
- [ ] 49 组 untracked 内容全部完成分类；
- [ ] 私有音频、秘密、虚拟环境、缓存未进入 Git；
- [ ] 有价值源码没有丢失；
- [ ] 所有移动/删除都有可恢复证据；
- [ ] 提交按主题拆分，未夹带无关文件；
- [ ] 相关测试通过；
- [ ] 最新 `origin/main` 已同步；
- [ ] 输出最终工作区状态和剩余人工决策；
- [ ] `CANON_CHANGE = NO`。

## 11. 最终报告格式

执行完成后，必须按以下结构回复：

1. **执行摘要**
2. **恢复了什么**
3. **删除了什么，以及为何可再生**
4. **移动/归档了什么，以及恢复路径**
5. **提交与 PR 列表**
6. **测试与 CI 准确结果**
7. **最终 `git status`**
8. **仓库外恢复目录与 manifest 路径**
9. **HUMAN_DECISION_REQUIRED**（没有则明确写“无”）
10. **CANON_CHANGE = NO**

## 12. 给执行 Agent 的最后提醒

本任务的优先级是：

```text
不丢数据 > 不泄露秘密 > 不污染 main > 工作区干净 > 减少文件数量
```

不要为了得到一个空的 `git status` 而删除无法判断的内容。先建立证据和恢复路径，再行动。
