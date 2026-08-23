# W08 UI Recovery Contract

```text
VISUAL_REDESIGN = FORBIDDEN
```

默认恢复应尽量静默。

允许最小状态：

```text
无法恢复上次播放状态
```

或：

```text
本地文件不可用
```

## 禁止

- recovery dashboard
- raw snapshot viewer
- schema migration UI
- stack trace
- engineering logs
- modal spam on every startup

## Principle

正常恢复：
```text
用户几乎感觉不到
```

异常恢复：
```text
用户仍然能继续使用
```
