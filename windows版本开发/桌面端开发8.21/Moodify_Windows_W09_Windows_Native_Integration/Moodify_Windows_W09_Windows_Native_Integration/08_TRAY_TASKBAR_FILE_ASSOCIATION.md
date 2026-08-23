# Tray / Taskbar / File Association Policy

## Tray

如果 runtime 安全支持，菜单只需：

```text
打开 Moodify
播放/暂停
下一首
退出
```

W09 不默认把 Close 改成最小化到托盘。

Tray Quit 必须：

```text
W08 flush
→ playback/native teardown
→ release single-instance lock
→ exit
```

## Taskbar

优先：
- correct app identity/icon
- minimize/restore behavior
- window activation

不要为了数量加入无意义的 taskbar progress。

## File Association

W09 负责“应用可以接收文件”的能力。

真正安装器注册可留 W12。

支持扩展名必须来自真实 import/decode 支持列表，不可拍脑袋。

Windows 默认播放器选择属于用户；Moodify 不得强制抢占。
