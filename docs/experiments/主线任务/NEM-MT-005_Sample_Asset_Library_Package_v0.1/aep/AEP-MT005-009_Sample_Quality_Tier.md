# AEP-MT005-009｜样本质量分层

## 目标

建立样本质量、用途、问题类型和可用性分层规则。

## 输入

- MT-001 Runtime 输出；
- MT-002 / MT-003 MRS 评分结果；
- MT-004 preset 使用记录；
- 当前真实 AI 音乐样本；
- 当前存储目录与云端路径。

## 输出

`sample_quality_tiers.md`

## 执行原则

1. 先建立身份和元数据，再扩大样本数量；
2. 每个样本必须有 sample_id；
3. 每个样本必须记录来源和权限状态；
4. 每个样本必须有可追踪存储路径；
5. Runtime 输出必须能反向关联到原始样本；
6. MRS 记录必须能关联 sample_id、run_id 和 preset_id；
7. 权限不确定样本不得进入公开展示或商业使用；
8. 不允许为了方便而跳过 registry。

## 验收标准

- 输出文件存在；
- 字段完整；
- 可被 AI 接手继续执行；
- 可被 Runtime / MRS / preset 节点使用；
- 不破坏节点目录规则；
- 不产生权限边界混乱。

## 失败处理

如果本 AEP 无法完成，应记录在：

```text
reports/failure_report.md
decisions/Decision_Log.md
```

并说明阻塞原因、缺失输入和下一步建议。
