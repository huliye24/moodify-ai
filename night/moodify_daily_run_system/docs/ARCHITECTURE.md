# Moodify Daily Run System Architecture

## 1. 定位

Moodify Daily Run System 是 Moodify 的外层 Runtime，不是核心 DSP 算法库。

它的职责是：

```text
样本管理
运行队列
云端夜跑
指标记录
失败分析
日报生成
工艺记忆
下一轮实验建议
```

它不负责：

```text
音频处理算法本身
v01 / legacy 重构
MRS 正式公式定义
API 服务
前端界面
```

## 2. 分层结构

```text
Moodify Core
  v01 / legacy / DSP / CLI
        ↑
        │  通过 command_templates 调用
        │
Moodify Daily Run System
  registry → queue → runner → metrics → report → craft memory → planner
```

## 3. 为什么不侵入核心代码？

当前 Moodify 已经存在 v01 与 legacy 双线结构。  
Daily Run System 先作为外层调度层生长，可以避免今晚为了自动化而破坏核心工程。

## 4. 数据流

```text
data/night_inputs/*.wav
  ↓ register
data/moodify_runtime/input_registry.jsonl
  ↓ plan
data/moodify_runtime/run_queue.jsonl
  ↓ run
outputs/daily_runs/<run_id>/
  ├── daily_run.log
  ├── manifest.csv
  ├── summary.json
  └── <sample_id>/<preset>/metrics_before_after.json
  ↓ report
reports/daily_runs/daily_report_<run_id>.md
  ↓ craft
data/moodify_runtime/craft_memory/craft_memory_seed_<run_id>.md
```

## 5. 核心原则

1. 每日重复运行才是数据来源。
2. 每个任务必须可追踪。
3. 每次失败必须被记录。
4. 每个输出必须能关联输入、preset、参数和指标。
5. 报告不是装饰，是第二天复盘入口。
6. 工艺记忆比单次运行结果更重要。
