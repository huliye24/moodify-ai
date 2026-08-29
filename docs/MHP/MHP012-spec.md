# MHP-012：Treatment Record 本地处理记录 — 设计规格

> 日期：2026-05-30
> 来源：ChatGPT
> 定位：本地 JSON 处理记忆，不是数据库
> 意义：动态参数推荐算法的地基

---

## 核心设计

`scripts/v01_create_treatment_record.py` — 把一次处理的完整信息保存为结构化 JSON。

每条 record 包含：
before_features / preset_params / after_features / delta_features / loudness_match / inspector paths / human_feedback (pending) / algorithm_learning (placeholder)

## 数据来源

从 inspector metrics_comparison.json 读取 before/after/delta/loudness，从 v01_presets 读取 15 参数。

## 未来路线

MHP-012 → MHP-013 (汇总) → MHP-014 (规则推荐) → MHP-015 (统计) → MHP-016 (学习推荐)
