# MFD-006 — Reliability & Local State
## Codex 正式执行任务书

**任务编号：** MFD-006  
**执行对象：** Codex  
**执行模式：** 稳定性收敛 / 本地状态设计 / 故障恢复 / 边界验证  
**前置条件：** MFD-005 = GO

---

# 0. 核心目标

本包只解决：

> **软件在正常使用和常见故障下，如何不丢状态、不泄露 secret、不重复播放、不失控重试，并能从异常中恢复。**

不要用本包扩展产品范围。

---

# 1. Preflight

开始前确认：

- MFD-005 = GO；
- Moodify Minimal Player 已是默认界面；
- PlaybackEngine 稳定；
- Player API / BFF 契约稳定；
- Desktop repo clean；
- 已知 session/auth 机制；
- 已知 playback manifest expiry 行为；
- Windows 测试环境可用。

记录：

```text
desktop branch
desktop SHA
backend API version
Electron version
Windows version
```

---

# 2. 本地状态分类

必须先把所有本地状态分成三类。

## A. Durable Client State

可以跨重启保存：

```text
lastTrackId
lastPlaybackPositionMs
volume
windowBounds
windowMaximized
lastSuccessfulAppVersion
```

根据真实产品需要，可以增减。

## B. Ephemeral Runtime State

不能当 durable truth 保存：

```text
currentPlaybackState
loading
buffering
retrying
temporary error
current signed URL
current request id
in-flight request
```

## C. Sensitive State

必须特殊处理：

```text
session token
refresh token
signed playback URL
private user metadata if any
```

不得混在普通 preferences JSON。

---

# 3. Local State Store

建立一个单一 Desktop local state authority，例如：

```text
LocalStateStore
```

必须统一管理：

- schema
- version
- read
- write
- migration
- corruption fallback
- atomicity / safe write

禁止：

```text
组件 A 写 localStorage
组件 B 写 JSON
组件 C 写 electron-store
组件 D 写 sqlite
```

形成四套本地状态。

---

# 4. Storage 技术选择

优先选择：

> 简单、透明、足够可靠的本地状态方案。

可以是：

- electron-store
- 自建 JSON + schema + atomic write
- 当前项目已经采用的稳定方案

不建议为了几个字段引入 SQLite。

如果已有成熟 local state infra：

优先复用。

---

# 5. State Schema Versioning

本地状态必须有：

```text
schemaVersion
```

例如：

```json
{
  "schemaVersion": 1,
  "playback": {
    "lastTrackId": "trk_xxx",
    "positionMs": 48123,
    "volume": 0.72
  },
  "window": {
    "width": 960,
    "height": 720
  }
}
```

未来字段变化必须有：

- migration
- reset policy
- corruption policy

---

# 6. Playback Resume

重启恢复目标：

```text
lastTrackId
+
lastPositionMs
```

但必须遵守：

- track 仍对用户可见；
- track 仍 READY；
- playback asset 可以重新取得；
- manifest 必须重新获取；
- signed URL 不能从磁盘直接复用。

推荐：

```text
app start
→ load persisted track id
→ query Cloud
→ request fresh manifest
→ load
→ seek to persisted position
→ READY
```

默认不要自动开始播放，除非已有明确产品决定。

---

# 7. Position Persistence

不要每 50ms 写磁盘。

建议：

- 内存持续更新；
- 每 N 秒节流写；
- pause 时写；
- track switch 时写；
- app close 时写。

必须避免：

- 高频 IO
- race
- 写入倒退 position
- track A position 写进 track B

至少需要绑定：

```text
trackId + position
```

---

# 8. Volume Persistence

保存用户音量。

要求：

- 0–1 或 0–100 只选一种内部标准；
- clamp；
- corrupted value fallback；
- 首次安装有明确默认值。

不要把系统音量当成 App 自己的持久化值。

---

# 9. Window State

保存：

- size
- position
- maximized 可选

恢复时必须检查：

> 上次窗口位置是否仍然在当前显示器可见范围。

处理：

- 用户拔掉第二显示器；
- 分辨率改变；
- DPI 改变。

不能恢复到屏幕外。

---

# 10. Session Persistence

如果 MFD-003 已有正式 auth：

必须使用安全存储 abstraction。

优先：

- OS-backed secure storage
- Electron `safeStorage`（如适用）
- 已批准的 credential storage

禁止：

```text
token in localStorage
token in plain JSON
token in Redux persist
token in renderer source
token in logs
```

若当前 Alpha auth 尚未支持 refresh：

明确记录限制。

---

# 11. Session Expiry

必须处理：

```text
valid
→ expired
→ refresh if possible
→ renewed
```

如果无法 refresh：

```text
SESSION_EXPIRED
→ clear invalid session safely
→ user-facing auth-required state
```

不要：

- 无限请求 401
- 每个 endpoint 各自处理一套 refresh
- 并发触发 10 个 refresh

建议建立：

> single-flight session refresh

---

# 12. Manifest Expiry

建立单一策略：

```text
PlaybackManifestManager
```

职责：

- 判断 expiry；
- near-expiry threshold；
- refresh；
- deduplicate refresh；
- map errors；
- 不持久化 signed URL。

禁止多个组件各自 refresh manifest。

---

# 13. Network State

不要求做“网络监控系统”。

只需要：

- API failure typed；
- media failure typed；
- retry 可控；
- offline / degraded 状态可理解。

网络恢复后：

> 用户应能够重试。

可做有限自动恢复，但必须防止无限 retry。

---

# 14. Retry Policy

必须统一。

至少区分：

## Retryable

```text
UPSTREAM_UNAVAILABLE
NETWORK_INTERRUPTED
RATE_LIMITED (after policy)
temporary manifest fetch failure
```

## Non-retryable

```text
FORBIDDEN
TRACK_NOT_FOUND
unsupported media
invalid client contract
```

建议：

```text
bounded exponential backoff
+
max attempts
+
jitter optional
```

Alpha 可以简单。

但绝不允许：

```text
while(true) retry()
```

---

# 15. Concurrency Guard

必须处理常见竞态：

```text
rapid next
rapid previous
play while loading
seek during source change
session refresh during manifest refresh
app quit during persistence write
```

原则：

> 新 intent 应能取消或 supersede 旧 intent。

至少实现：

- AbortController 或同等取消；
- request generation / operation id；
- stale response rejection。

---

# 16. Duplicate Playback Prevention

切歌或 reload 时必须保证：

- 旧 engine source 停止；
- event listener 清理；
- timer 清理；
- 新 source 唯一；
- 不出现 A+B 同时发声。

这个检查必须进入真实 smoke。

---

# 17. Crash / Abnormal Exit

本包不要求 crash-reporting SaaS。

但要：

- main uncaught error 已有基础处理；
- 本地 state 不因半写入而损坏；
- 下次启动能读；
- corrupted state 可 reset。

至少测试：

> 杀掉进程后重开。

---

# 18. Corrupted Local State

人为制造：

```text
invalid JSON
wrong schemaVersion
invalid volume
missing track id
negative position
huge window bounds
```

期望：

- app 不崩溃；
- fallback；
- 必要时 reset；
- 有安全日志；
- 不上传敏感内容。

---

# 19. Local Cache Boundary

MFD-006 可以建立**轻量缓存边界**，但不建立离线音乐库。

允许缓存：

- non-sensitive track display metadata
- last known library summary
- short-lived response cache（如确有需要）

默认禁止持久缓存：

- 完整音频文件
- signed URL
- stems
- processing artifacts
- user-uploaded private audio
- auth header

如果缓存 API 响应：

必须有：

- TTL
- version
- invalidation
- size bound

---

# 20. Offline Behavior

首版定义：

> Moodify Desktop 是网络播放器。

因此断网后不承诺完整离线播放。

如果正在播放的 Chromium buffer 可以短暂继续：

这是运行行为，不是离线产品承诺。

用户体验应表达：

```text
网络不可用
[重试]
```

不要假装是 offline mode。

---

# 21. App Start Sequence

建议统一：

```text
App Boot
→ load local durable state
→ validate / migrate
→ restore secure session
→ validate session
→ restore last track reference
→ fetch fresh Cloud state
→ fetch fresh PlaybackManifest
→ load engine
→ seek persisted position
→ READY
```

任何一步失败：

> 映射成明确可恢复状态。

---

# 22. App Quit Sequence

建议：

```text
quit intent
→ stop accepting new playback intent
→ flush playback position
→ flush window state
→ clear ephemeral resources
→ dispose engine
→ close
```

不能因等待网络无限阻塞退出。

---

# 23. Logging

可靠性日志至少允许记录：

```text
app version
state migration result
session refresh result (no token)
manifest refresh result (no full URL)
retry attempt
playback error code
state corruption fallback
```

禁止：

- token
- Authorization
- full signed URL
- refresh token
- private media query
- raw personal metadata

---

# 24. Tests

至少包括：

## Unit
- state schema validation
- migration
- corrupted values
- retry policy
- session refresh lock
- manifest refresh lock
- stale request rejection

## Integration
- boot restore
- session expired → refresh
- expired manifest → refresh
- network error → retry
- track switch race
- quit flush

## Windows smoke
- close/reopen
- force kill/reopen
- offline/reconnect
- session expiry simulation
- manifest expiry simulation
- move window to second monitor then remove monitor if feasible
- rapid next/previous
- rapid play/pause
- seek while switching

---

# 25. 性能边界

监控：

- state writes frequency
- memory growth after repeated track switch
- listener count
- timer count
- API duplicate calls

至少进行一次：

```text
连续切歌 50 次
```

确认：

- 不明显内存失控；
- 不叠音；
- 不出现请求暴增。

不需要做正式性能基准平台。

---

# 26. 禁止项

严禁：

- offline full library
- background full-audio cache
- download manager
- local music import
- upload
- playlist product expansion
- recommendation
- analytics platform
- crash SaaS
- sync across devices
- tray
- media keys
- auto update
- installer
- code signing
- DSP
- WASAPI
- native audio
- new Cloud state machine

---

# 27. Definition of Done

必须全部满足：

1. 单一本地状态 authority；
2. schema version；
3. migration / reset；
4. last track restore；
5. position restore；
6. volume restore；
7. window restore；
8. off-screen window recovery；
9. session secure persistence；
10. session expiry handling；
11. manifest refresh handling；
12. signed URL 不落盘；
13. bounded retry；
14. concurrency cancellation；
15. stale response rejection；
16. duplicate playback prevention；
17. corrupted state recovery；
18. abnormal exit recovery；
19. no full offline product；
20. unit tests pass；
21. integration tests pass；
22. Windows smoke pass；
23. rapid interaction smoke pass；
24. no secret leak；
25. evidence complete。

---

# 28. 最终回报

Codex 最终只报告：

1. local state architecture
2. persisted fields
3. sensitive-state handling
4. boot restore flow
5. session recovery
6. manifest recovery
7. retry policy
8. race-condition handling
9. corrupted-state tests
10. abnormal-exit tests
11. Windows smoke
12. known limitations
13. diff summary
14. MFD-007 readiness

最后：

> `MFD-007: GO / CONDITIONAL GO / NO-GO`
