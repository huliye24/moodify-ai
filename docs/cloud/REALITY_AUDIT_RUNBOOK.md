# Cloud Production Reality Audit Runbook

**状态:** INTERNAL ops runbook（不构成对外产品面）
**日期:** 2026-08-24
**任务阶段:** Cloud Production 001-A — Reality Audit（不是 Implementation 001）
**性质:** 只读云端现实扫描；**不实施任何云端生产系统**
**CANON_CHANGE:** NO
**执行状态:** 文档就绪；脚本就绪；报告骨架就绪；**等待 ops 在真实 ECS 上执行**

---

## 0. 这是什么 / 这不是什么

### 是什么

- **只读云端现实扫描** 的 ops runbook
- 验证 `CURRENT_ARCHITECTURE.md §1` 2026-08-17 快照是否仍然准确
- 为 `docs/cloud/CLOUD_EXECUTION_CHECKLIST.md §5` 9 项触发条件中的 1-3 项提供事实基础
- 为"是否进入 Cloud Production Implementation 001"提供 owner 决策依据

### 不是什么

- **不是** Cloud Production Implementation 001（不是"建设云"）
- **不是** database migration / API redesign
- **不是** moodify-qa / moodify-pulse 物理删除
- **不是** AI Audio Platform / API Platform / Enterprise Infrastructure 宣布

按 `CURRENT_ARCHITECTURE.md R6/R10`：

> 本文件只记录已由运行时证据支持的现状；理想架构不得写入。

按 `CURRENT_CANON.md §3 不变量 #4`：

> Canon 不虚构现实：云端/生产能力以 P00 现实快照与运行时证据为准，未验证不写成已运行。

→ **先测量,后建设**。本 runbook 只服务"测量"。

---

## 1. 路线图（用户已明确）

```
Phase 0  熵减                       ✅ 完成
Phase 1  云现实扫描                  ⬅ 下一步（当前 runbook 落地）
Phase 2  OSS + Storage Layer        等待 Phase 1 完成
Phase 3  Audio Asset Pipeline        等待 Phase 2 完成
Phase 4  Upload → Analyze → Report → Play  等待 Phase 3 完成
Phase 5  商业 Demo                  等待 Phase 4 完成
```

Phase 0 已完成的事（来自 `docs/reduction/REDUCTION_EXECUTION_001_REPORT.md` + `REDUCTION_EXECUTION_002_REPORT.md` + `MAINLINE_DECLARATION.md` + `Delta 报告`）：

- 冻结未授权 QA 产品化方向（STATUS 头）
- 建立 v1.0 主线边界（5 文件入口）
- 建立 Cloud Production INTERNAL entry
- 列出删除候选（owner 签字 + 30 天观测才可执行）
- 不引入第二产品身份

Phase 0 → Phase 1 的过渡：不是"建设"，是"测量"。

## 2. 当前文档树（Phase 0 状态）

```
docs/
├── canon/                              CANONICAL 第 3 级（不动）
├── brand/public/                       CANONICAL Public Brand 主题权威（不动）
├── STATUS.md                           v1.0 工作状态入口（其他 agent）
├── development/README.md               开发入口（其他 agent）
├── cloud/                              Cloud Production 入口
│   ├── README.md                       （其他 agent）
│   ├── CLOUD_PRODUCTION_V0.1.md        INTERNAL entry（Reduction Execution 001）
│   ├── CLOUD_EXECUTION_CHECKLIST.md    触发条件 9 项（Reduction Execution 001）
│   ├── ALIYUN_ECS_REALITY_REPORT_2026-08-24.md   ⬅ 本 runbook 产物（骨架）
│   └── REALITY_AUDIT_RUNBOOK.md        ⬅ 本文件
├── reduction/                          治理补强
└── (其他既有文件不动)

ops/
├── web_origin/                         既有 ops 模板（不动）
├── ear_batch/                          既有 ops 模板（不动）
├── data_node/                          既有 ops 模板（不动）
├── cloud_capabilities/                 既有 ops 模板（不动）
└── cloud_audit/                        ⬅ 新增（本次 runbook 产物）
    ├── aliyun_ecs_reality_audit.sh     只读审计脚本
    └── aliyun_ecs_reality_audit.README.md  使用说明
```

## 3. 任务书(原始 Codex 提示)

按用户原命令：

```text
# Moodify Cloud Production 001-A
# Alibaba ECS Reality Audit

目标:
  重新确认阿里云杭州 ECS 当前真实状态。

本任务为只读审计。

禁止:
  - 修改代码
  - 安装软件
  - 修改服务
  - 创建云资源
  - 删除文件
  - 修改数据库

[Step 1] 基础信息 (uname / os-release / hostname / uptime / lscpu / free / df)
[Step 2] 系统服务 (systemctl list-units --type=service --state=running)
[Step 3] Docker 环境 (docker ps -a / images / volume ls / network ls)
[Step 4] Moodify 目录扫描 (/opt /home /root /var/www /var/lib) + secrets 排除
[Step 5] 网络检查 (ss -tulpn)
[Step 6] 数据库状态 (只读; 不 migration / 不 create table / 不 delete)
[Step 7] 阿里云工具 (aliyun cli / ossutil; 不输出 AccessKey)
[Step 8] 生成报告 (docs/cloud/ALIYUN_ECS_REALITY_REPORT_2026-08-24.md)
```

## 4. 执行流程

```
1. ops 在目标 ECS 上运行 ops/cloud_audit/aliyun_ecs_reality_audit.sh
2. 脚本输出到 stdout (无副作用)
3. ops 把 stdout 复制到 docs/cloud/ALIYUN_ECS_REALITY_REPORT_2026-08-24.md
4. 移除任何意外 secret
5. 在 §11 Recommendation 回答 CLOUD_EXECUTION_CHECKLIST.md §5 触发条件
6. owner 签字
7. 提交到仓库
8. 根据触发条件满足度,决定是否进入 Phase 2 (OSS + Storage Layer)
```

## 5. 与现有 ops 模板的复用

本 runbook 不发明新模板,而是**复用既有**：

- `ops/web_origin/probe_resources.sh` (set -u + TS-prefixed line + 远程 curl probe) → 复用其 `set -u` + 显式 timestamp
- `ops/ear_batch/remote/remote_preflight.sh` (set -euo pipefail + check_command + 文件存在性) → 复用其 `command -v` 检查模式(但不强制失败,因为本审计是**只读**而非**部署**)
- `ops/web_origin/scan_secrets.sh` (PATTERNS + EXCLUDE) → 复用其 secret 排除模式,绝不打印

## 6. 安全约束

按 `ops/web_origin/scan_secrets.sh` 的 `PATTERNS` 列表:

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

本 runbook 配套审计脚本已避免触发这些 pattern。如发现意外泄露,立即停止 + 报告 owner。

## 7. 不做的事(再次声明)

- 不修改任何业务代码
- 不安装 / 启动 / 停止任何软件 / 服务
- 不创建 / 删除任何云资源
- 不修改任何数据库 schema
- 不打印任何 AccessKey / SecretKey / password / token / private key
- 不引入 QA Platform / AI Platform / Enterprise Infrastructure 命名(`PUBLIC_BRAND_CONSTITUTION.md §2.2` 禁单)
- 不把 Cloud Production 包装为对外产品面(`INTERNAL_SYSTEMS.md §2` 已是内部角色级)
- 不动 moodify-qa / moodify-qa-desktop / moodify-pulse 物理删除(需 owner + 30 天观测)
- 不实施 database migration / API redesign / product expansion
- 不修改 Canon(`docs/canon/*` / `docs/brand/public/*` / `AGENTS.md`)
- 不声明 Canon Change

## 8. 验收

按用户原命令验收标准:

```
✓ 必须: 零代码修改
✓ 必须: 零配置修改
✓ 必须: 零服务修改
✓ 必须: 生成真实云端报告 (docs/cloud/ALIYUN_ECS_REALITY_REPORT_2026-08-24.md)
✓ 不必须: 所有子系统齐全 (缺口本身是有价值的信息)
```

本 runbook 当前已满足全部"必须"项中的"不修改"(本 runbook 不修改任何业务代码 / 配置 / 服务)。"生成真实云端报告"项需要 ops 执行后才能满足,这是本 runbook 的下游任务。

## 9. 下一步

1. ops 在真实 ECS 上执行 `ops/cloud_audit/aliyun_ecs_reality_audit.sh`
2. 报告提交 + owner 签字
3. 满足 `docs/cloud/CLOUD_EXECUTION_CHECKLIST.md §5` 全部 9 项触发条件后, 才能进入 Cloud Production Implementation 001 实际代码 / 数据库 / API 修改
4. 当前**任一**触发条件均未满足,**不**进入实施

---

**Runbook 结束。等待 ops 在目标 ECS 上执行审计脚本。**