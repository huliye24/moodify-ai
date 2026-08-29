# MHP-014：Treatment Record Aggregator — 设计规格

> 日期：2026-05-30
> 来源：ChatGPT
> 定位：本地 JSON 汇总器，不是数据库
> 比喻：单条 record = 记忆，aggregator = 账本

---

## 核心设计

`scripts/v01_aggregate_treatment_records.py` — 扫描 `treatment_records/` 下所有 JSON，生成 `summary.json` + `summary.md`。

## 汇总内容

- record_count、preset 级别 avg delta、human_feedback 状态统计
- 每 preset 的平均 crest/presence/air/dynamic_range/correlation delta
- 容错：缺失字段 → null，不中断

## 工具链

```
pipeline → inspector → calibrate → treatment_record → aggregator
  手          眼          尺           记忆              账本
```

## 下一步

MHP-015 (Feedback Updater) → MHP-016 (Adaptive Recommender)
