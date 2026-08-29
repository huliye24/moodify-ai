# Multi-select Model

## State

推荐：

```text
selected_ids
anchor_id
focused_id
```

ID 必须稳定。

## Rules

### Click
选中单项，清除其他项。

### Ctrl+Click
toggle。

### Shift+Click
根据当前 view order 选择 anchor 到 target 的范围。

### Ctrl+A
选中当前 view 内全部可操作项。

### Escape
清空 selection。

## View Mutation

### Sort Change
保留 selection by ID。

### Search Change
推荐：
- 保留仍存在于 result 的 selection
- 移除不可见项

也可全部清空，但必须固定。

### View Change
推荐清空。

## Duplicate Queue Items
Queue view 如果同 Track 多次出现，应按 QueueItem ID 选择，而不是 Track ID。
