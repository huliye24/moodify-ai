# Moodify Windows Desktop Completion — W09 Windows Native Integration 系统融合

**Package ID:** `MFY-WIN-W09-WINDOWS-NATIVE-001`  
**日期：** 2026-08-21  
**阶段：** Windows Desktop Completion / 09 of 12  
**CANON_CHANGE：** `NO`  
**VISUAL_REDESIGN：** `FORBIDDEN`  
**前置：** W08 `W09_GATE = PASS`  
**下一包：** W10 Moodify Cloud Bridge

## 目标

W09 把已经稳定的 Track / Playback / Queue / Recovery 接入 Windows：

```text
Media Keys
→ System Media Controls
→ Track Metadata
→ Single Instance
→ Open With / Open File
→ Tray / Taskbar
```

原则：

> Windows 是 Moodify 的系统适配层，不是第二套播放器。

系统 Play/Pause 必须路由到 W04 Playback；Previous/Next 必须路由到 W05 Queue；系统展示的歌曲信息只来自 Track authority。

本包不做完整安装器、自动更新、云端处理、设置中心、DSP、UI 重设计。文件关联的“应用侧接收能力”可在 W09 完成，但真正 installer 注册可留到 W12。

最终体验应包括：

```text
键盘媒体键暂停/继续
系统媒体面板显示当前歌曲
系统下一首推动 Moodify Queue
第二次启动只激活已有 Moodify
“用 Moodify 打开”音频时交给主实例
退出前正常写入 W08 恢复状态
```
