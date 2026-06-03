# Versioning Rules

## 样本库版本

```text
sample_asset_library_vMAJOR.MINOR
```

## 数据集版本

```text
baseline_set_v0.1
validation_set_v0.1
stress_set_v0.1
```

## 规则

- 样本加入会增加数据集版本；
- 样本移动必须记录变更；
- 权限状态变化必须记录；
- 删除或归档不能破坏历史 run 记录；
- metadata schema 变化必须保留兼容说明。
