# AB_PREFERENCE_DATA_REPORT — 偏好学习数据

任务：DSK-MFY-PAIRWISE-JUDGE-001
日期：2026-08-08

## 1. 数据形态

`<case_root>/09_learning/pairwise_preferences.jsonl`（CaseLearningStore 原子追加），字段：

```
case_id / preferred_candidate_id / other_candidate_id / basis /
evaluator_id / created_at / schema_version /
label_source: MACHINE_ONLY | HUMAN_CONFIRMED | HUMAN_OVERRIDE /
machine_outcome: A_WINS | B_WINS | INCONCLUSIVE /
machine_confidence: LOW | MEDIUM | HIGH /
eligible_for_training: bool
```

## 2. 训练卫生规则

- **MACHINE_ONLY**（模型自动落盘）：`eligible_for_training = False` —— 未经确认的模型判断**永不**作为 ground truth
- **HUMAN_CONFIRMED / HUMAN_OVERRIDE**（人工确认/覆盖）：`eligible_for_training = True`
- 覆盖后机器决策**不被改写**（judgment.json 不可变，human_decision.json 独立事件）

## 3. 当前数据

- 黄金案例 HUMAN_OVERRIDE：machine A_WINS → human CHOOSE_B，preferred=B，eligible=True（`outputs/pairwise_golden/cases/PW-GOLDEN-006/`）
- 黄金案例 CLEAR_A_WIN/B_WIN：MACHINE_ONLY 记录，eligible=False
- 真实使用：`case pairwise-judge` + `case pairwise-decision` 落盘；API 端点同链路

## 4. 导出

复用 `learning/exports.py::export_learning_records`（仅导出 eligible 记录，其余进 excluded）。批量导出在数据量积累后执行，本次无新增训练数据集。
