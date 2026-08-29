# MHP-005 回传单：ChatGPT 全景判断

> 日期：2026-05-30
> 来源：ChatGPT
> 状态：Claude B 已执行 README + PROJECT_SNAPSHOT

---

## 核心判断

**README 和 PROJECT_SNAPSHOT 都需要，职责不同。**

- README → 给新人/GitHub/未来用户，5 分钟了解项目
- PROJECT_SNAPSHOT → 给 Claude/ChatGPT/智能体，快速恢复上下文

## MHP-005 方向

**不要新增 preset。** MHP-005 应该是"预设质量标定与 DSP 参数微调"。

## 下一步路线

```
MHP-004-B README / Quickstart
MHP-004-C Project Snapshot
MHP-004-D API/CLI smoke tests → pytest
MHP-005 Preset Quality Calibration
MHP-006 baseline 工具整理
```

## 风险发现

v01_pipeline 有 pytest 覆盖，CLI/API 已人工验收，但 CLI/API smoke tests 还未系统进入 pytest。后续 MHP-004-D 补。
