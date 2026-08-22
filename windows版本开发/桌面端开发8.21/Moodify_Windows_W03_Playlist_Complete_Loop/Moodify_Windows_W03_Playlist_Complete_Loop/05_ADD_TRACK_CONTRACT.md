# Add Track to Playlist Contract

这是 W03 的核心功能契约。

## 1. Use Case

```text
addTrackToPlaylist(playlist_id, track_id)
```

或现有架构的等价 use-case。

## 2. Preconditions

- Playlist exists
- Track exists
- Track ID stable
- Persistence available

Track `UNAVAILABLE` 不一定阻止添加，取决于现有模型，但必须有确定行为。

## 3. Recommended Result

```text
ADDED
ALREADY_IN_PLAYLIST
PLAYLIST_NOT_FOUND
TRACK_NOT_FOUND
FAILED
```

## 4. Idempotency

如果不允许 duplicate：

```text
add(P1, T1)
add(P1, T1)
→ exactly one canonical relation
```

## 5. Ordering

第一次添加默认：

```text
position = end
```

如果批量添加：

```text
preserve user selection order
```

除非现有产品定义另有规则。

## 6. UI Path

优先：

```text
Track context menu
→ 添加到歌单
→ Playlist Name
```

所有 UI 入口必须调用同一个 domain use-case。

## 7. Persistence

成功必须以持久化完成为准，而不是仅 UI optimistic update。

如使用 optimistic UI，失败时必须 rollback。

## 8. Non-goals

本 contract 不负责：

- Queue insertion
- Play next
- Favorite
- Cloud sync
