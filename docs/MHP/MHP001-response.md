# MHP-001 回传单：ChatGPT 架构判断

> 日期：2026-05-30
> 来源：ChatGPT
> 状态：已确认，进入 MHP-002

---

## 核心判断

**不是把 60 个文件砍成 10 个文件，而是在 60 个文件之上，开出一条 10 个文件以内的 v0.1.0 主线。**

## 策略：分层冻结 + 旁路收束

- 复杂模块（physics/calibration/evaluation/llm/optimizer/safety/memory）保留不动
- 新增 `v01_*` 系列文件作为干净主路
- CLI/API 先走 v01 主线，旧 WorkflowOrchestrator 保留给未来

## v0.1.0 目标目录

```
moodify-core-package/src/moodify/
├── v01_types.py          # 新增：v0.1.0 轻量数据结构
├── v01_presets.py        # 新增：3 个处理预设
├── v01_analyzer.py       # 新增：频谱图 + 指标
├── v01_diagnostics.py    # 新增：诊断报告
├── v01_pipeline.py       # 新增：主流程编排
├── v01_exporter.py       # 新增：WAV 导出
├── processing/           # 保留：DSP 底座
├── api/main.py           # 改为调用 v01_pipeline
└── experimental/         # 移入：physics/calibration/...
```

## 重构顺序

1. 统一项目身份（README/pyproject/api/version）
2. 新增 v01 主线文件
3. CLI 收束为 analyze/process/serve
4. API /process 改为调用 v01_pipeline
