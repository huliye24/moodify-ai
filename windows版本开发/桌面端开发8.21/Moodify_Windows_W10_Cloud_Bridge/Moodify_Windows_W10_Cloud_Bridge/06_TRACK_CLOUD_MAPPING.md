# Track ↔ Cloud Mapping

## Principle

Track 仍是核心身份。

推荐：

```text
Track.id
  ↓
CloudPreparation.track_id
  ↓
PreparedSource
```

## Local + Cloud

一个 Track 可以同时有：

```text
LOCAL source
CLOUD_PREPARED source
```

它们不是两首不同的歌。

## Versioning

如果 backend 返回多个 prepared versions：

W10 只需要：
- identify latest/current usable version
- avoid accidental duplicate active version

复杂版本浏览留未来。

## Source Revision

如果本地源文件内容发生变化：
旧 CloudPreparation 是否仍有效必须明确。

推荐用：
- source revision
- checksum
- source fingerprint
- import revision

之一判断。

不得仅凭 filename 认为还是同一个云准备结果。
