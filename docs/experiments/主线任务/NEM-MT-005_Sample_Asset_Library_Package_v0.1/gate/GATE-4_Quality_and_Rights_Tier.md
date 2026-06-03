# Gate 4｜质量与权限分层

## 目标

样本能按质量、用途、来源和权限状态分层。

## 通过条件

- 相关文件齐全；
- 样本身份可追踪；
- 存储路径可复现；
- 权限状态明确；
- Runtime / MRS / preset 记录可以关联 sample_id；
- 可进入下一 Gate。

## 不通过条件

- 样本只有文件名，没有 sample_id；
- 没有来源记录；
- 没有权限状态；
- 原始音频和处理结果混放；
- Runtime 输出无法追踪回原始样本；
- MRS 历史无法关联具体 run；
- 权限不确定样本被标记为可公开或可商用。

## Gate 结论字段

```text
Gate Status: PASS / HOLD / FAIL
Reviewer: AI / Human / Mixed
Date:
Reason:
Next Action:
```
