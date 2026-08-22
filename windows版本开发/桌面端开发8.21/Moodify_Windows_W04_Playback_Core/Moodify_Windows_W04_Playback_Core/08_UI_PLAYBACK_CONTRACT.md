# W04 UI Playback Contract

```text
VISUAL_REDESIGN = FORBIDDEN
```

## Current Controls

当前 Alpha 已有：

```text
Previous
Play
Next
```

W04 目标不是换样式，而是让它们真正工作。

## Minimal Additions

允许加入：

```text
progress bar
elapsed time
duration
volume
loading
error/unavailable message
```

保持视觉轻量。

## Enable / Disable

### Play

无 Track：

```text
disabled
```

Track ready/paused：

```text
enabled
```

### Previous / Next

依据当前 stable context 是否存在。

不要仅因为 UI 有按钮就强行造下一首。

## Loading

可以：

```text
播放按钮 loading state
```

或轻微文本反馈。

## Error

最小文案：

```text
无法播放这首歌曲
```

source missing：

```text
无法找到本地文件
```

## No Engineering UI

禁止显示：

- decoder logs
- source URI
- generation token
- engine state dump
- Ear / DSP / Evidence
