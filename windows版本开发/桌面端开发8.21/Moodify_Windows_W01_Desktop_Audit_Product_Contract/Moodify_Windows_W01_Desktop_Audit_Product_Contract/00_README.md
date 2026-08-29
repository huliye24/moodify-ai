# Moodify Windows Desktop Completion — W01

**Package ID:** `MFY-WIN-W01-DESKTOP-AUDIT-001`  
**日期：** 2026-08-21  
**阶段：** Windows Desktop Completion / 01 of 12  
**任务类型：** Audit-first / Architecture Discovery / Product Contract  
**CANON_CHANGE：** `NO`  
**VISUAL_REDESIGN：** `FORBIDDEN`  
**下一包：** W02 — Music Library 本地音乐库（本包不得开始 W02）

---

## 1. 任务目的

W01 不以“马上补更多功能”为目标，而是先把当前 Moodify Windows Desktop 的真实结构查清楚，并建立后续 W02–W12 共用的产品与数据骨架。

本包要回答：

```text
UI
↓
Runtime / Desktop Shell
↓
Player State
↓
IPC / API
↓
Domain Model
↓
Persistence
↓
File System
↓
Tests
↓
Build / Release
```

任何一个环节的真实 authority 不清楚，后续功能都会继续以临时状态、重复数据结构或局部补丁的方式增长。

---

## 2. 当前产品边界

执行者进入仓库后必须先读取仓库 authority，至少包括：

1. `AGENTS.md`
2. `docs/canon/CURRENT_CANON.md`
3. `docs/canon/PRODUCT_BOUNDARY.md`
4. `docs/canon/AUTHORITY_ORDER.md`
5. `docs/canon/CURRENT_ARCHITECTURE.md`
6. `docs/REPOSITORY_STATUS.md`
7. `docs/brand/public/README.md`

本包服从当前 Canon：

- 对外产品只有 **Moodify Music / Moodify Player**
- 第一阶段核心用户动作是 **PLAY**
- Moodify Ear / 分轨 / 判断 / Evidence / 内部生产链路保持内部复杂度
- 不把内部工程复杂度重新暴露到公开播放器
- 不创建第二个公开产品身份
- 不静默改 Canon
- 不虚构未验证的云端能力

---

## 3. W01 的核心产物

W01 完成时，应形成下面这些真实、可复用的事实：

- Windows 桌面端真实代码位置
- 实际技术栈与启动入口
- UI 页面 / 组件 / 路由地图
- Track、Playlist、Queue、Playback 的当前 state owner
- 本地音乐导入链路
- 歌单创建与“添加歌曲到歌单”链路
- 播放核心链路
- 本地持久化方式与 schema
- 文件路径、移动、删除、重复导入行为
- IPC / API 边界
- 构建、打包、安装与测试入口
- 当前功能矩阵：WORKING / PARTIAL / PLACEHOLDER / BROKEN / MISSING / UNKNOWN
- “歌单创建后难以添加歌曲”的根因
- W02 的安全施工边界

---

## 4. 候选产品模型

W01 允许提出候选模型，但必须先审计现实，不得“看见候选模型就直接重构”。

候选实体：

```text
Track
Library
Playlist
PlaylistItem
Queue
PlaybackSession
Favorite
History
AppState
CloudTrack
```

真实实现应由 W01 证据确认后再决定。

---

## 5. 不允许做的事情

- 不重做当前 UI
- 不把界面改成 Spotify 式信息密集播放器
- 不因为看到旧代码就大规模删除
- 不新造第二套 store / state machine / queue authority
- 不把数据库、localStorage、JSON、SQLite 等任一方案先验指定为答案
- 不在审计结束前迁移持久化 schema
- 不在本包偷偷实现 W02–W12
- 不加入皮肤商城、社区、评论、AI 对话、EQ 工程面板等扩展功能
- 不以“能跑”为唯一完成标准

---

## 6. UI 冻结基准

`reference/current_windows_alpha.png` 是当前 Windows Alpha 的产品视觉参考。

W01 可以修复阻塞审计的最小问题，但不得改变其视觉方向。

后续功能优先通过：

1. 右键菜单 / contextual actions
2. 二级页面
3. modal / popover
4. 状态变化
5. 少量必要的 inline action

来扩展，而不是不断往首页堆按钮。

---

## 7. W01 结束条件

只有当 `08_W02_HANDOFF_GATE.md` 满足 PASS 条件时，才允许进入 W02。

若存在关键事实无法验证：

```text
W02_GATE = BLOCKED
```

并明确：

- blocker
- evidence
- missing fact
- owner / next action

不得用猜测把 UNKNOWN 改成 PASS。
