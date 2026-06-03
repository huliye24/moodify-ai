# MT-001 Evolution Gates｜进化闸门

所属节点：NEM-MT-001｜Runtime 云端运行系统  
用途：判断 MT-001 是否可以从节点建档进入基础可运行、无人值守、真实样本、长时稳定和最终采纳阶段。

---

## Gate 0｜节点建档

### 要求

- NEM 文件创建完成；
- AEP 拆分完成；
- 节点目标明确；
- 节点边界明确；
- 验收标准明确；
- 压缩包结构完成。

### 通过标准

```text
MT-001_Runtime_NEM_Package 完成，并可放入 docs/nem/
```

### 当前状态

进行中。

---

## Gate 1｜基础可运行

### 要求

- Runtime 可在云端启动；
- 能处理测试音频；
- 能输出结果；
- 不依赖本地电脑。

### 通过标准

```text
3 个测试音频 × 3 个 preset = 9 个任务成功运行
```

### 证据

```text
运行命令：
日志文件：
输出目录：
最终报告：
失败数量：
```

### 当前状态

接近完成。

---


### Evidence (2026-06-03 UTC)

```text
command: bash scripts/mt001_smoke_run.sh configs/mt001_runtime_smoke.json mt001_gate1_20260603
log: logs/mt001_gate1_20260603.log
summary: outputs/mt001_smoke/mt001_gate1_20260603/summary.json
manifest: outputs/mt001_smoke/mt001_gate1_20260603/manifest.csv
report: reports/mt001_smoke/daily_report_mt001_gate1_20260603.md
selected: 9
success: 9
failed: 0
manifest_rows: 9
status: PASS
```

## Gate 2｜无人值守运行

### 要求

- 可使用后台命令启动；
- 不需要 Claude 监视；
- 不需要人工盯屏；
- 跑完自动停止；
- 跑完生成总结。

### 通过标准

```text
一次无人值守 Day Run 成功完成
```

### 当前状态

待验证。

---


### Evidence (2026-06-03 UTC)

```text
launcher: detached tmux session
session: mt001-gate2
command: tmux new-session -d -s mt001-gate2 -c /home/ubuntu/moodify-mainline "bash scripts/mt001_smoke_run.sh configs/mt001_runtime_smoke.json mt001_gate2_unattended_20260603"
session_result: exited automatically
log: logs/mt001_gate2_unattended_20260603.log
summary: outputs/mt001_smoke/mt001_gate2_unattended_20260603/summary.json
manifest: outputs/mt001_smoke/mt001_gate2_unattended_20260603/manifest.csv
report: reports/mt001_smoke/daily_report_mt001_gate2_unattended_20260603.md
selected: 9
success: 9
failed: 0
manifest_rows: 9
status: PASS
```

## Gate 3｜真实样本运行

### 要求

- 接入 10–30 首真实 Suno / Udio / AI 音乐样本；
- 每首生成多个处理版本；
- 输出结果可追踪；
- 形成真实工程数据。

### 通过标准

```text
10–30 首真实 AI 音乐完成批量处理
```

### 当前状态

待执行。

---

## Gate 4｜长时稳定运行

### 要求

- 支持 24h 运行；
- 支持 36h 运行；
- 日志不丢失；
- 失败任务可追踪；
- 系统不会因单个任务失败而中断。

### 通过标准

```text
24h Run 成功完成，且最终报告完整生成
```

### 当前状态

待执行。

---

## Gate 5｜工程地基采纳

### 要求

- Runtime 成为 Moodify 默认云端运行系统；
- 后续 MRS、Night Worker、Daily Run 都基于该节点运行；
- 文档、日志、报告和目录结构稳定。

### 通过标准

```text
MT-001 状态从 ACTIVE 升级为 ADOPT
```

### 当前状态

未完成。


