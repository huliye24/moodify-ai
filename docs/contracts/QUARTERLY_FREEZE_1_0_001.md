# Quarterly Release Freeze — v1.0.0（2026-08-14 → 2026-11-14）

**Document ID:** MFY-QUARTERLY-FREEZE-001
**Version:** 1.0
**Date:** 2026-08-14
**Package:** MFY_QUARTERLY_RELEASE_FREEZE_001 (62)
**Candidate:** MFY-PHASE1-RC-20260814-2（57 包修正后基线）

## 1. 版本节奏

```text
1.0.0  季度正式版本（本冻结基线）
1.0.1  P0 安全/数据/核心阻断修复
1.0.2  必要兼容修复
1.1.0  下一季度功能版本（2026-11-14 后）
```

## 2. 冻结契约索引（12 类）

| # | 冻结面 | 权威位置 | 版本 |
|---|---|---|---|
| 1 | API namespace/错误码/幂等 | docs/contracts/music/music_public_api.md + 各路由 | FROZEN |
| 2 | DB schema/migration/权威 ID | data_plane_freeze_001.md（58）+ models.py | FREEZE |
| 3 | Ear 测量 profile/规则/判断范围 | authority/scope_contract.py + MAMSE 系列 | FREEZE |
| 4 | Music Track/Version/Passport/发布生命周期 | publication_state.md + routes | FROZEN |
| 5 | Bridge 状态/publish-safe | routes_bridge.py（52） | FREEZE |
| 6 | Design tokens/组件状态语义 | design_tokens_v1.md（45） | APPROVED |
| 7 | 官网/Ear/Music 路由与 CTA | 46/47/49 包 | FREEZE |
| 8 | Web/Android 最低兼容 | music-web Node 22 / Android minSdk 26 | FREEZE |
| 9 | 环境变量名/配置格式/systemd/nginx 接口 | ops/web_origin（57 纳入候选） | FREEZE |
| 10 | 备份/恢复/manifest/artifact 格式 | backup_snapshot.sh + release manifest | FREEZE |
| 11 | 公开 claim 与成熟度标签 | TERMINOLOGY_AND_CLAIMS.md（44） | APPROVED |
| 12 | SLO/告警/支持边界 | reliability_capacity_dr_001.md（61） | FREEZE |

## 3. 变更政策

| Change | 季度政策 |
|---|---|
| P0 安全/数据损坏 | 允许紧急补丁（1.0.1，紧急流程 §5） |
| 核心旅程阻断 | 补丁前重跑全部受影响门（1.0.2） |
| 文案笔误（不改变 claim） | 受控补丁 |
| 视觉打磨 | 默认下季度 |
| 新功能 | 下季度（1.1.0） |
| 破坏性 schema/state/API | **禁止** |
| 指标/规则语义变更 | 新版本 + 数据分离（不覆写） |
| 公开 claim 成熟度升级 | 新证据 + 人类批准 |

## 4. 兼容矩阵（Web/Android/服务）

| 面 | 兼容基线 |
|---|---|
| music-web | Node ≥22.13；无浏览器版本硬依赖（PWA 特性渐进） |
| Android（Ear 客户端） | minSdk 26 / targetSdk 36 |
| music-android | EXPERIMENTAL 壳（不承诺兼容，明确标注） |
| BFF ↔ 杭州 API | /internal/v1/music 契约 FROZEN |
| Ear API | /api/v1/auditory/* 契约 FREEZE |

## 5. 紧急变更流程（季度内）

1. 判定为 P0 安全/数据损坏/核心阻断 → 走紧急流程；
2. 记录影响 + 修复设计（含数据迁移/回滚）；人类产品权威批准；
3. 备份先行 + dry-run + 前后校验 + 应用层约束测试重跑（58 纪律）；
4. 修复后重跑受影响门（core/music/静态检查 + 专项）；
5. 版本 1.0.x，release notes 更新，冻结契约索引同步。

## 6. Deprecation 政策

- 弃用面必须有：公告期（≥1 个补丁版本）、迁移路径、回滚；
- 季度内不弃用任何 FROZEN 契约；弃用决策归 1.1.0 规划。

## 7. 支持/错误目录

- 错误模型统一 `{error:{code,message,request_id}}`（51/52 契约）；
- 支持边界：身份越权/数据泄漏/发布异常走安全事件 runbook（59 R-SEC1–4）；
- 一般故障走 A1–A10 告警 + R1–R3 手册（53）。

## 8. 下季度积压边界（1.1.0 候选，不在本季度实现）

- 分片续传/断点续传、正式密码恢复、Music Android 产品化、
  Ear 公开质量评分（明确不立项）、社交 Feed、支付结算；
- 视觉打磨（64 包发现项归 1.1.0 或受控补丁）。

## 9. Release Notes 与 Known Limitations

- Known limitations：music-android 壳 EXPERIMENTAL；单实例 BFF 限速；Ear 实验指标阈值 9 月前不调（MAMSE 系列）；XEngine 无 FK 依赖应用层守卫。
- 本冻结随 63 独立验证与 64 视觉终审结论更新（若产生修复，走变更政策）。
