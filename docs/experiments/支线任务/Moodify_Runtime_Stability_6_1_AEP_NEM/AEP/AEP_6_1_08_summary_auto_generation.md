# AEP-6.1.08
# Summary 自动生成实验

## 1. AEP 元信息

```text
AEP ID: AEP-6.1.08
AEP Name: Summary Auto-generation Test
中文名称：Summary 自动生成实验
所属 NEM：NEM-6.1-RUNTIME-STABILITY
所属工程链：Runtime Stability Side E-Chain
优先级：P0
状态：READY_TO_EXECUTE
```

---

## 2. 实验目的

验证 Runtime 是否能在实验结束后自动生成 summary，使 Moodify 具备无人值守运行后的自动复盘能力。

---

## 3. 实验边界

本 AEP 只验证：

```text
summary 文件生成
summary 字段完整性
summary 数值可信度
summary 与日志一致性
Gate 状态输出
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
准备一组小规模任务
确认 summary 输出路径存在或可自动创建
确认日志已生成
```

---

## 5. 执行步骤

```text
1. 执行一个小规模任务队列。
2. 等待 Runtime 结束。
3. 检查 summary 是否自动生成。
4. 检查 summary 字段是否完整。
5. 对照日志验证 summary 数值。
6. 检查是否输出 ADOPT / HOLD / REJECT 初步判断。
```

---

## 6. 需要采集的指标

```text
summary_generated
summary_path_exists
has_total_tasks
has_success_tasks
has_failed_tasks
has_success_rate
has_exit_code_distribution
has_duration_stats
has_stuck_task_count
has_final_gate
summary_log_consistency
```

---

## 7. 通过标准

```text
summary_generated = true
summary 字段完整
summary 与日志一致
包含最终 Gate 判断
```

---

## 8. 失败判定

```text
任务结束但无 summary
summary 字段缺失
summary 数值与日志不一致
没有最终结论
```

---

## 9. 输出文件建议

```text
outputs/runtime_stability_6_1/summary_auto_generation/
logs/runtime_stability_6_1/summary_auto_generation.log
reports/runtime_stability_6_1_summary_auto_generation.md
```

---

## 10. Claude / Codex 执行指令

```text
请执行 AEP-6.1.08：Summary 自动生成实验。

请基于当前 Moodify 项目完成实验设计、命令执行、日志检查、指标统计和结论判断。
最终输出一个 Markdown 小报告，包含：实验目的、执行命令、输出路径、关键指标、发现的问题、最终结论。
```
