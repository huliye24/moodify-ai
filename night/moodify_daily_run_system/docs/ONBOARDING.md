# Moodify Daily Run System Onboarding

## 1. 快速开始

```bash
cd /home/ubuntu/moodify-o3is

# 如果还没有配置
cp configs/runtime_config.example.json configs/runtime_config.json

# 创建目录
mkdir -p data/night_inputs data/moodify_runtime outputs/daily_runs reports/daily_runs logs

# 生成测试音频
python3 examples/generate_test_audio.py

# dry-run
bash scripts/smoke_test.sh
```

## 2. 如果 dry-run 成功

检查 `configs/runtime_config.json` 里的 `command_templates`。

你需要确认当前 Moodify 的真实 CLI 参数，例如：

```bash
python3 cli.py process --help
```

然后保留正确的一条，例如：

```json
"{python} cli.py process --input {input} --output {output_dir} --preset {preset}"
```

## 3. 正式运行

```bash
bash scripts/run_daily.sh
```

## 4. 常见问题

### 找不到 moodify_runtime

确认你在项目根目录执行：

```bash
python3 -m moodify_runtime.cli --help
```

### CLI 参数错误

运行：

```bash
python3 cli.py process --help
```

修改 `configs/runtime_config.json` 的 `command_templates`。

### 没有音频被登记

检查：

```bash
ls data/night_inputs/
```

支持：

```text
.wav .mp3 .flac .m4a .aac .ogg
```

### 队列没有新任务

可能是样本已经登记且任务已经生成。查看：

```bash
cat data/moodify_runtime/input_registry.jsonl
cat data/moodify_runtime/run_queue.jsonl
```

## 5. 推荐每日节奏

```text
白天：挑样本、看报告、写复盘
晚上：云端自动跑
第二天：看 daily_report 和 craft_memory_seed
每周：整理有效工艺卡
每月：升级一版参数策略或 MRS 公式
```
