# Codex 执行任务书 — MFY-WIN-W01-DESKTOP-AUDIT-001

## 0. 执行身份

你正在执行 **Moodify Windows Desktop Completion W01**。

这是一次“先建立事实，再允许建设”的任务。

```text
CANON_CHANGE = NO
VISUAL_REDESIGN = FORBIDDEN
IMPLEMENTATION_MODE = AUDIT_FIRST
START_W02 = NO
```

---

## 1. 第一原则

### 1.1 先读 authority，再读实现

先读取并记录：

- `AGENTS.md`
- `docs/canon/CURRENT_CANON.md`
- `docs/canon/PRODUCT_BOUNDARY.md`
- `docs/canon/AUTHORITY_ORDER.md`
- `docs/canon/CURRENT_ARCHITECTURE.md`
- `docs/REPOSITORY_STATUS.md`
- `docs/brand/public/README.md`

如果文件路径发生变化，应寻找其当前等价 authority，并在报告中说明。

### 1.2 不预设 Windows 技术栈

不要因为任务背景提到过 Electron，就直接假设当前桌面端一定是 Electron。

必须从仓库和可运行证据确认：

- Windows 应用代码位置
- package / project manifest
- bootstrap / main entry
- renderer / UI entry
- desktop bridge / preload / native layer（如有）
- 打包方案
- 运行时版本

如果实际不是 Electron，按真实技术栈审计。

---

## 2. Phase A — Repository Discovery

建立 `artifacts/windows/w01/repository-map.md`。

至少定位：

- Windows app root
- desktop bootstrap
- renderer root
- routing
- player implementation
- audio element / engine / library
- data layer
- persistence layer
- IPC / native bridge
- API client
- tests
- build scripts
- packaging config
- update config（如有）
- assets
- shared contracts
- any reused web implementation

每个条目必须给出**实际路径**。

对找不到的条目标 `MISSING`，对无法确认的标 `UNKNOWN`。

---

## 3. Phase B — User Journey Audit

在可运行环境中，逐条验证以下用户路径。

### J01 冷启动 / Empty State

验证：

- 首次启动显示什么
- 无歌曲时是否稳定
- 是否出现空指针、错误 toast、console error
- “添加歌曲 / 选择本地歌曲”是否一致

### J02 添加单首本地歌曲

验证：

- 文件选择器
- 支持格式
- Track ID 如何生成
- 元数据如何读取
- 文件路径如何保存
- 重复导入行为
- 导入后 UI 是否即时更新
- 是否可播放

### J03 创建歌单

验证：

- 创建入口
- 名称校验
- 空歌单
- 持久化
- restart 后是否存在

### J04 添加歌曲到歌单 —— 本包最高优先级审计

必须真实执行：

```text
已有 Track
→ 已有 Playlist
→ 选择 Track
→ Add to Playlist
→ PlaylistItem / relation 产生
→ UI 更新
→ restart
→ relation 仍然存在
```

定位当前断点，并给出 root cause：

- UI 没入口？
- 入口存在但事件未接？
- store mutation 不完整？
- playlist schema 没 track relation？
- persistence 没写入？
- UI 没重新订阅？
- ID 类型不一致？
- 路径数据和 Track 数据混在一起？
- 只有 mock / local component state？
- 其他？

禁止只写“功能未完成”。

### J05 播放

验证：

- play
- pause
- previous
- next
- seek（如果存在）
- duration
- end-of-track
- unavailable source
- error handling

### J06 重启恢复

关闭应用后重新启动，核验：

- library
- playlists
- playlist items
- current track
- queue（如存在）
- playback position（如存在）
- volume（如存在）
- window state（如存在）

### J07 源文件失效

将已导入本地音频：

- rename
- move
- delete

分别测试。

观察系统是：

- crash
- silently disappear
- stale reference
- unavailable state
- re-link
- prompt
- other

---

## 4. Phase C — Function Matrix

使用本包的 `04_FUNCTION_MATRIX.csv` 作为起点。

状态只允许：

- `WORKING`
- `PARTIAL`
- `PLACEHOLDER`
- `BROKEN`
- `MISSING`
- `UNKNOWN`

Severity：

- `P0`：阻止桌面版形成基本闭环
- `P1`：严重影响日常播放与管理
- `P2`：体验缺口
- `P3`：非核心优化

每一项填写：

- UI entry
- code path
- state owner
- persistence
- IPC/API
- test coverage
- evidence

---

## 5. Phase D — State Authority Map

输出 `artifacts/windows/w01/state-authority-map.md`。

必须回答：

| Domain | 当前 source of truth | 谁写 | 谁读 | 是否持久化 | 冲突 |
|---|---|---|---|---|---|
| Track | ? | ? | ? | ? | ? |
| Library | ? | ? | ? | ? | ? |
| Playlist | ? | ? | ? | ? | ? |
| PlaylistItem | ? | ? | ? | ? | ? |
| Queue | ? | ? | ? | ? | ? |
| PlaybackSession | ? | ? | ? | ? | ? |
| Favorite | ? | ? | ? | ? | ? |
| History | ? | ? | ? | ? | ? |
| AppState | ? | ? | ? | ? | ? |
| CloudTrack | ? | ? | ? | ? | ? |

如果同一个 Domain 有两个竞争 authority，必须明确标记。

不要在 W01 直接“用第三套系统解决两套系统冲突”。

---

## 6. Phase E — Persistence Audit

记录：

- 存储技术
- 文件 / DB / browser storage 位置
- schema
- schema version
- migration
- backup / recovery
- atomicity
- corruption handling
- path portability
- data deletion
- upgrade compatibility

尤其验证：

```text
Playlist
↕
PlaylistItem
↕
Track
```

这三个关系当前究竟是持久化实体、嵌套数组、路径列表、临时 UI state，还是其他形式。

---

## 7. Phase F — File Identity Audit

本地音乐不能只从“界面上看起来存在”来判断。

记录当前系统如何识别 Track：

- raw absolute path
- normalized path
- file URI
- content hash
- metadata tuple
- generated UUID
- database ID
- server ID
- mixed identity

测试：

- 同一文件重复导入
- 同名不同文件
- 不同目录同名文件
- 文件移动
- Windows 大小写 / slash normalization
- Unicode / 中文 / 空格路径
- 超长路径（能测则测，不能测写明）

---

## 8. Phase G — Playback Architecture Audit

画出：

```text
User Action
→ UI event
→ player state
→ audio engine
→ source resolution
→ playback
→ event callbacks
→ UI update
→ persistence/history
```

确认：

- 播放引擎到底是什么
- single player or multiple instances
- current track authority
- next/prev 从哪里决定
- queue 与 playlist 是否耦合
- 播放错误如何回收
- 播放结束如何前进
- UI 与 engine 是否可能不同步

---

## 9. Phase H — Product Model Proposal

在完成现实审计后，使用 `05_PRODUCT_MODEL_CANDIDATE.md` 对照当前实现。

输出三类结论：

### KEEP
当前结构足够稳定，后续直接复用。

### REPAIR
概念正确，但实现不完整。

### MIGRATE
当前结构会阻塞 W02–W08，需要后续迁移。

任何 `MIGRATE` 都必须包含：

- current
- target
- why
- migration boundary
- data preservation
- rollback
- tests

W01 只提出 migration plan，不执行大迁移。

---

## 10. Phase I — UI Freeze Verification

读取 `06_UI_FREEZE_CONTRACT.md` 与参考图。

验证当前实现是否已经偏离。

本包禁止：

- 主导航大改
- 色彩系统重做
- 组件体系整体替换
- 加入工程型控制台
- 首页卡片化 / dashboard 化
- 大量新增主按钮

如果某个功能需要 UI，先写入后续包的 interaction proposal，不在 W01 顺手扩张。

---

## 11. Phase J — Build / Test / Release Reality

记录真实命令：

```text
install
dev
test
lint
build
package
run packaged app
```

确认：

- 能否在 Windows 构建
- 构建产物在哪里
- 是否有签名
- 是否有 installer
- app version 从哪里来
- 数据升级会不会丢
- CI 是否覆盖 Windows

无法验证的必须写 `BLOCKED`。

---

## 12. Required Outputs

所有审计产物写到：

`artifacts/windows/w01/`

至少：

1. `W01_AUDIT_REPORT.md`
2. `repository-map.md`
3. `function-matrix.csv`
4. `state-authority-map.md`
5. `playback-flow.md`
6. `persistence-audit.md`
7. `playlist-add-root-cause.md`
8. `product-model-assessment.md`
9. `build-test-reality.md`
10. `evidence-manifest.json`
11. `W02_HANDOFF.md`

可以补充截图、日志、测试结果，但不得提交私人音频或 secrets。

---

## 13. Allowed Code Changes

默认：**不改业务功能。**

仅允许：

- 为审计增加无副作用的诊断
- 修复使 W01 无法启动 / 无法验证的极小 blocker
- 增加测试 harness / fixture（不得改变产品行为）
- 文档与 evidence

任何行为变更必须在报告中单独列出。

---

## 14. Definition of Done

W01 结束时必须明确回答：

1. Windows Desktop 实际在哪里？
2. 实际技术栈是什么？
3. Track authority 是什么？
4. Playlist authority 是什么？
5. PlaylistItem relation 是什么？
6. “添加歌曲到歌单”为什么不完整？
7. Player authority 是什么？
8. Queue 是否存在？
9. Persistence authority 是什么？
10. restart 后哪些状态真实恢复？
11. missing file 会怎样？
12. build / test / package 是否真实可用？
13. W02 从哪里开始才不会重复造系统？
14. W02 Gate = PASS 还是 BLOCKED？

最后输出：

```text
W01_STATUS = PASS | BLOCKED
W02_GATE = PASS | BLOCKED
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```
