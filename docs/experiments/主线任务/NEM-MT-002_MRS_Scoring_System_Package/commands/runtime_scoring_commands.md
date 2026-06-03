# Runtime Scoring Commands

## 不启用 MRS

```bash
python3 -m moodify_runtime.run --scoring off
```

## 启用 quick_mrs

```bash
python3 -m moodify_runtime.run --scoring quick_mrs
```

## 启用 full_mrs

```bash
python3 -m moodify_runtime.run --scoring full_mrs
```

## 启用指定 MRS Open 版本

```bash
python3 -m moodify_runtime.run --scoring mrs_open_v031
```

## 原则

MRS 必须作为可选评分列，不应阻塞主音频处理任务。


## MT-002 Post-run Manifest Scoring

```bash
cd /home/ubuntu/moodify-mainline
.venv/bin/python scripts/mt002_mrs_score_manifest.py \
  --manifest outputs/mt001_gate3_real_ai/mt001_gate3_real_ai_20260603/manifest.csv \
  --run-id mt002_mrs_baseline_gate3_20260603 \
  --output-dir reports/mt002_mrs_baseline \
  --expected-records 90 \
  --require-complete
```

This keeps MRS optional and post-run: Runtime outputs are not mutated, and scoring failure is recorded in MT-002 evidence instead of blocking audio processing.
