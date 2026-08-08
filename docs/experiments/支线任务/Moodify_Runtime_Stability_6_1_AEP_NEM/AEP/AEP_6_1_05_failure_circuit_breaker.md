# AEP-6.1.05
# 失败熔断实验

## 1. AEP 元信息

```text
AEP ID: AEP-6.1.05
AEP Name: Failure Circuit Breaker Test
中文名称：失败熔断实验
所属 NEM：NEM-6.1-RUNTIME-STABILITY
所属工程链：Runtime Stability Side E-Chain
优先级：P0
状态：READY_TO_EXECUTE
```

---

## 2. 实验目的

验证 Runtime 在连续失败时是否能够触发熔断、跳过异常任务或停止运行，防止错误扩散和资源浪费。

---

## 3. 实验边界

本 AEP 只验证：

```text
连续失败检测
失败阈值配置
熔断触发
错误日志记录
安全停止
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
准备 3-5 个故意损坏或不支持的输入文件
设置连续失败阈值
确认 Runtime 支持失败计数或可添加失败计数逻辑
```

---

## 5. 执行步骤

```text
1. 准备异常输入样本：空文件、损坏音频、不支持格式、错误路径。
2. 将异常样本加入任务队列。
3. 设置连续失败阈值，例如 3。
4. 启动 Runtime。
5. 检查是否在连续失败后触发熔断。
6. 检查日志是否记录失败原因。
7. 检查 summary 是否记录熔断事件。
```

---

## 6. 需要采集的指标

```text
failure_task_count
max_consecutive_failures
circuit_breaker_triggered
trigger_threshold
stop_reason
error_log_complete
summary_records_breaker
```

---

## 7. 通过标准

```text
连续失败达到阈值后触发熔断
日志记录每个失败原因
summary 记录熔断事件
系统安全退出或跳过异常批次
```

---

## 8. 失败判定

```text
连续失败后仍无限执行
失败原因不记录
熔断无效
进程崩溃但没有 summary
```

---

## 9. 输出文件建议

```text
outputs/runtime_stability_6_1/failure_circuit_breaker/
logs/runtime_stability_6_1/failure_circuit_breaker.log
reports/runtime_stability_6_1_failure_circuit_breaker.md
```

---

## 10. Claude / Codex 执行指令

```text
请执行 AEP-6.1.05：失败熔断实验。

请基于当前 Moodify 项目完成实验设计、命令执行、日志检查、指标统计和结论判断。
最终输出一个 Markdown 小报告，包含：实验目的、执行命令、输出路径、关键指标、发现的问题、最终结论。
```
