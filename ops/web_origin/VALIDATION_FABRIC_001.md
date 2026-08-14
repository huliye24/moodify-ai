# Cloud Resource & Validation Fabric — 设计文档

**Document ID:** MFY-VALIDATION-FABRIC-001
**Version:** 1.0
**Date:** 2026-08-14
**Status:** LIVE — package MFY_CLOUD_RESOURCE_AND_VALIDATION_FABRIC_001 (56)
**Executor:** DeepSeek（只读盘点；云端写操作需另行授权）

## 1. 资源矩阵

| Resource | Current fact（2026-08-14 只读探测） | Authority | Validation use | Access boundary | Backup | Rollback | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| Windows 本地开发机 | E:\moodify；Python 3.11/Node 22/AS JBR | 非权威 | LOCAL_DEV 测试、构建、静态检查 | 本地 | git | git | huliye24 | 可用 |
| LA 服务器 103.144.246.242 | nginx 80/443 + Ear API :8000 + BFF :8100 + worker；/healthz 200 | Ear 权威 + Music BFF | CANARY/PRODUCTION 代理链 | SSH root（~/.ssh/moodify_cloud） | backup_snapshot.sh | rollback_static_origin.sh | huliye24 | 在线 ✓ |
| LA 媒体根 /opt/moodify/music-media | Range 206（49 包 5/5） | 不可变 asset+sha256 | E2E 播放验证 | nginx alias | media-manifest.sha256 | 引用恢复 | huliye24 | 在线 ✓ |
| 杭州 ECS 120.55.191.146 | Music Data API :8000 /health 200（公网可达） | Music 数据权威 | CANARY/PRODUCTION 数据面 | service key（internal） | mysqldump（53 脚本） | forward-fix/restore | huliye24 | 在线 ✓ |
| PolarDB cn-hangzhou | 16 表 + auth_sessions + user_roles + evidence_bridge（XEngine 无 FK） | 唯一权威 DB | 迁移/备份/恢复演练 | VPC（对等阻塞中，R06） | mysqldump 待凭据 | restore + 校验 | huliye24 | **BLOCKED（凭据/VPC）** |
| cloudflared | 域名证书管理（manage_cert_dns.py） | 域名/证书 | 证书临期告警（A8） | 服务器 | 证书备份 | 重签 | huliye24 | 在线 ✓ |
| Ear cases/evidence | case 目录 + review.sqlite3 | Evidence manifest | 48/52 升级与桥验证 | 服务器本地 | backup_snapshot.sh | 清单重建 | huliye24 | 在线 ✓ |
| 域名 | rongjingmusic.com / rongjingwenchuan.com / rongjinwenchuan.xyz | 边界契约 | E2E 入口 | 公网 | DNS | DNS | huliye24 | 在线 ✓ |

## 2. 真实路径（2026-08-14 已验证）

```text
浏览器 ──https──▶ nginx(LA 103.144.246.242)
   ├─ /healthz           → 200 ✓
   ├─ /audio/*           → Range 206 ✓（媒体根 alias）
   ├─ /api/v1/*          → Ear API :8000 → 200 ✓
   └─ /api/v1/music/*    → BFF :8100 → 杭州 120.55.191.146:8000 /internal/v1/music → catalogue 200 ✓
杭州 :8000 ──▶ PolarDB（VPC 对等未就绪 → 临时直连已记录，R06）
```

## 3. 路径分类

| 路径 | 状态 | 说明 |
|---|---|---|
| 浏览器→nginx→Ear/Music | **CURRENT（通）** | 本包只读探测全 200 |
| BFF→杭州 internal | **CURRENT（通）** | service key 场景未注入（探测为匿名 read） |
| 杭州→PolarDB | **BLOCKED** | R06 凭据/VPC 对等；58 包解除 |
| 官网静态发布（current symlink） | CURRENT | 46 包静态站待发布（部署归 60/65） |
| Ear 工作台（apps/ear-workbench） | 待部署 | 47 包产物；随 60 部署 |

## 4. 57–65 执行环境分配

| 包 | 环境 | 用途 |
|---|---|---|
| 57 候选完整性 | LOCAL_DEV（本地 clean build）+ CLOUD_VALIDATION（云端干净环境） | 自包含候选重建 |
| 58 数据面 | CLOUD_VALIDATION（隔离库）→ PRODUCTION 冻结 | R06 解除 + 迁移/备份/恢复 |
| 59 安全隐私验收 | CANARY（真实代理链） | 身份/权限/隐私/缓存 |
| 60 产品 E2E | CANARY（用户入口开始） | 官网/Ear/Music/Creator/Bridge 闭环 |
| 61 可靠性/容量/DR | CLOUD_VALIDATION + CANARY | soak/故障注入/备份恢复/回滚 |
| 62 季度冻结 | PRODUCTION 发布纪律 | 版本节奏冻结 |
| 63 DeepSeek 独立验证 | 全部（独立复验） | 只找证据不足，不签 GO |
| 64 Codex 视觉终审 | CANARY 页面 + 视觉浏览器 | 审美/层级终审 |
| 65 Canary GO | CANARY → PRODUCTION | 人类签署 GO + 7 天稳定 |

**不得把 LOCAL/CLOUD_VALIDATION 的 PASS 写成 PRODUCTION PASS。**

## 5. 验证数据集

| 集 | 内容 | 用途 | 禁止 |
|---|---|---|---|
| 合成 fixture | 基准 wav（clipped/dual_tone/impulse/mono/pink_noise，192KB） | Ear 案例/升级/桥测试 | — |
| 公开 Music | cadeau10 专辑五曲（线上 LA） | 播放/Range/E2E | 重新编码 |
| 专用测试账号 | invite 制测试 user（51 包） | 身份/权限/创建者流程 | 生产用户数据 |
| 私人数据 | — | — | **禁止云端未经授权测试**（56 包禁止项） |

## 6. 资源隔离与命名

- 验证任务前缀：`validation/<包号>/`（case/evidence 目录）；不触碰生产权威 case。
- 数据库：58 包在隔离库（`moodify_validation`）执行迁移演练，不污染 `moodify_dev`。
- 命名：验证资产带 `val-` 前缀 + 日期戳，回收窗口 7 天。
- 上传临时文件：验证上传失败自动清理（既有 allocate/promote 语义）。

## 7. 资源预算（Phase I 季度）

| 项 | 预算 |
|---|---|
| 并发 worker | 1（既有 2C2G 单 worker，KEEP_2C2G 裁决） |
| 磁盘余量 | 媒体+证据 ≥3GB（worker 守卫） |
| 本地验证窗口 | 每包 ≤10min 全量回归 |
| 云端 soak | 61 包 ≥72h 连续观察 |
| 备份 RPO | 24h；恢复 RTO 目标 ≤4h（53 包定义） |
| 测试账号 | ≤5 个（invite 制） |

## 8. 事实边界

- 本包只读探测于 2026-08-14 执行；未写入任何云端资源。
- R06（PolarDB 凭据/VPC 对等）保持 BLOCKED，58 包解除。
- 凭据不得写入仓库/日志/交接（56 包禁止项）。
