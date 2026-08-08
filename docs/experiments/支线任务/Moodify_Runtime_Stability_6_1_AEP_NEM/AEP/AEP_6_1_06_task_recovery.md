# AEP-6.1.06
# 任务恢复实验

## 1. AEP 元信息

```text
AEP ID: AEP-6.1.06
AEP Name: Task Recovery Test
中文名称：任务恢复实验
所属 NEM：NEM-6.1-RUNTIME-STABILITY
所属工程链：Runtime Stability Side E-Chain
优先级：P0
状态：READY_TO_EXECUTE
```

---

## 2. 实验目的

验证 Runtime 在中断后是否可以恢复未完成任务，且不会重复处理已经完成的任务。

---

## 3. 实验边界

本 AEP 只验证：

```text
任务状态持久化
中断恢复
已完成任务跳过
未完成任务继续
恢复日志记录
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
准备至少 20 个任务
确认任务状态有持久化文件
确认 Runtime 可从队列状态恢复
准备一次人工中断或模拟崩溃
```

---

## 5. 执行步骤

```text
1. 创建 20 个以上任务的队列。
2. 启动 Runtime。
3. 在完成一部分任务后主动中断进程。
4. 检查已完成任务状态。
5. 重新启动 Runtime。
6. 验证已完成任务是否被跳过。
7. 验证未完成任务是否继续执行。
8. 检查最终 summary。
```

---

## 6. 需要采集的指标

```text
tasks_before_interrupt
completed_before_interrupt
remaining_after_interrupt
duplicated_task_count
recovered_task_count
recovery_success
summary_generated
```

---

## 7. 通过标准

```text
已完成任务不重复
未完成任务可继续
duplicated_task_count = 0
recovery_success = true
summary 正确记录恢复过程
```

---

## 8. 失败判定

```text
重启后从头开始全部重复
任务状态丢失
恢复后 summary 错误
恢复后任务队列损坏
```

---

## 9. 输出文件建议

```text
outputs/runtime_stability_6_1/task_recovery/
logs/runtime_stability_6_1/task_recovery.log
reports/runtime_stability_6_1_task_recovery.md
```

---

## 10. Claude / Codex 执行指令

```text
请执行 AEP-6.1.06：任务恢复实验。

请基于当前 Moodify 项目完成实验设计、命令执行、日志检查、指标统计和结论判断。
最终输出一个 Markdown 小报告，包含：实验目的、执行命令、输出路径、关键指标、发现的问题、最终结论。
```
