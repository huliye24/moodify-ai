# Aliyun ECS Reality Audit — Ops Runbook

**状态:** INTERNAL ops runbook（不构成对外产品面）
**日期:** 2026-08-24
**对应任务:** Cloud Production 001-A — Alibaba ECS Reality Audit
**配套脚本:** `ops/cloud_audit/aliyun_ecs_reality_audit.sh`
**目标报告:** `docs/cloud/ALIYUN_ECS_REALITY_REPORT_2026-08-24.md`
**CANON_CHANGE:** NO
**执行状态:** 脚本就绪；未运行（需要 ops 在真实 ECS 上运行）

---

## 0. 这是什么

这是 **Cloud Production 001-A** 的 ops 执行手册。任务是**只读**云端现实扫描，**不实施任何云端生产系统**。

按 `CURRENT_ARCHITECTURE.md R6/R10` "本文件只记录已由运行时证据支持的现状；理想架构不得写入"，本审计的目的正是为 v0.1 提供事实基础，而不是建设云。

## 1. 与 Canon / 既有治理文件的关系

| 文件 | 关系 |
|---|---|
| `docs/cloud/CLOUD_PRODUCTION_V0.1.md` | §2 Already Running 引用 `CURRENT_ARCHITECTURE.md §1`（2026-08-17 快照）。**本审计独立验证**该快照是否仍然准确。 |
| `docs/cloud/CLOUD_EXECUTION_CHECKLIST.md §5` | 9 项触发条件 全部要求"先核验"。本审计是触发条件 1-3 的事实基础。 |
| `docs/cloud/README.md` | Cloud Production 入口。本审计补充其 `Current Infrastructure` 表的实时数据。 |
| `docs/STATUS.md §Cloud (Active — Build to READY)` | 当前缺口列表。本审计回答缺口是否真实。 |
| `docs/reduction/REDUCTION_EXECUTION_001_REPORT.md` | 本次执行的上游。本审计是执行 Cloud Production Implementation 001 触发条件 1-3 的 ops runbook。 |
| `CURRENT_ARCHITECTURE.md §1` | 2026-08-17 P00 快照。本审计刷新该快照。 |
| `INTERNAL_SYSTEMS.md §4` | 外部能力分类（Audiolla / FFmpeg / Demucs / Basic Pitch）。本审计验证其当前状态。 |
| `ops/web_origin/probe_resources.sh` | 既有只读远程资源探测模式。本审计脚本复用其 `set -u` + TS-prefixed 输出风格。 |
| `ops/ear_batch/remote/remote_preflight.sh` | 既有远程 preflight 模板。本审计复用其 `check_command` 模式（只读 + 不阻塞）。 |
| `ops/web_origin/scan_secrets.sh` | 既有 secrets 排除模式（`PATTERNS` + `EXCLUDE`）。本审计**复用其 secret pattern**，永不打印。 |

## 2. 为什么先做这个

按用户原始意图：

> 现在不能做：
> - ❌ 删除 moodify-qa
> - ❌ 重构数据库
> - ❌ 直接设计 API 平台
> - ❌ 宣布 AI Audio Platform
>
> 因为这些都会重新增加熵。
>
> 因此给 Codex 的下一条命令应该调整一下。
> 不是 Cloud Production Implementation 001。
> 而是：Cloud Production 001-A：Alibaba ECS Reality Audit。
> 重新确认阿里云杭州 ECS 当前真实状态。

下一阶段真正目标是建立"upload → analyze → report → play" 闭环。但闭环之前，必须知道：

- ECS 有没有 Docker
- worker 是否运行
- 数据库有没有真实数据
- PolarDB 是否可用
- OSS 是否需要开通
- 哪个服务应该成为 authority

→ **先测量,后建设**。

## 3. 触发条件

按 `docs/cloud/CLOUD_EXECUTION_CHECKLIST.md §5` 9 项条件中的 1-3 项：

- **触发 1:** P00 重新核验当前 LA / 杭州部署 — 不是引用 2026-08-17 快照；登录云主机核验当前 listening / queue / worker 状态。
- **触发 2:** PolarDB 核验 — 当前 BLOCKED；必须先解除 BLOCKED 才能谈 schema。
- **触发 3:** OSS / R2 / S3 选型决策 — 人类 owner 决策 + `CANON_CHANGE = YES`（CD-011 后续）。

**触发 1 通过** = 本审计脚本在目标 ECS 运行成功 + 报告提交 + owner 签字。

## 4. 执行步骤（ops 视角）

### 4.1 准备

1. ops 工程师以 `ops` 身份 SSH 登录目标 ECS（杭州 120.55.191.146 / LA 103.144.246.242 / 或 owner 指定其他节点）。
2. 复制 `ops/cloud_audit/aliyun_ecs_reality_audit.sh` 到目标 ECS（scp 或 git pull 后取）。
3. 确认当前目录可读（无需可写）。

### 4.2 运行

```bash
# 在目标 ECS 上
bash aliyun_ecs_reality_audit.sh "$(hostname)"
# 或带自定义 label
bash aliyun_ecs_reality_audit.sh "hangzhou-prod-2026-08-24"
```

预期行为：

- 脚本**只**运行只读命令（`uname`, `cat`, `find`, `ss`, `docker ps`, `psql --version` 等）。
- 脚本**不**写任何文件（无 `>` 输出重定向，无 `tee`，无 `mysql ... CREATE`）。
- 脚本**不**打印任何 AccessKey / SecretKey / password / token / private key。
- 脚本**不**安装 / 删除任何软件。
- 脚本**不**启动 / 停止任何服务。
- 脚本退出码 = 0（即使某些子系统缺失）。

### 4.3 输出处理

脚本输出到 stdout。ops 工程师：

1. 复制 stdout 到 `docs/cloud/ALIYUN_ECS_REALITY_REPORT_2026-08-24.md`（手动替换 `[PENDING — REQUIRES LIVE EXECUTION BY OPS]` 占位）。
2. 移除任何意外出现的 secret / token / key（脚本已努力避免，但人工复核仍必要）。
3. 在 §11 Recommendation 中回答：

   ```
   Does this target ECS satisfy the Cloud Production Implementation 001
   triggers from docs/cloud/CLOUD_EXECUTION_CHECKLIST.md §5 ?
   - 触发 1 (P00 重新核验 LA / 杭州): YES / NO
   - 触发 2 (PolarDB 核验): YES / NO
   - 触发 3 (OSS / R2 / S3 选型): YES / NO
   - 其它 6 项 (data authority / state machine / owner / 30 天观测 / 测试 / 历史 / 回滚): 见 §11
   ```

4. 提交给 owner 签字。

## 5. 验收

按 Codex 任务书验收标准：

- 必须：零代码修改
- 必须：零配置修改
- 必须：零服务修改
- 必须：生成真实云端报告
- 不必须：所有子系统齐全（缺口本身是有价值的信息）

## 6. 安全约束

按 `ops/web_origin/scan_secrets.sh` 的 `PATTERNS` 列表：

```
PRIVATE KEY-----
AKIA[0-9A-Z]{16}
ghp_[A-Za-z0-9]{36}
sk-[A-Za-z0-9]{20,}
xox[baprs]-[A-Za-z0-9-]{10,}
MOODIFY_BFF_SESSION_SECRET=[^<$]
MOODIFY_INTERNAL_API_KEY=[^<$]
MOODIFY_HANGZHOU_KEY=[^<$]
MOODIFY_DB_PASSWORD=[^<$]
BEGIN (RSA|EC|OPENSSH) PRIVATE KEY
```

本审计脚本已避免触发这些 pattern。如发现意外泄露，立即停止运行 + 报告 owner。

## 7. 与既有 ops 模板对比

| 模板 | 模式 | 本审计复用 |
|---|---|---|
| `ops/web_origin/probe_resources.sh` | `set -u` + TS-prefixed line + 远程 curl probe | 复用 `set -u` + 显式 timestamp |
| `ops/ear_batch/remote/remote_preflight.sh` | `set -euo pipefail` + `check_command` + 文件存在性 | 复用 `command -v` 检查（不强制失败） |
| `ops/web_origin/scan_secrets.sh` | `PATTERNS` + `EXCLUDE` grep | 复用 secret pattern（环境变量 4 字符 preview + REDACTED） |
| `ops/web_origin/soak_probe.sh` | 时间序列 + `<minutes> <interval>` | 不复用（本审计是一次性） |
| `ops/web_origin/deploy_moodify_service.sh` | 部署 / 写操作 | **不**复用（本审计只读） |
| `ops/data_node/scripts/preflight_24x7.sh` | 24x7 数据节点 preflight | 可参考但不直接复用 |

## 8. 不做的事（再次声明）

- 不修改任何代码
- 不安装任何软件
- 不启动 / 停止任何服务
- 不创建 / 删除任何云资源
- 不修改任何数据库
- 不打印任何 AccessKey / SecretKey / password / token / private key
- 不引入 QA Platform / AI Platform / Enterprise Infrastructure 命名（`PUBLIC_BRAND_CONSTITUTION.md §2.2` 禁单）
- 不把 Cloud Production 包装为对外产品面（`INTERNAL_SYSTEMS.md §2` 已是内部角色级）
- 不动 moodify-qa / moodify-qa-desktop / moodify-pulse（物理删除需 owner + 30 天观测）
- 不实施 database migration / API redesign / product expansion

## 9. 下一步

1. ops 在真实 ECS 上运行脚本。
2. 报告提交 + owner 签字。
3. 满足 `CLOUD_EXECUTION_CHECKLIST.md §5` 全部 9 项触发条件后, 才能进入 Cloud Production Implementation 001 实际代码 / 数据库 / API 修改。
4. 当前**任一**触发条件均未满足,**不**进入实施。

---

**Runbook 结束。等待 ops 在目标 ECS 上执行审计脚本。**