# Gate Report — MFY-PHASE1-DEPTH-005

日期：2026-08-09

| Gate | 状态 | 证据 |
|---|---|---|
| G1 范围完整 | PASS | lab 为验证基础设施；非产品处理/母带 |
| G2 算子权威 | PASS | 9 算子 versioned（lab-perturbation-v1）+ 梯级 |
| G3 真值完整 | PASS | 真值从算子参数构造（test_ground_truth_derived_from_construction） |
| G4 基线对照 | PASS | C1-C6 全有未扰动对照（测试） |
| G5 可复现 | PASS | 同 spec 同结果（测试） |
| G6 削波实验 | PASS | HARD_CLIP iou 0.86 + delta ✓（门槛 iou≥0.5） |
| G7 静音实验 | PASS | SILENCE iou 1.0（门槛 ≥0.8） |
| G8 电平实验 | PASS | GAIN_STEP recall 1.0 + rms 方向 ✓（定位偏差已分类 TEMPORAL） |
| G9 频谱实验 | PASS | LOWPASS recall 1.0 + cutoff 方向 ✓ |
| G10 立体声/相位 | PASS | ANTIPHASE iou 0.83 + correlation 方向 ✓ |
| G11 噪声/动态 | PASS | NOISE/DYNAMIC delta 方向 ✓ |
| G12 误报安全 | PASS | mono 源上无 stereo 域误报（测试） |
| G13 校准输出 | PASS | 4 KEEP + 5 REVIEW_DETECTOR；auto_update=False（证据记录） |
| G14 失败分类 | PASS | GAIN_STEP 定位 → TEMPORAL_FAILURE 已分类 |
| G15 低资源 | PASS | 快速矩阵 9 实验 < 60s（CI 实用） |
| G16 回归 | PASS | Phase I-A/B/C/D 套件保持绿（全量回归） |
| G17 证据 | PASS | artifacts/mfy_phase1_depth_005/ |

## 结论

17/17 门 PASS。无未解决真值完整或系统性 P0 检测失败。

`MFY-PHASE1-DEPTH-005 VERIFICATION: PASS`
