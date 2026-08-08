# DSK-MFY-CAPABILITY-ACCRETION-021｜失败台账

**日期：** 2026-08-02 UTC  
**规则：** 历史失败不得删除或改写为成功（PR-007）。

| # | 阶段 | 失败 | 根因 | 处置 |
|---|---|---|---|---|
| 1 | Stage C | CLI `propose` 单 case 报"minimum sample threshold not met" | **非失败——防污染机制正确工作**（单 case 不触发提案） | 聚合路径（3 case）由测试覆盖；CLI 行为保持（拒绝是特性） |
| 2 | lint | 7 个未用 import / 无占位 f-string | 草稿残留 | `ruff --fix` 清理 |

## 负面知识沉淀

- 防污染门槛（N≥3）实测：单例案例被拒绝触发提案——这正是设计意图
  （论文 021 编排 Stage B 防污染规则），记录为"正确行为"而非失败。

## 边界

- 记录与 ExecutionRecord/验证结果的关联按 record_id 字段链接，不重复存储；
  跨包自动编译（执行→测量→判断）留给集成任务。
- 未触碰 moodify_runtime（只读了解），接口对接需 SCOPE_CHANGE_REQUEST。
