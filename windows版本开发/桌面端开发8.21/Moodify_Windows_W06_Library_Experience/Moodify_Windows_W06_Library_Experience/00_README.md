# Moodify Windows Desktop Completion — W06 Library Experience 音乐管理体验

**Package ID:** `MFY-WIN-W06-LIBRARY-EXPERIENCE-001`  
**日期：** 2026-08-21  
**阶段：** Windows Desktop Completion / 06 of 12  
**任务类型：** Product implementation / Library Experience  
**CANON_CHANGE：** `NO`  
**VISUAL_REDESIGN：** `FORBIDDEN`  
**前置依赖：** W05 `W06_GATE = PASS`  
**下一包：** W07 — Desktop Interaction 桌面交互层

---

## 1. W06 的目标

W06 不再扩展底层播放系统，而是解决：

> 当 Music Library 里开始有几十、几百甚至几千首歌时，用户怎么快速找到自己想听的音乐？

本包建立：

```text
Library
→ All Songs
→ Recently Added
→ Recently Played
→ Favorites
→ Search
→ Sort
→ Metadata Browsing
→ Play / Queue / Playlist Actions
```

W06 完成后，Moodify Windows 应从“能播歌”进入“能日常管理音乐”。

## 2. 强制前置门槛

执行前必须读取：

```text
artifacts/windows/w05/W05_IMPLEMENTATION_REPORT.md
artifacts/windows/w05/queue-authority.md
artifacts/windows/w05/queue-source-policy.md
artifacts/windows/w05/W06_HANDOFF.md
```

必须确认：

```text
W05_STATUS = PASS
W06_GATE = PASS
```

否则：

```text
W06_STATUS = BLOCKED
```

禁止因为要做搜索、收藏、最近播放而重建 Track / Library / Playlist / Playback / Queue。

## 3. 本包要做

- All Songs 全部歌曲
- Recently Added 最近添加
- Recently Played 最近播放
- Favorites 收藏
- Search 搜索
- Sort 排序
- 基础 metadata browsing
- History / Favorite 最小 authority
- 与 Playlist / Queue / Playback 联动
- restart persistence
- empty states
- performance baseline
- tests / evidence

## 4. 不做

- 大型专辑/艺术家详情系统
- 推荐算法
- AI 搜索
- 云端歌词
- 社交
- 评分/评论
- 智能歌单
- 复杂筛选器
- skin/community
- DSP/EQ
- Windows native integration
- release hardening
- visual redesign

## 5. 核心原则

### Library Experience 是 View，不是第二套 Library

```text
All Songs
Recently Added
Recently Played
Favorites
Search Results
```

都必须是现有 Track/Library authority 上的派生视图。

### Favorites 是 relation

```text
Favorite → track_id
```

不是复制一份 Track。

### Recently Played 是 History projection

```text
Playback Event
→ History
→ Recently Played View
```

不是 UI 临时数组。

### Search / Sort 不改变 authority

Search 和 Sort 只影响 projection，不改变 Track identity、Playlist order 或 Queue order。

## 6. 最终用户体验

```text
打开全部歌曲
→ 搜索“夜”
→ 找到歌曲
→ 收藏
→ 下一首播放
→ 加入歌单
→ 之后在“收藏”里找到
→ 播放后出现在“最近播放”
→ 重启后这些状态仍然存在
```
