# Auth / Idempotency / Security Contract

## Client Secrets

Windows 客户端禁止保存：

```text
server master key
service-key
database password
Audiolla/LALAL.AI secret
cloud admin credential
```

如果真实 API 目前只能用 service-key：
W10 应标记 CLIENT_AUTH_BLOCKED。

## Recommended Client Auth

可接受：

```text
user/session token
short-lived signed upload URL
short-lived prepared-source URL
scoped token
```

## Idempotency

同一 Track 的并行 active request 必须阻止。

若 backend 支持 idempotency key，必须使用。

推荐 identity 输入：

```text
track_id
+ source revision/fingerprint
```

## Logs

不得记录：
- access token
- signed URL query secret
- service credential
- raw private audio

## Endpoint Config

生产 endpoint 不应散落硬编码。

使用现有 config/environment/channel。
