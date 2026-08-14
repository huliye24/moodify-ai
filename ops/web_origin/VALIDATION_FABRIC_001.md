# Cloud Resource & Validation Fabric — 设计文档（v1.1）

**Document ID:** MFY-VALIDATION-FABRIC-001
**Version:** 1.1（2026-08-14 更新：补全任务 3 完整字段；57–65 执行状态落地）
**Date:** 2026-08-14
**Status:** LIVE — package MFY_CLOUD_RESOURCE_AND_VALIDATION_FABRIC_001 (56)
**Executor:** DeepSeek（只读盘点；云端写操作需另行授权）

## 1. 资源矩阵（任务 3 全字段）

| Resource | 身份/区域 | Current fact（2026-08-14 只读） | 产品归属 | 权威数据 | 禁止数据 | 网络路径 | 运行方式 | 日志 | 备份 | 回滚 | Owner | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Windows 本地开发机 | dev / 本机 | E:\moodify；Py 3.11/Node 22/AS JBR | 全产品 | 无 | 无（仅构建） | 本地 | pytest/node/gradle | 测试输出 | git | git | huliye24 | 可用 |
| LA 服务器 103.144.246.242 | prod / LA | nginx 80/443 + Ear API :8000 + BFF :8100 + worker；/healthz 200 | Ear + Music BFF | Ear case/evidence、Music BFF 转发 | 私人音频、PolarDB 凭据 | SSH root（~/.ssh/moodify_cloud） | systemd（moodify-api/music/worker/cloudflared） | 脱敏（无 token/路径） | backup_snapshot.sh | rollback_static_origin.sh | huliye24 | 在线 ✓ |
| LA 媒体根 /opt/moodify/music-media | prod / LA | Range 206（49 包 5/5） | Music | 不可变 asset+sha256 | 重编码/覆盖 | nginx alias（/audio/） | nginx 静态 | 访问日志（无正文） | media-manifest.sha256 | 引用恢复 | huliye24 | 在线 ✓ |
| 杭州 ECS 120.55.191.146 | prod / cn-hangzhou | Music Data API :8000 /health 200 | Music | users/tracks/versions/bridge | Ear 内部测量 | 公网 :8000（internal service key） | systemd | 结构化（request_id） | mysqldump（53 脚本） | forward-fix/restore | huliye24 | 在线 ✓ |
| PolarDB cn-hangzhou | prod / cn-hangzhou | 16+4 表（XEngine 无 FK） | Music | 唯一权威 DB | 私人音频 | VPC（对等阻塞中，R06） | MySQL/PolarDB | 慢查询（脱敏） | mysqldump 待凭据 | restore + 校验 | huliye24 | **BLOCKED（凭据/VPC）** |
| cloudflared | prod / LA | manage_cert_dns.py | 域名/证书 | 证书 | 私钥明文 | 服务器本地 | systemd | 证书日志 | 证书备份 | 重签 | huliye24 | 在线 ✓ |
| Ear cases/evidence | prod / LA | case 目录 + review.sqlite3 | Ear | evidence manifest | 私人源音频 | 服务器本地 | worker（幂等） | 案例日志（脱敏） | backup_snapshot.sh | 清单重建 | huliye24 | 在线 ✓ |
| 域名 | 公网 | 三域名（music/ear/xyz） | 全产品 | 边界契约 | — | DNS | cloudflared/DNS | — | DNS | DNS | huliye24 | 在线 ✓ |

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
| 杭州→PolarDB | **BLOCKED** | R06；58 包已冻结解除计划（步骤 2–3 待人类授权） |
| 官网静态发布（current symlink） | 待发布 | 46 静态站完整（57/63 修复 HTML 后）；部署归 60/65 |
| Ear 工作台 | 待部署 | 47 产物完整（57 修复后）；随 60 部署 |

## 4. 57–65 执行状态（v1.1 更新，不再只是分配）

| 包 | 环境 | 状态（2026-08-14） |
|---|---|---|
| 57 候选完整性 | LOCAL_DEV → CLOUD_VALIDATION | **DONE_LOCAL**（29 文件纳入 + 双 P0 HTML 修复；干净环境可重建） |
| 58 数据面 | CLOUD_VALIDATION → PRODUCTION | **DONE_LOCAL**（冻结 + 约束测试）；云端 **BLOCKED_ON_AUTH**（凭据/VPC） |
| 59 安全验收 | CANARY | **DONE_LOCAL**（计划/runbook/扫描）；真机 **BLOCKED_ON_AUTH** |
| 60 产品 E2E | CANARY | **DONE_LOCAL**（清单/脚本）；真机 **BLOCKED_ON_AUTH** |
| 61 可靠性/容量/DR | CLOUD_VALIDATION + CANARY | **DONE_LOCAL**（soak 脚本/SLO/矩阵）；真机 **BLOCKED_ON_AUTH** |
| 62 季度冻结 | PRODUCTION 纪律 | **DONE**（v1.0.0 冻结文档） |
| 63 独立验证 | 全部 | **DONE**（干净环境全绿 + P0 修复 + READY_FOR_VISUAL_REVIEW） |
| 64 Codex 视觉终审 | CANARY 页面 + 视觉浏览器 | **BLOCKED_ON_CODEX**（证据包已备） |
| 65 Canary GO | CANARY → PRODUCTION | **BLOCKED_ON_AUTH + BLOCKED_ON_HUMAN**（授权 A–E + GO 签署） |

## 5. 验证数据集

| 集 | 内容 | 用途 | 禁止 |
|---|---|---|---|
| 合成 fixture | 基准 wav（clipped/dual_tone/impulse/mono/pink_noise，192KB） | Ear 案例/升级/桥测试 | — |
| 公开 Music | cadeau10 专辑五曲（线上 LA） | 播放/Range/E2E | 重新编码 |
| 专用测试账号 | invite 制测试 user（51 包） | 身份/权限/创建者流程 | 生产用户数据 |
| 私人数据 | — | — | **禁止云端未经授权测试**（56 禁止项） |

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
| 云端 soak | 61 包 ≥72h 连续观察（soak_probe.sh 已备） |
| 备份 RPO | 24h；恢复 RTO 目标 ≤4h（53/58 定义） |
| 测试账号 | ≤5 个（invite 制） |

## 8. 事实边界（v1.1）

- 本包只读探测于 2026-08-14 执行；未写入任何云端资源。
- R06 保持 BLOCKED（计划已冻结于 58）；凭据/VPC 授权待人类提供。
- 凭据不得写入仓库/日志/交接（56 禁止项）。
- 57–65 本地面已完成（63 独立验证确认）；剩余阻塞均为授权/Codex/人类签署类。
