# Queue Mutation Policy

## Play Next

```text
insert after current item
```

多个 Play Next 连续操作必须定义顺序。

推荐：

```text
latest Play Next goes directly next
```

例如：

```text
Current A
Play Next B
Play Next C
→ A, C, B
```

若产品希望 FIFO，也可以，但必须测试和固定。

## Append

```text
append tail
```

## Remove Future Item
立即移除。

## Remove Current Item
推荐：

```text
audio continues
current QueueItem becomes detached-current
on ended → advance to nearest surviving next
```

实现如果过于复杂，也可选择立即 next，但必须避免突然 stop。

## Reorder
reorder QueueItems，不更改 Track/Playlist。

## Clear
推荐：

```text
keep current playing item
remove all future items
```

这样用户点击清空队列不会立即中断音乐。

如果无 current Track：

```text
Queue becomes empty
```
