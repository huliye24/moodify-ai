# Moodify Windows Desktop Completion — W02 Music Library

**Package ID:** `MFY-WIN-W02-MUSIC-LIBRARY-001`  
**日期：** 2026-08-21  
**阶段：** Windows Desktop Completion / 02 of 12  
**任务类型：** Core implementation / Local Music Library  
**CANON_CHANGE：** `NO`  
**VISUAL_REDESIGN：** `FORBIDDEN`  
**前置依赖：** W01 `W02_GATE = PASS`  
**下一包：** W03 — Playlist 歌单完整闭环

---

## 1. W02 的目标

W02 只解决一个核心问题：

> 把“用户选择了一首本地音乐”升级成“这首音乐成为 Moodify 中稳定、可持久化、可再次引用的 Track”。

本包不追求功能数量，而是建立 Windows 端后续所有播放、歌单、队列、历史、收藏都能复用的 **Music Library authority**。

目标链路：

```text
Local File
→ Validate
→ Identify
→ Read Metadata
→ Persist Track
→ Add to Library
→ Resolve Source
→ Player
→ Restart
→ Still Exists
```

---

## 2. 强制前置门槛

执行 W02 前，必须读取：

```text
artifacts/windows/w01/W01_AUDIT_REPORT.md
artifacts/windows/w01/state-authority-map.md
artifacts/windows/w01/persistence-audit.md
artifacts/windows/w01/playlist-add-root-cause.md
artifacts/windows/w01/W02_HANDOFF.md
```

如果：

```text
W02_GATE != PASS
```

则：

```text
W02_STATUS = BLOCKED
```

停止业务实现，只输出 blocker 报告。

禁止绕过 W01 的 UNKNOWN，自行猜测架构。

---

## 3. 本包建设边界

### 要做

- 建立 / 修复唯一 Track authority
- 建立 / 修复唯一 Library authority
- 本地单曲导入
- 本地多曲导入（若当前技术栈支持）
- 元数据读取
- 稳定 Track ID
- 路径规范化
- 重复导入处理
- Library 持久化
- restart 恢复
- missing / moved / renamed source 的安全状态
- remove from library
- player 从 Library Track 解析可播放 source
- migration（仅 W01 证明需要时）
- 自动化测试
- evidence

### 不做

- Playlist 完整功能
- Queue
- Favorites
- History
- Search / filter 的完整 UX
- Cloud sync
- CloudTrack production
- skin/community
- Ear / DSP / Evidence UI
- Windows 原生媒体键
- updater / installer 完整化
- 主界面重设计

---

## 4. 产品原则

### Library 是持久资产

```text
File Picker Result != Library
```

用户选择文件后，应用应产生稳定 Track，并被后续功能引用。

### Track identity 不能依赖标题

以下不能单独作为唯一 ID：

- title
- artist
- filename
- absolute path

最终 identity 策略必须服从 W01 的现实结构，并满足本包 invariant。

### 文件失效 ≠ Track 消失

推荐目标：

```text
source missing
→ Track.availability = UNAVAILABLE
→ relation preserved
→ UI can surface unavailable state
```

不要因为源文件移动就自动删除 Library / Playlist relation。

### Library 与 Player 解耦

Player 不应拥有第二份 Track truth。

```text
Player references Track
Library owns Track
```

---

## 5. 交付结果

W02 完成后应达到：

```text
导入音乐
→ Library 可见
→ 可播放
→ 重启仍存在
→ 重复导入不制造脏数据
→ 文件失效不崩溃
→ Library 中移除不删除原文件
```

W03 将直接复用 Track / Library authority 构建 Playlist relation。
