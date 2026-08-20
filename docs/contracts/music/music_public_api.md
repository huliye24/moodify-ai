# Moodify Music Public API Contract — v1 (Frozen)

Status: FROZEN (MFY-DATA-FOUNDATION-001-REV2 Phase I)
Boundary: `LA BFF` — `/api/v1/music`（Web 与未来 Music Mobile 共用）
数据权威：PolarDB MySQL B (moodify_dev)，经杭州 `/internal/v1/music`。

## 通用约定

- Error model（全部错误）：
  ```json
  { "error": { "code": "RESOURCE_NOT_FOUND", "message": "...", "request_id": "..." } }
  ```
- Request ID：`X-Request-Id` 透传（缺失时生成）。
- Idempotency：关键写请求携带 `Idempotency-Key` 头；同 key 同 payload 返回相同结果；
  同 key 不同 payload → `409 IDEMPOTENCY_CONFLICT`。
- Actor：BFF 从会话/演示身份解析用户，注入 `X-Moodify-Actor-User-Id`；客户端不传。
- Auth state：`PUBLIC_USER_AUTH_NOT_PRODUCTION_READY`（bootstrap 演示身份）。
- Time：ISO-8601 UTC。
- Money：整数 minor unit + ISO-4217 货币码（本阶段 CNY）。

## Identity / Bootstrap

| Method | Path | 说明 |
|---|---|---|
| GET | /api/v1/music/bootstrap | 当前用户 + auth_state + demo_creator_handle |

## Creator

| Method | Path | 说明 |
|---|---|---|
| GET | /api/v1/music/creators/by-handle/{handle} | CreatorProfile（handle 规范化小写） |
| GET | /api/v1/music/creators/{id}/page | CreatorPage 聚合：profile + published tracks + albums + follower_count + viewer_following |
| POST | /api/v1/music/creators | 创建（user_id/handle/display_name/bio）；409 HANDLE_TAKEN |

## Track / Version / Passport

| Method | Path | 说明 |
|---|---|---|
| GET | /api/v1/music/catalogue | published tracks（按 published_at 降序，≤100） |
| GET | /api/v1/music/tracks/{id} | Track + current version + creator_handle |
| POST | /api/v1/music/tracks | 创建草稿（creator_id/title/…） |
| POST | /api/v1/music/tracks/{id}/versions | 添加版本（audio_asset_key 必填；MEDIA_UPLOAD_DEFERRED） |
| PUT | /api/v1/music/tracks/{id}/passport | 创作护照（来源声明，非版权确权） |
| GET | /api/v1/music/tracks/{id}/passport | 读护照 |
| POST | /api/v1/music/tracks/{id}/publish | draft→published；需 current version + passport；409 否则 |

## Follow / Favorite / Play

| Method | Path | 说明 |
|---|---|---|
| PUT/DELETE | /api/v1/music/users/{user_id}/follows/{creator_id} | 关注/取关（幂等） |
| PUT/DELETE | /api/v1/music/users/{user_id}/favorites/{track_id} | 收藏/取消（幂等） |
| POST | /api/v1/music/play-events | 播放事件（轻量埋点） |

## License / Support Intents（Creator Inbox 数据源）

| Method | Path | 说明 |
|---|---|---|
| POST | /api/v1/music/license-intents | 提交授权意向（真实 lead，非许可授予） |
| GET | /api/v1/music/creators/{id}/license-intents | Creator Inbox（owner 可见） |
| POST | /api/v1/music/support-intents | 支持意向（状态仅 expressed/contact_requested/cancelled） |

## 契约不变量

- Browser / Music Mobile 永不直连 PolarDB（必经 LA BFF）。
- BFF 永不直连 PolarDB（AC-14）。
- `support_intents` 永不出现 paid/settled（无真实支付）。
- Creation Passport 不构成版权确权；Ear 实验评分不自动成为公开质量认证。
- Ear 工作流与 Music 商业数据无共享状态。

## 已知限制（本阶段诚实声明）

- 生产公开登录未完成（演示 bootstrap 身份）。
- 真实媒体上传未完成（资产引用模式）。
- 无支付/结算；无法律许可工作流。
- 分页：catalogue/inbox 当前固定上限，未做 cursor 分页（Phase 3 补）。
