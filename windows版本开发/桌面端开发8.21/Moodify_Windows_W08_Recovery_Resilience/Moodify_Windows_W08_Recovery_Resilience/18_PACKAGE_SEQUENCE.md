# Windows Desktop Completion Sequence

```text
W01 现状审计 / 产品模型 / 开发冻结
↓
W02 Music Library
↓
W03 Playlist
↓
W04 Playback Core
↓
W05 Queue
↓
W06 Library Experience
↓
W07 Desktop Interaction
↓
W08 Recovery & Resilience             ← 当前包
↓
W09 Windows Native Integration
↓
W10 Cloud Bridge
↓
W11 Settings & Audio Environment
↓
W12 Release Hardening
```

W08 的意义：

> 从“这次打开能用”，进入“每次打开都可靠”。

做完这一层，W09 再去接系统媒体键、托盘、文件关联等 Windows 原生能力，才不会把不稳定 session 状态扩散进操作系统集成层。
