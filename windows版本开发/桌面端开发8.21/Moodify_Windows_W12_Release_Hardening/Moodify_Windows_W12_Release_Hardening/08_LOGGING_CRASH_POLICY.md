# Production Logging & Crash Diagnostics

## Production Logs

至少记录：

```text
startup
shutdown
version/build
migration
fatal player error
database error
recovery failure
native integration failure
cloud request failure summary
uncaught exception
```

## Levels

```text
INFO
WARN
ERROR
```

默认不输出 debug flood。

## Privacy

不得记录：
- password
- access token
- service-key
- signed URL secret
- private audio payload
- unnecessary full local paths

## Crash Artifact

至少：

```text
version
build
OS
runtime
exception
stack
timestamp
last subsystem markers
```

## Crash Loop

如果连续启动因恢复坏 session 崩溃：
下一次启动跳过 session restore，进入安全空 session。

不得清 Library。
