# Moodify Daily Run System v0.1

> 代码是工程的身体，重复工作流是工程的代谢。  
> Moodify Daily Run System 用来把每天重复的音频处理工作，变成可积累的数据、指标、报告和工艺记忆。

这是一个可以放进 `moodify-o3is` 根目录的外层 Runtime 代码库。它**不侵入** Moodify 的 v01 / legacy 核心代码，只通过现有 CLI 调用处理流程。

## 1. 它解决什么问题？

Moodify 不能只靠偶尔实验生长，必须形成每日重复工作流：

```text
输入样本
  ↓
样本登记 input_registry.jsonl
  ↓
生成任务 run_queue.jsonl
  ↓
云端夜间自动处理
  ↓
保存 manifest / metrics / logs
  ↓
生成 daily_report.md
  ↓
沉淀 craft_memory_seed.md
  ↓
第二天复盘，进入下一轮实验
```

## 2. 核心目录

```text
moodify_runtime/
  config.py          配置加载
  registry.py        样本登记系统
  queue.py           运行队列系统
  runner.py          每日运行器
  metrics.py         基础指标与 pseudo MRS 占位
  report.py          日报生成
  craft_memory.py    工艺记忆种子
  failure.py         失败分析
  planner.py         下一轮建议
  cli.py             命令入口

configs/
  runtime_config.example.json

scripts/
  install_into_moodify.sh
  run_daily.sh
  schedule_daily.sh
  smoke_test.sh

docs/
  ARCHITECTURE.md
  ONBOARDING.md
  DATA_SCHEMA.md
```

## 3. 安装到 Moodify

把本代码库复制到 `moodify-o3is` 根目录后执行：

```bash
cd /home/ubuntu/moodify-o3is
bash scripts/install_into_moodify.sh
```

把音频放进：

```text
data/night_inputs/
```

## 4. 先生成测试音频

```bash
python3 examples/generate_test_audio.py
```

## 5. Smoke Test

```bash
bash scripts/smoke_test.sh
```

这个命令只做 dry-run，不真正处理音频，用来验证 registry / queue / command template。

## 6. 正式每日运行

```bash
bash scripts/run_daily.sh
```

它会依次执行：

```bash
python3 -m moodify_runtime.cli register
python3 -m moodify_runtime.cli plan
python3 -m moodify_runtime.cli run
python3 -m moodify_runtime.cli report
python3 -m moodify_runtime.cli craft
python3 -m moodify_runtime.cli next
```

## 7. 晚上定时运行

例如服务器时间 23:30 开始：

```bash
bash scripts/schedule_daily.sh 23:30
```

## 8. 第二天看结果

```bash
ls outputs/daily_runs/
cat outputs/daily_runs/<run_id>/summary.json
cat reports/daily_runs/daily_report_<run_id>.md
cat data/moodify_runtime/craft_memory/craft_memory_seed_<run_id>.md
```

## 9. 重要说明：pseudo MRS 不是正式 MRS

`metrics.py` 里包含 `pseudo_mrs_v001`，它只是 Daily Run v0.1 的工程占位指标，用来验证“处理前后可比较”的数据链路。

正式版本应替换为：

```text
MRS v0.2 / v0.3
```

也就是你正在建立的 Moodify Reality Score 体系。

## 10. 这个系统的长期目标

从：

```text
能跑
```

升级为：

```text
能记
能算
能比
能报告
能复盘
能沉淀
能生成下一轮实验
```

这就是 Moodify 从脚本变成工程体系的第一步。
