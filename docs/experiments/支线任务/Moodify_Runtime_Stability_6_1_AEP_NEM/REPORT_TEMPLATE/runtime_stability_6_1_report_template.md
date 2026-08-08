# Moodify Runtime 稳定性实验 6.1 报告

## 1. 报告信息

```text
实验名称：Runtime 稳定性实验 6.1
NEM ID: NEM-6.1-RUNTIME-STABILITY
报告日期：
执行环境：
项目路径：
执行人 / 智能体：
最终 Gate：ADOPT / HOLD / REJECT
```

---

## 2. 执行摘要

```text
总任务数：
成功任务数：
失败任务数：
成功率：
exit code = 0 数量：
非 0 exit code 数量：
unrecognized arguments 次数：
最大连续失败次数：
平均单任务耗时：
P90 耗时：
P95 耗时：
卡住任务数量：
summary 是否生成：
日志是否完整：
任务恢复是否通过：
失败熔断是否通过：
```

---

## 3. AEP 执行结果

| AEP ID | 名称 | 状态 | 关键结果 | 结论 |
|---|---|---|---|---|
| AEP-6.1.01 | 特殊文件名 Smoke Test |  |  |  |
| AEP-6.1.02 | 90-task Full Test |  |  |  |
| AEP-6.1.03 | 6h Endurance Run |  |  |  |
| AEP-6.1.04 | 24h Day Run |  |  |  |
| AEP-6.1.05 | 失败熔断实验 |  |  |  |
| AEP-6.1.06 | 任务恢复实验 |  |  |  |
| AEP-6.1.07 | 日志完整性实验 |  |  |  |
| AEP-6.1.08 | Summary 自动生成实验 |  |  |  |

---

## 4. 指标统计

### 4.1 成功率

```text
success_rate =
```

### 4.2 exit code 分布

```text
exit_code_distribution =
```

### 4.3 unrecognized arguments

```text
unrecognized_arguments_count =
```

### 4.4 连续失败

```text
max_consecutive_failures =
```

### 4.5 耗时统计

```text
average_task_duration =
median_task_duration =
p90_task_duration =
p95_task_duration =
max_task_duration =
```

### 4.6 卡住任务

```text
stuck_task_count =
stuck_task_list =
```

### 4.7 summary 生成

```text
summary_generated =
summary_path =
summary_valid =
```

---

## 5. 问题清单

| 问题 | 影响 | 严重等级 | 建议修复 |
|---|---|---|---|
|  |  |  |  |

---

## 6. Gate 判断

最终 Gate：

```text
ADOPT / HOLD / REJECT
```

判断理由：

```text
1.
2.
3.
```

阻塞项：

```text
1.
2.
3.
```

---

## 7. 下一步建议

如果 ADOPT：

```text
进入 MRS 批量跑分支线
进入 Preset 工艺库实验
进入 8h/24h 潮汐循环
准备 Electron Runtime 集成
```

如果 HOLD：

```text
修复 blocking issue
重跑失败 AEP
补齐 summary / resume / circuit breaker
暂缓长时潮汐循环
```

如果 REJECT：

```text
暂停后续支线
优先修 Runtime
重新执行 6.1
```

---

## 8. 结论

```text
本次 Runtime 稳定性实验说明：
```
