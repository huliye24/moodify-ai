# Phase I Launch Acceptance — Candidate Freeze & Gate Check

**Document ID:** MFY-PHASE1-LAUNCH-ACCEPTANCE-001
**Version:** 1.0
**Date:** 2026-08-14
**Package:** MFY_PHASE1_PUBLIC_LAUNCH_ACCEPTANCE_001 (54)
**Status:** CANDIDATE FROZEN — 真机端到端与人类 GO 待执行

## 1. 候选冻结

| 组件 | 版本/commit | 说明 |
|---|---|---|
| 产品框架/治理 | 7319c93（四框架 APPROVED v1.0 + 权威索引 + 术语表） | 人类批准 2026-08-14 |
| 设计系统 | 06b2e6b（tokens v1 + 组件库 + a11y 基线 7/7） | Web/Android 归并 |
| 官网 | 90f9aa4（七路由静态站 + 检查 6/6） | 部署路径 rongjingmusic.com/current |
| 身份/安全 | a7378ae（自托管会话/CSRF/CORS/no-store/无 demo 身份） | 决策记录 identity_access_privacy.md |
| Ear 表面 | 088b25e + a4927a8（job API + 工作台七页） | 真实案例全链路 |
| Ear 升级 | 7eec681（范围合同/审核队列/四端点） | 639 测试绿（core） |
| Music 聆听 | 9b5e7eb（播放契约/五曲 Range 5/5） | 线上媒体验证 |
| Music Creator | 45e7f91（幂等/越权/媒体保留） | 94 测试绿（music） |
| 证据桥 | 68811f5（交换状态机 + 10 测试） | 104 全绿（music） |
| 生产运维 | 8031c0f（拓扑/告警/secrets/备份演练） | 本地演练通过 |
| 数据库 schema | 16 表 + auth_sessions + user_roles + evidence_bridge（PolarDB/MySQL） | XEngine 无 FK（已知） |
| 证据索引 | artifacts/phase1_launch/EVIDENCE_INDEX.md（本分支） | LIVE |
| 域名 | rongjingmusic.com / rongjingwenchuan.com / rongjinwenchuan.xyz | 边界契约 FROZEN |

## 2. 端到端场景 → 证据映射（真机待执行项标注 ⚠）

| 场景 | 证据 |
|---|---|
| 官网新访客理解 / CTA / claim | 46 截图 + check_site 6/6；⚠ 真机访客测试 |
| Ear 成功/无需干预/越界人工/inconclusive/failed | 47 真实案例（job_4b85…）+ 48 四一级状态测试 + ⚠ human_required 真机截图 |
| worker 中断恢复 | 48 worker 幂等 resume（既有测试）+ ⚠ 真机故障注入 |
| Music 匿名发现/播放/seek | 49 五曲 Range 矩阵 5/5（线上 206）+ 播放器静态检查 |
| 登录后 favorite/follow/library | 51 会话测试 + 49 幂等检查 |
| Creator 全流程 + 中断恢复 + 越权失败 | 50 服务端 4 测试 + 客户端 6 检查 |
| Bridge 全流程 | 52 十测试（attach/detach/终态/审计） |
| Operations smoke/告警/回滚/备份 | 53 拓扑 + 告警表 + 本地恢复演练（ID/hash 零漂移）+ ⚠ 真机演练 |

## 3. P0 门检查（54 包 §3，55 包统一 Gate 标记口径）

| 门 | 标记 | 证据 |
|---|---|---|
| 产品身份与边界正确 | **PASS_LOCAL** | 44 治理冻结 + 身份回归守卫 |
| 无伪功能和误导 claim | **PASS_LOCAL** | 46/47/49/50 静态检查（无伪入口/无禁语） |
| 身份/所有权/隐私/CSRF/CORS/TLS | **PASS_LOCAL** | 51 测试套件；⚠ 真机 TLS/HSTS（59 包） |
| Ear 判断权威与人工升级 | **PASS_LOCAL** | 48 十五测试；⚠ 真机升级队列（59/60 包） |
| Music 播放与 Creator 发布 | **PASS_LOCAL**（媒体链 PASS_LIVE：Range 5/5） | 49/50 测试 + 线上 Range 矩阵 |
| 私人音频/证据/秘密不泄露 | **PASS_LOCAL** | 53 secrets scan clean + 47/51 no-store 断言；⚠ 真机扫描（59 包） |
| Range/缓存/PWA 正确 | **PASS_LOCAL**（媒体链 PASS_LIVE） | 49 Range 5/5 + sw.js 断言 |
| 数据备份可恢复 / release 可回滚 | **PASS_LOCAL** | 53 ID/hash 零漂移；⚠ 真机 PolarDB 恢复（58/61 包） |
| 关键页面可访问/移动可用 | **PASS_LOCAL** | 45 a11y 基线 + 46/47/49 宽度截图；⚠ 真机人工验证（64 包） |
| 监控/告警/owner/incident 通道 | **PARTIAL** | 53 告警表齐；⚠ cron 挂载与告警通道（61 包） |
| 全部 P0 证据进入统一索引 | **PASS** | EVIDENCE_INDEX（43–55 全部登记，55 包核对） |

**结论：PASS_LOCAL 不得覆盖 PASS_LIVE；任一 ⚠ 真机项未过即 NO_GO。**

## 4. P1 条件接受（候选清单）

| 项 | 影响 | 缓解 | owner | 复验 |
|---|---|---|---|---|
| music-android 薄壳（EXPERIMENTAL） | 移动端无完整产品 | 明确标注不冒充完整可用 | 49/50 | 上线后 9 月评估 |
| 多实例 BFF 限速不共享 | 多实例下限速弱 | Phase 1 单实例 | 53 | 扩容时 |
| 断点续传缺失 | 大文件上传中断 | drafts resume 覆盖到 media_ready | 50 | 上线后按需 |
| 日志聚合未自动化 | 观测依赖人工查 | 告警表 + 检查脚本 | 53 | 上线 24h 内 |
| Ear human_required 真机截图 | 证据缺口 | 48 已具队列；真机补拍 | 48/54 | 上线演练 |

## 5. 上线步骤（54 包 §5，真机执行）

1. 确认备份与回滚点（backup_snapshot.sh + release 目录）；
2. 部署候选（官网静态 / Ear API+worker / BFF+杭州 / 媒体引用）；
3. 内部 smoke（verify_origins.sh + /health 全链路）；
4. 小范围 canary（官网→Music 读路径→Ear 案例）；
5. 验证官网/Ear/Music/身份/媒体/证据；
6. **人类签署 GO**（GO_NO_GO_RECORD.md，不可自动化）；
7. 扩大流量 + 24 小时观察（A1–A10 告警表 + 回滚责任人）；
8. 观察期结束：关闭 Phase I 或进入修复循环。

## 6. 自动回滚/人工决策条件（54 包 §6）

- 立即回滚/关闭：身份越权、私人数据泄漏、错误发布、权威数据损坏、广泛播放失败、Ear 错误越权裁决、队列/数据库不可恢复故障。
- 性能退化/局部 UI 问题：incident owner 按 runbook 决策，不扩大权限。
