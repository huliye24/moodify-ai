# Gate Report — MFY-PHASE1-DEPTH-002

日期：2026-08-09

| Gate | 状态 | 证据 |
|---|---|---|
| G1 范围完整 | PASS | 仅 auditory events 层；无 MSE/语义分段/云/模型训练 |
| G2 profile 权威 | PASS | temporal_profile_v1.yaml 唯一来源（4 域 window/hop + merge + 阈值） |
| G3 窗口可复现 | PASS | 同输入同 profile → 同事件（确定性测试） |
| G4 分类完整 | PASS | 仅 8 类 P0；forbidden 标签断言互斥 |
| G5 削波定位 | PASS | 2.0-2.6s fixture：start/end 误差 <0.2s（hop 50ms 界内），IoU ≥0.5 |
| G6 静音定位 | PASS | 4.0-5.0s fixture：边界误差 ≤0.15s |
| G7 立体声/相位 | PASS | 反相段 → NEGATIVE_CORRELATION + PHASE_RISK，proxy 语义保持 |
| G8 频谱 dropout | PASS | 宽带→带限 fixture → ESTIMATOR_DERIVED，confidence ≤0.6；静音排除 |
| G9 电平事件 | PASS | spike/drop fixture 检测（相对基线中位数） |
| G10 合并/防抖 | PASS | 150ms 内合并、远距离分离（确定性） |
| G11 误报安全 | PASS | 干净正弦/噪声零事件 |
| G12 证据解析 | PASS | 每事件 evidence_windows（W 编号）+ rules + profile_id |
| G13 无假精度 | PASS | localization_precision_ms = hop |
| G14 低资源 | PASS | 每域单遍窗口化；无 GPU/云；内存 = 每域 1-2 数组 |
| G15 回归 | PASS | Phase I-A 测量测试保持绿（全量回归） |
| G16 证据 | PASS | artifacts/mfy_phase1_depth_002/ |

## 结论

16/16 门 PASS。无未解决 P0 定位/证据缺陷。

`MFY-PHASE1-DEPTH-002 VERIFICATION: PASS`
