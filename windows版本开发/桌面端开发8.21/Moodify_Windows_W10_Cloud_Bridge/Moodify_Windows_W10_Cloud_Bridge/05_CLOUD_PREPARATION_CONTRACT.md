# CloudPreparation Contract

推荐语义：

```text
CloudPreparation {
  id
  track_id
  status
  created_at
  updated_at
  error_code?
  prepared_source?
}
```

## Status

客户端标准化：

```text
NOT_REQUESTED
QUEUED
PREPARING
READY
FAILED
CANCELLED
UNKNOWN
```

真实 backend status 通过 adapter mapping。

## User Projection

```text
NOT_REQUESTED → 用 Moodify 准备
QUEUED/PREPARING → 正在准备…
READY → 准备完成
FAILED → 准备失败
UNKNOWN → 状态暂不可用
```

禁止用户看到 internal processing stages。

## READY Invariant

只有：

```text
prepared source can actually be resolved
```

才允许 READY。

如果 backend 说 completed 但 asset 不可播放：
客户端必须视为未完成/失败状态并记录 evidence。
