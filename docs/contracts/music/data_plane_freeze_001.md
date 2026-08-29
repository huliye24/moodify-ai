# Production Data Plane Freeze — 2026-08-14 → 2026-11-14

**Document ID:** MFY-DATA-PLANE-FREEZE-001
**Version:** 1.0
**Date:** 2026-08-14
**Package:** MFY_PRODUCTION_DATA_PLANE_001 (58)
**Status:** FREEZE 文档生效；**R06 云端解除待授权**（凭据注入 + VPC 对等）

## 1. 权威数据平面（冻结三个月）

```text
浏览器 → LA BFF（direct_db=false，只转发）
BFF ──service key──▶ 杭州 Music Data API :8000 ──▶ PolarDB（VPC 对等，目标路径）
Ear worker/data node（独立权威，与 Music DB 永不合并）
媒体根（不可变 asset + SHA-256）｜ Ear case/evidence（独立权威）
```

- LA BFF 永不直连 PolarDB（现有 `direct_db: False` 契约保持）。
- 客户端永不直连 PolarDB（仅杭州 internal API 可达）。
- Music 与 Ear 数据库分离；证据桥只存外部引用（52 包）。

## 2. Schema / Migration Baseline

- 引擎：MySQL（PolarDB XEngine）；utf8mb4；UTC（连接强制 time_zone=+00:00）。
- 16+ 表基线（DATA_FOUNDATION-001-REV2）+ auth_sessions + user_roles + evidence_bridge（51/52 增量）。
- migration 规则：dry-run 先行 → 前后校验 → 不自动逆向破坏回退（forward-fix/restore）。
- **XEngine 无 FK**：所有关键关系由应用层守卫（下表测试对应）。

| 关键关系 | 应用层守卫 | 测试 |
|---|---|---|
| Creator ↔ User | require_actor_matches + ensure-user 幂等 | 51 test_identity、50 test_creator_publishing |
| Track ↔ Creator | _require_owner（tracks 路由） | test_console 越权、50 IDOR |
| TrackVersion ↔ Track | version 创建 ownership 检查 | test_lifecycle |
| EvidenceBridge ↔ Track/User | require_actor_matches + request_key 唯一 | 52 test_evidence_bridge |
| review_tasks ↔ case | 外部引用 + 审计（Ear 侧） | 48 test_authority |

## 3. RPO / RTO（58 定义，真机实测归 61）

| 项 | 目标 |
|---|---|
| RPO | 24h（backup_snapshot.sh 每日；PolarDB 快照待真机） |
| RTO | ≤4h（隔离恢复 + 对账） |
| 备份内容 | PolarDB dump/snapshot + 媒体引用清单 + Ear case/evidence 清单 |

## 4. 紧急变更流程（三个月内）

1. 禁止：无治理新功能、破坏性 schema、状态机与指标语义漂移、合并 Music/Ear 数据；
2. 允许：P0 安全/数据/核心阻断修复（版本 1.0.x）；
3. 任何 schema 变更：备份先行 + dry-run + 前后校验 + 应用层约束测试重跑；
4. 破坏性变更（改列/删表/语义漂移）→ 紧急变更流程（人类产品权威批准）或推迟下一季度（62 包节奏）。

## 5. R06 解除执行计划（待人类授权后执行）

| 步骤 | 动作 | 授权需求 |
|---|---|---|
| 1 | 只读核对 LA/杭州/PolarDB 网络、VPC、安全组、DNS、端口 | 只读 SSH 访问 |
| 2 | VPC 对等或等价安全连接（杭州 ECS ↔ PolarDB VPC） | **云网络操作权限** |
| 3 | 凭据注入正式 secret/env 机制（不落 Git/日志/交接） | **凭据提供（注入方式）** |
| 4 | 关闭临时直连，验证日志不回显 | 服务器操作 |
| 5 | BFF→Data API→PolarDB health/read/write（专用测试账号 + 可回收数据） | 写授权（验证数据） |
| 6 | migration dry-run → 升级 → 完整性检查 → 并发写测试 | 服务器操作 |
| 7 | PolarDB 备份 → 隔离恢复 → entity/ID/hash 对账零漂移 | 服务器操作 |
| 8 | RPO/RTO 实测记录 | 服务器操作 |

**阻塞项：步骤 2（VPC 对等）与步骤 3（凭据注入）需要人类提供批准与凭据注入方式。**

## 6. 事实边界

- 本文件冻结数据面纪律；云端执行未开始（无凭据/无网络操作授权）。
- 本地已具备：幂等/超时防重复测试（51/50/52）、应用层约束测试（本包补充）、备份脚本与本地恢复演练（53）。
- 输出状态：`READY_FOR_DATA_PLANE_REVIEW`（待 Codex 检查点）——数据权威分离确认、三个月兼容承诺已定义、技术 PASS 未扩大为产品 GO。
