# Moodify v2 — TreatmentPlan 设计文档

**版本：TreatmentPlan Design 1.0**
**日期：2026-07-25**
**对应执行步骤：P0 / Step 8**
**实现文件：`domain/treatment_plan.py`**

## 1. 定位

`TreatmentPlan` 是 Designer 线程的输出——一份结构化的音频处理方案，包含 1-3 个独立 A/B/C 候选变体。

设计原则：**先结构化，再接入 LLM**。MVP 阶段 Designer 使用规则模板生成 Plan，LLM 作为可插拔的后续实现替换模板引擎。

## 2. 三层模型结构

```
TreatmentPlan (方案)
├── plan_id, project_id, brief_revision, diagnosis_id
├── variants: list[TreatmentVariant] (1-3 个，标签 A/B/C)
│
└── TreatmentVariant (变体)
    ├── variant_id, label (A/B/C)
    ├── objective, problems[], preserve[], risks[]
    ├── target_metrics: dict[str, float]
    │
    └── actions: list[TreatmentAction] (有序步骤)
        ├── action_id, order (从 1 连续)
        ├── step_type: TreatmentStepType (17 种)
        ├── public_summary, reason
        ├── target_metrics, parameter_bounds
        └── prerequisites: list[str]
```

## 3. TreatmentPlan（方案级）

| 字段 | 类型 | 说明 |
|---|---|---|
| `schema_version` | `Literal["treatment_plan.v1"]` | 版本路由 |
| `plan_id` | `str` | 唯一 ID |
| `project_id` | `str` | 所属项目 |
| `brief_revision` | `int` (ge=1) | 基于哪个版本的 Brief 生成 |
| `diagnosis_id` | `str` | 基于哪个诊断线程 |
| `variants` | `list[TreatmentVariant]` | 1-3 个候选变体 |
| `recommended_variant_id` | `str \| None` | Designer 推荐的变体 |
| `recommendation_reason` | `str \| None` | 推荐理由 |
| `created_by_thread_id` | `str` | 生成此 Plan 的 Designer 线程 ID |
| `created_at` | `datetime` (tz-aware) | 创建时间 |
| `metadata` | `dict[str, Any]` | 扩展元数据 |

**约束：**
- 1 ≤ variants ≤ 3
- variants 的 ID 唯一，labels 从 A 开始连续
- 若设 `recommended_variant_id`，必须同时设 `recommendation_reason`

## 4. TreatmentVariant（变体级）

| 字段 | 类型 | 说明 |
|---|---|---|
| `variant_id` | `str` | 变体唯一 ID |
| `label` | `Literal["A", "B", "C"]` | 变体标签 |
| `name` | `str` | 人类可读名称，如 "Natural Repair A" |
| `objective` | `str` | 变体目标，如 "优先保留原始质感" |
| `problems` | `list[str]` (min=1) | 要解决的问题列表 |
| `preserve` | `list[str]` | 要保留的特质列表 |
| `actions` | `list[TreatmentAction]` (min=1) | 有序工程步骤 |
| `risks` | `list[str]` (min=1) | 风险声明 |
| `expected_output` | `str` | 预期产出描述 |
| `target_metrics` | `dict[str, float]` | 目标指标值 |

**约束：**
- problems / preserve / risks 列表项非空、不区分大小写去重
- actions 的 `action_id` 唯一，`order` 从 1 连续

## 5. TreatmentAction（步骤级）

| 字段 | 类型 | 说明 |
|---|---|---|
| `action_id` | `str` | 步骤唯一 ID |
| `order` | `int` (ge=1) | 执行顺序 |
| `step_type` | `TreatmentStepType` | 步骤类型（17 种之一） |
| `public_summary` | `str` | 人类可读摘要 |
| `reason` | `str` | 执行原因 |
| `target_metrics` | `dict[str, float]` | 此步骤的目标指标 |
| `parameter_bounds` | `dict[str, tuple[float, float]]` | 参数边界（min ≤ max） |
| `prerequisites` | `list[str]` | 前置 action_id 列表 |

### TreatmentStepType 枚举（17 种）

| 步骤类型 | 说明 |
|---|---|
| `IMPORT` | 导入源音频 |
| `STEM_SEPARATION` | 音轨分离 |
| `VOCAL_CORRECTION` | 人声修正 |
| `NOISE_REDUCTION` | 降噪 |
| `SPECTRAL_BALANCE` | 频谱均衡 |
| `DYNAMIC_SHAPING` | 动态塑形 |
| `TRANSIENT_REPAIR` | 瞬态修复 |
| `SPACE_DESIGN` | 空间设计 |
| `STEREO_CONTROL` | 立体声控制 |
| `STEM_MIX` | 音轨混音 |
| `LOUDNESS_NORMALIZATION` | 响度标准化 |
| `TRUE_PEAK_LIMITING` | 真峰限制 |
| `PLATFORM_EXPORT` | 平台导出 |
| `QUALITY_REVIEW` | 质量审查 |
| `MANUAL_ADJUSTMENT` | 手动调整 |
| `APPROVAL` | 审批 |
| `DELIVERY` | 交付 |

## 6. 不变式汇总

| 层级 | 不变式 |
|---|---|
| **Plan** | 1 ≤ variants ≤ 3；variant_id 唯一；labels 从 A 连续；推荐必附理由 |
| **Variant** | action_id 唯一；order 从 1 连续无跳空；列表项无空无重复 |
| **Action** | parameter_bounds min ≤ max；prerequisites 无重复；metric 名称非空 |

## 7. 模型配置

TreatmentPlan 和 TreatmentVariant 均为 `frozen=True`——方案一旦生成不可就地修改。修改意图通过创建新 Plan（`brief_revision` 递增）实现。

TreatmentAction 也是 `frozen=True`。

## 8. A/B 测试语义

```
TreatmentPlan
├── Variant A: Natural Repair (conservative)
│   └── Actions: NOISE_REDUCTION → SPECTRAL_BALANCE → DYNAMIC_SHAPING → LOUDNESS_NORM
│
├── Variant B: Release Ready (aggressive)
│   └── Actions: VOCAL_CORRECTION → SPECTRAL_BALANCE → DYNAMIC_SHAPING +
│                 SPACE_DESIGN → STEREO_CONTROL → TRUE_PEAK_LIMITING → LOUDNESS_NORM
│
└── Variant C: Creative Polish (experimental) — optional
```

Worker 可执行其中任一变体，产生对应的 `AudioVersion`。Judge 对多个版本的指标进行横向比较。

## 9. 与 DSP Worker 的接口

Worker 读取 `TreatmentAction` 序列：

1. 按 `order` 排序
2. 检查 `prerequisites`（前置步骤是否完成）
3. 将 `step_type` 映射到 DSP chain 节点
4. 在 `parameter_bounds` 约束内搜索最优参数
5. 以 `target_metrics` 为目标验证产出

## 10. 序列化示例

```json
{
  "schema_version": "treatment_plan.v1",
  "plan_id": "tp_a1b2c3d4e5f6",
  "project_id": "a1b2c3d4e5f6",
  "brief_revision": 1,
  "diagnosis_id": "dx_a1b2c3d4e5f6",
  "variants": [
    {
      "variant_id": "tp_a1b2c3d4e5f6_A",
      "label": "A",
      "name": "Natural Repair",
      "objective": "Produce warm intimate mix; prioritize original texture preservation",
      "problems": ["mild spectral imbalance", "low-end muddiness"],
      "preserve": ["emotional phrasing", "dream-like atmosphere"],
      "actions": [
        {
          "action_id": "act_01",
          "order": 1,
          "step_type": "SPECTRAL_BALANCE",
          "public_summary": "Gentle 3-band EQ to clarify low-mids",
          "reason": "Diagnosis flagged mild spectral imbalance",
          "target_metrics": {"spectral_balance_score": 0.75},
          "parameter_bounds": {"low_mid_gain": [-2.0, 1.0]},
          "prerequisites": []
        }
      ],
      "risks": ["May not fully resolve diagnosis-flagged issues"],
      "expected_output": "A naturally enhanced version with minimal processing artifacts",
      "target_metrics": {"mrs_delta": 5.0}
    }
  ],
  "recommended_variant_id": "tp_a1b2c3d4e5f6_A",
  "recommendation_reason": "Based on diagnosis, a conservative approach best preserves the original texture",
  "created_by_thread_id": "design_a1b2c3d4e5f6",
  "created_at": "2026-07-25T10:05:00Z",
  "metadata": {}
}
```

## 11. 验收结论

- ✅ 三层结构化模型（Plan → Variant → Action）
- ✅ 支持 1-3 个 A/B/C 候选变体
- ✅ 17 种步骤类型覆盖完整 DSP 链
- ✅ 每步定义参数边界、目标指标和前置依赖
- ✅ Frozen 模型保证方案不可变，修订通过新 Plan 实现
- ✅ Designer 规则模板已实现（`services/designer.py`），LLM 可插拔
- ✅ 可追踪：plan → brief_revision + diagnosis_id + created_by_thread_id 完整追溯链
