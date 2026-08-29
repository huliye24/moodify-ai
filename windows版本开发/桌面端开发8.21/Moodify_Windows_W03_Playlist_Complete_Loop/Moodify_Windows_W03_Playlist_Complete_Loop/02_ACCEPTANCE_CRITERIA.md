# W03 Acceptance Criteria

## A. Preflight

- [ ] W02_STATUS = PASS
- [ ] W03_GATE = PASS
- [ ] Track authority 已复用
- [ ] Library authority 已复用
- [ ] Persistence authority 已复用
- [ ] 未创建 shadow Track store

## B. Playlist Authority

- [ ] 唯一 Playlist authority
- [ ] Playlist ID 稳定
- [ ] PlaylistItem relation 明确
- [ ] PlaylistItem 通过稳定 Track ID 引用 Track
- [ ] PlaylistItem 不复制 Track truth
- [ ] ordering 有持久化 authority
- [ ] UI 不成为 playlist truth

## C. Create / Rename / Delete

- [ ] create
- [ ] empty name validation
- [ ] Unicode / 中文
- [ ] rename
- [ ] rename restart persistence
- [ ] delete confirmation
- [ ] delete restart persistence
- [ ] delete playlist 不删除 Library Track
- [ ] delete playlist 不删除原始文件

## D. Add Track

- [ ] 单曲添加
- [ ] 批量添加 domain support
- [ ] context menu `添加到歌单`
- [ ] multiple playlist support
- [ ] repeated click deterministic
- [ ] duplicate add policy 已明确
- [ ] add restart persistence
- [ ] unavailable Track 行为明确
- [ ] 不通过 metadata copy 建立 relation

## E. Remove Track

- [ ] 从歌单移除
- [ ] Track 仍在 Library
- [ ] 原始文件未删除
- [ ] 其他歌单不受影响
- [ ] restart 后仍保持移除

## F. Reorder

- [ ] first → last
- [ ] last → first
- [ ] middle reorder
- [ ] repeated reorder
- [ ] restart 保留顺序
- [ ] unavailable Track 不破坏排序
- [ ] add/remove 后 position 仍正确
- [ ] DOM index / UI array 不是唯一 truth

## G. Playlist Detail

- [ ] 名称
- [ ] Track count
- [ ] Track list
- [ ] availability
- [ ] play action
- [ ] remove action
- [ ] reorder interaction
- [ ] 视觉保持当前 Moodify Alpha 方向

## H. Playback Integration

- [ ] Playlist Track 可调用 existing Player
- [ ] 不创建正式 Queue authority
- [ ] 删除 playlist 不使 current playback crash
- [ ] unavailable Track 安全失败
- [ ] Player 不成为 Playlist authority

## I. Persistence / Migration

- [ ] Playlist 持久化
- [ ] PlaylistItem 持久化
- [ ] ordering 持久化
- [ ] migration 如有则可重复
- [ ] 旧数据未静默丢失
- [ ] schema mismatch 不 reset all

## J. Tests / Evidence

- [ ] domain tests
- [ ] persistence tests
- [ ] UI integration tests
- [ ] referential-safety tests
- [ ] restart tests
- [ ] regression tests
- [ ] evidence manifest

## PASS Rule

必须满足：

```text
Stable Playlist
+ Stable PlaylistItem relation
+ Add
+ Remove
+ Reorder
+ Rename
+ Delete
+ Restart
+ No Track/File data loss
```

才允许：

```text
W03_STATUS = PASS
W04_GATE = PASS
```
