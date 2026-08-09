# PATCH_REPORT — 推荐层实现清单

任务：DSK-MFY-TASTE-FEED-PATCH-001
日期：2026-08-09

## 1. 新增包 `moodify/recommendation/`

| 文件 | 职责 |
|---|---|
| `models.py` | 8 个 frozen dataclass：Track / AuditoryProfile / UserTasteProfile / RecommendationRequest / RecommendationCandidate / PlaybackSession / FeedbackEvent / RecommendationOutcome |
| `policy.py` | RecommendationPolicy（from_yaml 权威路径 `configs/recommendation_policy_v1.yaml`）：评分权重/反馈权重/探索预算/新鲜度/质量门/口味更新率 |
| `feedback.py` | 事件捕获（append-only JSONL）+ 派生标签（SKIP_HARD<10s 或 <25% / SKIP_SOFT / COMPLETION / REPLAY / LIKE / SAVE） |
| `taste.py` | 口味更新：长期（alpha 0.05×权重）慢移 + 短期（alpha 0.30×权重）快移；novelty tolerance 跳变（skip↑/完成↓，0.20~0.60）；merge 0.7/0.3 |
| `rank.py` | 候选生成（相似检索 + 探索池）+ 过滤（不可用/严重质量/会话重复）+ 加权评分（偏好匹配 1.0/新颖 0.15/多样 0.20/连贯 0.10/质量 0.25）+ 会话重排（多样性）+ 解释 token |
| `service.py` | FeedService：轨道注册/For You 生成（request_id + ranking_version + impression 落盘）/反馈→口味/收藏库 |
| `golden.py` | 7 黄金场景（确定性） |
| `__init__.py` | 公共导出 |

## 2. 配置

- `configs/recommendation_policy_v1.yaml`：唯一策略来源（candidate_pool 20/exploration 20%/freshness 30 天/事件权重 save 1.0 > replay 0.6 > like 0.8 等）

## 3. API（routes/recommendation.py，已注册）

- `GET /api/v1/feed/for-you`、`POST /api/v1/feed/request`
- `POST /api/v1/feed/feedback`（event_type 校验，400 VALIDATION）
- `POST /api/v1/tracks/register`、`GET /api/v1/tracks/{id}/auditory-profile`
- `GET /api/v1/library/saved`、`POST /api/v1/library/save`、`DELETE /api/v1/library/save/{id}`

## 4. CLI（cli_v2/main.py）

- `feed request <user> [--size]`、`feed feedback <user> <track> <event> [--request-id] [--elapsed-ms]`、`feed taste <user>`

## 5. 事件与可追溯（AT-03/06）

- 事件：IMPRESSION/PLAY_START/PROGRESS/COMPLETION/SKIP/REPLAY/LIKE/SAVE/SESSION_END（9 类）
- 每次 feed 请求：request_id + ranking_version（rec_v1）+ 每条 impression 落盘（rank_position）；反馈事件可回链 request
- 派生：硬跳/软跳/强完成/强亲和（权重可配置）

## 6. 战略一致性

- 听觉核心未动（AT-07）；无 CWC/token/藏品/交易 reintroduce（AT-08）；无社交/社区膨胀（AT-09，仅 feed/收藏）
- 推荐消费听觉表示（feature_vector 证据链接，非平行特征管线）

## 7. 已知限制 / DEFER

- Android UI（feed 入口/播放反馈手势）DEFER——core/API 就绪
- 轻量加权启发式（非 ML 排序）；实验就绪（权重/预算可配置）
- moodify_runtime/recommenders（运维推荐器）原样保留，不混淆
