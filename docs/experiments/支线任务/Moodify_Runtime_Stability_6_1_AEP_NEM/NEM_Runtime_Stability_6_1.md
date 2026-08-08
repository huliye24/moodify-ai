# NEM-6.1-RUNTIME-STABILITY  
# Runtime 稳定性验证节点

## 1. 节点定义

```text
NEM ID: NEM-6.1-RUNTIME-STABILITY
NEM Name: Runtime Stability Validation Node
中文名称：Runtime 稳定性验证节点
所属项目：Moodify
所属工程链：Runtime Stability Side E-Chain
节点状态：READY_TO_EXECUTE
目标 Gate：ADOPT / HOLD / REJECT
```

---

## 2. 节点使命

Runtime 是 Moodify 的工程地基。

如果 Runtime 不能稳定运行，则后续所有支线实验都会失去可靠性：

- MRS 评分不可信
- Preset 优化不可复盘
- 样本库无法批量处理
- 报告系统无法自动生成
- 潮汐循环无法无人值守
- Electron 桌面端无法形成稳定产品闭环

因此，本 NEM 的使命是：

> 验证 Moodify Runtime 是否具备真实任务环境下的稳定运行能力、异常处理能力、恢复能力、日志能力和 summary 自动生成能力。

---

## 3. 节点边界

本 NEM 只处理 Runtime 稳定性，不处理以下问题：

```text
不调整 MRS 公式
不优化 preset 音质
不判断 AI 音乐真实度
不做 UI / Electron 桌面端开发
不做商业化功能设计
不做样本资产库标准
```

本节点只回答：

```text
系统能不能稳定跑？
系统能不能跑完？
系统能不能记录？
系统能不能恢复？
系统能不能自己总结？
```

---

## 4. 输入

### 4.1 项目输入

```text
Moodify 当前代码库
moodify_runtime/
configs/
data/night_inputs/
workers/
scripts/
logs/
outputs/
```

### 4.2 样本输入

建议至少准备：

```text
3 个短音频样本
10 个真实 AI 音乐样本
30 个真实 AI 音乐样本
特殊文件名样本集
损坏样本 / 空文件 / 不支持格式样本
```

### 4.3 配置输入

建议路径：

```text
configs/runtime_stability_6_1.json
```

---

## 5. 输出

### 5.1 实验输出目录

```text
outputs/runtime_stability_6_1/
```

### 5.2 日志目录

```text
logs/runtime_stability_6_1/
```

### 5.3 报告目录

```text
reports/runtime_stability_6_1_report.md
```

---

## 6. 核心指标

```text
success_rate
exit_code_distribution
unrecognized_arguments_count
max_consecutive_failures
average_task_duration
median_task_duration
p90_task_duration
p95_task_duration
max_task_duration
stuck_task_count
summary_generated
log_integrity_passed
recovery_passed
circuit_breaker_passed
```

---

## 7. 通过标准

### ADOPT

```text
90-task full test 成功率 >= 98%
6h endurance run 无卡死
24h day run 可自动结束并生成 summary
unrecognized arguments = 0
summary 自动生成成功
日志完整
任务恢复实验通过
失败熔断实验通过
```

### HOLD

```text
成功率 90% - 98%
失败原因明确
summary 存在但字段不完整
日志存在少量缺失
恢复机制可用但不完美
长时运行存在局部异常但可解释
```

### REJECT

```text
成功率 < 90%
unrecognized arguments 多次出现
任务经常卡死
24h run 无法完成
summary 无法生成
日志缺失严重
失败无法恢复
```

---

## 8. 本 NEM 对主线的意义

本节点完成后，Moodify 将从“可以手动跑实验”进入：

```text
可以自动跑实验
可以自动记录实验
可以自动复盘实验
可以自动生成报告
可以支撑长期潮汐循环
```

这意味着 Moodify 的开发生态开始从“人工推动”转向“系统自运行”。

---

## 9. 与 AEP 的关系

本 NEM 由 8 个 AEP 组成：

```text
AEP-6.1.01 特殊文件名 Smoke Test
AEP-6.1.02 90-task Full Test
AEP-6.1.03 6h Endurance Run
AEP-6.1.04 24h Day Run
AEP-6.1.05 失败熔断实验
AEP-6.1.06 任务恢复实验
AEP-6.1.07 日志完整性实验
AEP-6.1.08 Summary 自动生成实验
```

每个 AEP 都是一个独立可执行、可验证、可复盘的工程原子包。
