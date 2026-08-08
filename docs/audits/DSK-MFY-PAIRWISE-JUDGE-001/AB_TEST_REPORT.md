# AB_TEST_REPORT — Pairwise Judge 测试结果

任务：DSK-MFY-PAIRWISE-JUDGE-001
日期：2026-08-08

## 1. 命令与结果

| 命令 | 结果 |
|---|---|
| `pytest tests/evaluation -q`（PYTHONPATH=E:/moodify） | ✅ 26 passed |
| `python src/moodify/evaluation/pairwise/run_golden.py` | ✅ 6/6 黄金案例符合预期 |
| `verify_pairwise_contract.py`（core） | ✅ aligned（6 项 coverage 全 true） |
| Android `:app:testDebugUnitTest :app:assembleDebug` | ✅ BUILD SUCCESSFUL |
| ruff（core + tests） | ✅ All checks passed |

## 2. 验收标准对照（11_ACCEPTANCE_TESTS.md）

| AT | 覆盖 |
|---|---|
| AT-01 A/B 入口 | ✅ Android WorkDetailScreen 判断卡片 + CLI + API |
| AT-02 独立来源 | ✅ candidates.json 独立 hash（candidate_a/b 各自 sha256） |
| AT-03 规范分析复用 | ✅ scan_audio 同管线 |
| AT-04 证据矩阵 | ✅ dimension_results（a/b 值 + 相对结果 + evidence_refs） |
| AT-05 三态 | ✅ A_WINS/B_WINS/INCONCLUSIVE |
| AT-06 弃权 | ✅ NEAR_TIE 黄金案例 INCONCLUSIVE |
| AT-07 失败测试 | ✅ A/B_ANALYSIS_FAILURE 黄金案例 INCONCLUSIVE + analysis_failed |
| AT-08 人工确认 | ✅ record_human_decision CONFIRM_MODEL |
| AT-09 人工覆盖 | ✅ HUMAN_OVERRIDE 黄金案例（机器与人决策都保留） |
| AT-10 可追溯 | ✅ 源 hash/策略版本/比较版本/evidence_refs |
| AT-11 可复现 | ✅ 确定性 RNG 合成 + 同输入同结果 |
| AT-12 训练卫生 | ✅ MACHINE_ONLY eligible=False；HUMAN_* eligible=True |
| AT-13 UX | ✅ 卡片显示胜者/置信度带/理由 |

## 3. 已知残余

- transient/residual、MSE 结构维度无检测器（规格标注"仅当已支持"）
- 置信度只用 LOW/MEDIUM/HIGH 带（无假精度）
- API 的 human-decision 依赖持久化 case 目录（MOODIFY_WORKSPACE_ROOT/pairwise/）
