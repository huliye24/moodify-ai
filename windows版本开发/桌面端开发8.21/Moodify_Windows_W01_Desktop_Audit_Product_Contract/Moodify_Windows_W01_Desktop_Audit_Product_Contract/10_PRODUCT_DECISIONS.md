# W01 Product Decisions — Frozen for this package

这些不是实现细节，而是 W01 用于避免无边界扩张的产品决策。

## D01 — First-class value

Windows 1.0 的价值不是“功能越多越好”，而是：

> 用户把音乐交给 Moodify，然后可以稳定、自然、持续地听下去。

## D02 — PLAY remains the center

所有 Library / Playlist / Queue / History / Settings 都是为 PLAY 服务，不改变公开产品身份。

## D03 — UI is not the problem to solve in W01

当前 Alpha 的视觉方向被冻结。

W01 解决的是：

- 事实不清
- 状态不清
- 数据关系不清
- 功能闭环不完整
- 重启与错误行为不清

不是重新设计界面。

## D04 — Playlist is a long-lived collection

Playlist 不等于 Queue。

```text
Playlist = 长期组织
Queue = 当前播放顺序
```

这条边界将直接影响 W03/W05。

## D05 — Import creates durable library state

“选择本地歌曲”不能只是把文件丢给 `<audio>` 播放一次。

W02 的目标将是把 Track 纳入可管理、可持久化、可引用的 Library。

W01 只负责确认当前到底做到了哪一步。

## D06 — Missing local file is a state, not an excuse to destroy relations

目标行为倾向：

```text
Track source missing
→ mark unavailable
→ preserve library / playlist identity
→ allow future repair/relink
```

最终实现仍需 W01 先确认现实架构。

## D07 — Feature expansion is layered

后续建设顺序：

```text
W01 Audit / Contract
W02 Library
W03 Playlist
W04 Playback
W05 Queue
W06 Library Experience
W07 Desktop Interaction
W08 Recovery
W09 Windows Native
W10 Cloud Bridge
W11 Settings / Audio Environment
W12 Release Hardening
```

W01 不提前跨包施工。
