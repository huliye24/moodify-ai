# MHP-004 回传单：ChatGPT 测试方案

> 日期：2026-05-30
> 来源：ChatGPT
> 状态：待 Claude B 执行

---

## 核心判断

**不要把测试一次性做大。先用 3 个测试文件锁住 v0.1.0 主线。**

## 测试分层

| 文件 | 覆盖 | 层 |
|------|------|---|
| `test_v01_presets_types.py` | 类型 + 预设 | 第一层 |
| `test_v01_analyzer_diagnostics_exporter.py` | 分析 + 诊断 + 导出 | 第二层 |
| `test_v01_pipeline.py` | 端到端 pipeline | 第三层 |

## 其他判断

- pytest marker：v01 / legacy / experimental，**不设默认 -m v01**
- baseline/：**不合并、不修复**，后续单独 MHP-006
- **全部使用 mock_wav fixture，不需要真实音频**

## 执行任务

MHP-004-A → Claude B（见 MTP 任务单）
MHP-004-A-CHECK → Claude C（见审计任务单）
