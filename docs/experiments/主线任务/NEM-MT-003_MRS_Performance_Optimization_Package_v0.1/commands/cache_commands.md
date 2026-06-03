# Cache Commands｜MT-003

## 开启缓存

```bash
python3 -m moodify.mrs.score_batch --input-dir data/night_inputs --mode quick_mrs --cache on
```

## 清理缓存

```bash
rm -rf runs/cache/mrs_features/*
```

## 查看缓存大小

```bash
du -sh runs/cache/mrs_features
```
