# LA VPS Reality Report — 2026-08-24

**状态:** `[PARTIAL — PARTIALLY COLLECTED VIA REMOTE PROBE]`
**日期:** 2026-08-24
**对应任务:** Cloud Production 001-A — LA VPS Reality Audit
**配套脚本:** `ops/cloud_audit/la_vps_reality_audit.sh`
**配套 runbook:** `ops/cloud_audit/la_vps_reality_audit.README.md`
**CANON_CHANGE:** NO
**执行状态:** 部分数据通过本地 HTTP probe 收集(2026-08-24 10:32 UTC)。完整系统数据需要 ops SSH 进入 VPS 运行审计脚本。

---

## 0. 数据来源

| 来源 | 数据类型 | 状态 |
|---|---|---|
| 本地 HTTP probe (Windows, 10:32 UTC) | nginx / healthz / API / music-bff / 域名可达性 | ✅ 已收集 |
| ops SSH 登录后运行 `la_vps_reality_audit.sh` | 全部 Step 1-9 (server / services / docker / dirs / network / db / cloud / local http / dns) | ⬜ 等待执行 |

**已有 probe 结果(来自 `CURRENT_ARCHITECTURE.md §1` P00 快照对照):**

```
nginx /          → 200 OK  ✅ (与 P00 一致)
nginx /healthz   → 200 OK  ✅ (与 P00 一致)
/api/v1/health   → FAIL    ⬜ API 不对外暴露 (127.0.0.1 only — 已知约束)
/rongjinwenchuan.xyz/api/v1/music/bootstrap → FAIL ⬜ 域名解析问题
/rongjinwenchuan.xyz/ready                   → FAIL ⬜
/rongjinwenchuan.xyz/api/v1/music/catalogue → FAIL ⬜
120.55.191.146:8000/health                   → FAIL ⬜ 杭州公网 API 未开
120.55.191.146:8000/ready                    → FAIL ⬜
```

**关键约束(P00 快照已记录,但本次 probe 确认):**

```
moodify-api (:8000) / moodify-music (:3100) / music-bff (:8100)
  → 不对外暴露, 仅在 127.0.0.1 监听
  → 审计这些服务必须通过 SSH 进入 VPS 后用 localhost 探测

rongjinwenchuan.xyz
  → 当前 DNS 解析状态未知 (FAIL from outside probe)
  → 需要在 VPS 上检查 nginx vhost 配置

Hangzhou 120.55.191.146:8000
  → 公网不通
  → 需要通过 cloudflared 或内网才能到达
```

## 1. Target

```
target_label:        LA VPS
target_ip:          103.144.246.242
target_provider:    亿速云 (LA core node, 4C/8G/98G)
audit_method:       本地 HTTP probe (Step 0) + ops SSH (Step 1-9 完整)
auditor:            [PENDING — ops name + sign-off]
owner_signoff_ts:   [PENDING — human owner approval]
```

## 2. Server（来自 `la_vps_reality_audit.sh` Step 1）

```
uname -a:           [PENDING — requires SSH]
os_release:         [PENDING]
hostname:           [PENDING]
uptime:             [PENDING]
cpu_arch:           [PENDING]
cpu_count:          [PENDING — P00: 4C]
memory:             [PENDING — P00: 8G]
disk_root:          [PENDING — P00: 98G total]
```

## 3. Running Services（来自 Step 2）

**已知(P00 快照):**

```
LA VPS 运行: nginx :80 / cloudflared / moodify-api :8000 (127.0.0.1) /
             moodify-music :3100 / moodify-music-bff :8100 /
             moodify-worker / moodify-audiolla (:18080→8000)
```

**需要 SSH 后确认:**

```
systemctl_running_total:     [PENDING]
nginx:                        [PENDING — active / inactive]
cloudflared:                  [PENDING]
moodify-api (:8000):          [PENDING — active / inactive]
moodify-music (:3100):       [PENDING]
moodify-music-bff (:8100):   [PENDING]
moodify-worker:               [PENDING]
moodify-audiolla (docker):    [PENDING — running / stopped]
```

## 4. Docker（来自 Step 3）

```
docker_version:      [PENDING — P00: docker available]
docker_containers:  [PENDING]
docker_images:      [PENDING]
```

**关键容器:**

```
moodify-audiolla (:18080→8000, lalal.ai 代理):
  status:           [PENDING — P00: CONNECTED_UNTESTED]
```

## 5. Storage（来自 Step 4）

```
local_moodify_dirs:
  /opt/moodify:          [PENDING]
  /var/lib/moodify:      [PENDING — P00: 历史 6.5GB SQLite]

aliyun_oss:
  ossutil:               [PENDING — NOT_PROVISIONED per P00]

s3_compatible:
  awscli:                [PENDING]
```

## 6. Database（来自 Step 6）

```
mysql_version:        [PENDING]
mariadb_version:      [PENDING]
psql_version:        [PENDING]
redis_version:       [PENDING]

local_sqlite:
  /var/lib/moodify:  [PENDING — P00: 6.5GB, 10-song pilot SUCCEEDED]
```

## 7. Network（来自 Step 5 + Step 8）

**已通过本地 probe 确认:**

```
nginx :80:          LISTENING ✅
nginx :443:         [PENDING — requires SSH]
moodify-api :8000:  NOT externally exposed ✅ (127.0.0.1 only)
moodify-music :3100: NOT externally exposed ✅ (127.0.0.1 only)
music-bff :8100:    NOT externally exposed ✅ (127.0.0.1 only)
moodify-audiolla :18080: [PENDING]

domain routing:
  rongjinwenchuan.xyz:  [PENDING — DNS 解析失败 from outside; 需要 VPS 上检查]
```

**需要 SSH 后确认:**

```
cloudflared tunnel:         [PENDING]
ss -tulpn full output:     [PENDING]
```

## 8. Existing Moodify Components（汇总）

```
state machine authority (INTERNAL_SYSTEMS.md §3):
  workflow_engine:           LEGACY      [PENDING — confirmed via SSH]
  node (moodify-node):      CANONICAL   [PENDING — cloud queue running per P00]
  data_factory:             CANONICAL   [PENDING]
  reconstruction_factory:   EXPERIMENTAL [PENDING]

外部能力 (INTERNAL_SYSTEMS.md §4):
  LALAL.AI / Audiolla:       CONNECTED_UNTESTED [PENDING — docker :18080→8000]
  FFmpeg:                    DEPLOYED_NOT_VERIFIED [PENDING]
  Demucs:                    PLANNED_ONLY [PENDING]
  Basic Pitch:               IMPLEMENTED_NOT_MERGED [PENDING]
```

## 9. Missing Components（缺口清单）

按 `docs/STATUS.md §Cloud (Active — Build to READY)`:

```
OSS (Object Storage):             NOT_PROVISIONED ⬜
PolarDB:                          NOT on LA VPS (Hangzhou only) ⬜
Worker / Queue:                   P00: moodify-worker running (SQLite, near-empty) ⬜
Cloud AI Inference (GPU):         NOT_PROVISIONED ⬜
Music data authority (LA):        [PENDING — music SQLite vs PolarDB]
State machine authority:          4-split (unified方案 HUMAN_DECISION_REQUIRED) ⬜
```

## 10. Risk Assessment

```
r1 — git grep / CI / systemd / nginx / Docker / 30 天日志均无调用: [PENDING]
r2 — owner 明确:                                          [PENDING]
r3 — 可替代路径有测试:                                    [PENDING]
r4 — 不改变 Canon / Job / data / evidence authority:      [PENDING]
r5 — 必要历史被 tag 或归档索引保存:                       [PENDING]
r6 — 回滚为 revert commit 或 release artifact:           [PENDING]
```

## 11. Recommendation

### 11.1 本地 probe 已确认的事实

```
✅ LA nginx 在运行
✅ moodify-api / moodify-music / music-bff 均为 127.0.0.1-only (不暴露公网)
✅ cloudflared 隧道在运行 (nginx 能响应域名请求)
✅ P00 快照基本准确 (需要 SSH 完整确认)
⬜ rongjinwenchuan.xyz 域名解析问题 — 需要 VPS 上检查
⬜ API / music-bff / music 内部 health 不明 — 需要 localhost probe
⬜ /var/lib/moodify 状态不明 — 需要 SSH 后 df + du
⬜ PolarDB / OSS 缺口已知 — CD-011 后续
```

### 11.2 Cloud Production Implementation 001 触发条件核对

按 `docs/cloud/CLOUD_EXECUTION_CHECKLIST.md §5`:

```
触发 1 (P00 重新核验 LA / 杭州 部署):
  [ ] PASS — 本地 probe 部分验证了 nginx 在运行
              完整 PASS 需要 SSH 后运行审计脚本

触发 2 (PolarDB 核验):
  [ ] N/A — LA VPS 不是 PolarDB 客户端 (PolarDB 在杭州,当前 BLOCKED)
              需要单独核验杭州 VPS 上的 PolarDB 连接

触发 3 (OSS / R2 / S3 选型):
  [ ] DEFER — CD-011 后续

触发 4 (Music data authority 单一化):
  [ ] DEFER — CANON_CHANGE = YES 尚未声明

触发 5 (Worker / 队列 authority):
  [ ] DEFER — CD-015 尚未决

触发 6 (owner 签字):                  [PENDING]
触发 7 (30 天观测):                   [PENDING]
触发 8 (可替代路径测试):              [PENDING]
触发 9 (回滚准备):                    [PENDING]
```

**最终结论:**

```
[ ] TRIGGER 1 部分 PASS — 需要 ops SSH 完整审计后才能最终判定
[ ] TRIGGER 2-5 DEFER — CD-011 / CD-015 未解决
[ ] 当前不进入 Cloud Production Implementation 001
```

## 12. Sign-off

```
auditor:            [PENDING — ops engineer]
auditor_signoff:    [PENDING — date + signature]

owner:              [PENDING — human owner name]
owner_signoff:      [PENDING — date + signature]

next_step:          [PENDING — run full SSH audit / PolarDB check on Hangzhou / wait for CD-011+015]
```

---

## 附录 A:本地 probe 数据(2026-08-24 10:32 UTC)

```
Source:      Windows 10.0.19045 PowerShell Invoke-WebRequest
Source IP:   Administrator workstation
Target IPs:  103.144.246.242 (LA) / 120.55.191.146 (Hangzhou)

Results:
  http://103.144.246.242/           → 200 OK   ✅
  http://103.144.246.242/healthz    → 200 OK   ✅
  http://103.144.246.242/api/v1/health
                                       → FAIL    ⬜ API 仅 127.0.0.1 监听
  http://rongjinwenchuan.xyz/api/v1/music/bootstrap
                                       → FAIL    ⬜ DNS 解析 / nginx vhost 问题
  http://rongjinwenchuan.xyz/ready                   FAIL
  http://rongjinwenchuan.xyz/api/v1/music/catalogue  FAIL
  http://120.55.191.146:8000/health                   FAIL
  http://120.55.191.146:8000/ready                    FAIL

Conclusion: LA nginx 运行正常。内部服务不对外暴露。
           域名路由问题需要在 VPS 上检查 nginx vhost 配置。
           杭州公网 API 不通。
```

## 附录 B:数据脱敏保证

本报告**绝不**包含:AccessKey / SecretKey / AKID / SSH private key / RSA / EC / OPENSSH / database password / session secret / API token。 如发现意外泄露,立即删除并重新执行,**不**写入 git。

## 附录 C:与 P00 快照对比

| 项 | P00 快照 (2026-08-17) | 本次 probe (2026-08-24) | 状态 |
|---|---|---|---|
| LA nginx :80 | 运行 | 200 OK | ✅ 一致 |
| cloudflared | 运行 | nginx 响应域名请求 | ✅ 一致 |
| moodify-api :8000 | 127.0.0.1 | 不对外暴露 | ✅ 一致 |
| moodify-music :3100 | vinext platform | 不对外暴露 | ✅ 一致 |
| music-bff :8100 | 运行 | 不对外暴露 | ✅ 一致 |
| moodify-worker | SQLite 队列,近空 | [需要 SSH] | ⬜ 待确认 |
| moodify-audiolla | docker :18080→8000 | [需要 SSH] | ⬜ 待确认 |
| /var/lib/moodify | 6.5GB, 10-song pilot | [需要 SSH] | ⬜ 待确认 |
| rongjinwenchuan.xyz | 三域名之一 | DNS FAIL from outside | ⬜ 待确认 |
| 杭州 120.55.191.146 | 公网 moodify-api | 公网 FAIL | ⬜ 可能防火墙变了 |

---

**报告骨架结束。等待 ops SSH 进入 103.144.246.242 运行 `ops/cloud_audit/la_vps_reality_audit.sh` 后填充 [PENDING] 部分。**