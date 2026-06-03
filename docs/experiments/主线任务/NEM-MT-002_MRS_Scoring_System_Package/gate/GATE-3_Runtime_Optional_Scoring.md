# GATE-3_Runtime_Optional_Scoring｜Runtime 可选评分

## Gate 目标

MRS 能作为 Runtime 可选评分列运行，失败不阻塞主音频处理。

## 通过条件

- 有明确输入；
- 有明确输出；
- 有可复查日志；
- 有可下载或可归档报告；
- 失败项被记录；
- 下一步动作明确。

## 状态标记

```text
PENDING / ACTIVE / PASS / HOLD / FAIL
```

## 升级规则

只有当本 Gate 的核心条件完成并被记录后，节点才可以进入下一 Gate。若关键验证失败，应标记为 HOLD，而不是强行通过。
