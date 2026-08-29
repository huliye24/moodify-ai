# MFD-003 Security & Auth Boundary

## 核心原则

Desktop 是不可信客户端。

即使它是我们的官方程序，也必须假设：

- 用户可以反编译；
- 用户可以读本地文件；
- 用户可以抓包；
- 用户可以修改 renderer；
- 用户可以复制 token；
- 用户可以调用公开 API。

因此：

> **所有真正的权限控制必须发生在服务器。**

---

## Desktop 可以持有

- user session token
- refresh token（若安全策略允许）
- public API base URL
- app version
- non-secret client id

---

## Desktop 绝对不能持有

- service key
- DB password
- OSS access key secret
- Cloudflare API token
- Audiolla token
- LALAL token
- private infrastructure credentials

---

## Token Storage

MFD-003 如果落地 auth：

优先使用 OS-backed secure storage。

如 MFD-002 尚未建立：

可以实现 token storage abstraction。

禁止：

```text
token.json
localStorage plaintext
settings.json plaintext
source code constant
.env packaged into app
```

---

## Signed URL

signed URL 本身属于临时敏感信息。

要求：

- 不长期持久化
- 不完整打印日志
- 过期后重新请求 manifest
- 不当作永久媒体地址保存

---

## Authorization

服务端必须确认：

```text
session.user
    can access
track
    can receive
playback manifest
```

不能只判断：

> track id 存在。

---

## Rate limit

Alpha 可以轻量，但至少考虑：

- manifest abuse
- auth brute force
- asset URL regeneration abuse

不要求复杂计费系统。
