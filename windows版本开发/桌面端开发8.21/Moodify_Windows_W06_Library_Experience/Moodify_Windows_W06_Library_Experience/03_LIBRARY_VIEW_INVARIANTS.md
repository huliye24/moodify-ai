# Library Experience Invariants

## L-01 Views Are Projections
All Songs / Recently Added / Recently Played / Favorites / Search Results 都不是新的 Library authority。

## L-02 Favorite Is Relation
```text
Favorite.track_id → Track.id
```

## L-03 History Is Event Data
History 可以多次记录同一 Track，但不复制 Track truth。

## L-04 Recently Played Is Derived
Recently Played 是 History 的 projection。

## L-05 Search Is Pure
Search 不改变 Track identity。

## L-06 Sort Is Pure
Sort 不写回 Playlist/Queue 顺序。

## L-07 Metadata Is Defensive
null / malformed metadata 不得 crash。

## L-08 Actions Reuse Domain Use Cases
不同 view 不得复制播放、排队、加歌单业务逻辑。

## L-09 Removal Is Non-destructive
W06 不删除用户原始文件。

## L-10 History Follows Playback Reality
History 不能只由 UI click 决定。

## L-11 No Recommendation Product
W06 不是推荐系统。

## L-12 No Visual Rebuild
只提升日常管理能力，不重做 Moodify 视觉。
