# DSK-MFY-CAPABILITY-ACCRETION-021｜验证报告

**日期：** 2026-08-02 UTC

## 1. 测试结果

| 套件 | 结果 |
|---|---|
| `tests/capability_registry/test_knowledge.py`（新增 8） | **8/8 PASS** |
| capability_registry 全量（017-021 = 69） | **69/69 PASS** |
| 009 回归 `tests/score_engine/`（55） | **55/55 PASS** |
| Ruff | clean |
| CLI smoke：`capability history / propose / policy` | 正常 |
| 旧 CLI 回归 | 无回归 |

## 2. 知识循环端到端（合成 fixture，`outputs/deepseek_validation/DSK-MFY-CAPABILITY-ACCRETION-021/`）

| 步骤 | 结果 |
|---|---|
| 3 case ×（measurement + judgment）+ 1 negative 写入 | ✅ |
| `capability history` 展示三类记录 | ✅ |
| `capability propose` 单 case | ✅ 拒绝（样本门槛 1 < 3，防污染） |
| 3 case 聚合提案（未确认） | ✅ confirmed=False |
| 未确认提案 apply | ✅ 拒绝（不自动生效） |
| 人工确认后 apply | ✅ policy/1 生效，引用被替代规则 policy/0.0 + 来源 |
| 二次 apply | ✅ policy/2 递增 |

## 3. 失败矩阵

| 场景 | 期望 | 实测 |
|---|---|---|
| 单例触发提案 | 拒绝（N≥3 门槛） | ✅ |
| 提案未确认即应用 | 拒绝 | ✅ |
| 已生效记录删除/改写 | 禁止（只追加 superseded） | ✅ |
| 记录 round-trip | 无损 | ✅ |
| 政策版本递增 | policy/1 → policy/2 | ✅ |
| 政策地质引用 | 变更携带被替代规则+来源 | ✅ |
| 负面知识一等公民 | rejected/fallback/validation_failure 持久化 | ✅ |

## 4. 未运行项（如实记录）

- 179 个 Workspace v2 全量回归未跑（未触碰 Core 实现与 moodify_runtime）。
- 知识循环与 019 ExecutionRecord/020 验证结果的自动关联仅按 record_id 字段
  链接（不重复存储）；跨包自动编译（执行→测量→判断）留给集成任务。
- 真实生产案例的数据积累依赖后续生产运行（本任务为机制与防污染保证）。

## 5. 过程中失败与修正（记入 FAILURE_LEDGER）

- CLI propose 单 case 触发样本门槛拒绝——这是**正确行为**（防污染），
  不是失败；聚合路径由测试覆盖。
- 无运行期失败；7 个 lint（未用 import/f-string）由 --fix 清理。
