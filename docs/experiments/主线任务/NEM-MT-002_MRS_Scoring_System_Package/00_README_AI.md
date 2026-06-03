# AI 接手说明｜NEM-MT-002 MRS 跑分系统

你正在接手 Moodify 的 MRS 跑分系统判断标准节点。

## 你的角色

你不是来重新发明 Moodify，也不是来直接替换 MRS 公式。你的任务是：

1. 读取节点状态；
2. 理解 MRS 作为开放跑分单位的定义；
3. 按 Gate 和 AEP 顺序执行；
4. 每次只推进一个可验收工程原子包；
5. 运行后更新报告、日志、状态和 Decision Log；
6. 保持 Runtime 主流程稳定，不让 MRS 阻塞音频处理。

## AI 阅读顺序

1. `00_PACKAGE_MANIFEST.json`
2. `00_NODE_STATUS.md`
3. `rules/AI_Execution_Rules.md`
4. `rules/MRS_Benchmark_Rules.md`
5. `nem/NEM-MT-002_MRS_Scoring_System.md`
6. 当前 Gate 文件
7. 当前 AEP 文件
8. 对应 templates / schemas / commands

## 禁止事项

- 不要把 MRS 改成 0-100 满分制。
- 不要把人工听感作为主要 ground truth。
- 不要让 MRS 失败导致 Runtime 主流程失败。
- 不要把 MRS 评分和音频处理主任务强绑定。
- 不要删除已有验证记录。
- 不要在未记录 Decision Log 的情况下修改评分标准。

## 执行原则

MRS 应作为开放跑分单位：

```text
基准样本附近可以约等于 1000
更接近真实声音可以高于 1000
更差、更塑料、更破坏性处理应低于基准
不设置满分
允许长期突破
```

每次公式升级都必须通过 Validation Matrix，而不是只看单个样本表现。
