# Aliyun ECS Reality Report — 2026-08-24

**状态:** `[PENDING — REQUIRES LIVE EXECUTION BY OPS]`
**日期:** 2026-08-24
**对应任务:** Cloud Production 001-A — Alibaba ECS Reality Audit
**配套脚本:** `ops/cloud_audit/aliyun_ecs_reality_audit.sh`
**配套 runbook:** `ops/cloud_audit/aliyun_ecs_reality_audit.README.md`
**CANON_CHANGE:** NO
**执行状态:** **未运行**。Cursor / 自动 agent **不**拥有云端 SSH 访问能力。本文件是**骨架**,由 ops 工程师在真实 ECS 上执行审计脚本后填充。

---

## 0. 为什么本文件是骨架

按 `AGENTS.md §Agent Rules`：

> 不虚构云端/生产能力：未验证不写成已运行（Canon 与事实分离，R6/R10）。

按 `CURRENT_ARCHITECTURE.md` 顶部：

> 规则 R6/R10：本文件只记录已由运行时证据支持的现状；理想架构不得写入。

→ 本文件不写"假定的 ECS 状态"。所有 `[PENDING]` 区块由 ops 工程师执行 `ops/cloud_audit/aliyun_ecs_reality_audit.sh` 后,人工填充。

## 1. Target

```
target_label:        [PENDING — ops fill]
audit_ts:            [PENDING — ops fill]
target_kind:         [PENDING — 例: "Hangzhou Aliyun ECS 120.55.191.146"]
target_provider:     [PENDING — 例: "Alibaba Cloud ECS"]
audit_method:        SSH login as ops; bash aliyun_ecs_reality_audit.sh
auditor:             [PENDING — ops name + sign-off]
owner_signoff_ts:    [PENDING — human owner approval]
```

## 2. Server（来自 `aliyun_ecs_reality_audit.sh` Step 1）

```
uname -a:            [PENDING]
os_release:          [PENDING]
hostname:            [PENDING]
uptime:              [PENDING]
cpu_arch:            [PENDING]
cpu_count:           [PENDING]
memory:              [PENDING]
disk_root:           [PENDING]
disk_data:           [PENDING]
```

## 3. Running Services（来自 Step 2）

```
systemctl_running_total:  [PENDING]

关键服务:
  nginx:                  [PENDING — active / inactive / not-installed]
  docker:                 [PENDING]
  cloudflared:            [PENDING]
  mysql:                  [PENDING]
  postgres:               [PENDING]
  redis:                  [PENDING]
  moodify-api:            [PENDING — unit name / process / unknown]
  moodify-music:          [PENDING]
  moodify-worker:         [PENDING]
  moodify-data-worker:    [PENDING]
```

**对照 `CURRENT_ARCHITECTURE.md §1` 2026-08-17 快照：**

```
[ ] LA VPS 103.144.246.242 上运行的 nginx / cloudflared / moodify-api /
    moodify-music / moodify-music-bff / moodify-worker / audiolla
    → 仍是当前状态? YES / NO / 部分

[ ] 杭州 VPS 120.55.191.146 上运行的 moodify-api / moodify-data-worker /
    4 timers / /var/lib/moodify
    → 仍是当前状态? YES / NO / 部分
```

## 4. Docker（来自 Step 3）

```
docker_version:      [PENDING]
docker_containers:   [PENDING — list from `docker ps -a`]
docker_images:       [PENDING — list from `docker images`]
docker_volumes:      [PENDING]
docker_networks:     [PENDING]
```

**关键容器（如有）：**

```
moodify-audiolla:    [PENDING — running / stopped / not-present]
port 18080 → 8000:   [PENDING — exposed / not-exposed]
```

## 5. Storage（来自 Step 4 + Step 7）

```
local_moodify_dirs:
  /opt/moodify:          [PENDING — present / absent]
  /var/lib/moodify:      [PENDING — present / absent (历史 6.5GB SQLite)]
  /home/*/moodify:       [PENDING]

aliyun_oss:
  ossutil:               [PENDING — installed / not-installed]
  oss_buckets:           [PENDING — DO NOT print credentials]

s3_compatible:
  awscli:                [PENDING]
  configured_buckets:    [PENDING]

其他对象存储:
  [PENDING — minio / ceph / etc.]
```

## 6. Database（来自 Step 6）

```
mysql_version:        [PENDING]
psql_version:         [PENDING]
redis_version:        [PENDING]

local_sqlite_files:
  [PENDING — list from find, DO NOT open]

远端数据库连接性:
  PolarDB MySQL 8.0.13 (172.27.118.106):   [PENDING — connect / not-connect / auth-required]
  PolarDB MySQL 8.0.18 (172.27.118.104):   [PENDING]
  PolarDB PG 16.14     (101.133.107.206):   [PENDING]
```

> 安全约束：**不**打印数据库密码；**不**打开 / 复制 SQLite 文件；**不**输出 schema 内容。

## 7. Network（来自 Step 5）

```
ss -tulpn (top 40):
  [PENDING — process → port → protocol]

关键端口 loopback 可达性:
  port 80:     [PENDING — LISTENING / not-listening]
  port 443:    [PENDING]
  port 8000:   [PENDING — moodify-api?]
  port 8100:   [PENDING — moodify-music-bff?]
  port 3100:   [PENDING — moodify-music?]
  port 18080:  [PENDING — moodify-audiolla?]
```

## 8. Existing Moodify Components（汇总）

按 `INTERNAL_SYSTEMS.md §3-4` 4 state machine + 4 外部能力分类核对：

```
state machine authority:
  workflow_engine:           [PENDING — present / absent / state]
  node (moodify-node):       [PENDING]
  data_factory:              [PENDING]
  reconstruction_factory:    [PENDING]

外部能力:
  LALAL.AI / Audiolla:       [PENDING — CONNECTED_UNTESTED / DEPLOYED_NOT_VERIFIED / not-deployed]
  FFmpeg:                    [PENDING — DEPLOYED_NOT_VERIFIED / not-installed]
  Demucs:                    [PENDING — PLANNED_ONLY / not-installed]
  Basic Pitch:               [PENDING — IMPLEMENTED_NOT_MERGED / not-installed]
```

## 9. Missing Components（缺口清单）

按 `docs/STATUS.md §Cloud (Active — Build to READY)` 的缺口表核对：

```
OSS (Object Storage):             [PENDING — NOT_PROVISIONED / partial / provisioned]
PolarDB:                          [PENDING — BLOCKED / accessible / blocked-with-creds]
Worker / Queue:                   [PENDING — SQLite-near-empty / production-queue]
Cloud AI Inference (GPU):         [PENDING — none / partial]
Music data authority:             [PENDING — single SQLAlchemy / dual / unspecified]
State machine authority:          [PENDING — single / 4-split / other]
```

## 10. Risk Assessment

按 `MOODIFY_PRODUCT_AUDIT.md §7 DELETE 安全阀 6 项` + `CURRENT_ARCHITECTURE.md R6/R10`:

```
r1 — git grep / CI / systemd / nginx / Docker / 30 天日志均无调用: [PENDING]
r2 — owner 明确:                                          [PENDING]
r3 — 可替代路径有测试:                                    [PENDING]
r4 — 不改变 Canon / Job / data / evidence authority:      [PENDING]
r5 — 必要历史被 tag 或归档索引保存:                       [PENDING]
r6 — 回滚为 revert commit 或 release artifact:           [PENDING]
```

## 11. Recommendation

按 `docs/cloud/CLOUD_EXECUTION_CHECKLIST.md §5` 9 项触发条件,回答:

```
触发 1 (P00 重新核验 LA / 杭州 部署):
  [ ] PASS — 本审计独立验证了 CURRENT_ARCHITECTURE.md §1 2026-08-17 快照
  [ ] FAIL — 现实与快照不一致, 见 §3 + §8

触发 2 (PolarDB 核验):
  [ ] PASS — PolarDB 已解除 BLOCKED, 可访问, schema 可读
  [ ] FAIL — PolarDB 仍 BLOCKED, 见 §6
  [ ] N/A — 目标 ECS 不是 PolarDB 客户端 (LA VPS)

触发 3 (OSS / R2 / S3 选型):
  [ ] PASS — 人类 owner 已决策 (CD-011 后续)
  [ ] FAIL — 尚未决策, 见 §5
  [ ] DEFER — 选择延后到下一轮

触发 4 (Music data authority 单一化):
  [ ] PASS — `CANON_CHANGE = YES` 已声明 + CD-015 已决
  [ ] FAIL — 未声明 Canon Change, 见 §8

触发 5 (Worker / 队列 authority):
  [ ] PASS — CD-015 已决
  [ ] FAIL — 未决

触发 6 (owner 签字):                  [PENDING — human owner approval]
触发 7 (30 天观测):                   [PENDING — required before any DELETE]
触发 8 (可替代路径测试):              [PENDING]
触发 9 (回滚准备):                    [PENDING]
```

**最终结论:**

```
[ ] TRIGGER 1-9 全部 PASS — 可进入 Cloud Production Implementation 001
[ ] 部分 PASS — 进入下一轮补强 (见具体缺口)
[ ] 大部分 FAIL — 重新执行本审计 + 重新评估 Canon
```

## 12. Sign-off

```
auditor:          [PENDING — ops engineer]
auditor_signoff:  [PENDING — date + signature]

owner:            [PENDING — human owner name]
owner_signoff:    [PENDING — date + signature]

next_step:        [PENDING — Cloud Production Implementation 001 / 重新审计 / 退回 Phase 0]
```

---

## 附录 A:数据脱敏保证

本报告**绝不**包含：

- AccessKey / SecretKey / AKID 字符串
- 任何 SSH private key / RSA / EC / OPENSSH key block
- 数据库密码 / 任何 `password=` 后面的明文
- session secret / API token / bearer token
- 任何 `*.pem` / `*.key` / `*.crt` 文件内容

如发现意外泄露,立即删除该报告并重新执行审计,**不**写入 git。

## 附录 B:与现有 Canon 的核对

- `CURRENT_ARCHITECTURE.md §1` 2026-08-17 快照 — 本审计刷新该快照
- `INTERNAL_SYSTEMS.md §3` 4 state machine — 本审计 §8 核对
- `INTERNAL_SYSTEMS.md §4` 4 外部能力 — 本审计 §8 核对
- `MOODIFY_PRODUCT_AUDIT.md §7` DELETE 安全阀 6 项 — 本审计 §10 核对
- `docs/cloud/CLOUD_EXECUTION_CHECKLIST.md §5` 9 项触发条件 — 本审计 §11 回答
- `CURRENT_CANON.md §3 不变量 #4` "Canon 不虚构现实" — 本审计严格遵守
- `PUBLIC_BRAND_CONSTITUTION.md §2.2 禁单` — 本审计 §8 §11 不引入新命名

---

**报告骨架结束。等待 ops 在真实 ECS 上执行审计脚本后填充。**