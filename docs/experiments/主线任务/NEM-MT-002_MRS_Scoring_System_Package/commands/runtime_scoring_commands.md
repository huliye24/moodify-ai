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
