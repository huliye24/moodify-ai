# Production Topology — Phase I Freeze

**Document ID:** MFY-PRODUCTION-TOPOLOGY-001
**Version:** 1.0
**Date:** 2026-08-14
**Status:** LIVE — package MFY_PRODUCTION_OPERATIONS_OBSERVABILITY_001 (53)
**Owner:** Human product authority + ops (huliye24)

> **CLASSIFICATION (2026-08-14) — Per Constitution v2.0: the PUBLIC product topology is the official website → Moodify Music (`rongjinwenchuan.xyz`, Music BFF, PolarDB, media root). Moodify Ear API/worker, ProductionCase/Evidence storage, human review, Workbench and the Intervention Laboratory are INTERNAL production dependencies that stay release-blocking only where they affect Music playback. This document does not assert any deployment beyond what is recorded.**

## 1. 组件清单（owner / region / port / health / data authority / backup / rollback）

| 组件 | 位置/region | port | health | 数据权威 | 备份 | 回滚 |
|---|---|---|---|---|---|---|
| 官网静态 origin | LA 103.144.246.242（/var/www/rongjingmusic.com/current） | 80/443 | /healthz | 静态文件 | release 目录保留 | rollback_static_origin.sh（symlink 切换） |
| Ear API（FastAPI） | LA 103.144.246.242 | 8000 | /api/v1/health + queue | ProductionCase/测量契约 | case 目录 + review.sqlite3 | 旧版本 artifact 切换 + systemd restart |
| Ear worker/data node | LA 103.144.246.242（systemd moodify-worker） | — | queue 心跳（job age） | 队列（node.sqlite3） | metadata_backup + sqlite backup | 停止/恢复（幂等 resume） |
| Music BFF | LA 103.144.246.242（systemd moodify-music） | 8100 | /health（direct_db False） | 无（转发） | 无状态 | 旧 artifact 切换 |
| Music Data API | 杭州 120.55.191.146 | 8000 | /health | users/tracks/versions/bridge | PolarDB dump + 媒体清单 | forward-fix + restore |
| 数据库 | PolarDB（MySQL）cn-hangzhou | 3306 | 连接探测 | 唯一权威 | 一致性备份（53 §6） | restore + 校验 |
| 媒体根 | LA /opt/moodify/music-media/audio/ | 443（nginx alias） | Range 探测 | 不可变 asset+sha256 | 引用清单 + 对象复制 | 引用恢复，不删媒体 |
| Ear evidence/case | LA case 目录 | 8000 文件服务 | manifest 校验 | evidence manifest | case 目录备份 | 清单重建 |
| CDN/nginx | LA 103.144.246.242 | 80/443 | verify_origins.sh | — | 配置版本化 | nginx -t + reload |
| 域名/证书 | rongjingmusic.com / rongjingwenchuan.com / rongjinwenchuan.xyz | — | cloudflared 证书管理 | — | 证书备份 | manage_cert_dns.py 重签 |

## 2. 关键路径（真实代理链）

```text
浏览器 → nginx(LA, TLS) → [静态 /audio alias | /api/v1 → Ear API :8000 | /api/v1/music → BFF :8100]
BFF :8100 → Hangzhou :8000 /internal/v1/music（service key + request id）
杭州 :8000 → PolarDB（同一 VPC 对等；凭据阻塞中 → 临时直连已记录）
```

## 3. 缓存与私密策略

- 官网静态：`Cache-Control public, max-age=3600`（nginx）；版本化文件名。
- 私人 API：BFF 中间件强制 `no-store`（51 包实现）；PWA sw 不缓存 /api/*（33 包实现）。
- 音频：nginx alias + Range 206（49 包线上矩阵 5/5）；永不缓存截断为整文件。
- Ear case 响应：no-store；工作台代理同源（47 包 dev_proxy 形态 = 生产 nginx 同源形态）。

## 4. 构建与发布纪律

- 可重现构建：commit + lock hash + runtime 版本记录于 release 清单；
- 环境与 secrets 分离：`.env.example` 无真实值；secrets 仅服务器环境；
- 静态发布：原子 symlink 切换（deploy_static_origins.sh + rollback_static_origin.sh）；
- API/worker：版本化 artifact + 迁移前备份 + dry-run；
- 数据库 migration：先 dry-run、前后校验、不自动逆向破坏回退（forward-fix/restore 为主）；
- Android 签名密钥不进入仓库。

## 5. 已知缺口（53 上线前 owner 明确）

| 缺口 | owner | 缓解 |
|---|---|---|
| PolarDB 凭据/VPC 对等阻塞 | 51/53 | 临时直连已记录；对等后收敛 |
| 证书自动续期监控 | 53 | cloudflared 证书管理脚本 + 告警（见 ALERTS_AND_RUNBOOK） |
| 多实例 BFF 速率限制共享 | 53 | 单实例 Phase 1 可接受；多实例需共享存储 |
| 断点续传/分片上传 | 50 | V1 范围外，drafts resume 覆盖 |
