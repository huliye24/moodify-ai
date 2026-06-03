# AEP-MT006-003｜MRS 解释层

所属节点：NEM-MT-006｜报告与可解释性系统  
AEP 类型：Atomic Engineering Package｜工程原子包  
状态：PLANNED  

## 1. 目标

把 MRS 总分和子维度变化翻译成可理解解释。

## 2. 输入

- sample_id
- preset_id
- run_id
- 原始音频路径
- 处理后音频路径
- MRS before / after
- preset 参数与处理链
- Runtime 日志

## 3. 输出

- 对应模块的 Markdown / JSON / 图表 / 报告片段
- 可被报告生成器调用的结构化结果

## 4. 执行要求

1. 每个输出必须保留可追踪 ID。
2. 每个解释必须对应 MRS、preset 或可视化证据。
3. 不允许生成无法追溯来源的结论。
4. 所有模板应优先使用 Markdown + JSON。

## 5. 验收标准

- 文件可被 AI 读取；
- 字段含义清晰；
- 输出能接入 Runtime 报告流程；
- 结果可回流样本资产库和工艺库。

## 6. 下一步

完成本 AEP 后，更新：

- `00_NODE_STATUS.md`
- `decisions/Decision_Log.md`
- `reports/README_reports.md`
