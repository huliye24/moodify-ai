# MHP-021：Feedback-aware Aggregator Enhancement — 设计规格

> 日期：2026-05-30
> 来源：ChatGPT
> 等级：L2
> 定位：让账本理解人耳反馈趋势

## 核心

增强 `v01_aggregate_treatment_records.py`，在声学 delta 统计之上增加 human_feedback 维度：

- feedback_overview（全局覆盖率 + better_rate）
- feedback_scores（每 preset 的 avg clarity/warmth/space 等 7 维）
- feedback_quality（coverage / better_rate / completed/pending 计数）
- summary.md 新增 Feedback Score Summary / Pending Feedback / Positive Feedback 表

## 意义

从"记录发生了什么"升级为"记录哪些处理被人判断为更好"——Adaptive Preset 的前置条件。
