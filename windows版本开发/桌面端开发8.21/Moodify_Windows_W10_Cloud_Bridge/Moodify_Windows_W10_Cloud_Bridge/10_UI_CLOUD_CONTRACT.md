# W10 UI Cloud Contract

```text
VISUAL_REDESIGN = FORBIDDEN
```

## Allowed States

### Not Requested
```text
用 Moodify 准备
```

### Active
```text
正在准备…
```

### Ready
```text
准备完成
```

### Failed
```text
准备失败
重试
```

### Offline
```text
网络不可用
```

## Recommended Trigger

W10 初期推荐：

```text
MANUAL
```

避免批量导入后自动产生大量云任务。

## Forbidden UI

不展示：

```text
Ear
Stem
LALAL.AI
Audiolla
Judge
Intervene
Verify
Evidence
Worker
FFmpeg
Job State Machine
DSP presets
```

## Placement

优先：
- Track context action
- current Track secondary state
- lightweight detail row

不要重做首页。
