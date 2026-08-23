# Moodify Cloud 黑箱现状调查 — 2026-08-17

> 只读调查。来源：洛杉矶服务器 + 杭州阿里云 ECS + PolarDB 三处真实扫描（2026-08-17 11:00-11:20 CST），配合仓库对照。
> 所有「实际状态」均来自扫描输出；未验证项明确标注 `UNVERIFIED`。

---

## 1. 真实云端拓扑

```text
Internet
   │
   ├── Cloudflare（DNS + 隧道代理）
   │     └── rongjingmusic.com / rongjingwenchuan.com → LA 隧道
   │
   ├── 洛杉矶 103.144.246.242（亿速云 Yisu，moodify-ear-runner）★核心节点
   │     ├── nginx :80（三域名反向代理）
   │     ├── cloudflared 隧道（:20241）
   │     ├── moodify-api（uvicorn :8000，Ear API）
   │     ├── moodify-music（node vinext :3100，Music Platform）
   │     ├── moodify-music-bff（uvicorn :8100，Music Public BFF）
   │     ├── moodify-worker（moodify-node worker，SQLite 队列）
   │     └── docker: moodify-audiolla（:18080→8000，lalal.ai 分离代理）
   │
   └── 杭州 120.55.191.146（阿里云 ECS，标准实例）
         ├── moodify-api（uvicorn 0.0.0.0:8000，公网，service-key 鉴权）
         ├── moodify-data-worker（moodify-node worker + 4 timers）
         └── → PolarDB 私网 172.27.118.x
               ├── PolarDB MySQL 8.0.13（172.27.118.106）—— 空，历史遗留
               ├── PolarDB MySQL 8.0.18（172.27.118.104）—— moodify_dev（19 表，数据极少）
               └── PolarDB PostgreSQL 16.14（公网 101.133.107.206:5432）—— 上海，在线，未确认内容
```

**回答：**
1. 真实运行中的云服务器：**2 台**（LA + 杭州）。PolarDB 3 个实例（2 MySQL + 1 PG）为托管数据库。
2. 每台：
   | 项 | LA 103.144.246.242 | 杭州 120.55.191.146 |
   |---|---|---|
   | 云厂商 | 亿速云 Yisu | 阿里云 |
   | 地区 | 洛杉矶 | cn-hangzhou |
   | CPU | 4 vCPU AMD EPYC 7H12 | 2 vCPU Intel Xeon |
   | RAM | 7.9GB（用 1.4GB） | 1.6GB（用 452MB） |
   | 磁盘 | 98GB（用 19GB） | 40GB（用 15GB） |
   | OS | Ubuntu 22.04 LTS | Ubuntu 26.04（kernel 7.0） |
   | 公网 | 103.144.246.242/24，仅公网 | 120.55.191.146 + 私网 172.21.10.9/20 |
   | 用途 | 官网/音乐平台/API/BFF/Ear worker/audiolla | 数据工厂 worker + 内部 API |
3. 核心节点：**洛杉矶**（官网、API、音乐、隧道入口都在这里）。
4. 官网=LA nginx+cloudflared；API=LA:8000 + 杭州:8000；音频任务=LA moodify-worker + audiolla 容器；数据库=PolarDB（杭州 VPC 私网）。
5. 我不知道的资产：**docker 容器（audiolla）**（记忆里曾记录「无 docker」，现已有）；**music-platform（node/vinext :3100）与 music-bff（:8100）**为新服务。无 Serverless/对象存储/CDN（除 Cloudflare 免费 DNS/隧道）。无其他机器。
6. GitHub 设想存在但云端不存在的节点：腾讯云三台（已删）；无 GPU 节点；PolarDB 旧实例实际为空（GitHub 记忆曾把它当目标实例）。

## 2. 服务器内运行盘点

### LA（103.144.246.242）

| 服务 | 用途 | 端口 | 启动方式 | 代码路径 | 数据路径 | 状态 |
|---|---|---|---|---|---|---|
| nginx | 反向代理 3 域名 | 80 | systemd | /etc/nginx | — | running |
| cloudflared-moodify | Cloudflare 隧道 | 20241 | systemd | /root/.cloudflared | — | running |
| moodify-api | Ear FastAPI | 127.0.0.1:8000 | systemd (user moodify) | /opt/moodify/current | /var/lib/moodify | running |
| moodify-music | Music Platform（node vinext） | 127.0.0.1:3100 | systemd | /opt/moodify/music/current | /opt/moodify/music-media | running |
| moodify-music-bff | Music Public BFF | 127.0.0.1:8100 | systemd | /opt/moodify/music-bff | — | running |
| moodify-worker | Ear unattended worker | — | systemd | /opt/moodify/current | /var/lib/moodify/node.sqlite3 | running（16KB，近空） |
| docker + moodify-audiolla | lalal.ai 分离代理 | 127.0.0.1:18080→8000 | systemd docker | /srv/moodify/audiolla/data | 容器卷 | running (healthy, Up 15h) |

无 Redis/Celery/supervisor/pm2/caddy。cron 无业务任务。内存 Top：audiolla python 770MB、node 123MB、dockerd 88MB、uvicorn 68MB。

### 杭州（120.55.191.146）

| 服务 | 用途 | 端口 | 启动方式 | 代码路径 | 数据路径 | 状态 |
|---|---|---|---|---|---|---|
| moodify-api | Moodify API（内部） | 0.0.0.0:8000（公网） | systemd | /opt/moodify-music/.venv (Py3.14) | — | running，service-key 鉴权 |
| moodify-data-worker | Data Factory worker | — | systemd (user moodify) | /opt/moodify/.venv | /var/lib/moodify | running |
| moodify-inbox-ingest.timer | 每 1 分钟 | — | systemd timer | — | /var/lib/moodify | enabled |
| moodify-resource-probe.timer | 每 5 分钟 | — | systemd timer | — | — | enabled |
| moodify-daily-report.timer | 00:05 | — | systemd timer | — | — | enabled |
| moodify-metadata-backup.timer | 00:20 | — | systemd timer | — | — | enabled |

公网开放：22、8000。3306/5432/443/6379 关闭。

## 3. 当前可执行的音频链路

**结论先行：云端当前没有「上传 → 处理 → 返回」的完整 Ear 链路在真实生产流量中运行。**

真实存在的链路（逐一验证）：

```text
LA 网站（rongjingmusic.com/rongjinwenchuan.xyz）
  → nginx → music-bff:8100 / music:3100
  → 静态音频文件（music-media/audio，248MB，5 个文件）
  → 浏览器播放
```

- 上传入口：无公开上传端点的生产证据（API 存在但 node.sqlite3 队列近空，16KB）。
- job/queue：SQLite（LA node.sqlite3 16KB；杭州 data_node 的 SQLite 有历史 pilot 数据）。
- audiolla 容器：lalal.ai 分离的本地代理（健康），属于「代码已部署」层级——分离请求须显式调用，无自动 pipeline 证据。

**真实案例**：无。当前唯一可完整无人干预的链路是「静态音乐网站播放」。

## 4. Moodify 当前听觉能力（云端）

| 能力 | 状态 |
|---|---|
| Signal（waveform/loudness/LUFS/峰值/RMS/动态范围/clipping/silence/stereo/phase/spectral/transient） | **代码存在（仓库，MAMSE 系列等）但未在云端生产链路运行** |
| Structure（BPM/beat/onset/key/section） | 同上 |
| Source（vocal/drum/bass/instrument 分离） | 部分代码存在（stems 模块）+ **audiolla 容器已部署（lalal API 代理，可运行但无自动 pipeline）** |
| Perception（harshness/muddiness/brightness 等） | 代码存在（auditory 模块），云端未接入 |
| Decision（自动判断是否处理/生成方案/preset/BYPASS） | 代码存在（干预实验室/预设系统），**云端无生产预设生成** |
| Verification（前后比较/改善判断/回滚/重处理） | 代码存在（算法评审器 MFY-ALGORITHMIC-REVIEW-001），云端未接入 |

**云端实际稳定运行的能力 = 网站托管 + 音乐文件播放 + 基础 API + 数据工厂批处理（杭州 worker，历史 pilot 数据）。**

## 5. Moodify Ear 真实存在程度

Ear 在仓库中是：文档 + Python 工具 + CLI + 数据结构 + 实验（MAMSE 系列 16 篇、干预实验室、evidence 系统）。
云端部署的 Ear 部分：**moodify-api（:8000）+ moodify-worker（SQLite 队列）** —— 部署但**无真实生产流量**（队列近空）。

六层真实状态：
- Listen：代码层完整（分析器/特征），云端未形成生产输入
- Represent：代码层完整（MAMSE/张量/描述符），云端未运行
- Judge：代码层（判定/算法评审），云端未接入
- Intervene：代码层（干预实验室/数据工厂），杭州 worker 有历史 pilot 批处理
- Verify：代码层，云端未接入
- Learn：**不存在**（无反馈闭环，见 §28）

**code exists ≠ system can actually hear。当前云端没有一个真实用户音频经过 Listen→Judge 链路。**

## 6. 云端真实模型

扫描结论：**云端当前没有任何 AI 模型文件/checkpoint 在推理。**
- 无 Demucs/Basic Pitch/ONNX/PyTorch/TF/HF cache 的运行进程（服务与进程列表无）。
- audiolla 容器是 **lalal.ai 云端 API 的本地代理**（psyb0t/audiolla 镜像），模型在 lalal 云端，不在本机。
- LA `/opt/moodify/capabilities` 有 basic-pitch 相关目录（工具代码，非模型推理进程证据）。
- 仓库内模型（bsroformer 权重等）**下载待办状态**（记忆：bsroformer 权重下载未完成）。

**明确回答：当前完全没有 AI inference 在生产运行。**

## 7. AI 与 DSP 边界

云端当前处理链（实际运行的）：
```text
FFmpeg          → 部署于杭州（8.0.1），未看到活跃音频转换任务
lalal.ai API    → 经 audiolla 容器代理（已部署，无自动调用证据）
数据工厂        → 杭州 worker 历史批处理（DSP 合成/处理，pilot 阶段）
预设/干预       → 仓库代码，云端未运行
```

**Moodify Cloud 目前主要是「静态音乐托管 + API 壳 + 数据工厂批处理」，真正的机器听觉成分（判断、感知缺陷检测、自动决策）没有进入生产。** 自动化脚本 ≠ AI。

## 8. 视觉依赖

- 云端与仓库均无基于封面/图片/MV/OCR/多模态模型的音乐判断（无此类模型、无此类代码路径证据）。
- spectrogram：仓库内是**数值输入/证据工具**（MAMSE 描述符），非视觉模型输入；云端未运行。
- 无流程读取歌名/歌手/专辑/metadata 影响声音处理决策（处理链决策基于音频测量）。
- **若只给 random-id.wav：当前云端实际能做的 = 存储 + 网站播放 + （若显式调用）audiolla 分离 + （杭州 worker）数据工厂批处理。Ear 判断链路不可用。**

## 9. 数据位置

| 数据 | 位置 | 状态 |
|---|---|---|
| 原始音频 | /root/moodify-ear-remote（LA，11MB，incoming） | 少量 |
| 播放音频 | /opt/moodify/music-media/audio（LA，248MB，5 文件） | 生产 |
| 音乐平台 releases | /opt/moodify/music/releases（LA，3.6GB） | 部署产物 |
| 分轨 | 无 | — |
| 处理中间文件 | /var/lib/moodify（杭州 6.5GB：data_factory*/fi_* 历史批处理） | 实验 |
| 输出音乐 | 同上（data_factory 产出） | 实验 |
| preset | 仓库代码；云端无生产 preset 数据 | — |
| analysis result | 仓库；云端无 | — |
| job state | SQLite：LA /var/lib/moodify/node.sqlite3（16KB）；杭州 data_node | 近空/历史 |
| 用户信息 | moodify_dev.users = 0 行 | 空 |
| logs | journald（LA/杭州） | 运行中 |
| 模型 | 无 | — |

## 10. PolarDB 真实角色

| 实例 | 地区/引擎 | 库 | 表 | 数据 | 生产使用 |
|---|---|---|---|---|---|
| pc-bp1112f8t24wdta5t (172.27.118.106) | 杭州 MySQL 8.0.13 | 无业务库 | 0 | 空 | **否（空壳）** |
| pc-bp19502y46246gv6n (172.27.118.104) | 杭州 MySQL 8.0.18 | moodify_dev | 19 表（XEngine） | tracks 32、track_versions 6、audit 10、idempotency 18、creation_passports 6；users/albums/playlists 等 0 | **有 schema 无流量（种子/演示级）** |
| pc-uf65m4xqwst72vq5a (101.133.107.206) | 上海 PG 16.14 | 未确认 | — | — | 在线未用（mylab3） |

- authority：**moodify_dev（新实例）是唯一业务库**，但数据量≈0。
- 旧实例为空 → 历史资源堆积确认。
- SQLite 仍在使用：LA worker 队列、杭州 data_node 状态（PolarDB 未接管队列）。

## 11. 对象存储

**无 OSS/S3/R2。** 所有音频在服务器磁盘（LA music-media 248MB + music releases 3.6GB；杭州 /var/lib/moodify 6.5GB）。磁盘总量：LA 19G/98G 用、杭州 15G/40G 用。

## 12. 队列系统

- **SQLite 自研队列**（moodify-node worker）：LA node.sqlite3（16KB，几乎无任务）、杭州 data_node（历史 pilot 10 曲全成功）。
- 无 Redis/Celery/RQ/cron 业务队列。
- 并发=1 worker/机；retry/timeout/失败处理 = 代码实现（节点守卫），生产无真实负载验证。
- **服务器重启：未完成任务的恢复逻辑存在（recover_interrupted_jobs，24x7 包验证过），但当前队列近空，无可恢复任务。**

## 13. 资源使用（扫描时刻）

| 指标 | LA | 杭州 |
|---|---|---|
| Load | 0.08 | 0.17 |
| RAM | 1.4G/7.9G | 452M/1.6G |
| 磁盘 | 19G/98G | 15G/40G |
| 典型音频处理峰值 | audiolla 容器 770MB（当前驻留） | 历史 10 曲 pilot 0 OOM（swap ~1GiB） |

## 14. CPU 能力边界（无 GPU）

- 杭州 2C/1.6GB 实测可跑完整曲目（10-song pilot 全 SUCCEEDED，0 OOM，swap ~1GiB）。
- Demucs 类分离：**未在本机测试**；audiolla 走云端 API。
- 同时两首：未实测；杭州 1.6GB 内存 + swap 是硬约束（LSM 结论：并行=1）。
- 推荐并发：**1**（杭州），LA 4C/8GB 可适度（未实测）。

## 15. 前 10 瓶颈（工程现实）

1. P0 无对象存储（音频全在本地磁盘，不可扩展）
2. P0 数据库空转（moodify_dev 无业务流量，schema 先行）
3. P1 云端无 AI 推理（无模型、无 serving）
4. P1 队列近空 → Ear worker 空转（部署了没活干）
5. P1 无反馈学习闭环
6. P2 杭州 1.6GB 内存硬限（并行=1，全量测试本地都吃力）
7. P2 部署为 tar 发布（无 git/CI，不可审计）
8. P2 旧 PolarDB 空实例 + 上海 PG 未用（资源堆积）
9. P3 无监控面板（journald 裸日志）
10. P3 无备份演练（只有杭州 metadata backup timer）

## 16. 最脆弱处

- 10 users：无问题（容量充裕）
- 100 users：**数据库无用户体系流量**（users=0），API 壳先暴露；LA 磁盘/带宽仍够
- 1000 songs：**磁盘与对象存储缺失**先告警（LA 98GB 盘、无 OSS）；分离任务走 lalal API（计费+限流）

## 17. 「看起来完成实际没有」

- README/记忆宣称的 16 表 → 实际 19 表，但**数据≈0**
- Ear worker 部署 → **队列近空，无真实任务**
- audiolla 分离 → **容器健康但无自动 pipeline 调用**
- 感知缺陷检测/自动 preset/身份干预 → **仓库代码，云端未运行**
- 「Moodify Cloud」名称 → **实际是 2 台 VPS + 3 个托管 DB，无完整产品闭环**

## 18. 技术债

- P0：无对象存储；DB 无业务数据
- P1：无模型 serving；Ear 链路未联通；部署不可复现（tar 手工）
- P2：旧 PolarDB 空实例；上海 PG 未用；无监控；env 散布 systemd 内联
- P3：journald 无持久化策略；无备份恢复演练

## 19. 安全结构（只读确认）

- SSH：LA 密钥登录（root）；杭州 root+密码（paramiko/密码）
- secrets：LA /etc/moodify/node.env（0644 非敏感）；杭州 systemd Environment 内联；PolarDB 凭据本地 0600（polardb_admin.env 等）
- DB：PolarDB 私网（杭州 VPC 对等），上海 PG 公网+白名单仅 120.55.191.146
- API：杭州 service-key 鉴权（401 无 key）；LA :8000 仅 127.0.0.1
- 上传：无生产上传端点
- HTTPS：Cloudflare 隧道终止（源站 HTTP）
- 风险结构：root 直接运行多数服务；无 fail2ban（LA）；无 rate limit 证据

## 20. 备份与灾难恢复

- 情况 A 磁盘损坏：LA 丢 3.6GB releases + 248MB 媒体 + 配置（GitHub 可重建大部分，媒体文件**不可重建**）；杭州丢 6.5GB 实验数据（**部分永久丢失**）
- 情况 B PolarDB 丢失：moodify_dev 数据≈0，损失小
- 情况 C 误删用户音乐：当前无用户音乐可删
- 情况 D 重建：代码 GitHub 可重建；tar 发布需重做；audiolla 容器需重拉镜像；**不存在一键重建流程**

## 21. 部署可复现性

**否。** 无 docker compose（除 audiolla 单容器）、无 CI、无部署脚本全流程。依赖 Codex 历史操作 + 手工 tar + 记忆中的 systemd 文件。

## 22. GitHub 与 Cloud 差异

- GitHub 有、Cloud 没有：GPU 节点、模型权重、Ear 分析管线运行、干预/预设/验证生产接入
- Cloud 有、GitHub 没有：audiolla 容器部署、music-platform/bff 生产实例、杭州 systemd env 配置、/var/lib/moodify 6.5GB 实验数据、PolarDB 实际 schema 状态
- 版本不一致：moodify-music 部署（20260813 时间戳 releases）；仓库与云端 music 版本漂移未验证
- 私有配置/脚本/数据：systemd env、polardb 凭据、fi_* 实验脚本、数据工厂历史产出

**若只看 GitHub，会高估：Ear 生产可用性；会低估：audiolla 已部署、music 平台已在 LA 运行。**

## 23. 真实 API

| Method | Path | 用途 | 认证 | 调用方 | 工作 |
|---|---|---|---|---|---|
| GET | /healthz（LA:8000、杭州:8000） | 健康 | 杭州需 service-key | 探针 | ✓ |
| GET | rongjinwenchuan.xyz/api/v1/music/* | Music BFF | — | 网站/App | ✓（BFF 在线） |
| — | LA:8000（Ear API） | 127.0.0.1 仅内网 | — | nginx/内部 | 在线，无外部流量证据 |
| — | 杭州:8000（内部数据 API） | service-key | LA BFF → 杭州 | ✓ | 在线 |

无生产 upload/job-create 流量的证据。

## 24. App 与云端连接

Android 3.1 播放器：本地文件 + 云端 URL 播放（resolveUrl）。**真实连接：App 可播放 LA 静态音频 URL；无用户账户、无上传、无处理等待闭环。**
App → Cloud → Process → Cloud → Play 闭环：**未形成**（处理侧无生产流量）。

## 25. 网站与 Cloud

官网（rongjingmusic.com 展示 + rongjinwenchuan.xyz Music 平台）与 API 同机（LA）。网站挂掉 → Music 平台与 BFF 同挂（同一台机器），但杭州 API/PolarDB 不受影响。

## 26. 每曲 preset 系统

- 数据结构：仓库有（v01_presets / 干预实验室）
- 云端：**无生产 preset 数据、无生成流水线**
- Song A→Preset A / Song C→BYPASS：仓库代码能力，云端未运行
- App 播放：不使用 preset

## 27. 外部服务接入

| 服务 | 状态 |
|---|---|
| Audiolla / LALAL.AI | **服务器已装（容器）+ 健康**；无自动 pipeline 调用 |
| Matchering | 仅讨论/代码（仓库） |
| Demucs | 仅仓库（权重未下载） |
| Basic Pitch | 仓库工具 + LA capabilities 目录；无运行证据 |

## 28. 反馈学习闭环

**不存在。** 无 skip/replay/choose 反馈采集，无训练数据累积。

## 29. 真实数据资产

- 真实歌曲：5 文件（LA music-media，248MB）
- 测试片段/处理 pair/stem/preset/AB/用户行为：**无云端数据**
- 失败案例：杭州 fi_*（失败注入实验）
- 数据工厂 pilot：杭州 6.5GB（10 曲历史批处理，实验级）
- 可用于训练：极少（pilot 批处理产物为主）

## 30. 最接近「Moodify 核心」的三样

1. **杭州数据工厂 worker + 6.5GB 批处理实验**（Sound→Measure 真实发生过）
2. **audiolla 容器（lalal 分离代理）**（唯一部署的「听/分离」外部能力）
3. **LA Ear API + worker 骨架**（可承载未来链路）

## 31. 删除 App 与网站后云端剩什么

`audio.wav → processed.wav / analysis.json / preset.json / evidence.json`：**不能**。
缺：上传/任务路由（无生产端点）、分析运行（无模型推理/无管线接入）、preset 生成（未部署）、evidence 输出（未接入）。只有 audiolla 分离 + 数据工厂批处理可达。

## 32. 现有硬件能力天花板（短期）

- 杭州 2C/1.6GB：单 worker 完整曲目 DSP/分析可行（pilot 验证），并行=1，swap 依赖
- LA 4C/8GB：可承载 API/worker 常驻 + audiolla 代理；Ear 分析可跑但不适合重载
- 无 GPU：神经网络推理（分离/embedding）不可行；**基于规则/信号分析的 Ear 全链路（Listen→Judge→Intervene→Verify）在 CPU 上可行**（仓库已验证 34.9s/全曲 MAMSE-001 等）

## 33. GPU 会解决 / 不会解决

- 会：source separation 推理、embedding、神经网络缺陷检测、生成式处理
- 不会：数据质量、评价体系、pipeline 联通、架构、反馈闭环、产品定义 —— **这些是当前真正的缺口，与 GPU 无关**

## 34. Current Cloud Truth

| 层 | 状态 | 真实能力 | 最大问题 |
|---|---|---|---|
| Compute | 2×VPS | 网站+API+worker 常驻 | 无 GPU |
| Storage | 本地磁盘 | 248MB 媒体+3.6GB releases+6.5GB 实验 | 无对象存储 |
| Database | PolarDB×2+PG×1 | moodify_dev 19 表 | 数据≈0 |
| Queue | SQLite 自研 | 单 worker | 近空 |
| Audio Analysis | 代码存在 | 仓库完整 | 云端未运行 |
| AI | 无 | — | 无模型无 serving |
| Separation | audiolla 容器 | lalal API 代理 | 无自动 pipeline |
| Judgment | 代码存在 | 算法评审器 | 云端未接入 |
| Processing | 数据工厂 | 杭州批处理 pilot | 实验级 |
| Preset | 代码存在 | — | 云端无 |
| Verification | 代码存在 | 算法评审 | 云端未接入 |
| Learning | 无 | — | 无闭环 |
| API | LA:8000/3100/8100 + 杭州:8000 | 健康 | 无生产流量 |
| Android | 3.1 | 本地+URL 播放 | 无上传/账户闭环 |
| Web | 2 站 + Music 平台 | 静态+播放 | 同机单点 |
| Security | 结构存在 | service-key/隧道/白名单 | root 直跑、无 fail2ban |
| Observability | journald | 裸日志 | 无面板 |
| Backup | 杭州 metadata timer | 元数据备份 | 无恢复演练 |

```text
CURRENT MOODIFY CLOUD = 两台北美/杭州 VPS 上运行的静态音乐网站 + API 壳 + 数据工厂批处理
                     + 一个已部署的健康 lalal 分离代理容器
                     + 一个 19 表但几乎无数据的 PolarDB 库
                     + 一个部署但队列近空的 Ear worker。
它还不是「能听」的系统：听、判、预、验的完整能力都只存在于仓库代码，
云端没有任何真实音频经过 Listen→Judge 链路。
```

## 35. 不可替代、值得继续积累的东西

**目前几乎没有云端独有资产不可替代** —— 若只保留 3 件：audiolla 容器部署（唯一部署的外部听音能力）、杭州数据工厂 6.5GB 历史批处理（唯一真实处理数据）、PolarDB schema（唯一结构化容器）。它们都小、都可重建。

**真正的积累缺口不在云端硬件，而在把仓库中已验证的听觉代码（MAMSE/干预/评审）接到真实音频链路上，并开始积累真实数据。**
