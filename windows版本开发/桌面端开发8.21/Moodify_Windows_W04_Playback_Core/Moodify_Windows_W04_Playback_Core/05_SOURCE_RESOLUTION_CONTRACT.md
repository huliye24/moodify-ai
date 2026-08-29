# Source Resolution Contract

## Goal

Playback 永远从稳定 Track identity 出发。

```text
track_id
→ Track authority
→ source resolver
→ playable source
→ engine
```

## Resolver Result

建议：

```text
RESOLVED
UNAVAILABLE
UNSUPPORTED
INVALID
FAILED
```

## Local Source

至少处理：

- path normalization
- file exists
- readable
- engine compatibility
- URI conversion if needed by renderer/webview
- platform-safe escaping

## Security

如果 desktop runtime 需要：

- file://
- custom protocol
- IPC
- native bridge

必须复用当前安全边界。

禁止为了方便打开：

- arbitrary unrestricted filesystem bridge
- unsafe node integration
- broad shell access

除非 W01 已证明当前架构就是如此且有既定安全模型。

## Source Changes

Track source 在播放前失效：

```text
resolver fails
→ Playback ERROR
→ Track remains
```

播放中源文件被删除：

行为取决于 OS / engine buffering，但不得 crash。

## Cloud

W04 不实现 CloudTrack production。

只保留 resolver architecture 能未来支持：

```text
source_kind = LOCAL | CLOUD | ...
```

的边界即可。
