# AEP-6.1.04
# 24h Day Run

## 1. AEP 元信息

```text
AEP ID: AEP-6.1.04
AEP Name: 24h Day Run
中文名称：24h Day Run
所属 NEM：NEM-6.1-RUNTIME-STABILITY
所属工程链：Runtime Stability Side E-Chain
优先级：P1
状态：READY_TO_EXECUTE
```

---

## 2. 实验目的

验证 Moodify Runtime 是否具备 24 小时无人值守运行能力，这是进入潮汐循环系统前的关键前置实验。

---

## 3. 实验边界

本 AEP 只验证：

```text
24 小时无人值守
自动停止
自动汇总
长期资源稳定性
异常任务隔离
最终报告生成
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
准备足够的输入任务
设置 24 小时运行上限
确保日志和 summary 路径固定
确保磁盘空间足够
确认可以后台运行
```

---

## 5. 执行步骤

```text
1. 创建 24h day run 配置。
2. 启动后台运行。
3. 不依赖 Claude / ChatGPT 实时监视。
4. 运行结束后检查进程退出状态。
5. 检查最终 summary。
6. 检查任务推进曲线。
7. 检查是否有卡住任务。
8. 输出 24h day run 报告。
```

---

## 6. 需要采集的指标

```text
run_duration_hours
completed_tasks
success_tasks
failed_tasks
success_rate
tasks_per_hour
average_task_duration
p95_task_duration
stuck_task_count
max_consecutive_failures
summary_generated
```

---

## 7. 通过标准

```text
可运行到设定时间或正常完成任务队列
自动停止
summary_generated = true
stuck_task_count = 0
max_consecutive_failures <= 2
日志完整
```

---

## 8. 失败判定

```text
24h 过程中进程崩溃
任务卡死
无法自动停止
无最终 summary
日志中断严重
```

---

## 9. 输出文件建议

```text
outputs/runtime_stability_6_1/24h_day_run/
logs/runtime_stability_6_1/24h_day_run.log
reports/runtime_stability_6_1_24h_day_run.md
```

---

## 10. Claude / Codex 执行指令

```text
请执行 AEP-6.1.04：24h Day Run。

请基于当前 Moodify 项目完成实验设计、命令执行、日志检查、指标统计和结论判断。
最终输出一个 Markdown 小报告，包含：实验目的、执行命令、输出路径、关键指标、发现的问题、最终结论。
```
