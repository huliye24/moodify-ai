# Moodify v2 — CreativeBrief 设计文档

**版本：CreativeBrief Design 1.0**
**日期：2026-07-25**
**对应执行步骤：P0 / Step 6**
**实现文件：`domain/creative_brief.py`**

## 1. 定位

`CreativeBrief` 是用户结构化的创作意图载体。它是诊断、设计、处理、审查四个阶段的**共同输入**——Analyst 读取它来确定诊断重点，Designer 读取它来生成 TreatmentPlan，Worker 按 brief 约束执行处理，Judge 检查产物是否偏离 brief。

Brief 本身是一个可编辑值对象，内嵌于 `AudioProject`。修改 Brief 是"修订意图"，不改变音频历史。

## 2. 字段设计

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `schema_version` | `Literal["creative_brief.v1"]` | 固定值 | 版本路由 |
| `goal` | `str` | min_length=1 | 一句话目标，如 "Produce a warm intimate release-ready mix" |
| `preserve` | `list[str]` | 非空、无重复 | 必须保留的特质，如 "emotional phrasing"、"natural dynamics" |
| `avoid` | `list[str]` | 非空、无重复 | 必须避免的结果，如 "clipping"、"harsh highs" |
| `platform` | `str` | min_length=1 | 目标平台，如 "streaming"、"club"、"film"、"demo" |
| `reference` | `list[str]` | 非空、无重复 | 参考音轨路径或链接（可为空列表） |

## 3. 不变式

### 3.1 列表项非空且不区分大小写去重
`preserve`、`avoid`、`reference` 的每一项去除空白后必须非空，且 casefold 比较下无重复。

### 3.2 preserve 与 avoid 不冲突
同一项不能同时出现在 `preserve` 和 `avoid` 中（casefold 比较）。例如不能既想 "preserve dynamics" 又 "avoid dynamic range"。

## 4. 模型配置

```python
model_config = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    validate_assignment=True,
)
```

`validate_assignment=True` 使 PATCH 更新 Brief 某个字段时仍然触发全部校验。

## 5. API 操作

| 端点 | 方法 | 说明 |
|---|---|---|
| `/workspace/projects/{id}/brief` | POST | 首次创建 Brief（前提：project.brief 为 None） |
| `/workspace/projects/{id}/brief` | PATCH | 部分更新 Brief（前提：project.brief 已存在） |

**PATCH 语义：** 只更新请求中提供的非 None 字段。`CreativeBriefPatch` 是全部可选字段的 Pydantic 模型。

**修改记录：** Brief 变更时，`AudioProject.updated_at` 自动更新，提供隐式的"最后修改时间"。

## 6. 可扩展性

`reference` 字段当前是 `list[str]`，承载文件路径或 URL。Phase 2 可升级为结构化引用：

```python
class ReferenceItem(BaseModel):
    type: Literal["track", "stem", "url", "timecode"]
    path_or_url: str
    label: str | None = None
    time_range: tuple[float, float] | None = None
```

当前 `list[str]` 设计足以满足 MVP 需求（"像 X 一样" 的参考音轨），升级时 `list[str]` → `list[str | ReferenceItem]` 向下兼容。

## 7. 在流水线中的使用

```
Brief.goal    ─── Designer 生成 TreatmentPlan 的目标描述
Brief.preserve ── Designer 的 actions[].preserve 继承
Brief.avoid    ── Designer 的 actions[].parameter_bounds 受约束
                 ── Judge 检查候选版本是否违反 avoid 项
Brief.platform  ── Designer 设置 LOUDNESS_NORMALIZATION 的 target_lufs
                 ── Designer 设置 TRUE_PEAK_LIMITING 的 ceiling
Brief.reference ── (Phase 2) 用于 MRS 参考对比
```

## 8. 序列化示例

```json
{
  "schema_version": "creative_brief.v1",
  "goal": "Warm intimate mix for streaming",
  "preserve": [
    "original emotional phrasing",
    "dream-like atmosphere",
    "natural musical dynamics"
  ],
  "avoid": [
    "harsh high frequencies",
    "over-compressed vocal",
    "clipping",
    "excessive stereo widening"
  ],
  "platform": "streaming",
  "reference": []
}
```

## 9. 验收结论

- ✅ 6 个字段，语义明确，满足 MVP 的 Brief 需求
- ✅ 2 组 Pydantic validators 防止数据矛盾
- ✅ 支持中英文文本（`str_strip_whitespace=True`）
- ✅ 可序列化为标准 JSON
- ✅ PATCH 部分更新语义已实现（`CreativeBriefPatch`）
- ✅ Designer 已在 `services/designer.py` 中读取 Brief 并据此生成 Plan
- ✅ Judge 通过 Brief.avoid 检查产出质量
