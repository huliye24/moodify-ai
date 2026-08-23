# 04 — Deployment Boundary

**规则:** P02 只设计并记录，不实际部署。artifact identity 以时间戳 release 目录为准（部署非 git，精确 commit UNKNOWN）。

## 服务部署表

| Service | Source repo/path | Deploy node | Runtime | Process manager | Config source | Log path class | Restart policy | Health check | Expected port | Artifact identity | Rollback unit | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nginx | —（系统配置） | LA | nginx | systemd | /etc/nginx | /var/log/nginx | on-failure | :80 HTTP | 80 | 配置 | 配置回滚 | current |
| cloudflared-moodify | —（Cloudflare） | LA | cloudflared | systemd | /root/.cloudflared/config.yml | journald | on-failure | 隧道状态 | 20241 | config.yml | 配置回滚 | current |
| moodify-api（Ear） | moodify-core-package/src/moodify/api | LA | Python 3.10 venv + uvicorn | systemd（user=moodify） | /etc/moodify/node.env | journald | on-failure | /healthz 127.0.0.1:8000 | 8000（loopback） | /opt/moodify/releases/<ts>/ | 时间戳目录切换 | current |
| moodify-music（vinext） | 未知（仓库无对应构建源） | LA | node v20（/opt/node22） | systemd | EnvironmentFile（systemd） | journald | on-failure | :3100 | 3100（loopback） | /opt/moodify/music/current | 时间戳目录切换 | current（来源 UNKNOWN） |
| moodify-music-bff | moodify-music-package/src/moodify_music/bff | LA | Python + uvicorn | systemd | /etc/moodify/music-bff.env | journald | on-failure | /api/v1/music/* | 8100（loopback） | /opt/moodify/music-bff | 目录切换 | current |
| moodify-worker | moodify-core-package（node 模块） | LA | Python venv + moodify-node | systemd | /etc/moodify/node.env | journald | on-failure | SQLite 队列存在 | — | /opt/moodify/current | 目录切换 | current |
| moodify-audiolla | psyb0t/audiolla 镜像 | LA | docker | docker（systemd docker） | 容器 env | docker logs | restart=unless-stopped | healthcheck healthy | 18080（loopback→8000） | 镜像 sha256 | 镜像回滚 | current |
| moodify-api（数据） | moodify-music-package（venv 内含 moodify.api） | 杭州 | Python 3.14 venv + uvicorn | systemd | /root/moodify-api.env + /root/moodify-app-db.env | journald | on-failure | /healthz 0.0.0.0:8000 | 8000（公网） | /opt/moodify-music | 目录切换 | current |
| moodify-data-worker | moodify-core-package | 杭州 | Python 3.14 venv + moodify-node | systemd（user=moodify） | /opt/moodify 部署内 | journald | on-failure | 队列/状态文件 | — | /opt/moodify | 目录切换 | current |
| 4 timers | moodify-core-package（ops/data_node） | 杭州 | systemd timer | systemd | unit 文件 | journald | timer 持续 | 每周期触发 | — | unit 文件 | unit 回滚 | current |
| PolarDB moodify_dev | — | 托管 | MySQL 8.0.18 | 阿里云托管 | 控制台 | 控制台 | 托管 | 控制台 | 私网 3306 | 实例 | 备份恢复 | current（schema-only） |
| OSS | — | 托管 | 对象存储 | — | — | — | — | — | — | — | — | **NOT_PROVISIONED（P03）** |

## 部署边界规则

1. **发布模式：** 时间戳 tar 目录 + systemd 软链切换（`/opt/moodify/current`、`releases/<ts>/`）。现状无 git/CI 集成 → 记录为技术债（P00 TT-028），本包不改。
2. **配置来源：** systemd EnvironmentFile + 服务器本机 env 文件；禁止 env 进 Git/报告。
3. **日志：** journald（LA/杭州）；无持久化策略（P00 技术债 #P3）→ 记录不改。
4. **重启策略：** 全部 on-failure（现状）；audiolla restart=unless-stopped。
5. **健康检查：** /healthz（Ear API 双节点验证过）；music-bff 路由存在；vinext :3100 无独立健康端点证据。
6. **回滚单元：** 目录切换（时间戳 releases）或 unit 配置回滚；无一键回滚流程（P00 黑箱调查 §20 确认）→ 记录不改。
7. **目标（P03+ 执行，本包只记）：** 部署工件带 commit 身份（git archive 或构建产物 sha256 manifest）；部署脚本纳入仓库 ops/。
