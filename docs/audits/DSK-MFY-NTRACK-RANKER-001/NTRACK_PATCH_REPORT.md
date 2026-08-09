# NTRACK_PATCH_REPORT — N 轨排名实现清单

任务：DSK-MFY-NTRACK-RANKER-001
日期：2026-08-09

## 1. 新增包 `moodify/evaluation/ntrack/`

| 文件 | 职责 |
|---|---|
| `models.py` | 8 个 frozen dataclass：RankingCandidate / QualityGateResult / PairwiseRankingEdge / RankedCandidateResult / GlobalRankingEstimate / AlbumAwareRanking / HumanRankingDecision（含 round-trip） |
| `policy.py` | RankingPolicy（from_yaml 权威路径 `configs/ntrack_policy_v1.yaml`）+ 分级比较预算（≤15 全对 / ≤100 每候选 4 对 / >100 每候选 3 对） |
| `estimator.py` | Elo 风格全局排名（确定性双遍更新）：INCONCLUSIVE 边不动分数、环容忍、tie bands（min separation 10.0）、Top-K 边界置信带、plan_pairs 选择性比较 |
| `album.py` | 专辑感知重排：证据链接的特征向量（band/centroid/LUFS/DR）+ 相似度惩罚 + 多样性奖励（质量优先不破坏） |
| `service.py` | 编排：注册 → 按 hash 缓存分析（每次每版本一次）→ 质量门（ANALYSIS_FAILED/REJECTED 重复/REVIEW_REQUIRED 削波静音）→ 初始粗序 → 选择性比较 + Top-K 边界精修 → 全局估计 → 专辑重排 → `05_ntrack/` 持久化；record_human_ranking 派生 preference |
| `golden.py` | 7 个黄金案例（确定性 RNG seed 7，真实扫描） |
| `__init__.py` | 公共导出 |

## 2. 配置

- `configs/ntrack_policy_v1.yaml`：唯一阈值来源（预算/不确定性/质量门/专辑权重/Elo 参数）

## 3. CLI（cli_v2/main.py）

- `case ntrack-rank`：tracks ≥2 + --mode + --top-k + --config
- `case ntrack-human-ranking`：--human-order + --top-k + --must-keep + --rejected + --reason

## 4. API（routes/ntrack_ranking.py，已注册）

- `POST /api/v1/rankings`（≥2 轨 400 VALIDATION；未知资产 404；响应不泄漏本地路径）
- `POST /api/v1/rankings/{id}/human-ranking`
- `GET /api/v1/rankings/{id}`（含 album_rerank 摘要）

## 5. 学习卫生

- 机器序永不作为 ground truth；人工调整 → HumanRankingDecision 持久化 + 仅派生逻辑支持的相邻反转偏好（HUMAN_EDITED，eligible_for_training=True）

## 6. 已知限制

- API 同步执行（非异步 job；小批 N≤15 适用，大批需后台化——后续任务）
- Android UI（02/08 规格的 Phase 7）：DEFER，未实现
- 分析缓存为 case 内按 hash 复用；跨 case 全局缓存未做
- 专辑 sequencing（AlbumSequencePlanner）按规格保留为未来扩展点，未实现
