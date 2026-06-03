# AI Execution Rules｜MT-003

## 核心原则

1. 先 profiling，后优化。
2. 先测 10-30 首，再谈规模化。
3. 所有优化必须有 before / after。
4. MRS 必须是 Runtime 可选列，不允许强制阻塞主流程。
5. quick_mrs 用于批量排序，full_mrs 用于深度评估。
6. 缓存必须有版本号与失效规则。
7. 并行必须受资源上限控制。
8. 所有实验输出写入 reports/。
9. 所有关键选择写入 decisions/Decision_Log.md。
10. 公式层问题反馈给 MT-002，不在 MT-003 直接推翻评分体系。
