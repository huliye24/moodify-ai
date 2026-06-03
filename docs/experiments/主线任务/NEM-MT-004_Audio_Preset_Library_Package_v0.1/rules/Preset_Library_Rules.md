# Preset Library Rules

## Preset 必备字段

- preset_id
- preset_name
- category
- maturity_level
- version
- target_problem
- applicable_inputs
- not_applicable_inputs
- processing_chain
- parameter_summary
- mrs_before
- mrs_after
- delta_mrs
- side_effects
- runtime_callable
- created_at
- updated_at

## 成熟度规则

- IDEA：未实验
- EXPERIMENTAL：已实现但样本少
- CANDIDATE：多个样本有效
- STABLE：稳定可批量运行
- ADOPTED：正式工艺资产
- DEPRECATED：废弃或被替代

## 禁止事项

- 禁止响度作弊；
- 禁止通过过度压缩制造虚假提升；
- 禁止破坏高质量输入；
- 禁止无版本修改参数；
- 禁止无 registry 的野生 preset。
