# AB_PATCH_REPORT — Pairwise Judge 改动清单

任务：DSK-MFY-PAIRWISE-JUDGE-001
日期：2026-08-08

## 1. Core（moodify-core-package）

| 文件 | 改动 |
|---|---|
| `src/moodify/evaluation/pairwise/__init__.py` | 子包导出 |
| `src/moodify/evaluation/pairwise/models.py` | PairwiseCandidate / DimensionResult / PairwiseComparison / PairwiseJudgment / HumanPairwiseDecision / PreferenceRecord |
| `src/moodify/evaluation/pairwise/dimensions.py` | 5 维度比较（signal_integrity/loudness/对 -14 目标距离/dynamics/spectral_balance/stereo_phase）——证据不完整即 INSUFFICIENT，mono 弃权 |
| `src/moodify/evaluation/pairwise/policy.py` | DecisionPolicy（权重/覆盖/余量/冲突阈值，版本化）+ decide() 三态 + LOW/MEDIUM/HIGH 带 + 强制弃权 |
| `src/moodify/evaluation/pairwise/service.py` | run_pairwise_judge（scan×2→compare→decide→06_pairwise 持久化→preference）+ record_human_decision |
| `src/moodify/evaluation/pairwise/run_golden.py` | 6 黄金案例（确定性合成） |
| `src/moodify/learning/models.py` | PairwisePreference + label_source/machine_outcome/machine_confidence/eligible_for_training |
| `src/moodify/cli_v2/main.py` | `case pairwise-judge` + `case pairwise-decision` 命令 |
| `src/moodify/api/routes/pairwise_judge.py` | POST /api/v1/pairwise-judgments + /{id}/human-decision（v1 错误契约、不泄漏路径） |
| `src/moodify/api/main.py` | include_router |
| `configs/pairwise_policy_v1.yaml` | 策略配置（唯一阈值来源） |

## 2. 测试（tests/evaluation/，26 个）

test_pairwise_dimensions（5）/ test_pairwise_policy（8）/ test_pairwise_service（5，含真实扫描 e2e）/ test_pairwise_cli（3）/ test_pairwise_api（5）

## 3. Android（apps/android）

| 文件 | 改动 |
|---|---|
| `data/ApiModels.kt` | PairwiseJudgmentResult |
| `data/MoodifyApiClient.kt` | judgePair() + submitHumanDecision() |
| `ui/screens/WorkDetailScreen.kt` | JudgeCard（开始判断 → 结果 + 置信度 + 理由 → 人工决策行） |
| `res/values*.xml` ×6 | 14 个 judge_* key |

## 4. 数据/API 变化

- 持久化：`<case_root>/06_pairwise/{candidates,comparison,judgment,policy}.json` + `human_decision.json` + `09_learning/pairwise_preferences.jsonl`
- API 新增 2 端点（v1.py schema-frozen 未动）
- 训练卫生：MACHINE_ONLY 永不 eligible；HUMAN_CONFIRMED/HUMAN_OVERRIDE 才 eligible

## 5. 金路径结果

`case pairwise-judge` 真实跑通（合成 wav ×2）→ A_WINS HIGH + 06_pairwise 四产物 + preference 落盘（MACHINE_ONLY/eligible=False）→ `case pairwise-decision --decision CONFIRM_MODEL` → human_decision.json + eligible=True
