# Autoplay / Close / Startup Policy

## App Launch

默认：

```text
NO AUTOPLAY
```

W08 恢复 current Track/position，但恢复为 PAUSED/READY。

## Explicit Open With

用户显式双击音频：
继续服从 W09：
```text
open file → import/resolve → play
```

## Cloud READY

云处理完成不能无条件突然播放。

## Close

默认：

```text
Close Window = Quit
```

如果 W09 tray 支持且用户设置：

```text
Close Window = Minimize To Tray
```

才改变行为。

## Explicit Quit

无论 close behavior 是什么：

```text
Quit
→ W08 flush
→ teardown
→ exit
```

## Launch At Startup

仅真实支持时提供。
默认 OFF。

即使 ON：
```text
launch silently/normally
but no autoplay
```
