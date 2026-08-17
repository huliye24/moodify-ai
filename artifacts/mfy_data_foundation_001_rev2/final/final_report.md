# MFY-DATA-FOUNDATION-001-REV2 Final Report

## 1. Verdict

**`PASS_WITH_LIMITATIONS`**

数据基础（Phase A-F）与 12 步商业闭环数据层全部完成并真库验证；
Web 页面代码完成，线上部署与并行 self-hosted BFF 工作合并待人工确认。

## 2. Previous Phase Gate
- MFY-INFRA-FOUNDATION-001 PASS_WITH_HUMAN_BLOCKERS（4 项全过；安全组/白名单
  2 项人工项仍待办，不影响本阶段数据层）。

## 3. Product Boundary

### Moodify Ear
- canonical: moodify-core-package / apps/android / rongjingmusic.com
- 本阶段零改动（git 确认）；杭州 8000 同进程挂载 Music 路由，Ear 端点/队列不变
- regression: Ear health 200；Android 无改动（report 见 ear/android_ear_regression_report.md）

### Moodify Music
- canonical Web: apps/music-web（12 步页面代码完成）
- public API: /api/v1/music（LA BFF，契约冻结 docs/contracts/music/music_public_api.md）
- data authority: PolarDB MySQL B / moodify_dev（16 表）

## 4. Git
- repo: huliye24/moodify；branch: codex/mfy-data-foundation-001-rev2
- base: 5ef38d9（HEAD 6e73678 含并行 self-hosted BFF 提交）
- Draft PR: https://github.com/huliye24/moodify/pull/2

## 5. Database
- instance: pc-bp19502y46246gv6n；database: moodify_dev
- runtime identity: moodify_app@172.21.10.9（最小权限）；migration: moodify_migration@172.21.10.9
- migration: 003_cwc_idempotency_audit (head)；16 表 + alembic_version
- charset: 全表 utf8mb4/utf8mb4_unicode_ci（XEngine）；时间 UTC（会话时区 + CURRENT_TIMESTAMP）

## 6. Identity / Ownership
- platform user（users 表，auth_subject 预留）；creator 1:1 user（handle 唯一/规范化）
- track: creator_id + created_by_user_id；修改/发布经 ownership check（403 验证）
- publication states: draft/published/unlisted/archived（CHECK 约束 + 审计）

## 7. Creation Passport
- creation_passports 表（origin_type/tools/model/prompt_disclosure/rights_statement 等）
- 公开字段白名单；私有 prompt 默认 private；UI 免责声明；Ear evidence 仅外部引用不自动公开

## 8. Internal Data API
- /internal/v1/music（users/creators/tracks/versions/passport/albums/follows/
  favorites/play-events/license-intents/support-intents/cwc/catalogue）
- service-key 鉴权（X-Moodify-Service-Key / Bearer）+ 统一错误模型 + request_id

## 9. LA Public BFF
- upstream: http://120.55.191.146:8000（service key）
- timeout 5s；GET retry 1；写路径 Idempotency-Key 透传；缓存 30/60/300s
- **direct DB access = NO**

## 10. Web 12-Step Commercial Loop

| # | Step | Status |
|---|---|---|
| 1 | Identity boundary | PASS（bootstrap 演示身份） |
| 2 | Creator Space | PASS（/c/{handle} 聚合） |
| 3 | Track/asset create | PASS（MEDIA_UPLOAD_DEFERRED） |
| 4 | Passport | PASS（含免责声明） |
| 5 | Publish | PASS（版本+护照门控） |
| 6 | Public Track URL | PASS（/t/{id}） |
| 7 | Play | PASS（play-events 持久化） |
| 8 | Enter Creator Space | PASS（creator_handle 链接） |
| 9 | Follow | PASS（持久+幂等） |
| 10 | Favorite | PASS（持久+幂等） |
| 11 | License Intent | PASS（真库） |
| 12 | Creator sees intent | PASS（/inbox） |

**COMMERCIAL_LOOP = 12/12**（API 层真库验证；Web 页面代码完成，线上部署合并待人工）
→ 状态：数据层 COMPLETE；线上 Web 部署 PARTIAL（合并待办）

## 11. Support Intent
- support_intents 表；状态 expressed/contact_requested/cancelled；payment integration = NO

## 12. Idempotency
- Idempotency-Key + sha256(request hash) + idempotency_keys 表；同 key 同 payload 重放；
  不同 payload → 409 IDEMPOTENCY_CONFLICT（测试覆盖）

## 13. Audit
- audit_events 表：user/creator/track/version/passport/publish/follow/favorite/
  license/support/cwc 全动作；敏感字段脱敏（prompt/token/password）

## 14. Android Ear Isolation
- build: 未执行（无改动）；pairing/auditory workflow: 未触碰
- Music domain injected = NO；无 PolarDB/杭州凭据入 Android

## 15. Public API Contract Freeze
- docs/contracts/music/music_public_api.md（FROZEN，bootstrap/creator/track/
  passport/follow/favorite/license/support/error/分页限制）

## 16. Tests
- unit/API: 25 passed（models 约束、幂等冲突、审计脱敏、ownership、错误模型、全流程）
- migration: 本地 SQLite + 杭州 PolarDB upgrade→downgrade→upgrade 全链通过
- BFF: catalogue/track/bootstrap/by-handle 实测（真库）
- E2E: 12 步 API 层真库全通过；latency smoke 0.35-0.45s

## 17. Deployment
- 杭州 8000（Music 路由）+ LA BFF 8100 + nginx 路由 部署完成并验证
- Web release 构建完成（vite.config 差异）→ 线上保持并行 data-foundation 版（200）

## 18. Rollback
- 见 deployment/health.md：music symlink / BFF restart / 杭州 main.py+unit 备份恢复 /
  Alembic downgrade

## 19. Security / Privacy
- 全链路 service-key 鉴权；无 secret 进 git（key/password 仅本地 0600 + LA 0600 env）
- 审计脱敏；passport 隐私默认；浏览器/Android 永不直连 PolarDB

## 20. Known Limitations
- production public auth（演示 bootstrap 身份）
- object storage / real media upload（资产引用模式）
- payments / payouts（support_intents 无支付）
- legal licensing workflow（intent ≠ 许可）
- Music Mobile / iOS（Web First）
- advanced recommendation / observability / 备份缺口
- **线上 Web 部署待与并行 self-hosted BFF 链合并**（worker 模式 vite.config）

## 21. Evidence Paths
```
artifacts/mfy_data_foundation_001_rev2/
  preflight/（4 项）contracts/（2 项）
  schema/（6 项：review/alembic/table/index/fk/charset）
  api/（internal_routes 等——代码即证据，路由清单见 schema_review）
  web/（页面代码在 git HEAD）
  e2e/（commercial_loop_12_steps.md、latency_smoke.md）
  ear/（android_ear_regression_report.md）
  deployment/（health.md、releases.md）
  final/（本报告）
```

## 22. Recommended Phase 3（仅建议）
`MFY-MUSIC-COMMERCIAL-BETA-001`：真实身份/登录、对象存储 + 真实上传、
线上 Web 合并部署、Music Mobile 起点（契约已冻结）、首批外部创作者 beta、
许可运营、支付准备。

**停止，等待人工确认。**
