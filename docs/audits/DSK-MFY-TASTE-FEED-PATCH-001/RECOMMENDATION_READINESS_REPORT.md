# RECOMMENDATION_READINESS_REPORT — 推荐能力就绪度

任务：DSK-MFY-TASTE-FEED-PATCH-001
日期：2026-08-09

## 已就绪（本补丁）

| 能力 | 状态 |
|---|---|
| 内容听觉表示 | ✅ 7 维证据链接特征向量（band 分布/centroid/LUFS 距 -14/动态范围），从 scan metrics 解包 |
| 用户偏好建模 | ✅ 长短期口味向量（0.7/0.3 混合）+ novelty tolerance 0.20~0.60 |
| 候选生成 | ✅ 相似检索 + 探索池（20% 预算）+ 质量门过滤 |
| 排序 | ✅ 加权评分（偏好/新颖/多样/连贯/质量）+ 会话重排 |
| 反馈捕获 | ✅ 9 事件类型 + 派生标签 + 权重（save 1.0 > replay 0.6 > like 0.8 > completion 0.4 > start 0.1；hard skip -0.8） |
| 迭代学习 | ✅ 事件 → 口味向量实时更新（短期快/长期慢） |
| 可追溯 | ✅ request_id + ranking_version + impression/反馈落盘回链 |
| 解释 | ✅ explanation_tokens 每项 |
| 实验就绪 | ✅ 权重/预算/阈值全在 YAML |

## 部分就绪

| 能力 | 状态 |
|---|---|
| Android feed 面 | ⚠️ core/API 就绪；UI（入口 ≤2 步、播放手势反馈）DEFER |
| 真实轨道注册 | ⚠️ 需从 auditory scan 产物导入特征（register_track API 就绪） |
| 成功指标 | ⚠️ 事件已捕获，session length/completion rate 等聚合报表未建 |

## 未就绪（后续任务）

- ML 排序（learned weights / pairwise preference 模型训练）
- 夜间批量口味/轨道 profile 刷新（事件已存，可离线聚合）
- 新鲜度/趋势池（质量门后的 trending 切片）
- 隐私控制面（事件开关 UI）

## 关键事实边界

- 事件权重为启发式（save>replay>like>completion），待实验校准
- 特征向量与 ntrack 专辑重排共享约定（metrics 嵌套 dict 解包）
- `moodify_runtime/recommenders`（运维推荐器）与本推荐层不同域，不混淆
