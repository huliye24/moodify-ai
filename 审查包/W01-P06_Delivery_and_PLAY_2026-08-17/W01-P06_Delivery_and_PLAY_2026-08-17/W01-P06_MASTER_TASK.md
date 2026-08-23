# W01-P06 — Delivery + PLAY

**Wave:** Moodify Cognitive Wave 01  
**Package:** W01-P06  
**性质:** 播放交付建设 / READY → Authorized Delivery → Android PLAY  
**日期:** 2026-08-17  
**执行对象:** Codex  
**前置依赖:** W01-P00 ~ W01-P05 已完成并通过人类审核  
**后继任务:** W01-P07 Golden Song 001  
**原子任务数:** 2  
**核心目标:** 将一个已经被系统确认 READY 的音频对象，以安全、稳定、可追溯、低摩擦的方式交付到 Android，并形成第一条真正面向用户的 PLAY 主链。

---

# 0. P06 的唯一问题

P05 已经完成内部计算：

```text
Source
→ Compute Pipeline
→ Verify
→ CompletionCandidate
→ Control Plane
→ READY
```

P06 不再讨论：

- 分轨；
- 分析；
- Ear；
- DSP；
- Preset；
- Render；
- Verify；
- Job State Machine。

P06 只回答：

> **一个 READY Track，怎样成为用户可以按下 PLAY 就稳定听到的音频。**

目标主链：

```text
READY
  ↓
Playback Metadata
  ↓
Authorized Delivery
  ↓
Android Playback Session
  ↓
PLAY
```

---

# 1. 两个原子任务

## T06-1 — Playback Delivery Contract

建立服务端交付层：

- READY eligibility
- playback metadata
- authorized object access
- signed URL / proxy decision
- range request support
- content headers
- cache policy
- access TTL
- delivery failure semantics
- playback session evidence
- version identity

---

## T06-2 — Android PLAY Integration

让 Android 只依赖一套明确的播放合同：

- load READY track
- request playback metadata
- resolve playable URI
- PLAY / PAUSE
- next / previous / vertical swipe（若当前产品面已采用）
- buffering
- reconnect / retry
- expired delivery token refresh
- playback error mapping
- basic playback evidence
- no exposure of internal processing complexity

---

# 2. 前置 Gate

## GATE P06-0 — READY Contract Gate

必须读取 P04/P05：

- authoritative Job State Machine
- READY guard
- CompletionCandidate contract
- render/final object identity
- verification evidence
- object access class
- P06 Handoff

如果“READY 到底意味着什么”仍不明确：

> `STOP — READY_CONTRACT_INCOMPLETE`

---

## GATE P06-1 — Data Access Gate

必须读取 P03/P02：

- object storage role
- object key convention
- object access policy
- secret ownership
- network matrix
- signed URL / service boundary
- mobile credential restrictions

如果 Android 需要长期 OSS Secret 才能播放：

> `STOP — DELIVERY_SECURITY_INVALID`

---

## GATE P06-2 — Android Reality Gate

任何 UI/播放修改前，必须先扫描当前 Android：

- current player architecture
- Media3 / ExoPlayer / other engine
- playback service
- repository/data layer
- current local/remote source model
- queue model
- navigation
- background playback
- lifecycle handling
- audio focus
- lock screen / notification（如已存在）
- current tests
- current cloud/API client

先输出：

`CURRENT_ANDROID_PLAYBACK_REALITY.md`

不能先重写播放器。

---

# 3. Delivery Plane Invariants

必须建立 `DELIVERY_INVARIANTS.md`。

至少：

## DLV-INV-01 — READY Only
客户端只能获得 READY 对象的正式播放入口。

## DLV-INV-02 — No Long-Lived Cloud Secret
移动端不持有长期 OSS / DB 凭证。

## DLV-INV-03 — Playback URI Is Replaceable
客户端不能把一个临时签名 URL 当永久 Track identity。

## DLV-INV-04 — Track ID != URL
Track identity 独立于具体 CDN/OSS URL。

## DLV-INV-05 — Delivery Is Authorized
每次播放入口必须受用户/产品访问策略约束。

## DLV-INV-06 — Expiry Is Recoverable
签名 URL 过期后可刷新，不必重新处理音频。

## DLV-INV-07 — Range-Friendly
长音频播放必须支持合理的 byte-range / streaming behavior。

## DLV-INV-08 — Internal Complexity Hidden
客户端不需要知道 stem / analysis / Ear / DSP / pipeline 内部结构。

## DLV-INV-09 — Playback Failure != Compute Failure
播放失败不能把已经 READY 的 Job 重新变成 processing failure。

## DLV-INV-10 — Delivery Evidence Is Separate
播放事件可记录，但不能反向篡改生产 Evidence。

## DLV-INV-11 — Final Render Version Is Visible Internally
播放会话必须能追溯到 render object/version。

## DLV-INV-12 — Source Is Never Accidentally Exposed
若用户只应播放处理后的 render，不能因为 URL 设计错误暴露内部 source/stems。

---

# 4. Playback Metadata Contract

必须输出：

`PLAYBACK_METADATA_CONTRACT.md`

建议最小响应：

```json
{
  "track_id": "...",
  "playback_version": "...",
  "render_object_id": "...",
  "title": "...",
  "duration_ms": 0,
  "container": "m4a/wav/flac/...",
  "codec": "...",
  "sample_rate": 0,
  "channels": 2,
  "content_length": 0,
  "playback_uri": "...",
  "uri_expires_at": "...",
  "supports_range": true,
  "etag": "...",
  "ready_at": "...",
  "pipeline_version": "...",
  "profile_version": "..."
}
```

注意：

对客户端可以隐藏：

- pipeline_version
- profile_version
- internal object identity

但服务端必须能够追溯。

---

# 5. Signed URL vs Proxy Decision

P06 必须做一个明确 ADR。

允许候选：

## Option A — Signed OSS URL

优点：

- 简单；
- 少一层代理；
- 大文件直接走对象存储；
- 适合 One Song / pilot。

要求：

- 短 TTL；
- 不在日志长期保存完整签名 query；
- 可刷新；
- 权限检查发生在签发前；
- bucket 默认 private。

---

## Option B — API Streaming Proxy

优点：

- 权限完全由 API 控制；
- 可隐藏 object storage。

代价：

- API 带宽；
- range / seek 实现复杂；
- 多一层故障点。

---

## 决策原则

第一阶段优先：

> **最小可运行、最少新基础设施、最少带宽重复搬运。**

但最终必须根据 P02/P03 现实决定，不强制签名 URL。

---

# 6. Delivery API

若现有 API 可扩展，优先复用。

建议逻辑接口：

```text
GET /tracks/{track_id}/playback
```

返回：

- READY 验证结果
- playback metadata
- authorized URI / session
- expiry
- safe headers

---

## 6.1 READY Guard

服务端必须：

1. 查询 authoritative Track/Job 状态；
2. 确认 READY；
3. 确认 final/render object 存在；
4. 确认对象 access class；
5. 确认调用方有权限；
6. 生成可播放入口。

禁止：

- 客户端自己拼 OSS key；
- 客户端根据 DB 字段猜 URL；
- READY 之前签发正式播放入口。

---

# 7. HTTP / Streaming Contract

必须明确：

- MIME type
- Content-Length
- ETag
- Accept-Ranges
- Range request
- cache-control
- signed URL TTL
- redirect behavior
- network timeout
- retry safety

播放候选格式必须由 P05 Render Contract 决定。

P06 不重新转码。

---

# 8. Playback Session

建议引入轻量 `playback_session_id`，但不得把它做成第二套复杂任务系统。

用途：

- 一次播放入口签发
- delivery troubleshooting
- playback evidence correlation
- token refresh correlation

字段建议：

- playback_session_id
- track_id
- render_object_id
- user/access scope
- issued_at
- expires_at
- delivery_method
- app_version
- device_class（避免过度采集）
- correlation_id

---

# 9. Android Playback Architecture

必须先复用现有播放引擎。

如果已有 Media3/ExoPlayer：

> 优先继续使用。

禁止为了 P06：

- 自写音频解码器；
- 自写网络流媒体协议；
- 同时更换播放器框架；
- 同时重做完整 UI。

---

# 10. Android Data Flow

目标：

```text
UI
 ↓
Playback ViewModel / Controller
 ↓
Track Repository
 ↓
Moodify API
 ↓
PlaybackMetadata
 ↓
Player Engine
 ↓
Audio Output
```

内部处理流水线不进入客户端。

---

# 11. PLAY Surface

第一阶段保持最小：

- PLAY / PAUSE
- 当前 Track 基本状态
- 切歌
- buffering
- error/retry

如果已有垂直滑动切歌，可以接入，但不要在 P06 新增大型交互系统。

核心验收是：

> **按 PLAY 能听到 READY render。**

不是：

> UI 已经“足够漂亮”。

---

# 12. Playback State 与 Job State 分离

Android 允许有：

- IDLE
- LOADING
- BUFFERING
- PLAYING
- PAUSED
- ENDED
- ERROR

这是客户端 playback session state。

它不是 P04 Job State。

例如：

```text
Job = READY
Playback = BUFFERING
```

完全合法。

禁止因为播放网络失败，把 server Job 改成 FAILED。

---

# 13. Delivery Failure Taxonomy

必须形成：

`PLAYBACK_FAILURE_TAXONOMY.md`

建议：

- `TRACK_NOT_READY`
- `TRACK_NOT_FOUND`
- `ACCESS_DENIED`
- `DELIVERY_URI_EXPIRED`
- `DELIVERY_URI_INVALID`
- `NETWORK_UNAVAILABLE`
- `NETWORK_TIMEOUT`
- `RANGE_NOT_SUPPORTED`
- `OBJECT_NOT_FOUND`
- `UNSUPPORTED_MEDIA`
- `DECODER_ERROR`
- `AUDIO_FOCUS_LOST`
- `PLAYER_INTERNAL_ERROR`
- `UNKNOWN_PLAYBACK_ERROR`

注意：

这些是 Delivery/Playback failure。

不得污染 P04 compute failure taxonomy。

---

# 14. URL Expiry Recovery

必须测试：

```text
PLAYING / PAUSED
↓
signed URL expires
↓
seek / resume fails
↓
client requests refreshed playback metadata
↓
resume from previous position
```

要求：

- 不重新创建处理 Job；
- 不重新上传 source；
- 不重新 Render；
- 不丢失 track identity。

---

# 15. Offline / Cache Boundary

W01 第一阶段不建设完整离线音乐库。

可以利用播放器/HTTP 合理缓存。

但禁止：

- 默认长期下载源音；
- 默认把所有 render 永久存手机；
- 未定义授权就做“离线下载”。

如果已有缓存能力：

记录并约束。

---

# 16. Playback Evidence

P06 可以记录最小事件：

- PLAY_REQUESTED
- PLAY_STARTED
- PLAY_PAUSED
- PLAY_RESUMED
- PLAY_ENDED
- PLAY_FAILED

可带：

- track_id
- playback_session_id
- render version
- timestamp
- safe position/duration
- app version
- failure code

第一阶段不需要构建完整推荐/行为分析平台。

---

# 17. Privacy

默认不收集：

- 不必要设备标识
- 完整用户网络信息
- 音频监听录音
- 与播放无关传感器数据

Playback evidence 只为：

- 交付验证
- 故障定位
- Golden Song/Pilot 验收

---

# 18. Android Security

必须验证：

- no OSS AccessKey in APK
- no DB credential in APK
- no external audio-processing API key in APK
- no long-lived signed URL persisted insecurely
- HTTPS only for production
- debug endpoints not exposed in release
- logs do not dump signed query string

---

# 19. Tests

至少：

## TST-01 — READY Only
非 READY track 请求播放。

Expected:
- reject with TRACK_NOT_READY

## TST-02 — Valid Playback Metadata
READY track returns usable metadata.

## TST-03 — Object Missing
DB READY but object missing.

Expected:
- no playable URI
- OBJECT_NOT_FOUND / reconciliation evidence

## TST-04 — URL Expiry
expired URL refreshes.

## TST-05 — Range / Seek
seek works for production render format.

## TST-06 — Buffering Recovery
temporary network interruption recovers.

## TST-07 — Unauthorized Access
wrong user/access scope cannot obtain URI.

## TST-08 — No Client Secret
release APK/static scan contains no long-term cloud credential.

## TST-09 — Playback Failure Isolation
decoder/network error does not change Job from READY to FAILED.

## TST-10 — Track Identity Stable
URL refresh preserves same track/render identity.

## TST-11 — PLAY / PAUSE
basic control works.

## TST-12 — Next / Previous or Swipe
if in current product scope, transitions cleanly.

## TST-13 — App Lifecycle
background/foreground does not corrupt player state.

## TST-14 — Audio Focus
interruption behavior sane.

## TST-15 — Playback Evidence
start/fail/end produce safe events.

---

# 20. P06 End-to-End Acceptance

P06 至少完成一条测试/授权 READY 对象：

```text
READY track
→ playback metadata request
→ authorized URI
→ Android load
→ PLAY
→ seek
→ pause
→ resume
→ finish
```

如果使用签名 URL：

还要测试一次过期刷新。

---

# 21. 允许修改

- playback API
- signed URL / delivery adapter
- playback metadata model
- Android data layer
- Android playback controller
- player engine integration
- minimal UI wiring
- playback tests
- delivery logs/evidence
- safe health/diagnostics

---

# 22. 禁止修改

- audio pipeline
- render semantics
- Job state machine
- lease/retry
- DB/Object identity
- product Canon
- internal Ear logic
- unrelated UI redesign
- skin/community
- iOS
- offline library
- recommendation system
- social features

---

# 23. 必须输出

至少：

1. `00_P06_EXECUTIVE_SUMMARY.md`
2. `01_CURRENT_ANDROID_PLAYBACK_REALITY.md`
3. `02_DELIVERY_ARCHITECTURE.md`
4. `03_DELIVERY_INVARIANTS.md`
5. `04_PLAYBACK_METADATA_CONTRACT.md`
6. `05_DELIVERY_AUTHORIZATION_CONTRACT.md`
7. `06_SIGNED_URL_OR_PROXY_ADR.md`
8. `07_HTTP_STREAMING_CONTRACT.md`
9. `08_ANDROID_PLAYBACK_CONTRACT.md`
10. `09_PLAYBACK_FAILURE_TAXONOMY.md`
11. `10_PLAYBACK_EVIDENCE_CONTRACT.md`
12. `11_SECURITY_REVIEW.md`
13. `12_PLAYBACK_TEST_REPORT.md`
14. `13_P07_HANDOFF.md`
15. `14_P06_ACCEPTANCE_REPORT.md`

以及代码/测试。

---

# 24. P07 Handoff

P07 是第一次真正的 Golden Song。

P07 不再开发系统功能。

它使用 P00-P06 已经完成的现实系统，选择一个熟悉、授权、可完整评审的真实 Track，完整跑：

```text
Source
→ Upload
→ Data Plane
→ Job
→ Compute
→ Verify
→ READY
→ Delivery
→ Android
→ PLAY
```

P07 只修阻塞 Golden Song 的问题。

禁止扩展功能。

---

# 25. 验收标准

- [ ] P05 READY contract 已加载
- [ ] Android reality scan 完成
- [ ] delivery method ADR 完成
- [ ] READY-only guard
- [ ] mobile 无长期云 Secret
- [ ] signed URL/proxy 可刷新
- [ ] Track ID 与 URL 分离
- [ ] range/seek 支持
- [ ] playback failure 与 compute failure 分离
- [ ] PLAY/PAUSE 工作
- [ ] next/previous/swipe（若当前范围内）工作
- [ ] buffering/reconnect 工作
- [ ] URL expiry recovery 工作
- [ ] no source/stem accidental exposure
- [ ] playback evidence 可追溯到 render object
- [ ] Android release security scan 通过
- [ ] 测试 READY track E2E 播放通过
- [ ] P07 Handoff 完成
- [ ] 完成后停止，不进入 P07

---

# 26. 最终执行口令

> 执行 W01-P06 Delivery + PLAY。  
> 先读取 P03/P04/P05 的 Data、READY 与 Completion contracts，并先完成 Android Playback Reality Scan。  
> 完成两个原子任务：Playback Delivery Contract 与 Android PLAY Integration。  
> 只允许 READY 对象获得正式播放入口；客户端不持有 OSS/DB 长期凭证；Track identity 与临时 URL 分离；签名 URL 过期可刷新；支持合理 Range/Seek；播放失败不得污染已经 READY 的生产 Job。  
> Android 优先复用现有播放器框架，不重写解码器，不做无关 UI 扩张。  
> 以一个测试/授权 READY 对象完成 Android PLAY、seek、pause、resume、finish 与 URL refresh E2E 后停止。  
> 完成 P07 Handoff，等待人类审核，不进入 Golden Song。
