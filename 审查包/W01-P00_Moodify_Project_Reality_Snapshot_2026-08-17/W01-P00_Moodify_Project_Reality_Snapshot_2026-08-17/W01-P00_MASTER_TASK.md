# W01-P00 — Moodify Project Reality Snapshot

**Wave:** Moodify Cognitive Wave 01  
**Package:** W01-P00  
**性质:** 只读调查 / Reality Snapshot / Pre-Distillation Baseline  
**日期:** 2026-08-17  
**执行对象:** Codex / 具备仓库与服务器只读权限的执行 Agent  
**前置依赖:** 无  
**后继任务:** W01-P01 Canonical Convergence  
**总原则:** 先获得现实，再改变现实。

---

## 0. 为什么这个任务必须先做

本任务不是开发任务，也不是“顺便整理仓库”的任务。

Moodify 进入下一阶段之前，首先需要回答一个比“下一步做什么”更基础的问题：

> **Moodify 此刻真实存在的系统到底是什么？**

在此前的连续开发中，项目已经形成多个同时存在但未完全对齐的现实层：

- GitHub `main`；
- 未合并 PR 与任务分支；
- 本地或历史任务包；
- Android 应用；
- 数据工厂与 worker；
- 多台云服务器；
- PolarDB；
- 即将/已经开通的 OSS；
- 第三方音频能力；
- 真实音频数据；
- 历史 Canon、README、AGENTS、架构文档；
- 最近发生变化但尚未进入仓库权威层的产品认知。

如果直接继续开发，Agent 会被迫反复回答：

- 哪个版本是真的？
- 哪条任务已经执行？
- 哪个服务真的在运行？
- 哪个数据库真的在用？
- 哪套状态机才是权威？
- 哪条产品定位已经失效？
- 哪个“已完成”其实只有文档，没有运行证据？

这些重复理解就是认知摩擦。

W01-P00 的目标不是解决这些问题，而是**第一次把所有事实放到同一张桌子上**。

---

# 1. 执行边界

## 1.1 本包是严格只读任务

执行期间 **禁止**：

- 修改任何仓库文件；
- 创建 commit；
- push；
- merge / close PR；
- checkout 后修改工作树；
- 删除、移动、重命名文件；
- 修改数据库；
- 新建数据库表；
- 写入 OSS；
- 安装或升级软件包；
- 重启服务；
- reload systemd；
- 修改防火墙、安全组、VPC、DNS；
- 修改环境变量；
- 修改 crontab；
- 修改 systemd unit；
- kill 进程；
- 启停容器；
- 清理磁盘；
- 修复发现的 bug；
- “顺手”做重构；
- 输出任何 API Key、数据库密码、私钥、Token、Cookie 或完整 Secret。

**如果发现问题，只记录，不修复。**

---

## 1.2 允许的动作

仅允许：

- `git status/log/branch/show/diff` 等只读 Git 操作；
- GitHub PR / branch / commit / CI 状态读取；
- `find` / `ls` / `stat` / `du` 等文件系统只读扫描；
- `uname` / `lscpu` / `free` / `df` / `ps` / `ss` 等系统读取；
- `systemctl status/list-units/cat` 等只读读取；
- Docker / Podman 的 `ps`, `inspect`, `images` 等只读命令；
- 数据库元数据只读查询；
- OSS bucket / object metadata 只读列举；
- 日志读取；
- 配置文件读取，但必须对 Secret 进行遮蔽；
- 对现有音频资产做文件级统计；不要生成新音频产物。

---

# 2. 本包的四个原子任务

## T00-1 — GitHub / Repository Reality Scan

回答：

1. 当前 `main` HEAD 是什么？
2. 当前 root `README.md`、`AGENTS.md`、架构文档声明的产品身份是什么？
3. 当前有哪些 open PR？
4. 哪些 PR/branch 包含尚未进入 `main` 的真实能力？
5. 当前 active code surface 是什么？
6. 当前测试、CI、部署脚本覆盖哪些部分？
7. 是否存在多个 orchestration / queue / state machine / API authority？
8. 哪些目录明显属于 legacy / experimental / generated / local-only？
9. 哪些“当前状态文档”已经明显落后于代码？
10. 哪些代码只存在于 PR，而 production 环境可能已经部署？

### 必须检查

- `README.md`
- `AGENTS.md`
- `docs/REPOSITORY_STATUS.md`
- `docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md`
- `docs/ASSET_MODEL.md`
- `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md`
- `moodify-core-package/`
- `apps/android/`
- cloud / runtime / worker / data-factory 相关目录
- `.github/workflows/`
- deployment scripts
- open PR
- recent branches / commits

### 已知起始锚点（仅供重新核验，不得直接当最终事实）

截至本任务包制作时的外部只读观察：

- GitHub `main` 最近观察到的 HEAD：`fa88b0b9c41df5a57a3683712a7df4e2341d8ca5`
- root `README.md` / `AGENTS.md` 仍以 **The Ear of AI / Auditory Intelligence System** 为权威身份
- 存在 open draft PR `#21`：
  - branch: `codex/mfy-data-factory-001`
  - observed head: `e66cbf9d92379998b7748992e425954bfb4ca1d1`
  - 包含 Phase-I auditory data factory、serial Aliyun worker node、Android aesthetic/system changes 等工作
- 以上信息必须由执行者再次核验；若不同，以扫描时现实为准

---

## T00-2 — Task / Work Package Reality Scan

目的：区分“写过任务书”与“能力已经存在”。

扫描所有可访问的：

- 历史任务包；
- repo 中 task docs；
- Codex branch；
- PR；
- acceptance report；
- deployment evidence；
- runtime evidence；
- test evidence。

每个任务必须映射到以下**唯一主状态**之一：

| 状态 | 含义 |
|---|---|
| `PLANNED_ONLY` | 只有计划/任务书，没有实现证据 |
| `IMPLEMENTED_NOT_MERGED` | 已实现，但未进入 canonical main |
| `MERGED_NOT_DEPLOYED` | 已进入 canonical code，但无部署证据 |
| `DEPLOYED_NOT_VERIFIED` | 已部署，但缺真实验收证据 |
| `VERIFIED` | 有可追溯运行/测试/人工或机器验收证据 |
| `OBSOLETE` | 已被后续决策或实现取代 |
| `BLOCKED` | 被权限、资源、依赖或人类权威阻塞 |
| `UNKNOWN` | 证据不足，不能判断 |

> 不允许使用“基本完成”“应该完成”“看起来有了”作为正式状态。

另增加辅助字段：

- `canonical_relevance`: CURRENT / LEGACY / EXPERIMENTAL / UNCLEAR
- `evidence_refs`
- `runtime_refs`
- `next_dependency`
- `conflict_with_current_direction`

---

## T00-3 — Cloud / Infrastructure Reality Scan

对所有真实节点分别扫描，不允许把不同机器的信息混在一起。

最低目标节点：

1. 杭州 ECS
2. 洛杉矶服务器
3. PolarDB MySQL
4. PolarDB PostgreSQL
5. OSS（如已开通）
6. 任何当前承担 Moodify 运行职责但未列出的节点

每台 Linux 节点至少记录：

- node alias
- provider
- region
- public/private IP（如报告将外发，可只保留网段或脱敏）
- OS / kernel
- CPU
- RAM
- swap
- disk / mount / free space
- uptime
- Docker / container runtime
- Python
- FFmpeg / ffprobe
- Git
- running services
- listening ports
- systemd units
- cron timers
- deployed repository path
- deployed git commit / dirty state
- API service
- worker service
- queue backend
- database endpoint role（不输出密码）
- object storage role
- log locations
- model / external tool dependencies
- current concurrency
- restart/recovery behavior
- known failure evidence

### 数据库必须回答

- 实例与地域
- 引擎与版本
- 当前 Moodify 实际连接的是哪一台
- 已存在数据库/Schema（仅名称）
- 已存在与 Moodify 有关的表（仅结构元数据）
- 当前连接方式
- 是否 production-used / test-only / unused
- 是否存在多个相互冲突的数据权威

### OSS 必须回答

若已开通：

- region
- bucket
- endpoint / access mode
- directory/object-prefix convention
- versioning / lifecycle status
- current Moodify objects count/size
- source/stem/render/evidence 是否已经存在实际对象
- 当前代码是否真正连接

若未开通：

- 状态写 `NOT_PROVISIONED`
- 不创建 bucket
- 不做配置

---

## T00-4 — Data Assets / External Capability Reality Scan

### A. 音频与 Evidence

必须回答：

- 真实歌曲总数（按可访问范围）
- 真实音频文件在哪里
- 是否有唯一 track identity / hash
- 哪些已经 analyze
- 哪些已经 stem
- 哪些已经 process
- 哪些有 before / after
- 哪些有人耳评价
- 哪些存在完整 Evidence
- 哪些适合作为 Golden Case 候选
- 是否存在重复文件、孤立产物、无法追溯来源的 output

禁止把私人音频内容或未经授权音频打包进报告。

### B. 外部能力

逐项核验当前真实状态：

- LALAL.AI
- Audiolla
- FFmpeg
- Demucs 或其他 stem 工具
- 现有 DSP / processing chain
- Android playback
- cloud API
- PolarDB
- OSS
- 任何其他外部服务

状态只能为：

`AVAILABLE_UNCONNECTED`  
`CONNECTED_UNTESTED`  
`CONNECTED_TESTED`  
`PRODUCTION_USED`  
`EXPERIMENTAL`  
`DEPRECATED`  
`UNAVAILABLE`  
`UNKNOWN`

---

# 3. Truth Table：本包最重要的产物

本包最终必须形成统一的 `MOODIFY_TRUTH_TABLE.md` 与 `MOODIFY_TRUTH_TABLE.csv`。

每一项能力占一行。

至少包含：

| Field | Meaning |
|---|---|
| `id` | 唯一编号 |
| `domain` | repo / cloud / data / app / external / task |
| `capability` | 能力或系统名称 |
| `claimed_state` | 文档/口头声称状态 |
| `observed_state` | 扫描观察状态 |
| `main_status` | PLANNED_ONLY 等主状态 |
| `canonical_relevance` | CURRENT / LEGACY / EXPERIMENTAL / UNCLEAR |
| `code_ref` | commit/branch/path |
| `runtime_ref` | node/service |
| `evidence_ref` | test/log/report |
| `authority_conflict` | 是否存在权威冲突 |
| `confidence` | HIGH / MEDIUM / LOW |
| `notes` | 简要事实说明 |

### 重要规则

**Truth Table 记录事实，不做架构决策。**

例如：

错误：
> PR #21 是旧方向，所以应该删除。

正确：
> PR #21 当前未合并；包含 X/Y/Z；其产品表述与当前人类口头方向存在潜在冲突；是否保留由 W01-P01 决定。

---

# 4. 最终必须输出的 8 份文件

执行完成后，在一个新的**报告目录**中生成（不要写回产品源代码；若 Codex 需要提交报告，必须先等待人类明确授权）：

1. `00_EXECUTIVE_REALITY_SUMMARY.md`  
   - 1–3 页
   - 只回答“当前真实系统是什么”

2. `01_GITHUB_REPOSITORY_REALITY.md`  
   - main / PR / branch / authority / tests / deployment code

3. `02_TASK_PACKAGE_REALITY.md`  
   - 所有已知任务的事实状态

4. `03_CLOUD_INFRASTRUCTURE_REALITY.md`  
   - 每台机器、数据库、OSS 的真实角色

5. `04_DATA_AND_EXTERNAL_CAPABILITIES.md`  
   - 音频资产与第三方能力

6. `05_MOODIFY_TRUTH_TABLE.md`
7. `05_MOODIFY_TRUTH_TABLE.csv`
8. `06_CONFLICTS_UNKNOWNS_AND_BLOCKERS.md`

额外建议：

9. `07_CURRENT_SYSTEM_MAP.mmd`  
   - Mermaid
   - 必须画“现实”，不是理想架构

10. `08_EVIDENCE_INDEX.md`
   - 所有重要结论对应证据路径

---

# 5. 现实系统图规则

系统图必须使用三类线：

- **实线**：真实存在且有证据
- **虚线**：存在但状态未验证
- **点线或明确标签**：计划中、未部署

必须区分：

- GitHub canonical code
- unmerged code
- deployed runtime
- database
- object storage
- external APIs
- Android
- data/evidence

不得把“应该有”画成“已经有”。

---

# 6. 证据优先级

当不同来源冲突时，按以下顺序判断“现实状态”：

1. 真实运行时读取
2. 可重现测试 / CI / health evidence
3. 当前部署 commit / binary identity
4. GitHub commit / PR / source code
5. 当前 canonical docs
6. 任务完成报告
7. 历史任务书
8. 对话中的计划和推测

注意：

- 低级来源可以说明“意图”
- 不能覆盖高级来源证明的“现实”

---

# 7. Secret 与隐私规则

必须自动遮蔽：

- API Key
- AccessKey
- SecretKey
- Bearer Token
- Cookie
- JWT
- SSH private key
- DB password
- full DSN with password
- signed URL query string
- private audio content

允许记录：

- 环境变量名称
- secret 是否存在
- credential source（env / file / secret manager）
- endpoint hostname
- database name
- table name
- bucket name（若报告仅内部）
- Secret 的末 4 位仅在确有必要时

原则：

> **证明配置存在，不泄漏配置内容。**

---

# 8. Stop Conditions

遇到以下情况立即停止对应扫描，并标记 `BLOCKED`：

- 需要写权限才能继续；
- 需要重启服务才能确认；
- 需要安装软件；
- 需要修改安全组；
- 需要获取或输出 Secret；
- 数据库账号只有写权限且无法保证只读；
- OSS 操作可能产生写入；
- 无法确认命令是否会改变系统；
- 扫描会显著影响 production workload。

---

# 9. W01-P00 的验收标准

只有同时满足以下条件，才能标记本包完成：

- [ ] GitHub main / open PR / active branches 已扫描
- [ ] Canonical docs 与真实代码状态已对照
- [ ] 历史任务已进入统一状态表
- [ ] 所有已知云节点已分别扫描
- [ ] PolarDB MySQL / PostgreSQL 已核验用途
- [ ] OSS 已核验为 PROVISIONED 或 NOT_PROVISIONED
- [ ] 外部音频服务已分类
- [ ] 真实音频资产与 Evidence 已统计
- [ ] Truth Table 已形成
- [ ] 所有未知项均明确写 UNKNOWN，不猜测
- [ ] 所有冲突已单独列出
- [ ] 没有执行任何修改
- [ ] 没有泄漏 Secret
- [ ] 当前现实系统图已形成
- [ ] 所有重要结论均能追溯到 Evidence Index

---

# 10. 本包明确不做什么

W01-P00 不决定：

- Moodify 最终产品定位；
- Ear 是否对外；
- README 如何重写；
- PR #21 是否合并；
- 哪台机器以后承担控制节点；
- 是否使用 MySQL 还是 PostgreSQL 作为最终权威库；
- OSS 目录最终怎样设计；
- 状态机最终有哪些状态；
- 是否保留某个 processing chain；
- Golden Song 选哪一首；
- Android 最终 UI；
- 哪些规则应进入 Canon。

这些属于后继任务。

---

# 11. 向 W01-P01 交接的唯一问题

W01-P00 完成后，不直接开始开发。

交给 W01-P01 的输入只有：

> **“这是 Moodify 现在真实存在的系统。哪些现实应该被保留为 Canon，哪些应该降级、迁移、废弃或重新解释？”**

W01-P01 才开始做权威收敛。

---

# 12. 最终执行口令

> 以只读方式执行 W01-P00。  
> 不修复、不部署、不重构、不合并。  
> 对 GitHub、历史任务、云节点、数据库、对象存储、音频资产和外部能力进行事实核验。  
> 所有结论必须附证据；无法确认的项目写 UNKNOWN。  
> 最终输出统一 Truth Table、现实系统图、冲突清单和 Evidence Index。  
> 完成后停止，等待人类审核，不进入 W01-P01。
