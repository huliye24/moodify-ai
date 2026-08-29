# W03 Handoff Gate — Playlist

W03 只有在 Music Library 成为稳定 authority 后才可开始。

## Required

- [ ] W02_STATUS = PASS
- [ ] Track authority 唯一
- [ ] Library authority 唯一
- [ ] Track ID 稳定
- [ ] Track 可 restart 恢复
- [ ] Player 可通过 Track 播放
- [ ] duplicate import 已稳定
- [ ] missing source 不崩溃
- [ ] remove from library 不删除源文件
- [ ] persistence schema 明确
- [ ] migration 已完成或 NOT_REQUIRED
- [ ] W03 可通过 `track_id` 或等价稳定 ID 建 PlaylistItem relation

## W03 must reuse

```text
Track
Library
Persistence
Source Resolver
```

## W03 must not create

```text
PlaylistTrack copy with duplicated metadata
Raw file path arrays as new authority
Second Track store
Second Library store
Player-owned playlist truth
```

## Gate

满足上述条件：

```text
W03_GATE = PASS
```

否则：

```text
W03_GATE = BLOCKED
```
