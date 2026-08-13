# Moodify Music — Shared Client Contract (v1)

Status: FROZEN — MFY_MUSIC_APP_FOUNDATION_001 Checkpoint C
Consumers: Music Web/TS、Music Android/Kotlin。同一服务端事实，客户端仅解析。

## 传输

- HTTPS only；base URL：`https://rongjinwenchuan.xyz/api/v1/music`
- 客户端永不直连 PolarDB；永不持有内部 service key。

## 错误模型（全部端点）

```json
{ "error": { "code": "RESOURCE_NOT_FOUND", "message": "...", "request_id": "..." } }
```

| 字段 | 语义 |
|---|---|
| code | 稳定机器码（见枚举表），不得从 message 解析 |
| message | 人类可读，可翻译 |
| request_id | 每请求生成/透传；日志排查键 |

HTTP 状态：400 校验、401 匿名、403 所有权、404 不存在、409 冲突（幂等/重复）、412 并发、413/415/422 媒体、503 Beta 门控/容量、504 上游超时。

## 分页

- `cursor` 参数 + `next_cursor` 响应；keyset 稳定排序（时间戳+id），刷新不重复不漏项。
- `limit` 默认/上限每端点固定；超限 400 INVALID_LIMIT。

## Capability 语义

`bootstrap` 响应中的 `capabilities`：

| 字段 | 含义 |
|---|---|
| account_actions | 账户写（收藏/关注/歌单/Library） |
| creator_writes | 创作者写（发布/护照/控制台） |

未登录或受限账户：capabilities 为 false；**UI 禁用而非报错**。

## 状态枚举（TS 与 Kotlin 共用，禁止漂移）

| 域 | 值 |
|---|---|
| track.status | draft / published / unlisted / archived |
| track visibility | public / private |
| license_intent.status | submitted / reviewing / contacted / accepted / declined / closed |
| support_intent.status | expressed / contact_requested / cancelled |
| lifecycle stage | draft / version_ready / passport_ready / published / archived |
| playlist.visibility | private / public |

## 幂等

关键写：`Idempotency-Key` 头（客户端生成 UUID）。同 key 同 payload 重放原响应；
不同 payload → 409 IDEMPOTENCY_CONFLICT。超时重试必须复用同 key。

## 媒体

- 音频 URL：`https://rongjinwenchuan.xyz/audio/{asset_key}`（Range 支持）。
- 封面缺省：统一 Moodify 黑胶（客户端不得伪造独立封面）。
- 音频 Range 响应不得缓存截断；播放失败显示可恢复提示。

## TS / Kotlin 一致性

- 类型来源：本契约 + music-client.ts（TS 权威实现）；Kotlin DTO 逐字段映射
  （apps/music-android/.../dto/*.kt），由 fixture JSON（`shared-fixtures/`）双端解析验证。

## 未承诺

- 离线曲库下载（V1 不做）；后台播放受平台限制（iOS Safari 无后台、Android 需
  MediaSession+前台服务策略），不承诺平台不支持行为。
