# Status / Retry / Offline Policy

## Polling

若无 push：

```text
request accepted
→ poll
→ stepped/exponential backoff
→ stop at READY/FAILED/CANCELLED
```

不要每秒无限轮询。

## Retryable

```text
timeout
connection reset
429
temporary 5xx
```

## Non-retryable

```text
invalid file
unsupported format
401/403 until auth refreshed
malformed request
```

## Max Retry

必须有上限。

## Offline

网络断开：

```text
preparation status = temporarily unavailable
local Playback remains
```

网络恢复：
重新 refresh active preparation。

## Unknown Status

```text
UNKNOWN
```

不 crash，不映射成 READY。

## Cancel

只有后端真实支持 server-side cancel 才显示“取消准备”。

停止 polling 不能伪装成取消云任务。
