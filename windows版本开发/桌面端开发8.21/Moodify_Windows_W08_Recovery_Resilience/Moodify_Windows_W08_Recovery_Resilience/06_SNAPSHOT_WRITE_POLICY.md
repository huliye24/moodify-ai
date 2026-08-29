# Snapshot Write Policy

## Goal

可靠保存，不造成高频磁盘写入。

## Dirty Triggers

```text
track switch
playback pause
position checkpoint
volume settled
queue mutation
route/view change
window move/resize settled
graceful exit
```

## Position

不要每个 timeupdate 写。

建议：

```text
throttle ~10s
```

最终值根据 runtime 实测调整。

## Window

建议：

```text
debounce 500–1500ms
```

避免拖动窗口时连续写。

## Atomicity

如果文件：
```text
write temp
→ flush if practical
→ atomic rename
```

如果 DB：
```text
transaction
```

## Failure

写失败：
- log
- keep app running if safe
- next checkpoint retry
- do not clear previous valid snapshot
