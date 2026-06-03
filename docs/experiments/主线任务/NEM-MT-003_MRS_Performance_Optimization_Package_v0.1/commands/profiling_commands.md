# Profiling Commands｜MT-003

> 以下命令为模板，应根据服务器真实脚本名称调整。

## 1. 单文件 profiling

```bash
python3 -m moodify.mrs.profile --input data/night_inputs/example.wav --mode quick_mrs --output reports/profiling_single.json
```

## 2. 批量 profiling

```bash
python3 -m moodify.mrs.profile_batch --input-dir data/night_inputs --mode quick_mrs --records reports/mrs_performance_records.jsonl
```

## 3. full_mrs 对照

```bash
python3 -m moodify.mrs.profile_batch --input-dir data/night_inputs --mode full_mrs --records reports/mrs_performance_full_records.jsonl
```

## 4. 查看最慢任务

```bash
sort -t',' -k total_time_sec reports/mrs_performance_records.csv | tail
```
