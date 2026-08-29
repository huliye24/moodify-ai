# Queue Source Policy

## Recommended Policy: SNAPSHOT

当用户：

```text
Play Playlist
```

执行：

```text
Playlist ordered Track refs
→ materialize Queue snapshot
```

之后：

- Queue reorder 不修改 Playlist
- Playlist reorder 不修改当前 Queue
- Playlist add/remove 不修改当前 Queue
- 下一次重新 Play Playlist 时再生成新 Queue

## 为什么

这是最稳定、最可理解的行为：

```text
Playlist = collection
Queue = session
```

否则用户在播放中编辑歌单时，当前播放顺序会发生不可预测变化。

## Library

若 Library 有稳定 visible ordering：

```text
Play Track
→ snapshot current Library ordering
→ cursor selected Track
```

若无稳定排序：

```text
Queue = selected Track only
```

禁止猜测排序。

## Future
W06 做 search/sort 后，Library queue materialization 必须明确到底基于：
- current filtered/sorted view
- canonical library order

W05 只按现有真实稳定顺序。
