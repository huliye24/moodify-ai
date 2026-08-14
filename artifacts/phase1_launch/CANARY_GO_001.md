# Phase I Canary / GO / Quarterly Stability — 执行清单

**Document ID:** MFY-CANARY-GO-001
**Version:** 1.0
**Date:** 2026-08-14
**Package:** MFY_PHASE1_CANARY_GO_QUARTERLY_STABILITY_001 (65)
**状态:** 准备就绪；**GO 待人类签署**；真机步骤待部署授权

## 1. 时间线

```text
T+0    launch（候选 MFY-PHASE1-RC-20260814-2 + 63 修复）
T+2h   first review（A1–A10 首查）
T+24h  enhanced observation complete
T+72h  early stability review
T+7d   Phase I closure → 90 天季度冻结（62）
T+30d  operational health review
T+90d  next quarterly release（1.1.0 规划）
```

## 2. 前置授权需求（执行前由人类提供）

| # | 需求 | 用途 |
|---|---|---|
| A | PolarDB 凭据注入方式 + VPC 对等/安全连接权限 | 解除 R06（58 步骤 2–3） |
| B | LA/杭州服务器部署执行授权 | 部署官网/工作台/Ear/BFF（60 顺序） |
| C | 专用测试身份（56 数据集） | E2E/安全矩阵 |
| D | 人类 GO 签署 | 唯一合法 GO（55/63 铁律） |
| E | Codex 视觉终审结论（64） | 上线前视觉复查 |

## 3. T+0 顺序

```text
1. 备份点确认（backup_snapshot.sh + PolarDB 快照）→ 58 流程
2. 部署：官网静态（deploy_static_origins.sh）→ 工作台 → Ear API/worker（deploy_moodify_service.sh）→ BFF/数据面
3. 内部 smoke（verify_origins.sh + 全链路 health）
4. canary（官网→Music 读路径→Ear 案例）
5. 60 E2E 场景执行 + 61 soak 启动（72h）
6. Codex 视觉复查（64 清单）
7. 人类签署 GO（GO_NO_GO_RECORD.md）
8. 扩大流量 + 24h 观察（A1–A10）
```

## 4. 观察与关闭标准

| 观察 | 标准 |
|---|---|
| A1–A10 触发记录 | 全部 ≤1 次 P0，且 runbook 处置成功 |
| soak 可用性 | ≥99.5% |
| 备份执行 | 每日 100% |
| 7d 关闭条件 | 无未处置 P0；残余风险有 owner（RISK_REGISTER） |

## 5. 本包前已具备（DeepSeek 侧）

- 63 独立验证：非视觉 P0 全过 + READY_FOR_VISUAL_REVIEW；
- 候选自包含（57）+ 数据面冻结（58）+ 安全计划（59）+ E2E 清单（60）+ 可靠性矩阵（61）+ 季度冻结（62）；
- 本地全量：core 639 + music 108 + 静态检查 5 套绿。

## 6. 事实边界

- 本清单不构成 GO；GO 只能由人类产品权威在 GO_NO_GO_RECORD.md 签署；
- 真机项（§2 A/B/C）未授权前保持 NOT_RUN；
- 若修复产生：走 62 变更政策（P0 紧急补丁 → 重跑受影响门 → 更新候选版本）。
