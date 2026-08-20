# Test Results — MFY-PHASE1-DEPTH-002

日期：2026-08-09

| 套件 | 结果 |
|---|---|
| tests/auditory/test_temporal_hearing.py | 15 passed（G3-G13 全覆盖） |
| 全量回归 | 见 gate 记录（207 基线 + 15 新增） |
| Ruff（events + 测试） | All checks passed |

## 覆盖

- profile 权威（G2）、可复现（G3）、分类互斥（G4）
- 8 类检测器定位（G5-G9）
- 合并/防抖（G10）、干净对照误报（G11）、证据窗口（G12）、精度诚实（G13）
- 定位指标：recall/IoU/start-end 误差（evaluate_events）
