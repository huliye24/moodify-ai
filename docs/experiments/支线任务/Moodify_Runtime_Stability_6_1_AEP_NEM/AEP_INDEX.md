# AEP Index  
# Runtime 稳定性实验 6.1 工程原子包索引

## NEM 节点

```text
NEM ID: NEM-6.1-RUNTIME-STABILITY
节点名称：Runtime 稳定性验证节点
所属工程链：Runtime Stability Side E-Chain
目标：验证 Moodify Runtime 是否能稳定处理真实任务
最终 Gate：ADOPT / HOLD / REJECT
```

---

## AEP 列表

| AEP ID | 名称 | 目标 | 优先级 |
|---|---|---|---|
| AEP-6.1.01 | 特殊文件名 Smoke Test | 验证路径与参数解析稳定性 | P0 |
| AEP-6.1.02 | 90-task Full Test | 验证中等规模真实任务吞吐 | P0 |
| AEP-6.1.03 | 6h Endurance Run | 验证 6 小时连续运行稳定性 | P1 |
| AEP-6.1.04 | 24h Day Run | 验证无人值守长期运行能力 | P1 |
| AEP-6.1.05 | 失败熔断实验 | 验证连续失败时是否停止损失扩散 | P0 |
| AEP-6.1.06 | 任务恢复实验 | 验证中断后是否可继续未完成任务 | P0 |
| AEP-6.1.07 | 日志完整性实验 | 验证任务状态是否可追踪 | P0 |
| AEP-6.1.08 | Summary 自动生成实验 | 验证最终摘要是否自动生成 | P0 |

---

## 推荐执行顺序

### 阶段一：基础可靠性

```text
AEP-6.1.01 特殊文件名 Smoke Test
AEP-6.1.07 日志完整性实验
AEP-6.1.08 Summary 自动生成实验
```

### 阶段二：真实任务吞吐

```text
AEP-6.1.02 90-task Full Test
AEP-6.1.05 失败熔断实验
AEP-6.1.06 任务恢复实验
```

### 阶段三：长时无人值守

```text
AEP-6.1.03 6h Endurance Run
AEP-6.1.04 24h Day Run
```

---

## 节点完成定义

本 NEM 节点不是“跑了一次就算完成”，而是必须完成以下闭环：

```text
实验设计
→ 执行
→ 日志采集
→ 指标统计
→ 问题定位
→ Gate 判断
→ 报告沉淀
```
