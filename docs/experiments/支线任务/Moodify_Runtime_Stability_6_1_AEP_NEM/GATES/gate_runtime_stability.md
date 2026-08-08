# Runtime Stability Gate  
# Runtime 稳定性 Gate 判断标准

## 1. Gate 目标

本 Gate 用于判断：

> Moodify Runtime 是否可以作为后续支线实验、潮汐循环系统和 Electron 桌面端交付物的稳定地基。

最终状态只能是：

```text
ADOPT
HOLD
REJECT
```

---

## 2. ADOPT 标准

Runtime 可被正式采纳为稳定地基。

必须同时满足：

```text
90-task full test success_rate >= 98%
unrecognized_arguments_count = 0
exit_code 非 0 的任务原因明确
6h endurance run 无卡死
24h day run 可自动结束
summary_generated = true
log_integrity_rate >= 98%
task_recovery_passed = true
circuit_breaker_passed = true
stuck_task_count = 0
max_consecutive_failures <= 2
```

### ADOPT 后允许推进

```text
MRS 批量跑分
Preset 工艺库实验
潮汐循环 8h/24h 自动实验
Electron 桌面端 Runtime 集成
报告系统产品化
```

---

## 3. HOLD 标准

Runtime 基本可用，但仍有局部风险。

符合以下情况之一：

```text
90-task full test success_rate 在 90% - 98%
summary 生成但字段不完整
日志完整率在 90% - 98%
6h endurance run 通过，但 24h day run 存在异常
任务恢复可用但有少量重复
失败熔断逻辑可用但 summary 未记录完整
存在少量卡住任务，但原因明确
```

### HOLD 后允许推进

```text
继续局部开发
继续小规模实验
继续修复 Runtime
不建议进入大规模无人值守潮汐循环
不建议直接进入桌面端稳定版本集成
```

---

## 4. REJECT 标准

Runtime 不适合承载后续实验。

符合以下情况之一：

```text
90-task full test success_rate < 90%
unrecognized_arguments 多次出现
任务频繁卡死
24h day run 无法完成
summary 无法生成
日志缺失严重
任务恢复失败
失败熔断失败
进程异常退出且无错误记录
```

### REJECT 后必须处理

```text
暂停 MRS / Preset / 桌面端相关推进
优先修复 Runtime
重做 6.1 实验
直到至少达到 HOLD
```

---

## 5. Gate 报告格式

```text
Final Gate: ADOPT / HOLD / REJECT

Reasons:
- ...
- ...

Blocking Issues:
- ...

Recommended Next Actions:
- ...
```

---

## 6. Gate 哲学

Runtime Gate 的本质不是“证明一次能跑”，而是证明：

> 系统有资格进入无人值守、可复盘、可长期积累的工程状态。

只有通过 Runtime Gate，Moodify 才能从手工实验进入真正的潮汐循环。
