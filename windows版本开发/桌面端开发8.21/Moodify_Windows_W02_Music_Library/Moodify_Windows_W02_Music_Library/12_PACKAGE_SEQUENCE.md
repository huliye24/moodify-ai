# Windows Desktop Completion Sequence

当前编排：

```text
W01 现状审计 / 产品模型 / 开发冻结
↓
W02 Music Library                    ← 当前包
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
W08 Recovery & Resilience
↓
W09 Windows Native Integration
↓
W10 Cloud Bridge
↓
W11 Settings & Audio Environment
↓
W12 Release Hardening
```

## W02 的位置

W02 是后续所有功能的“地基”。

没有稳定 Track：

- Playlist 无法引用
- Queue 会复制数据
- History 会漂移
- Favorite 会重复
- Cloud mapping 会重做
- Player 会继续依赖临时文件对象

因此 W02 的完成标准不是“能显示歌曲列表”，而是：

> Track 成为一个真正稳定的产品实体。
