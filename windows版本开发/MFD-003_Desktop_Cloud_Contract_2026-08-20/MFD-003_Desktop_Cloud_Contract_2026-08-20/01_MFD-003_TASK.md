# MFD-003 — Desktop–Cloud Contract
## Codex 正式执行任务书

**任务编号：** MFD-003  
**执行对象：** Codex  
**执行模式：** 真实后端审计 + Player API 边界落地 + Desktop API client + 合同测试  
**前置条件：** MFD-002 = GO

---

# 0. 总目标

你的任务不是“调用几个接口”。

你的任务是：

> **建立 Moodify Desktop 对 Cloud 的唯一正式依赖面。**

之后 Desktop 不应该知道：

- Cloud 内部怎么处理音乐；
- Ear 怎么判断；
- Audiolla 怎么分轨；
- 哪台服务器在工作；
- PolarDB 表结构；
- OSS bucket 内部路径；
- service-key；
- 内部状态机。

Desktop 只应该知道：

> 用户是谁、可以看到哪些音乐、这一首应该如何被播放。

---

# 1. 阶段 A — 只读后端现状核验

开始任何代码修改前，先确认当前真实后端。

至少扫描：

- Music BFF
- public API
- internal API
- auth
- users
- tracks
- albums
- playlists
- queue
- playback/media
- object storage
- processed assets
- current service-key usage
- current CORS
- current reverse proxy / domain assumptions
- current Android API usage
- any existing token/session contract

输出：

`backend_contract_inventory.md`

每个能力必须标：

```text
VERIFIED_PUBLIC
VERIFIED_INTERNAL
PARTIAL
DOCUMENTED_ONLY
LEGACY
MISSING
UNKNOWN
```

不要因为路由文件存在就宣称“生产可用”。

---

# 2. Public Player API 的职责

Player API / BFF 只对用户产品暴露必要能力。

建议最小资源：

```text
Session
User
Library
Track
PlaybackManifest
Queue
ClientCapability
```

阶段 1 不要求全部做复杂 CRUD。

---

# 3. Session Contract

Desktop 必须使用：

> 用户级、可撤销、有限权限会话。

严禁：

- server service-key
- database password
- permanent infrastructure token
- internal API key

如果当前系统尚无成熟用户登录：

可以采用一个**明确的开发期过渡机制**，但必须满足：

1. 用户级；
2. 可撤销；
3. 权限有限；
4. 与 server-level secret 分离；
5. 明确标记 `ALPHA_TEMPORARY`；
6. 不阻塞未来正式 auth 替换。

不得把内部 service-key 包装一层后叫“用户 token”。

---

# 4. Track Contract

建议最小字段：

```text
Track {
  id
  title
  artist
  duration_ms
  playback_status
  version
}
```

可选：

```text
album
display_metadata
availability
```

不要把内部字段直接透出：

- internal file path
- OSS internal object key（除非仅服务端使用）
- stems
- processing logs
- diagnosis
- raw measurements
- internal preset parameters
- model outputs
- audit internals
- worker state

---

# 5. PlaybackManifest Contract

这是本包的核心。

建议概念：

```text
PlaybackManifest {
  track_id
  playback_id
  asset_version
  stream_url
  expires_at
  mime_type
  duration_ms
  content_length?
  checksum?
  playback_policy
}
```

其中：

`playback_policy`

首版只应该包含客户端真正需要的行为提示，例如：

```text
allow_seek
allow_cache
requires_online
```

不要把内部 DSP / preset / Ear judgment 塞进 manifest。

---

# 6. Playback URL

优先方向：

> 短期有效、用户授权后的播放 URL。

如果使用 OSS / object storage：

建议采用：

- signed URL
- temporary URL
- BFF tokenized streaming endpoint

而不是：

- 永久公网裸 URL
- bucket 长期公开
- 把对象存储 secret 下发到 Desktop

必须验证：

- URL expiration
- access after expiration
- wrong-user access
- invalid track
- unauthorized access

---

# 7. Library Contract

首版 library 只需要支持：

```text
GET visible tracks
GET track by id
```

如已有 playlist / queue，可以复用。

但不得为了 Desktop 重造第二套：

- tracks table
- library authority
- playlist authority

Cloud 仍是 authority。

Desktop 只消费。

---

# 8. Queue Contract

MFD-003 只定义。

可以定义：

```text
QueueItem
QueueSnapshot
```

如果当前后端没有 queue authority：

标记 `MISSING`。

不要在 Desktop 本地偷偷创建一个“生产 queue authority”。

MFD-004 可以有临时播放队列，但必须清楚区分：

```text
local playback order
!=
cloud canonical queue
```

---

# 9. API Versioning

必须建立最小版本策略。

推荐：

```text
/api/player/v1/
```

或当前后端已有更合理版本方式。

要求：

- Desktop 不绑定内部无版本 endpoint；
- contract 变化可追踪；
- breaking changes 有明确升级路径；
- Alpha 阶段也必须避免无版本 API 漂移。

---

# 10. Error Contract

统一错误结构，例如：

```text
{
  "error": {
    "code": "TRACK_NOT_FOUND",
    "message": "...",
    "retryable": false,
    "request_id": "..."
  }
}
```

建议至少：

```text
UNAUTHORIZED
FORBIDDEN
SESSION_EXPIRED
TRACK_NOT_FOUND
PLAYBACK_NOT_READY
PLAYBACK_URL_EXPIRED
ASSET_UNAVAILABLE
RATE_LIMITED
UPSTREAM_UNAVAILABLE
INTERNAL_ERROR
```

Desktop 不应该解析后端 Python traceback。

---

# 11. ClientCapability

预留：

```text
ClientCapability {
  platform
  app_version
  client_version
  playback_engine
}
```

首版不要做复杂协商。

只为以后：

- Desktop
- Android
- iOS
- native playback engine

留下边界。

---

# 12. Desktop API Client

在 Electron 工程内建立：

```text
services/api/
├── client
├── session
├── library
├── playback
└── errors
```

要求：

- renderer 不直接散落 fetch
- 所有请求集中
- timeout
- cancellation
- typed response
- typed error
- request id support
- no secret logging
- config-driven base URL

---

# 13. Main vs Renderer 的网络边界

优先评估：

```text
Renderer
  ↓ typed bridge/domain
Main / service layer
  ↓ HTTPS
Player API
```

如果选择 renderer 直接 HTTPS，必须解释为什么仍然安全、可控、可测试。

默认倾向：

> 网络访问集中在受控 service 层，不让 UI 到处 fetch。

不要因为 Electron 是网页技术，就把 Desktop 写成一个普通 browser SPA。

---

# 14. Android Contract Reuse

如果 Android 已有可用 API：

优先提取：

- schema
- endpoint semantics
- auth semantics
- playback resource semantics

不要复制：

- Android-specific state
- UI viewmodel
- mobile-only assumptions

最终要尽可能形成：

> **Player API 是跨客户端契约。**

而不是：

```text
Android API
Desktop API
iOS API
```

三套分裂协议。

---

# 15. Backend Changes

如果现有后端不能满足 Desktop：

允许在 MFD-003 做**最小 Player API / BFF 增补**。

但要求：

- 不重写 Cloud；
- 不动 Ear 核心；
- 不动处理 pipeline；
- 不新建第二个用户系统；
- 不直接暴露内部 API；
- 不修改与本包无关的数据库表；
- schema migration 必须最小且有证据。

如果可以完全通过 BFF 层适配：

> 优先 BFF。

---

# 16. Security Tests

必须至少验证：

### Auth
- no token
- invalid token
- expired token
- valid token

### Authorization
- valid user + own track
- valid user + unavailable track
- invalid track id

### Playback URL
- valid
- expired
- malformed
- unauthorized
- asset missing

### Logging
确认不会记录：

- token
- signed URL query secret
- Authorization header

---

# 17. Contract Tests

建议：

```text
tests/contracts/
├── session
├── library
├── track
├── playback_manifest
└── errors
```

如果前后端分仓库：

要有共享 schema 或基于 OpenAPI / JSON Schema / generated types 的明确策略。

不要靠人工复制 TypeScript interface 与 Python model 长期同步。

---

# 18. OpenAPI / Schema

如后端已有 FastAPI：

优先利用 OpenAPI。

但不得：

- 直接把整个 internal OpenAPI 暴露给 Desktop
- 把所有 internal endpoint 生成进 client

应该：

> 只生成 / 只维护 Player API 子集。

---

# 19. Observability

每个关键请求建议有：

```text
request_id
client_version
route
status
latency
```

但不要记录用户隐私或 signed URL secret。

MFD-003 不引入重型 tracing 平台。

先把 request correlation 做对。

---

# 20. 禁止项

严禁：

- service-key 放 Desktop
- DB credentials 放 Desktop
- direct SQL
- OSS secret 下发
- Ear internal API 暴露给 Desktop
- Audiolla token 下发
- LALAL token 下发
- 永久公开用户音频 URL
- renderer 日志打印 Authorization
- 用 mock 假装生产通过
- 为了省事关闭 auth
- 为了跨域关闭安全策略
- 将 internal endpoint 命名成 public 后直接暴露
- 重写 playback pipeline
- 实现正式播放引擎
- 正式播放器 UI

---

# 21. Definition of Done

必须全部满足：

1. 后端真实能力已核验；
2. Player API 边界明确；
3. Session contract 明确；
4. Track contract 明确；
5. PlaybackManifest contract 明确；
6. 用户级 auth 可用或有安全 alpha 过渡；
7. Desktop API client 已实现；
8. 不包含 server secret；
9. contract tests 通过；
10. authorization tests 通过；
11. stream resource 可达性已验证；
12. signed/temporary URL 策略已验证或明确阻塞；
13. Android/Desktop 不产生两套协议；
14. 有 versioning；
15. 有 error contract；
16. 有 evidence；
17. 尚未进入完整播放实现。

---

# 22. 最终回报

Codex 最终只报告：

1. 后端现状
2. 新/复用的 Player API
3. auth 方案
4. contract
5. Desktop client 变更
6. backend 变更
7. tests
8. security results
9. known gaps
10. MFD-004 readiness

最后：

> `MFD-004: GO / CONDITIONAL GO / NO-GO`
