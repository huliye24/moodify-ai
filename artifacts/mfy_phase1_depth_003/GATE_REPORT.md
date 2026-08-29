# Gate Report — MFY-PHASE1-DEPTH-003

日期：2026-08-09

| Gate | 状态 | 证据 |
|---|---|---|
| G1 范围完整 | PASS | 无神经嵌入/云/cache 平台/Phase II |
| G2 单一表示权威 | PASS | rep-v1 单一契约（AuditoryRepresentation） |
| G3 单一尺度权威 | PASS | scales.py 4 尺度注册（S0/S1/S2/S3），无散落常量 |
| G4 单一特征权威 | PASS | feature_registry → measurement_registry 解析（测试断言 authority_class） |
| G5 时间对齐 | PASS | 样本时钟 + 单调/有效时长不变量 + 跨尺度区间映射测试 |
| G6 多尺度正确 | PASS | S0/S1/S2 平面在 R301-R307 fixture 上行为正确 |
| G7 缺失值诚实 | PASS | NaN/null 语义；测试断言无伪造物理零 |
| G8 全局/局部一致 | PASS | S3 = compute_metrics（同一函数，完全一致）；R307 断言 metric_count |
| G9 事件映射 | PASS | 每事件 overlapping_windows 非空（R303/R307） |
| G10 频谱一致 | PASS | BANDS 集中定义（representation 路径单一来源） |
| G11 立体声完整 | PASS | mono/stereo 策略显式（corr 静音 NaN）；R303 反相验证 |
| G12 确定性 | PASS | 同输入同输出（allclose equal_nan + 全局 dict 相等） |
| G13 序列化 | PASS | JSON+NPZ round-trip 无语义损失（NaN 保留） |
| G14 资源有界 | PASS | 3min→10min：窗 11153→37193（3.3x），构建 18.7s→56.2s（3.0x）近似线性 |
| G15 回归 | PASS | Phase I-A/I-B 套件保持绿（全量回归） |
| G16 证据 | PASS | artifacts/mfy_phase1_depth_003/ |

## 结论

16/16 门 PASS。表示版本化、时间对齐、特征权威均无未决问题。

`MFY-PHASE1-DEPTH-003 VERIFICATION: PASS`
