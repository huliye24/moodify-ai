# Moodify Daily Run System Data Schema

## 1. input_registry.jsonl

每行一个输入样本。

```json
{
  "sample_id": "SMP_XXXX",
  "path": "data/night_inputs/song.wav",
  "filename": "song.wav",
  "source": "suno",
  "genre": "cinematic pop",
  "vocal_type": "female",
  "notes": "空间感贴片，高频偏亮",
  "size_bytes": 123456,
  "suffix": ".wav",
  "registered_at": "2026-06-02T00:00:00Z",
  "status": "active",
  "tags": [],
  "extra": {}
}
```

## 2. run_queue.jsonl

每行一个待处理任务。

```json
{
  "task_id": "TASK_SMP_XXXX_warm_vocal",
  "sample_id": "SMP_XXXX",
  "input_path": "data/night_inputs/song.wav",
  "preset": "warm_vocal",
  "status": "pending",
  "priority": 5,
  "reason": "daily_run",
  "created_at": "...",
  "started_at": null,
  "finished_at": null,
  "run_id": null,
  "output_dir": null,
  "attempts": 0,
  "last_error": null
}
```

## 3. manifest.csv

每次运行的任务结果。

字段：

```text
run_id
task_id
sample_id
input_path
preset
status
return_code
elapsed_seconds
output_dir
template_index
pseudo_mrs_before
pseudo_mrs_after
pseudo_delta_mrs
error
```

## 4. metrics_before_after.json

每个任务输出目录下的指标文件。

```json
{
  "input": {},
  "outputs": [],
  "best_output": {},
  "pseudo_mrs_before": 75.1,
  "pseudo_mrs_after": 78.2,
  "pseudo_delta_mrs": 3.1,
  "note": "pseudo_mrs_v001 是 Daily Run v0.1 占位指标，不是正式 MRS。"
}
```

## 5. craft_memory_seed.md

每日工艺记忆种子文件，不是最终结论。

它用于第二天人工复盘：

```text
哪些 preset 有效
哪些样本退化
哪些失败需要修
下一轮实验应该扩大哪里
```
