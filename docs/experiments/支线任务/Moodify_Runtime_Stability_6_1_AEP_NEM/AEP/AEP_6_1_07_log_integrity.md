# AEP-6.1.07
# 日志完整性实验

## 1. AEP 元信息

```text
AEP ID: AEP-6.1.07
AEP Name: Log Integrity Test
中文名称：日志完整性实验
所属 NEM：NEM-6.1-RUNTIME-STABILITY
所属工程链：Runtime Stability Side E-Chain
优先级：P0
状态：READY_TO_EXECUTE
```

---

## 2. 实验目的

验证每个任务是否都有完整日志记录，使 Runtime 运行过程可以被追踪、复盘和诊断。

---

## 3. 实验边界

本 AEP 只验证：

```text
日志字段完整性
任务级日志
错误日志
耗时日志
输出路径记录
summary 与日志一致性
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
准备一组可快速执行的任务
确认 Runtime 日志目录可写
确认日志格式稳定
```

---

## 5. 执行步骤

```text
1. 执行一组小规模任务。
2. 检查每个任务是否有 start 记录。
3. 检查每个任务是否有 end 记录。
4. 检查每个任务是否有 status。
5. 检查每个任务是否有 exit_code。
6. 检查是否记录 input_path 和 output_path。
7. 对照 summary 与日志统计是否一致。
```

---

## 6. 需要采集的指标

```text
total_tasks
tasks_with_start_log
tasks_with_end_log
tasks_with_status
tasks_with_exit_code
tasks_with_duration
tasks_with_output_path
log_integrity_rate
summary_log_consistency
```

---

## 7. 通过标准

```text
log_integrity_rate >= 98%
summary_log_consistency = true
每个失败任务都有错误原因
每个成功任务都有输出路径
```

---

## 8. 失败判定

```text
日志缺失严重
summary 与日志统计不一致
任务失败但无错误原因
任务成功但无输出路径
```

---

## 9. 输出文件建议

```text
outputs/runtime_stability_6_1/log_integrity/
logs/runtime_stability_6_1/log_integrity.log
reports/runtime_stability_6_1_log_integrity.md
```

---

## 10. Claude / Codex 执行指令

```text
请执行 AEP-6.1.07：日志完整性实验。

请基于当前 Moodify 项目完成实验设计、命令执行、日志检查、指标统计和结论判断。
最终输出一个 Markdown 小报告，包含：实验目的、执行命令、输出路径、关键指标、发现的问题、最终结论。
```
