# Identity, Access & Privacy — V1 Decision Record

**Document ID:** MFY-IDENTITY-ACCESS-PRIVACY-001
**Version:** 1.0
**Date:** 2026-08-14
**Status:** LIVE — package MFY_PLATFORM_IDENTITY_ACCESS_PRIVACY_001 (51)
**Owner:** Human product authority (huliye24) + engineering

## 1. 冻结决策（实现前拍板，2026-08-14）

| 决策 | 定案 | 理由 |
|---|---|---|
| 身份提供方/协议 | **自托管账号体系**（无外部 OAuth 依赖） | Phase 1 无外部服务约束；邀请制 HMAC 已有资产可演进 |
| 会话方式 | 服务端会话表（auth_sessions，可撤销）+ 不透明 token cookie | 可注销/撤销（P0）；无状态签名 token 无法撤销 |
| Cookie 属性 | HttpOnly + Secure + SameSite=Lax（session）；CSRF mirror cookie 非 HttpOnly | 防 XSS 窃取、跨站携带 |
| CSRF | 双提交（cookie 镜像 header），state-changing 全部要求（登录 POST /session 除外——invite code 即 bearer secret） | 标准防御 |
| CORS | 精确 origin 白名单（MOODIFY_BFF_CORS_ORIGINS），禁用 `*` | 防跨源读取 |
| 账户恢复 | 邀请制门控 + 支持重发邀请；正式密码恢复不在 V1 | 范围边界 |
| 邀请/Beta 门控 | 保留邀请制（digest 映射 user_id） | 现有资产 KEEP |
| 登出/撤销 | DELETE /session 服务端 revoke + 清 cookie | P0 |
| demo 身份 | 生产默认 `anonymous`；`demo_read_only` 仅显式 dev 环境 | 生产公开路径无 demo 身份（P0） |
| 登录滥用 | 每 IP 5 次/10 分钟限速（内存计数） | 最小保护 |

## 2. 威胁模型

资产：用户身份、creator 所有权、私有草稿、Ear 私人证据、媒体文件、会话、审计日志。
攻击者：匿名访客、伪造 actor 头、跨用户 IDOR、CSRF 跨站写、跨源读取、会话窃取/固定、PWA 缓存泄漏、秘密泄漏。
信任边界：公网 BFF（LA）→ 服务密钥内部 API（杭州）→ 数据库；客户端永远不可信。

| 威胁 | 防御 |
|---|---|
| 客户端伪造 actor 头 | BFF 永不读取客户端 actor 头；actor 只从会话解析（`_validate_session`） |
| IDOR（A 读 B 草稿/Inbox） | 路由级 `require_actor_matches` + 服务端 ownership check |
| CSRF | 双提交 token + SameSite=Lax |
| 会话窃取/固定 | 每次登录签发新 token；服务端存储 hash；revoke 即时失效 |
| 会话过期 | 12h TTL + 服务端校验（过期=无效） |
| PWA/共享缓存泄漏 | /api/* 永不缓存；私有路径 + Set-Cookie 响应强制 no-store |
| 秘密泄漏进 Git/日志 | token 只存 hash；日志不含 cookie/token/invite/私人路径；env.example 无真实值 |
| 媒体猜测访问 | asset_key 带 user 前缀 + sha256 目录，媒体根拒绝目录穿越 |

## 3. 授权矩阵（V1 实现范围）

| 角色 | 能力 | 实现 |
|---|---|---|
| anonymous listener | 读公开 catalogue/track/creator、播放 | 无 actor |
| authenticated listener | + favorite/follow/library/playlists | invite session |
| creator owner | + 自己的草稿/版本/Passport/发布/Inbox | ownership check（creator_id ↔ actor） |
| Ear operator | 运行案例/队列（Ear 侧） | Ear API 门（包 48 实施） |
| Ear human reviewer | 裁决升级案例（Ear 侧） | 包 48 实施（user_roles 表已备） |
| admin/service | 内部 API service key（server-to-server） | 现有 `service_key_required` |

`user_roles` 表已建（user_id/role/scope），Ear operator/reviewer 角色在 48 包消费。

## 4. 隐私与数据生命周期

- 公开：music public track/creator/evidence(publish-safe)；
- 私有：草稿、版本、Passport 草稿、Inbox、Ear source/evidence；
- 上传媒体隔离于媒体根，按 user 前缀分桶；
- 日志脱敏：不记录 cookie、token、邀请码、私人路径、音频内容；
- 删除：V1 默认保留审计 + 归档（自动删除不做）；备份保留见包 53。

## 5. 迁移（demo → 正式身份）

1. `ensure-user` 幂等：已知 user_id 永不改所有者；未知 id 需 display_name 才建行；
2. BFF 旧 demo 模式仅在显式 dev env 开启；生产默认 anonymous（读）+ invite session（写）；
3. 兼容窗口：/bootstrap 契约变更已随本包测试固化（PUBLIC_ANONYMOUS_READ / SESSION_AUTHENTICATED）；
4. 回滚：关闭受保护写能力（恢复 503 BETA_AUTH_REQUIRED 行为），保留公开只读；不回退到匿名 demo 身份执行真实写。

## 6. 新环境变量（无真实值）

```
MOODIFY_BFF_AUTH_MODE=anonymous            # anonymous | invite_beta | demo_read_only(仅dev)
MOODIFY_BFF_CORS_ORIGINS=https://…         # 逗号分隔精确 origin
MOODIFY_BFF_SESSION_SECRET=<≥32字符>        # 已有
MOODIFY_BFF_BETA_INVITES={"<sha256>":"<user_id>"}   # 已有
MOODIFY_INTERNAL_API_KEY=<service key>      # 已有（内部）
```

## 7. 事实边界

- Ear API（core-package）认证门与 human reviewer 角色由包 48 实施；本包冻结矩阵与角色表。
- 速率限制为进程内计数（单 BFF 实例）；多实例需共享存储——Phase 1 单实例可接受。
- 账户恢复/密码体系不在 V1 范围（邀请制门控覆盖）。
