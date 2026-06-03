# Runtime Integration Commands｜MT-003

## Runtime 不启用 MRS

```bash
python3 -m moodify_runtime.run --scoring off
```

## Runtime 启用 quick_mrs

```bash
python3 -m moodify_runtime.run --scoring quick_mrs
```

## Runtime 启用 full_mrs

```bash
python3 -m moodify_runtime.run --scoring full_mrs
```

## 推荐生产策略

- 日常批量：quick_mrs
- 关键样本：full_mrs
- 主流程压力大：off
