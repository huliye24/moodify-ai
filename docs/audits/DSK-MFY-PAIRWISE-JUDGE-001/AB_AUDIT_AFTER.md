# AB_AUDIT_AFTER — Pairwise Auditory Judge 审计结果

任务：DSK-MFY-PAIRWISE-JUDGE-001
日期：2026-08-08
前置：AB_AUDIT_BEFORE.md（同目录）

## 1. 栈与复用

- **core**：Python 3.11，`evaluation/pairwise/` 子包（models/dimensions/policy/service）+ `case pairwise-judge/pairwise-decision` CLI + 2 个 API 端点
- **复用面**：`auditory.service::scan_audio`（46+ 指标）→ `compare_dimensions`（5 维度）→ `decide`（决策策略）；`CaseLearningStore.append_preference`（偏好持久化）；`export_learning_records`（训练导出，未改动）
- **Android**：WorkDetailScreen 判断卡片 + `MoodifyApiClient.judgePair/submitHumanDecision`

## 2. 缺口闭合情况

| 缺口 | 状态 |
|---|---|
| Pairwise 领域模型（6 个 dataclass） | ✅ models.py |
| 5 维度比较引擎（证据完整才判、mono 弃权） | ✅ dimensions.py |
| 决策策略（三态 + 置信度带 + 弃权规则 + 版本化配置） | ✅ policy.py + configs/pairwise_policy_v1.yaml |
| CLI / API / Android UI | ✅ |
| PairwisePreference 训练卫生字段 | ✅（label_source/machine_outcome/machine_confidence/eligible_for_training） |
| transient/residual 维度 | ⏸ 无检测器 → 不在维度集内（如实标注） |

## 3. 黄金案例结果（6/6 符合预期）

| 案例 | 结果 |
|---|---|
| CLEAR_A_WIN | A_WINS HIGH（margin 0.65） |
| CLEAR_B_WIN | B_WINS HIGH（margin 0.65） |
| NEAR_TIE | INCONCLUSIVE LOW（margin 0.15 弃权） |
| A_ANALYSIS_FAILURE | INCONCLUSIVE（SpectrogramGenerationFailed） |
| B_ANALYSIS_FAILURE | INCONCLUSIVE（同上） |
| HUMAN_OVERRIDE | machine A_WINS → human CHOOSE_B，eligible=True |

## 4. 扫描对比

- `scan_ab_scope.py src/moodify` before：380 命中（无 pairwise 引擎）→ after：新增 pairwise 模块（设计内命中，verify_pairwise_contract 全绿）

## 5. 终态判定

**PAIRWISE_JUDGE_ALIGNED_AND_VERIFIED**（AT-01..13 全达标；transient/residual 与 MSE 结构维度如实标注为不支持）
