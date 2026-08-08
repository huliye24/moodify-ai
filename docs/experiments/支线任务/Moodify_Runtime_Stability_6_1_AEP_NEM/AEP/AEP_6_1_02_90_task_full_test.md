# AEP-6.1.02
# 90-task Full Test

## 1. AEP 元信息

```text
AEP ID: AEP-6.1.02
AEP Name: 90-task Full Test
中文名称：90-task Full Test
所属 NEM：NEM-6.1-RUNTIME-STABILITY
所属工程链：Runtime Stability Side E-Chain
优先级：P0
状态：READY_TO_EXECUTE
```

---

## 2. 实验目的

验证 Moodify Runtime 在 30 首音频 × 3 个 preset = 90 个真实任务下的中等规模吞吐能力与稳定性。

---

## 3. 实验边界

本 AEP 只验证：

```text
任务队列生成
批量处理稳定性
exit code 分布
平均任务耗时
失败率
summary 生成
```

本 AEP 不处理：

```text
不优化音质
不调整 MRS 权重
不修改产品 UI
不引入新商业功能
```

---

## 4. 前置条件

```text
准备 30 个真实或接近真实的 AI 音乐样本
准备 3 个 preset
确认输出目录空间充足
确认运行期间无其他重型任务抢占资源
```

---

## 5. 执行步骤

```text
1. 准备 30 个输入样本。
2. 注册样本到 input_registry.jsonl。
3. 生成 30 × 3 = 90 个任务。
4. 启动 Runtime 批处理。
5. 记录所有任务的 start/end/status/exit_code。
6. 统计成功率、失败率、平均耗时、P90/P95 耗时。
7. 检查是否生成 summary。
8. 输出 90-task full test 报告。
```

---

## 6. 需要采集的指标

```text
total_tasks
success_tasks
failed_tasks
success_rate
exit_code_distribution
average_task_duration
median_task_duration
p90_task_duration
p95_task_duration
max_task_duration
unrecognized_arguments_count
summary_generated
```

---

## 7. 通过标准

```text
success_rate >= 98%
exit code = 0 占绝大多数
unrecognized_arguments_count = 0
summary_generated = true
失败任务原因可解释
```

---

## 8. 失败判定

```text
success_rate < 90%
大量 exit code 非 0
出现系统性参数错误
任务跑完但无 summary
存在大量卡住任务
```

---

## 9. 输出文件建议

```text
outputs/runtime_stability_6_1/90_task_full_test/
logs/runtime_stability_6_1/90_task_full_test.log
reports/runtime_stability_6_1_90_task_full_test.md
```

---

## 10. Claude / Codex 执行指令

```text
请执行 AEP-6.1.02：90-task Full Test。

请基于当前 Moodify 项目完成实验设计、命令执行、日志检查、指标统计和结论判断。
最终输出一个 Markdown 小报告，包含：实验目的、执行命令、输出路径、关键指标、发现的问题、最终结论。
```
