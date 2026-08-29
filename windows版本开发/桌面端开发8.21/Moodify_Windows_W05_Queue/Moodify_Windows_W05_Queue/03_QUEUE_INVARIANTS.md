# Queue Invariants

## Q-01 Queue ≠ Playlist
Queue 是播放会话状态，Playlist 是长期收藏结构。

## Q-02 Queue ≠ Playback
Queue 决定顺序，Playback 决定音频执行。

## Q-03 QueueItem → Track
QueueItem 只引用稳定 Track identity，不复制 Track business truth。

## Q-04 Queue Mutation Is Local
```text
reorder/remove/clear Queue
```
不得修改 Playlist 或 Library。

## Q-05 QueueItem Identity
如果 Queue 允许同一 Track 多次出现，必须有独立 QueueItem ID。

## Q-06 Current Item Explicit
不能只靠数组 index + current Track 猜当前项，尤其当存在重复 Track 时。

## Q-07 Reorder Preserves Current Playback
Queue reorder 不应无故切歌。

## Q-08 Ended Advances Once
同一次播放结束只能推进一次。

## Q-09 Stale Playback Events Cannot Mutate Queue
旧 generation 的 ended/error 不得推进当前 Queue。

## Q-10 Error Skip Is Bounded
不能无限 skip。

## Q-11 Clear Is Non-destructive
Clear Queue 不删除 Track、Playlist、文件。

## Q-12 Queue Source Policy Explicit
Playlist → Queue 是 snapshot 还是 live 必须明确。

推荐 snapshot。

## Q-13 No Hidden Persistence Authority
W05 可留 persistence seam，但不要再建与 W08 冲突的恢复系统。

## Q-14 No Autoplay Recommendation
Queue 空了就是空了。
W05 不自动推荐下一首。
