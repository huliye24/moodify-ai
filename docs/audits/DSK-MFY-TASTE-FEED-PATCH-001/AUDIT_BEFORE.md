# AUDIT_BEFORE — 推荐层实施前审计

任务：DSK-MFY-TASTE-FEED-PATCH-001
日期：2026-08-09

## 运行时 / 栈

- Python 3.11 + moodify-core-package（v2.0.0，The Ear of AI）
- 已有听觉基础设施：auditory scan（53 指标）、Pairwise Judge（2e26fa4）、N-track Ranker（59d0b29）、access/CWC 计量（2b83b03）、contracts（af0e1d4）
- API：FastAPI `/api/v1`；CLI：`cli_v2/main.py`

## 现有"recommender"核查

- `moodify_runtime/recommenders/`：**运营优化推荐器**（score_disagreement/penalty_preset/runtime_reliability/operator_next_mhp）——生成运维动作建议，与音乐内容推荐不同域，**不可复用**，保持原样
- 无内容/用户偏好/反馈事件基础设施（feed/taste/event 零命中）

## 产品现状

- 4-tab（首页/听觉检测/案例/我的）：无 feed 入口（AT-01 导航扩展为后续 Android 波次）
- 无反馈事件（impression/play/skip/completion/replay/like/save）
- CWC 经济功能已由补丁 08 清除，无 reintroduce 风险（AT-08 满足）

## 决策

- 实现"最小可行"加权启发式管线（07 规格允许）：特征向量复用 ntrack album 的证据链接特征（band/centroid/LUFS/DR）
- 事件统一入口 POST /api/v1/feed/feedback（event_type 枚举），简化 06 规格的 8 个 player 端点
- 新包 `moodify/recommendation/`，持久化 MOODIFY_FEED_ROOT（默认 outputs/feed/）
