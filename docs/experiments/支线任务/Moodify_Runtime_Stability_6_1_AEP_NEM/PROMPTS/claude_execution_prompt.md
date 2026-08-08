# Claude 执行 Prompt  
# Moodify Runtime 稳定性实验 6.1

请你作为 Moodify 云服务器工程执行智能体，阅读本压缩包中的以下文件：

```text
README.md
NEM_Runtime_Stability_6_1.md
AEP_INDEX.md
AEP/*.md
GATES/gate_runtime_stability.md
REPORT_TEMPLATE/runtime_stability_6_1_report_template.md
```

你的任务是基于当前 Moodify 项目执行：

```text
NEM-6.1-RUNTIME-STABILITY
Runtime 稳定性验证节点
```

请按以下顺序推进：

```text
1. 检查当前 Runtime 命令模板是否稳定。
2. 执行 AEP-6.1.01 特殊文件名 Smoke Test。
3. 执行 AEP-6.1.07 日志完整性实验。
4. 执行 AEP-6.1.08 Summary 自动生成实验。
5. 执行 AEP-6.1.02 90-task Full Test。
6. 执行 AEP-6.1.05 失败熔断实验。
7. 执行 AEP-6.1.06 任务恢复实验。
8. 设计并执行 AEP-6.1.03 6h Endurance Run。
9. 设计并执行 AEP-6.1.04 24h Day Run。
10. 输出最终 Gate：ADOPT / HOLD / REJECT。
```

请务必输出以下指标：

```text
成功率
exit code 分布
unrecognized arguments 次数
连续失败次数
平均单任务耗时
中位数任务耗时
P90 / P95 耗时
最大任务耗时
卡住任务数量
summary 是否生成
日志是否完整
任务恢复是否通过
失败熔断是否通过
最终 Gate
```

推荐输出路径：

```text
outputs/runtime_stability_6_1/
logs/runtime_stability_6_1/
reports/runtime_stability_6_1_report.md
```

注意：

```text
本实验只判断 Runtime 稳定性。
不要调整 MRS 公式。
不要优化 preset 音质。
不要做 Electron UI。
不要改变主线任务方向。
```

完成后请给出：

```text
1. 执行摘要
2. 每个 AEP 的结果
3. 关键指标表
4. 发现的问题
5. 修复建议
6. 最终 Gate
7. 下一步建议
```
