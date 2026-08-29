# Moodify Windows Desktop Completion — W03 Playlist 完整闭环

**Package ID:** `MFY-WIN-W03-PLAYLIST-001`  
**日期：** 2026-08-21  
**阶段：** Windows Desktop Completion / 03 of 12  
**任务类型：** Core implementation / Playlist System  
**CANON_CHANGE：** `NO`  
**VISUAL_REDESIGN：** `FORBIDDEN`  
**前置依赖：** W02 `W03_GATE = PASS`  
**下一包：** W04 — Playback Core 播放核心

---

## 1. W03 的目标

W03 只解决一个产品问题：

> 用户已经拥有 Music Library 之后，可以把 Track 稳定地组织成歌单，并且这些歌单在重启后仍然存在、可以继续播放。

本包要完成：

```text
Library Track
→ Create Playlist
→ Add Track
→ PlaylistItem
→ Persist
→ Reorder
→ Remove
→ Restart
→ Still Correct
```

这一步完成后，Windows 端才第一次具备真正的“音乐管理”能力。

---

## 2. 强制前置门槛

执行 W03 前必须读取：

```text
artifacts/windows/w02/W02_IMPLEMENTATION_REPORT.md
artifacts/windows/w02/library-authority.md
artifacts/windows/w02/track-identity.md
artifacts/windows/w02/persistence-change.md
artifacts/windows/w02/W03_HANDOFF.md
```

必须确认：

```text
W02_STATUS = PASS
W03_GATE = PASS
```

否则：

```text
W03_STATUS = BLOCKED
```

禁止在 W02 未稳定时自行重建 Track / Library / persistence。

---

## 3. 本包建设边界

### 要做

- 创建歌单
- 重命名歌单
- 删除歌单
- 添加单首 Track 到歌单
- 批量添加 Track
- 从歌单移除 Track
- 歌单内排序 / 重排
- 统计歌曲数
- 重启恢复
- Playlist / PlaylistItem 持久化
- 右键“添加到歌单”
- 从 Library 到 Playlist 的引用
- 从 Playlist 发起播放
- 处理 unavailable Track
- migration（仅必要时）
- 自动化测试
- evidence

### 不做

- Queue 完整系统
- Shuffle / Repeat 的正式逻辑
- Favorites
- History
- Search / recommendation
- Cloud playlist sync
- 社交歌单
- 协作歌单
- 皮肤社区
- Windows 系统媒体键
- Release hardening
- UI redesign

---

## 4. 核心产品原则

### Playlist 是长期组织，不是 Queue

```text
Playlist = 长期组织结构
Queue = 当前播放顺序
```

本包不得让 Playlist 直接成为播放会话的唯一状态。

W04/W05 会分别处理 Playback / Queue。

### PlaylistItem 引用 Track，不复制 Track

推荐关系：

```text
Playlist
 └── PlaylistItem
       └── track_id → Track
```

禁止把整份 Track metadata 复制到 PlaylistItem 中作为第二套 authority。

### 删除歌单不删除歌曲

```text
Delete Playlist
≠
Remove Track from Library
≠
Delete original file
```

三者必须严格分离。

---

## 5. W03 完成后的用户体验

用户应该可以自然完成：

```text
新建“夜晚”
→ 右键歌曲
→ 添加到歌单
→ 夜晚
→ 打开歌单
→ 看见歌曲
→ 调整顺序
→ 删除其中一首
→ 重启 Moodify
→ 歌单和顺序仍然存在
```

如果其中任一关键环节依赖临时内存状态，本包不算完成。
