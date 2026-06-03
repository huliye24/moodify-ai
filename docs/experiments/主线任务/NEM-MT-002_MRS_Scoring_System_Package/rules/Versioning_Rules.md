# Versioning Rules｜版本规则

## 版本格式

```text
MRS Open v0.x.y
```

## 升级含义

- `x`：公式结构或尺度逻辑明显变化；
- `y`：权重、阈值、惩罚项、配置修正。

## 状态标记

```text
EXPERIMENTAL / HOLD / ADOPT / DEPRECATED
```

## ADOPT 条件

- 通过验证矩阵；
- 对真实样本有稳定结果；
- 不被 loudness cheat 欺骗；
- 不鼓励破坏高质量音频；
- Runtime 接入稳定；
- 有清晰报告和 Decision Log。
