# 03 — Cloud / Infrastructure Reality

**扫描方式：** 只读 SSH（LA 用密钥 + 远端 `bash -s` 执行脚本；杭州用 paramiko 密码认证，密码经临时文件不落命令行，用后删除）。
**扫描时间：** 2026-08-17 19:52–20:05 CST。**只读保证：** 全部为允许清单内命令；无修改、无安装、无重启、无写库。
**交叉验证：** 同日 11:00 有独立黑箱调查（仓库根 MOODIFY_CLOUD_CURRENT_STATE_2026-08-17.json/.md），与本扫描一致。

---

## Node: LA（moodify-ear-runner / 亿速云 Yisu）

| 项 | 值 |
|---|---|
| Provider / Region | 亿速云 Yisu，洛杉矶 |
| Public IP | 103.144.246.242（仅公网） |
| OS / Kernel | Ubuntu 22.04.2 LTS / 5.15.0-69-generic |
| CPU | 4 vCPU（AMD EPYC 7H12，KVM） |
| RAM / Swap | 7.7 GiB（用 1.3G，可用 6.1G）/ 无 swap |
| Disk | /dev/sda3 98G（用 19G，76G 可用，20%） |
| Uptime | 5 天 10 小时（load 0.14） |
| Docker | Docker 29.1.3；1 容器：`moodify-audiolla`（psyb0t/audiolla，127.0.0.1:18080→8000，Up 24h healthy） |
| Python / Node | Python 3.10.12（系统）/ node v20.19.4（/opt/node22） |
| FFmpeg / Git | ffmpeg 4.4.2-0ubuntu22.04.1 / git 2.34.1 |
| Repo path | /opt/moodify（releases/ 时间戳目录，最新 20260816T080310Z、20260816T080724Z）+ /opt/moodify/music（vinext）+ /opt/moodify/music-bff + /srv/moodify（audiolla 数据）+ /root/moodify-ear-remote、/root/moodify-baseline-recovery、/root/moodify-ops |
| Deployed commit | **无 git 仓库**（tar 发布，不可对齐 commit）→ UNKNOWN |
| Running services | nginx(:80)、cloudflared-moodify（隧道）、moodify-api(:8000, Ear FastAPI, user=moodify)、moodify-music(:3100, node vinext, user=root)、moodify-music-bff(:8100, uvicorn moodify_music.bff)、moodify-worker（moodify-node worker, SQLite）、docker+audiolla |
| Listening ports | 22、80（公网）；3100、8000、8100、18080、20241（127.0.0.1）；3100 另有 node 服务 |
| Queue | SQLite（/var/lib/moodify/node.sqlite3 16KB，近空） |
| DB dependency | 无直接 DB 进程；通过 BFF/API 访问（PolarDB 为杭州侧） |
| Object storage | 无 |
| Concurrency | 1 worker/服务；audiolla 驻留内存 ~770MB |
| Recovery | 24x7 recover_interrupted_jobs 代码存在；队列近空无可恢复任务 |
| Timers/cron | 无 Moodify 业务定时器（仅系统默认） |
| 证据 | raw_scan/LA_103_144_246_242_scan.txt |

**角色：** 核心节点 —— 官网（nginx+cloudflared 隧道，rongjingmusic.com / rongjingwenchuan.xyz）、Music 平台、BFF、Ear API、Ear worker、audiolla 分离代理。

---

## Node: 杭州（Aliyun ECS / 标准实例）

| 项 | 值 |
|---|---|
| Provider / Region | 阿里云 ECS，cn-hangzhou（实例 i-bp1dkujhln9jrdhi9iv6） |
| Public / Private IP | 120.55.191.146 / 172.21.10.9/20（VPC vpc-bp1sty2c4ogudtqo68dro） |
| OS / Kernel | Ubuntu 26.04 LTS（kernel 7.0.0-28） |
| CPU | 2 vCPU Intel Xeon Platinum |
| RAM / Swap | 1.6 GiB（用 413M）/ 2.0 GiB（用 53M） |
| Disk | /dev/vda3 40G（用 15G，23G 可用） |
| Uptime | 7 天 6 小时（load 0.32） |
| Docker | 无 |
| Python / FFmpeg / Git | Python 3.14.4 / ffmpeg 8.0.1 / git 2.53.0 |
| Repo path | /opt/moodify（core package + .venv）、/opt/moodify-music（moodify-music 0.1.0）、/opt/moodify-clean-check（G6-03 干净环境）、/root/moodify-core-package、/root/moodify_runtime、/root/moodify-pre-24x7-backup |
| Deployed commit | **无 git 仓库** → UNKNOWN |
| Running services | moodify-api(:8000, 0.0.0.0 公网, service-key 鉴权, uvicorn moodify.api.main:app)、moodify-data-worker（moodify-node worker, user=moodify） |
| Timers | moodify-inbox-ingest（1min）、moodify-resource-probe（5min）、moodify-daily-report（00:05）、moodify-metadata-backup（00:20） |
| Listening ports | 22、8000（公网；3306/5432/443/6379 关闭） |
| Queue | SQLite（/var/lib/moodify：node.sqlite3、inbox、data_factory、data_factory_v2、fi_* 历史实验） |
| DB dependency | /root/moodify-app-db.env（含 MOODIFY_DB_PASSWORD 等；本扫描未核验端点） |
| Object storage | 无 |
| Concurrency | 1 worker（LSM 并行=1） |
| Recovery | 同 24x7（recover_interrupted_jobs） |
| 证据 | raw_scan/HZ_120_55_191_146_scan.txt |

**角色：** 数据工厂 worker 节点 + 内部 API（公网 service-key 鉴权）。历史 10 曲 pilot 全 SUCCEEDED（0 OOM，swap ~1GiB）。

---

## Database: PolarDB（3 实例）

| 实例 | 引擎/版本 | 位置 | 库 | 表 | 数据 | Production-used | 直接核验 |
|---|---|---|---|---|---|---|---|
| pc-bp1112f8t24wdta5t | MySQL 8.0.13 | 杭州私网 172.27.118.106 | 无业务库 | 0 | 空壳 | 否 | BLOCKED（凭据不符） |
| pc-bp19502y46246gv6n | MySQL 8.0.18（XEngine） | 杭州私网 172.27.118.104 | moodify_dev | 19 | tracks 32 / track_versions 6 / audit 10 / idempotency 18 / creation_passports 6；users/albums/playlists = 0 | 有 schema 无流量（种子/演示级） | BLOCKED（凭据不符） |
| pc-uf65m4xqwst72vq5a | PostgreSQL 16.14 | 上海公网 101.133.107.206:5432 | 未确认 | — | 在线未用 | 否 | BLOCKED |

- 本扫描对 172.27.118.104/106 以 app-db env 密码尝试 `SHOW DATABASES` → `Access denied`（root 凭据不符）。实例内容核验**被凭据阻塞**（任务书 Stop Condition）。
- 表/行数来自**同日 11:00 黑箱调查**（声称真实扫描）→ 置信度 MEDIUM，需 W01-P03 或人工复核。
- authority：moodify_dev 是唯一业务库（≈0 数据）；SQLite 仍承载队列与 worker 状态（PolarDB 未接管）。

---

## OSS

- **NOT_PROVISIONED。** 无 OSS/S3/R2 任何 bucket 或对象存储服务证据（本地代码、云端 env 名、黑箱调查一致）。
- 音频全部在服务器磁盘：LA music-media 248MB + music releases 3.6GB；杭州 /var/lib/moodify 6.5GB。

## 其他节点

- **腾讯云三台（139.199.186.106 / 43.134.12.248 / 43.156.175.4）：OBSOLETE —— 2026-08-12 用户确认已删除，不再纳入架构。**
- 无 GPU 节点；无 Serverless/CDN（除 Cloudflare DNS+隧道）。

## 已知故障证据

- CI Deploy workflow（tag v1.0.0-data-foundation）failure（2026-08-11）。
- PR #21 的 Temporal Texture Guard 持续 failure。
- 无其他运行时故障证据（journald 未深扫）。

## 报告外发脱敏

- IP/端口以事实记录；密码/Key/Token 一律不输出（黑箱调查亦已脱敏）。
