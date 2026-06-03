# AI 接手说明｜NEM-MT-003

你正在接手 Moodify 的 MT-003 节点：MRS 性能优化与批量生产瓶颈突破。

## 你的目标

不要重新设计 MRS 真实度理论。  
不要重写 MT-002 的评分标准。  
本节点只解决一个问题：**让 MRS 可以用于批量生产。**

## 必须先读取的文件

1. `00_PACKAGE_MANIFEST.json`
2. `00_NODE_STATUS.md`
3. `rules/AI_Execution_Rules.md`
4. `nem/NEM-MT-003_MRS_Performance_Optimization.md`
5. 当前 Gate 文件
6. 当前 AEP 文件

## 执行规则

1. 每次只推进一个 AEP；
2. 先做性能基线，再做优化；
3. 不允许在没有 profiling 数据时盲目优化；
4. 不允许让 MRS 阻塞 Runtime 主流程；
5. 所有优化必须记录 before / after 指标；
6. 所有结论必须写入 reports 或 decisions；
7. 如果改变配置或接口，必须同步更新 templates 和 commands；
8. 如果发现 MRS 公式问题，不在本节点直接重构公式，只写入 backlog 或 feedback 给 MT-002。

## 当前推荐下一步

执行 AEP-MT003-001：建立 MRS 性能基线实验。

目标是回答：

- MRS 为什么每个文件需要 1-6 分钟；
- 时间主要消耗在加载、重采样、特征提取、WAV 中间文件、公式计算还是 I/O；
- 不同音频时长、文件大小、格式对耗时的影响；
- 哪些特征适合缓存；
- 是否需要 quick_mrs / full_mrs 两档。
