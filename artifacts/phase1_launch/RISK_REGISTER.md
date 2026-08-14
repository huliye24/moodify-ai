# Risk Register — Phase I Launch

**Document ID:** MFY-PHASE1-RISK-REGISTER-001
**Version:** 0.1
**Date:** 2026-08-14
**Package:** MFY_PHASE1_PRODUCT_LAUNCH_MASTERPLAN_001 (43)
**Status:** LIVE LEDGER — 每包完成时复审；残余风险必须有 owner

等级：`S` 严重（阻塞上线）/ `M` 中等（需在上线前处置）/ `L` 低（可接受残余）。

| # | 风险 | 等级 | 现状事实 | 缓解 | Owner | 状态 |
|---|---|---|---|---|---|---|
| R01 | 身份：三处 PARTIAL 认证（web 信任 OAuth 头 / BFF 邀请制 HMAC / Ear API 无 auth） | S | 51 包前无正式账号体系；Ear API 完全开放 | 51 包身份基线；Ear API 仅内网；上线前必须收敛 | 51 | OPEN |
| R02 | 私人音频泄漏（上传、证据、prompt） | S | 纪律存在（不提交私人音频/密钥）；无集中扫描；上传 API 未提交 | 53 包泄漏扫描 + 隐私策略；上传路径 fail-closed | 53 | OPEN |
| R03 | 证据权威（实验指标被当公开排名/认证） | S | 契约已禁止；无应用层门 | 44 已冻结；46/52 实施 publish-safe 门；零容忍计数 | 44→52 | MONITOR |
| R04 | 上传恢复（断点续传缺失） | M | drafts resume/abandon 已有；无分片续传 | 50 包按需实现；失败恢复表已定义（Music 框架 §12） | 50 | OPEN |
| R05 | 媒体播放（跨域/Range/缓存） | M | Media3 播放已交付；nginx 配置存在未上线级验证 | 53 包做 Range/缓存头/跨域验证 | 53 | OPEN |
| R06 | 跨域（LA BFF / 杭州 API / PolarDB 跨 VPC） | M | PolarDB 与 ECS 不同 VPC，定案 VPC 对等；凭据阻塞中 | 对等实施 + 凭据到位；51/53 边界测试 | 51/53 | BLOCKED（凭据） |
| R07 | 缓存（nginx/CDN 缓存导致陈旧或泄漏） | M | 缓存配置存在未验证 | 53 包缓存策略验证 + 验证脚本 | 53 | OPEN |
| R08 | 数据库（PolarDB XEngine 无 FK；备份） | M | 16 表已落库；备份未验证 | 53 包备份 + dry-run 恢复演练；变更走紧急流程 | 53 | OPEN |
| R09 | 域名/证书（三个域名、证书续期） | L | cloudflared 证书管理脚本存在；verify_origins.sh 验证入口 | 53 包证书续期监控；回滚脚本 | 53 | OPEN |
| R10 | 回滚（静态可回滚；API/DB 无） | M | rollback_static_origin.sh 存在 | 53 包建 API/DB 回滚 + 演练证据 | 53 | OPEN |
| R11 | 判断权威漂移（无人值守被包装成自治） | S | 44 已修正 AGENTS/README/宪法；无产品表面消费 HUMAN_REQUIRED | 47/48 实施升级路径；架构测试守护 | 47/48 | MONITOR |
| R12 | 人工评审资源（升级路径开通后谁听？） | M | 无真人盲评（2026-08-11 决策）；升级路径需要 designated reviewer | 48 包定义 reviewer 角色与记录格式 | 48 | OPEN |
| R13 | Music Android 壳价值不明 | L | 薄壳无产品表达 | 49/50 决定留/退；不虚标 | 49/50 | OPEN |

## 处置规则

- `OPEN`：owner 包负责在上线前关闭或转为 `MONITOR`。
- `MONITOR`：有持续守卫（测试/门），上线前人工复核。
- `BLOCKED`：有外部依赖（凭据/人类决策），解除后立即处置。
- 任一 `S` 级风险为 OPEN 时 Gate D/E 不得通过。
