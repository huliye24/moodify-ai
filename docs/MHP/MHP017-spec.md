# MHP-017：Treatment Record Feedback Updater — 设计规格

> 日期：2026-05-30
> 来源：ChatGPT
> 定位：把人类听感写回 Treatment Record
> 意义：让 Moodify 的记忆开始接收经验判断

---

## 核心设计

`scripts/v01_update_treatment_feedback.py` — CLI 工具，更新单条 record 的 `human_feedback`。

支持：8 维评分（1-5）、volume_matched、better_than_before、dry-run、自动 .bak 备份。

## 工具链扩展

```
pipeline → inspector → calibrate → record → aggregator → feedback_updater
  手          眼          尺        记忆       账本         经验
```

## 下一步

MHP-018 (Feedback-aware Aggregator) → MHP-019 (Adaptive Recommender)
