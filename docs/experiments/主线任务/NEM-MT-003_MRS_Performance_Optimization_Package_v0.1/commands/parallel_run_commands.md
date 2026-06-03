# Parallel Run Commands｜MT-003

## 2 workers

```bash
python3 -m moodify.mrs.score_batch --input-dir data/night_inputs --mode quick_mrs --workers 2
```

## 4 workers

```bash
python3 -m moodify.mrs.score_batch --input-dir data/night_inputs --mode quick_mrs --workers 4
```

## 注意

并行数不能只看 CPU，还要看磁盘 I/O、内存和 WAV 中间文件大小。
