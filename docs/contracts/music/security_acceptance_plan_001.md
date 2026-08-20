# Production Security & Privacy Acceptance — 测试计划与 Runbook

**Document ID:** MFY-SECURITY-ACCEPTANCE-001
**Version:** 1.0
**Date:** 2026-08-14
**Package:** MFY_PRODUCTION_SECURITY_PRIVACY_ACCEPTANCE_001 (59)
**Status:** 计划生效；真机执行待部署授权（59 §执行 2–4 需真实 HTTPS/nginx/BFF 链）

## 1. 测试身份矩阵（专用，不使用真实用户）

| 身份 | 类型 | 用途 |
|---|---|---|
| anonymous | 匿名 | 只读路径 |
| listener-a / listener-b | 认证听众 | favorite/follow/library |
| creator-a / creator-b | 创作者 | 草稿/Passport/发布隔离 |
| ear-operator | Ear 操作员 | 案例/队列 |
| reviewer-1 | 人工审核员 | 48 升级裁决 |
| service | 服务身份 | internal API（service key） |

## 2. P0 → 测试映射（本地基线 + 真机步骤）

| P0 | 本地证据（已绿） | 真机步骤（待授权） |
|---|---|---|
| 生产无 demo/bootstrap authority | 51 test_default_public_path_is_anonymous；AUTH_MODE 默认 anonymous | 检查生产 env AUTH_MODE ≠ demo_read_only |
| actor 伪造无效 | 51 test_actor_spoof_header_is_ignored | 真机 header 注入测试 |
| Creator A 无法访问 B 草稿/Passport/Inbox | 50 test_passport_write_is_owner_only + lifecycle isolation | 真机 A/B 账号交叉访问 |
| Music 用户无法访问 Ear private evidence | 52 内部字段不泄漏测试 + 47 no-store | 真机跨产品请求 |
| 非 reviewer 无法裁决 | 48 decide 校验 reviewer 必填 | 真机 reviewer 角色门（auth 落地后） |
| CSRF/CORS/Cookie/TLS/HSTS | 51 CSRF/CORS 测试 | 真机头检查（curl -I 全套） |
| session 撤销立即生效 | 51 revoke roundtrip | 真机登出后旧 cookie 请求 401 |
| private API/PWA/CDN 不缓存 | 51 no-store + sw.js 断言 | 真机 curl 头 + CDN 缓存检查 |
| 登录限速有效 | 51 rate limit 测试 | 真机 6 次尝试 → 429 |
| 路径穿越/MIME/size fail closed | 49/50 上传测试 | 真机上传边界 |
| secrets/私人内容扫描 clean | 53 scan_secrets.sh | 真机 + artifact 扫描（本包扩充规则） |
| 事件 runbook 可执行 | 本文件 §3 | 人工演练 |

## 3. 安全事件 Runbook

### R-SEC1 凭据/密钥轮换
1. 轮换 MOODIFY_BFF_SESSION_SECRET / MOODIFY_INTERNAL_API_KEY / MOODIFY_HANGZHOU_KEY；
2. 旧值保留一个 TTL（12h）内双接受；新值立即生效；
3. 会话全撤销：review.sqlite3 与 auth_sessions 全表 revoked_at=now（一次性脚本）；
4. 更新服务器 env，不落 Git/日志；验证日志无旧值回显。

### R-SEC2 账号禁用
1. users.status='disabled'（幂等）；auth_sessions 该 user 全 revoked；
2. 保留审计；不删除数据；
3. creator 公开内容保持只读；写路径拒绝（403）。

### R-SEC3 隐私事件（私人音频/证据疑似泄漏）
1. 立即关闭受影响上传/展示路径（fail closed，保持只读）；
2. 取证：请求日志（request ID 贯通）→ 影响面清单；
3. 回滚展示配置；通知规则按隐私政策；
4. 修复后重跑 51/52/59 安全矩阵。

### R-SEC4 会话全撤销（例行或事件）
```sql
UPDATE auth_sessions SET revoked_at = UTC_TIMESTAMP() WHERE revoked_at IS NULL;
```
+ 清空 BFF 内存会话缓存 + 通知用户重新登录。

## 4. Secrets/私人内容扫描扩充（scan_secrets.sh 增量规则）

| 类别 | 模式 |
|---|---|
| 私人路径 | `/var/lib/moodify`（泄漏语境）、`/opt/moodify`（泄漏语境）、`case_dir` 出现在日志/响应样例 |
| 私人音频 | 跟踪的 `.wav/.mp3/.flac`（Git 内私人音频）；允许：基准 fixture（已白名单） |
| 邀请码明文 | `MOODIFY_BFF_BETA_INVITES=.*[^}<>]`（带真实值） |

## 5. 事实边界

- 本地矩阵（51/52/50/48/49/53 测试）已覆盖除真机头检查外的全部 P0 逻辑面；
- 真机执行（§2 真机步骤列）需部署授权与专用测试身份注入；
- 本计划不执行破坏性渗透或影响真实用户的压力攻击（59 禁止项）。
