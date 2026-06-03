# Versioning Rules

## 版本格式

```text
vMAJOR.MINOR.PATCH
```

## 规则

- PATCH：轻微参数修正；
- MINOR：处理链调整；
- MAJOR：目标问题或整体逻辑改变。

## 回滚

所有稳定 preset 必须保留可回滚版本。

## 废弃

当 preset 被更优版本替代，或被证明副作用过大，应标记为 DEPRECATED。
