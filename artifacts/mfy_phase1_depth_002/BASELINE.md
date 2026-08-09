# MFY-PHASE1-DEPTH-002 Baseline

- Recorded: 2026-08-09
- Base: `codex/moodify-1.0-release-convergence` @ `19d8a77`（Phase I-A 之上；测量正确性 c04645f 已并入本分支）
- 初始测试：207 passed, 5 skipped（1.0 收敛分支基线）

## 现状审计

- `auditory/timeline.py`：DSK-MFY-AUDITORY-SCAN-001 的窗口化 JSONL（固定 1s 窗）——无事件模型、无 profile、无合并层
- `auditory/metrics.py` / `loudness.py` / `true_peak.py`（Phase I-A）：全轨级测量，无时间定位
- `auditory/stereo.py`：全轨 correlation/proxy

## 设计决策

- 新建 `auditory/events/` 包（models/rules/merge/evaluate/engine/temporal_profile/__init__）+ `configs/temporal_profile_v1.yaml`
- 窗口测量一次每域（integrity 100/50、level 400/100、spectrum 1000/250、stereo 500/100 ms），检测器共享——无重复全轨变换（G14）
- 8 类 P0 事件；无 forbidden 语义标签（G4）
- localization_precision_ms = 域 hop（诚实，不假装亚 hop 精度，G13）
- HF dropout 排除静音窗（静音是独立事件，G8 语义）
- level spike/drop 相对基线中位数（前 3 窗）——避免相邻窗一次跳变后不持续
