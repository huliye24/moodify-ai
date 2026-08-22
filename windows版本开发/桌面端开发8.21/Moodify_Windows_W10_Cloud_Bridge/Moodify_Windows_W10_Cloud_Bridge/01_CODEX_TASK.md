# Codex 执行任务书 — MFY-WIN-W10-CLOUD-BRIDGE-001

## 0. 执行模式

```text
PACKAGE = W10
FOCUS = MOODIFY_CLOUD_BRIDGE
CANON_CHANGE = NO
VISUAL_REDESIGN = FORBIDDEN
START_W11 = NO
```

W10 是“真实云端能力接入”，不是“根据产品愿景编造接口”。

---

## 1. Phase 0 — Preflight

必须读取：

```text
artifacts/windows/w09/W09_IMPLEMENTATION_REPORT.md
artifacts/windows/w09/W10_HANDOFF.md
artifacts/windows/w02/track-identity.md
artifacts/windows/w04/playback-authority.md
artifacts/windows/w08/W08_IMPLEMENTATION_REPORT.md
```

同时重新审计当前仓库/环境中真实 cloud client、endpoint、API contract。

输出：

`artifacts/windows/w10/preflight.md`

至少：

```text
W09_STATUS =
W10_GATE =
TRACK_AUTHORITY =
PLAYBACK_AUTHORITY =
RECOVERY_AUTHORITY =
API_CLIENT_REALITY =
CLOUD_ENDPOINT_REALITY =
AUTH_REALITY =
UPLOAD_REALITY =
OBJECT_STORAGE_REALITY =
JOB_STATUS_REALITY =
PREPARED_SOURCE_REALITY =
CURRENT_VERIFIED_CLOUD_CHAIN =
```

若 `W10_GATE != PASS`，停止。

---

## 2. Phase 1 — Cloud Capability Matrix

建立：

`artifacts/windows/w10/cloud-capability-matrix.md`

对每项标记：

```text
VERIFIED_LIVE
VERIFIED_PARTIAL
CODE_ONLY
CONFIG_ONLY
HISTORICAL_ONLY
BLOCKED
UNKNOWN
```

至少覆盖：

- create preparation request
- upload source
- object storage
- request id / job id
- processing status
- completion status
- failure status
- prepared asset URL/source
- authentication
- idempotency
- retry safety
- cancellation
- expiry
- authorization to retrieve prepared source
- client-visible error contract

### P0 Rule

只有 `VERIFIED_LIVE` / `VERIFIED_PARTIAL` 才允许接入产品代码。

`CODE_ONLY` 不等于 live。

---

## 3. Phase 2 — Define Cloud Boundary

建立窄的：

```text
CloudPreparationClient
```

候选能力：

```text
prepareTrack(track_id)
getPreparationStatus(preparation_id)
cancelPreparation(preparation_id)
resolvePreparedSource(preparation_id)
```

如果真实后端不支持某项，不实现假接口。

### Native/Desktop Layer

Windows app 只持有：

```text
cloud API adapter
```

不能在 renderer 里散落 fetch 调用。

输出：

`artifacts/windows/w10/cloud-client-boundary.md`

---

## 4. Phase 3 — Cloud Domain Model

推荐最小模型：

```text
CloudPreparation
- id
- track_id
- status
- progress?          # only if backend truly provides
- created_at
- updated_at
- error_code?
- prepared_source?
```

推荐 status：

```text
NOT_REQUESTED
QUEUED
PREPARING
READY
FAILED
CANCELLED
UNKNOWN
```

如果后端真实枚举不同，做 adapter mapping。

### 禁止

不要把内部生产状态：
```text
Analyze
Stem
Judge
Intervene
Verify
```

直接透传给用户。

---

## 5. Phase 4 — Track ↔ Cloud Mapping

CloudPreparation 必须引用稳定 Track ID。

推荐：

```text
Track
→ zero or one active CloudPreparation
→ zero or one current prepared source
```

如果支持多版本，必须明确：

```text
latest active
current preferred
historical versions
```

但 W10 不主动构建复杂版本管理器。

输出：

`artifacts/windows/w10/track-cloud-mapping.md`

---

## 6. Phase 5 — Request / Upload Flow

只有真实 backend 支持时才实施。

推荐流程：

```text
Track
→ resolve local source
→ validate file
→ prepare request
→ upload if required
→ receive preparation_id
→ persist mapping
→ status = QUEUED/PREPARING
```

### Required

- local source exists
- supported format
- auth present
- request timeout
- retry policy
- idempotency
- duplicate click protection
- upload partial failure
- cancellation if supported

### No Double Submission

连续点击：

```text
准备
准备
准备
```

不得创建三个重复云任务。

---

## 7. Phase 6 — Idempotency

必须检查后端是否已有：

```text
idempotency key
request token
client request id
```

如果有，复用。

如果没有：
客户端至少在本地阻止同一 Track 的并行 active preparation。

推荐 key 来源：

```text
track_id + source_revision
```

具体服从现有 identity architecture。

输出：

`artifacts/windows/w10/idempotency-policy.md`

---

## 8. Phase 7 — Authentication / Secrets

Windows 客户端不得内置：

- server master key
- database credential
- private service token
- Audiolla/LALAL.AI secret
- infrastructure admin key

如果当前 API 需要 service-key 才能访问：
这是产品 blocker。

W10 必须记录：

```text
CLIENT_AUTH_BLOCKED
```

而不是把 service-key 打进 exe。

### Allowed

只允许：
- user/session token
- scoped public client credential（若设计允许）
- backend-issued short-lived signed upload URL

输出：

`artifacts/windows/w10/cloud-auth-boundary.md`

---

## 9. Phase 8 — Status Refresh

如果后端没有 push/websocket：

使用 polling。

推荐：

```text
initial fast interval
→ exponential/stepped backoff
→ max interval
```

但不要后台无限高频请求。

需要处理：

- app foreground
- app background
- app restart
- network offline
- status endpoint timeout
- backend 5xx
- unknown status
- preparation expired

W08 Recovery 必须能恢复 active preparation IDs。

---

## 10. Phase 9 — Prepared Source Contract

只有后端明确提供可播放结果时，建立：

```text
PreparedSource
- source_kind = CLOUD_PREPARED
- locator / signed_url / asset_id
- mime/format
- expires_at? 
- checksum? 
- version?
```

具体字段服从真实 API。

### Security

如果是 signed URL：
- 不长期明文持久化超长有效期凭据
- expiry 要处理
- refresh/resign seam 要明确

如果是 asset ID：
由 backend resolve。

---

## 11. Phase 10 — Playback Source Selection

W04 Playback 仍为 authority。

W10 只增加 source policy：

```text
if READY cloud-prepared source is valid:
    prefer cloud-prepared source
else:
    fallback local source
```

但必须由产品决定是否自动 prefer。

本包推荐：

```text
READY → prefer prepared source
FAILED/OFFLINE → local fallback
```

如果 cloud source playback 失败：

```text
fallback local
```

且不得导致 Track identity 改变。

输出：

`artifacts/windows/w10/playback-source-policy.md`

---

## 12. Phase 11 — Offline / Network Failure

必须保证：

```text
No Network
≠
No Music
```

### Cases

- offline before request
- offline during upload
- offline during polling
- offline after READY
- signed URL expired
- API 401/403
- API 404
- API 429
- API 5xx
- timeout

本地 Track / Playlist / Queue 仍可继续使用。

---

## 13. Phase 12 — Retry / Backoff

区分：

### Retryable
- timeout
- 429
- temporary 5xx
- connection reset

### Non-retryable
- invalid file
- unsupported format
- unauthorized
- forbidden
- malformed request

禁止无限 retry。

要求：
- max attempts
- backoff
- jitter if appropriate
- user retry action
- no duplicate cloud task

---

## 14. Phase 13 — Cancel

如果 backend 真支持 cancel：
接入。

如果不支持：
UI 不要显示“取消处理”。

本地停止 polling ≠ server job cancelled。

必须准确表达。

---

## 15. Phase 14 — Restart Recovery

W08 snapshot / durable state 应能恢复：

```text
track_id
preparation_id
status last_known
```

重启后：

```text
if active:
    refresh status
if READY:
    re-resolve prepared source
if FAILED:
    retain failure state
```

不要因为重启重新提交任务。

---

## 16. Phase 15 — Minimal UI

保持当前简洁方向。

推荐 Track / current playback 附近只有：

### Not requested
```text
用 Moodify 准备
```

### Active
```text
正在准备…
```

### Ready
```text
准备完成
```

### Failed
```text
准备失败
重试
```

### Offline
```text
网络不可用
```

如果产品希望“准备”默认自动触发，也必须基于真实后端成本与行为，而不是 W10 自作决定。

### 禁止

用户 UI 不展示：

```text
Stem separation
Ear score
Judge
Intervention
Evidence
Audiolla
FFmpeg
Worker
job internal state
```

---

## 17. Phase 16 — UI Trigger Policy

必须在：

`artifacts/windows/w10/preparation-trigger-policy.md`

明确：

```text
MANUAL
AUTO_ON_IMPORT
AUTO_ON_FIRST_PLAY
SERVER_DEFINED
```

推荐 W10 初期：

```text
MANUAL
```

原因：
- 云端链仍在形成
- 成本可控
- 避免用户导入大量歌曲后自动产生大量任务
- 更容易验证

除非 W09/W10 当前产品已有明确自动策略。

---

## 18. Phase 17 — Error Wording

对用户只输出可理解状态：

```text
网络不可用
暂时无法准备这首歌
这首歌暂不支持云端准备
登录状态已失效
准备失败，请重试
```

不要输出：
- HTTP stack
- internal worker name
- database error
- third-party provider name
- secret IDs

---

## 19. Phase 18 — Telemetry / Evidence

至少内部记录：

```text
request started
request accepted
preparation id
status transitions
request duration
upload duration
READY
FAILED
retry count
fallback-to-local
```

不要记录完整私密音频内容。

不要在 evidence 中放用户真实私有音乐文件。

---

## 20. Phase 19 — Tests

### Capability
- endpoint verified
- auth verified
- request verified
- status verified
- prepared source verified

### Request
- one Track
- repeated click
- invalid file
- unavailable local source
- timeout

### Status
- QUEUED
- PREPARING
- READY
- FAILED
- unknown status

### Retry
- 429
- timeout
- 5xx
- max retry

### Playback
- local only
- READY cloud source
- cloud source failure → local fallback
- expired source

### Restart
- active preparation
- READY
- FAILED
- no resubmit

### Security
- no service secret in client
- auth token scoped
- signed URL handling
- logs

### Regression
- W02-W09 all main flows
- offline local playback
- no Track authority duplication
- no Playback authority duplication

---

## 21. Required Outputs

写入：

`artifacts/windows/w10/`

至少：

1. `W10_IMPLEMENTATION_REPORT.md`
2. `preflight.md`
3. `cloud-capability-matrix.md`
4. `cloud-client-boundary.md`
5. `cloud-preparation-contract.md`
6. `track-cloud-mapping.md`
7. `cloud-auth-boundary.md`
8. `idempotency-policy.md`
9. `preparation-trigger-policy.md`
10. `status-refresh-policy.md`
11. `playback-source-policy.md`
12. `offline-retry-policy.md`
13. `cloud-security-review.md`
14. `cloud-test-report.md`
15. `evidence-manifest.json`
16. `W11_HANDOFF.md`

---

## 22. Definition of Done

### Minimum PASS

至少必须真实证明：

```text
Windows Track
→ verified cloud request
→ verified status
```

且：

```text
offline/local playback remains safe
```

### Full PASS

如果真实后端已经支持：

```text
request
→ preparation
→ READY
→ prepared source
→ Playback
```

则完整打通。

如果后端只完成到中间：
必须输出 `VERIFIED_PARTIAL`，而不是伪造完成。

最后：

```text
W10_STATUS = PASS | PARTIAL | BLOCKED
W11_GATE = PASS | BLOCKED
CLOUD_CHAIN = VERIFIED_LIVE | VERIFIED_PARTIAL | BLOCKED
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```
