# Moodify Windows Desktop Completion — W07 Desktop Interaction 桌面交互层

**Package ID:** `MFY-WIN-W07-DESKTOP-INTERACTION-001`  
**日期：** 2026-08-21  
**阶段：** Windows Desktop Completion / 07 of 12  
**任务类型：** Product implementation / Desktop Interaction  
**CANON_CHANGE：** `NO`  
**VISUAL_REDESIGN：** `FORBIDDEN`  
**前置依赖：** W06 `W07_GATE = PASS`  
**下一包：** W08 — Recovery & Resilience 状态恢复与韧性

---

## 1. W07 的目标

W07 解决：

> Moodify 已经有音乐库、歌单、播放、队列和搜索，但它还需要真正“像一个 Windows 软件一样好用”。

本包不再新增核心业务对象，而是把已经稳定的 use-cases 接入真正的桌面交互：

```text
Mouse
Keyboard
Drag & Drop
Multi-select
Context Menu
Explorer Integration
→ Existing Domain Use Cases
```

核心目标：

```text
用户不必依赖“到处找按钮”
而是自然地：
双击
右键
拖拽
多选
批量操作
```

---

## 2. 强制前置门槛

执行前读取：

```text
artifacts/windows/w06/W06_IMPLEMENTATION_REPORT.md
artifacts/windows/w06/library-view-contract.md
artifacts/windows/w06/W07_HANDOFF.md
```

必须确认：

```text
W06_STATUS = PASS
W07_GATE = PASS
```

否则：

```text
W07_STATUS = BLOCKED
```

---

## 3. 本包要做

- 右键菜单统一化
- 双击 Track 播放
- 拖本地文件进入窗口导入
- 拖 Track 到 Playlist
- 多选
- 批量加入 Playlist
- 批量加入 Queue
- 批量收藏 / 取消收藏
- 批量从 Library 移除
- Delete / Backspace 的安全交互
- Enter / Space 等轻量键盘操作
- Reveal in Explorer
- 拖拽/多选状态视觉反馈
- Windows 路径/拖放边界安全
- interaction regression tests
- evidence

---

## 4. 本包不做

- 新业务 authority
- 新播放器
- 新 Queue
- 全局快捷键
- 系统媒体键
- 托盘
- 文件关联
- SMTC
- 开机自启
- 自动更新
- 云端上传
- UI 重设计
- skin/community
- Ear/DSP/Evidence UI

---

## 5. 核心原则

### Interaction 只调用已有 use-case

例如：

```text
右键“下一首播放”
→ Queue.playNext(track_id)
```

而不是：

```text
右键组件
→ 自己修改 queue array
```

### Drag & Drop 不建立第二套导入链

```text
File Drop
→ W02 Import Use Case
```

### Multi-select 是 UI selection state

多选不是新的业务集合 authority。

### 删除相关操作必须非常安全

```text
从歌单移除
从播放队列移除
从音乐库移除
删除原始文件
```

必须严格区分。

W07 仍然禁止删除用户原始音频文件。

---

## 6. 用户体验目标

完成后用户应可以自然做到：

```text
从资源管理器拖 20 首歌进 Moodify
→ 自动导入
→ Ctrl 选中其中 5 首
→ 右键加入某个歌单
→ 再拖一首歌到侧栏歌单
→ 双击播放
→ 右键“下一首播放”
→ 在资源管理器中定位
```

不需要为每一步找专门按钮。
