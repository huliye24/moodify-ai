# Quality Gate Rules

Preset 升级必须通过质量闸门。

## EXPERIMENTAL -> CANDIDATE

- 至少 5 个样本有效；
- 平均 MRS 提升为正；
- 无明显响度作弊；
- 副作用可接受。

## CANDIDATE -> STABLE

- 至少 20 个样本验证；
- 跨类型样本结果稳定；
- 高质量输入不被明显破坏；
- Runtime 可批量调用。

## STABLE -> ADOPTED

- 已进入真实工作流；
- 有稳定报告；
- 有版本记录；
- 有维护规则；
- 被用于产品或主线处理流程。
