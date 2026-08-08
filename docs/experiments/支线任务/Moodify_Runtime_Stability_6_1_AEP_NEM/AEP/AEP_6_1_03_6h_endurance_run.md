# AEP-6.1.03
# 6h Endurance Run

## 1. AEP 元信息

```text
AEP ID: AEP-6.1.03
AEP Name: 6h Endurance Run
中文名称：6h Endurance Run
所属 NEM：NEM-6.1-RUNTIME-STABILITY
所属工程链：Runtime Stability Side E-Chain
优先级：P1
状态：READY_TO_EXECUTE
```

---

## 2. 实验目的

验证 Moodify Runtime 是否可以连续运行 6 小时，不发生进程卡死、资源耗尽、日志中断或 summary 缺失。

---

## 3. 实验边界

本 AEP 只验证：

```text
6 小时连续运行
长时日志刷新
内存稳定性
CPU 持续占用
任务持续推进
自动停止和总结
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
准备足够任务队列
设置 6 小时运行上限
配置日志路径
配置最终 summary 路径
确认磁盘空间充足
```

---

## 5. 执行步骤

```text
1. 创建 6h endurance run 配置。
2. 启动后台运行。
3. 运行期间不需要 AI 人工监视。
4. 记录开始时间和结束时间。
5. 结束后检查进程是否正常退出。
6. 检查日志是否持续刷新。
7. 检查 summary 是否生成。
8. 统计 6 小时内完成任务数、失败数、平均耗时。
```

---

## 6. 需要采集的指标

```text
run_duration_hours
completed_tasks
success_tasks
failed_tasks
success_rate
stuck_task_count
max_log_silence_minutes
memory_peak
cpu_average
summary_generated
```

---

## 7. 通过标准

```text
运行接近 6 小时或按配置正常结束
无进程卡死
stuck_task_count = 0
summary_generated = true
日志连续
```

---

## 8. 失败判定

```text
进程异常退出
长时间无日志
任务停止推进
内存持续增长并接近耗尽
无 summary
```

---

## 9. 输出文件建议

```text
outputs/runtime_stability_6_1/6h_endurance_run/
logs/runtime_stability_6_1/6h_endurance_run.log
reports/runtime_stability_6_1_6h_endurance_run.md
```

---

## 10. Claude / Codex 执行指令

```text
请执行 AEP-6.1.03：6h Endurance Run。

请基于当前 Moodify 项目完成实验设计、命令执行、日志检查、指标统计和结论判断。
最终输出一个 Markdown 小报告，包含：实验目的、执行命令、输出路径、关键指标、发现的问题、最终结论。
```
