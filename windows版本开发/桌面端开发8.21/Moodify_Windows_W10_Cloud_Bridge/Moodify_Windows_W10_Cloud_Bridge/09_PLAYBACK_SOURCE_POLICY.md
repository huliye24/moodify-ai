# Playback Source Policy

W04 Playback authority 不变。

W10 只提供 source candidate。

推荐：

```text
if CloudPreparation == READY
and prepared source resolves
and source is valid:
    prefer CLOUD_PREPARED
else:
    use LOCAL
```

## Failure

cloud source load/play failure：

```text
record failure
→ fallback LOCAL if available
```

不得：
- 改 Track ID
- 清 Queue
- 删除 Playlist relation

## Offline

如果 cloud asset 需要网络：
offline 时直接 local fallback。

## Expiry

signed URL 过期：
```text
refresh/resign if supported
else local fallback
```

## User Visibility

用户不需要看到 URL/asset id。

只需要知道：
```text
准备完成
```
或：
```text
当前使用本地版本
```

后者甚至可以不主动显示，保持简洁。
